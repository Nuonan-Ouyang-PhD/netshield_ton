"""Read accepted RC1 window and event records. Output one row per arm."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path


def records(path, sources):
    raw = path.read_bytes()
    sources[str(path)] = hashlib.sha256(raw).hexdigest()
    return [json.loads(line) for line in raw.splitlines() if line.strip()]


def audit(root, arm, sources):
    session, number, method, capacity, attempt = arm.split("_")
    folder = root / f"{session}_{number}" / f"attempt_{attempt}" / f"{method}_{capacity}"
    deployment = json.loads((folder / "manifests/deployment.json").read_text())
    identities = sorted({v["identity"]["package_tree_sha256"] for v in deployment.values()})
    counts = Counter()
    service = defaultdict(Counter)
    core = {}
    for row in records(folder / "raw/core" / arm / "core_windows.jsonl", sources):
        if row["record_type"] == "core_event_stage":
            counts["core_event_stages"] += 1
            continue
        key = row["device_id"], row["window_index"]
        counts["duplicate_core_windows"] += key in core
        core[key] = row
        s = service[key[1]]
        for field in ("grant_bytes", "demand_bytes", "evidence_bytes_received"):
            s[field] += row[field]
        s["cap"] = row["shared_cap_bytes"]
    for device in ("P1", "P2", "P3"):
        base = folder / "raw/probe" / device / arm
        queue = 0
        for index, row in enumerate(records(base / "probe_windows.jsonl", sources)):
            counts["window_order_errors"] += index != row["window_index"]
            peer = core.pop((device, row["window_index"]))
            if row.get("drain_window"):
                assert row["generated_events"] == 0
                sent = row["application_payload_bytes"]
                generated = 0
            else:
                sent = row["payload_delivered_bytes"]
                generated = row["payload_generated_bytes"]
            counts["queue_residuals"] += queue + generated - sent != row["queue_bytes"]
            counts["receipt_disagreements"] += sent != peer["evidence_bytes_received"]
            queue = row["queue_bytes"]
        counts["final_queue_bytes"] += queue
        seen = set()
        for e in records(base / "event_ledger.jsonl", sources):
            if e.get("window_phase") != "measured":
                continue
            counts["generated"] += 1
            counts["duplicate_events"] += e["event_key"] in seen
            seen.add(e["event_key"])
            if e["requires_core"]:
                counts["core_required"] += 1
                t = e["result_received_monotonic_ns"]
                if t is None:
                    counts["missing_return"] += 1
                else:
                    dt = t - e["created_probe_monotonic_ns"]
                    counts["negative_latency"] += dt < 0
                    counts["timely_core"] += 0 <= dt <= e["deadline_ns"]
    counts["unmatched_core_windows"] = len(core)
    counts["rounds"] = len(service)
    for s in service.values():
        counts["receipt_cap_excess_rounds"] += s["evidence_bytes_received"] > s["cap"]
        counts["unallocated_demanded_bytes"] += max(0, min(s["cap"], s["demand_bytes"]) - s["grant_bytes"])
    return dict(arm=arm, identities=identities, **counts)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("campaign", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    index = json.loads((args.campaign / "ATTEMPT_INDEX.json").read_text())
    arms = [arm for item in index["accepted"] for arm in item["arms"]]
    assert len(set(arms)) == len(arms) == 216
    sources = {}
    rows = [audit(args.campaign, arm, sources) for arm in arms]
    with args.output.open("x") as f:
        json.dump(dict(arms=rows, private_sources=sources), f)
