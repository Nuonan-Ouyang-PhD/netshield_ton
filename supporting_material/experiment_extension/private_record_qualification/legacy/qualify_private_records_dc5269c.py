"""Check the accepted primary records against runtime and capacity identities."""
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

root, runtime, output = map(Path, sys.argv[1:])
sys.path.insert(0, str(runtime.resolve()))
from netshield.common import package_tree_sha256

registry = {}
counts = Counter()


def read(path):
    data = path.read_bytes()
    registry[str(path)] = hashlib.sha256(data).hexdigest()
    return data


def rows(path):
    return map(json.loads, read(path).splitlines())


tree = package_tree_sha256()
model_hashes = {p.stem: hashlib.sha256(read(p)).hexdigest()
                for p in (runtime / "artifacts/portable_models").glob("*.npz")}
for p in sorted((runtime / "netshield").rglob("*.py")):
    read(p)
roles = {"core","P1","P2","P3"}
primary = json.loads(read(root / "ATTEMPT_INDEX.json"))
for item in primary["accepted"]:
    for arm in item["arms"]:
        f, s, m, k, a = arm.split("_")
        base = root / (f+"_"+s) / ("attempt_"+a) / (m+"_"+k)
        deployed = json.loads(read(base/"manifests/deployment.json"))
        assert set(deployed) == roles
        cap = {"low":131072,"mid":262144,"high":393216}[k]
        for role, record in deployed.items():
            assert record["identity"]["package_tree_sha256"] == tree
            assert record["models"] == model_hashes
            folder = base/"raw"/("core" if role=="core" else "probe/"+role)/arm
            meta = json.loads(read(folder/"manifest.json"))
            assert meta["software"]["package_tree_sha256"] == tree
            cfg = meta["config"]
            assert cfg["app_capacity_bps"]*cfg["window_seconds"]/8 == cap
            counts["runtime_manifest_matches"] += 1
            if role == "core":
                continue
            pre = json.loads(read(base/"preflight"/(role+".json")))["data"]
            assert pre["hostname"]["stdout"].strip() == meta["software"]["hostname"]
            windows = list(rows(folder/"probe_windows.jsonl"))
            assert [r["window_index"] for r in windows] == list(range(295))
            events = [e for e in rows(folder/"event_ledger.jsonl") if e.get("window_phase")=="measured"]
            assert {e["origin_window_index"] for e in events} == set(range(5,95)) and len(events)==90
            for e in events:
                assert e["device_id"]==role and e["run_id"]==arm and e["deadline_ns"]==10**9
                counts["event_balance_errors"] += e["payload_bytes"] != sum(e[q] for q in (
                    "unique_payload_received_bytes","queued_remaining_bytes","inflight_payload_bytes","cancelled_discarded_bytes"))
                for q in ("duplicate_wire_bytes","inflight_payload_bytes","cancelled_discarded_bytes"):
                    counts[q] += e[q]
        by_window = {}
        for r in rows(base/"raw/core"/arm/"core_windows.jsonl"):
            if r["record_type"]!="core_window":
                continue
            w = by_window.setdefault(r["window_index"], {})
            assert r["device_id"] not in w and r["shared_cap_bytes"]==cap
            w[r["device_id"]] = r["grant_bytes"]
            counts["grant_demand_service_errors"] += not (0<=r["evidence_bytes_received"]<=r["grant_bytes"]<=r["demand_bytes"])
        assert set(by_window)==set(range(295))
        for w in by_window.values():
            assert set(w)==roles-{"core"} and sum(w.values())<=cap
            counts["verified_rounds"] += 1
with output.open("x") as stream:
    json.dump(dict(counts=counts, private_sources=registry),stream)
