"""Fail-closed qualification of recorded fields, not a transport/clock proof.

The three original positional arguments are preserved. Importing this module
does not import or execute the private runtime. See private_record_qualification
for the preserved dc5269c source, scope, and synthetic regression tests.
"""
from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import importlib
import json
import math
from pathlib import Path
import re
import sys


HERE = Path(__file__).resolve().parent
DEFAULT_INDEX = HERE.parent / "formal_campaign_audit/results/ATTEMPT_INDEX.json"
LEGACY = HERE / "private_record_qualification/legacy/qualify_private_records_dc5269c.py"
CAPS = {"low": 131072, "mid": 262144, "high": 393216}
ROLES = {"core", "P1", "P2", "P3"}
PROBES = ("P1", "P2", "P3")
ARM_PATTERN = re.compile(r"(F12_S\d{2})_([A-F])_(low|mid|high)_(a\d{2})\Z")
LIMITATIONS = [
    "Only archived recorded fields are checked; no hardware or detector is run.",
    "Package-tree digests are manifest attestations, not independent remote per-file receipts.",
    "Primitive transport chunk offsets, wire/NIC delivery, and in-flight transitions are not reconstructed.",
    "Boot epochs and cross-host clock alignment are not independently established.",
    "Return latency uses recorded creation and return timestamps on the originating probe only.",
    "Core stage rows are counted but their computation durations and queue ordering are not qualified.",
    "Optional window/manifest identity fields are checked when present; absent fields are counted.",
    "Historical event_key strings are opaque; uniqueness is scoped to the arm/probe, with explicit run/device/origin binding.",
    "Terminal byte conservation alone does not prove delivery, a returned result, or detection accuracy.",
    "A PASS here does not replace historical exclusions or certify a new physical campaign.",
]


class InvalidRecord(ValueError):
    def __init__(self, code: str, detail: str):
        super().__init__(detail)
        self.code = code


def require(condition: bool, code: str, detail: str) -> None:
    if not condition:
        raise InvalidRecord(code, detail)


def integer(value, name: str) -> int:
    require(type(value) is int and value >= 0, "invalid_integer",
            f"{name} must be a nonnegative integer, excluding bool and float")
    return value


def boolean(value, name: str) -> bool:
    require(type(value) is bool, "invalid_boolean", f"{name} must be a boolean")
    return value


def text(value, name: str) -> str:
    require(isinstance(value, str) and bool(value), "invalid_identity", f"{name} must be a nonempty string")
    return value


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def strict_json(data: bytes):
    def no_constant(value):
        raise InvalidRecord("nonfinite_json", f"non-finite JSON constant: {value}")
    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, "duplicate_json_key", f"duplicate JSON key: {key}")
            result[key] = value
        return result
    return json.loads(data, parse_constant=no_constant, object_pairs_hook=unique_object)


def load_runtime_tree(runtime: Path) -> str:
    """Load the supplied archived helper only when explicitly running an audit."""
    runtime = runtime.resolve()
    sys.path.insert(0, str(runtime))
    try:
        module = importlib.import_module("netshield.common")
        require(Path(module.__file__).resolve().is_relative_to(runtime),
                "runtime_import_identity", "package-tree helper was imported outside the supplied runtime")
        digest = module.package_tree_sha256()
    finally:
        sys.path.pop(0)
    require(isinstance(digest, str) and re.fullmatch(r"[0-9a-f]{64}", digest) is not None,
            "runtime_tree_digest", "runtime package-tree digest is not a SHA-256 hex string")
    return digest


class Checker:
    def __init__(self, campaign: Path, runtime: Path, expected_index: Path):
        self.campaign, self.runtime, self.expected_index = campaign, runtime, expected_index
        self.registry = {}
        self.counts = Counter({name: 0 for name in (
            "runtime_manifest_matches", "checked_rounds", "verified_rounds", "generated",
            "event_balance_errors", "grant_demand_service_errors", "duplicate_events",
            "queue_residuals", "receipt_disagreements", "final_queue_bytes",
            "queued_remaining_bytes", "inflight_payload_bytes", "cancelled_discarded_bytes",
            "duplicate_wire_bytes", "core_required", "returned_core", "timely_core",
            "missing_return", "negative_latency", "arms_completed")})
        self.errors, self.arm_reports = [], []
        self.expected_arms, self.private_arms = [], []
        self.event_keys = set()

    def read(self, path: Path) -> bytes:
        data = path.read_bytes()
        self.registry[str(path.resolve())] = sha256(data)
        return data

    def document(self, path: Path):
        return strict_json(self.read(path))

    def rows(self, path: Path) -> list[dict]:
        result = [strict_json(line) for line in self.read(path).splitlines() if line.strip()]
        require(all(isinstance(row, dict) for row in result), "record_shape", "JSONL rows must be objects")
        return result

    def error(self, code: str, detail: str, arm: str | None = None) -> None:
        self.errors.append({"code": code, "arm": arm, "detail": detail})

    def check_count(self, condition: bool, counter: str, detail: str, arm: str) -> None:
        if not condition:
            self.counts[counter] += 1
            self.error(counter, detail, arm)

    def identity(self, row: dict, arm: str, device: str | None, kind: str) -> None:
        for field, expected in (("run_id", arm), ("device_id", device)):
            if expected is None:
                continue
            if field in row:
                require(row[field] == expected, "identity_mismatch", f"{kind}.{field} differs from its enclosing arm/device")
                self.counts[f"{kind}_{field}_checked"] += 1
            else:
                self.counts[f"{kind}_{field}_absent"] += 1

    def arms(self, index: dict, label: str) -> list[str]:
        require(isinstance(index, dict) and isinstance(index.get("accepted"), list),
                "cohort_shape", f"{label} requires an accepted list")
        result = []
        for item in index["accepted"]:
            require(isinstance(item, dict) and isinstance(item.get("arms"), list),
                    "cohort_shape", f"{label} accepted entries require an arms list")
            for arm in item["arms"]:
                match = ARM_PATTERN.fullmatch(text(arm, "arm"))
                require(match is not None, "arm_identity", f"{label} arm identity has an unsupported shape")
                session, _, _, attempt = match.groups()
                for field, expected in (("session_id", session), ("attempt", attempt)):
                    if field in item:
                        require(item[field] == expected, "arm_identity", f"{label} {field} differs from arm identity")
                result.append(arm)
        require(bool(result), "empty_cohort", f"{label} accepted cohort is empty")
        require(len(result) == len(set(result)), "duplicate_arm", f"{label} repeats an accepted arm")
        return sorted(result)

    def check_cohort(self) -> None:
        self.expected_arms = self.arms(self.document(self.expected_index), "expected index")
        if self.expected_index.resolve() == DEFAULT_INDEX.resolve():
            require(len(self.expected_arms) == 216, "public_cohort_size", "public accepted index must contain 216 unique arms")
        self.private_arms = self.arms(self.document(self.campaign / "ATTEMPT_INDEX.json"), "private index")
        require(self.private_arms == self.expected_arms, "cohort_mismatch",
                f"accepted cohort differs: missing={sorted(set(self.expected_arms)-set(self.private_arms))}; "
                f"extra={sorted(set(self.private_arms)-set(self.expected_arms))}")

    def manifest(self, base: Path, arm: str, role: str, record: dict, tree: str,
                 model_hashes: dict, cap: int) -> Path:
        require(record["identity"]["package_tree_sha256"] == tree,
                "deployment_tree", "deployment package-tree digest differs from archived runtime")
        require(record["models"] == model_hashes, "deployment_models", "deployment model hashes differ from archived model files")
        folder = base / "raw" / ("core" if role == "core" else "probe/" + role) / arm
        meta = self.document(folder / "manifest.json")
        self.identity(meta, arm, role, "manifest")
        require(meta["software"]["package_tree_sha256"] == tree,
                "runtime_manifest_tree", "runtime manifest package-tree digest differs")
        cfg = meta["config"]
        for name in ("app_capacity_bps", "window_seconds"):
            value = cfg[name]
            require(type(value) in (int, float) and math.isfinite(value) and value > 0,
                    "capacity_config", f"{name} must be positive and finite, excluding bool")
        require(Fraction(str(cfg["window_seconds"])) == 1, "window_duration", "primary campaign windows must be one second")
        require(Fraction(str(cfg["app_capacity_bps"])) * Fraction(str(cfg["window_seconds"])) / 8 == cap,
                "capacity_config", "runtime manifest capacity does not match the arm's byte budget")
        for name, expected in (("windows", 95), ("warmup_windows", 5), ("drain_windows", 200)):
            if name in cfg:
                require(integer(cfg[name], name) == expected, "phase_config", f"{name} differs from primary campaign")
        if role != "core":
            pre = self.document(base / "preflight" / (role + ".json"))["data"]
            require(text(pre["hostname"]["stdout"].strip(), "preflight hostname") == text(meta["software"]["hostname"], "runtime hostname"),
                    "hostname_identity", "probe preflight and runtime hostname differ")
        self.counts["runtime_manifest_matches"] += 1
        return folder

    def core_windows(self, folder: Path, arm: str, cap: int) -> dict:
        core = {}
        for row in self.rows(folder / "core_windows.jsonl"):
            kind = row["record_type"]
            if kind == "core_event_stage":
                self.counts["core_event_stages_unqualified"] += 1
                continue
            require(kind == "core_window", "core_record_type", "unsupported core record type")
            window = integer(row["window_index"], "window_index")
            device = text(row["device_id"], "device_id")
            require(device in PROBES, "device_identity", "core window device is not P1/P2/P3")
            self.identity(row, arm, device, "core_window")
            key = device, window
            require(key not in core, "duplicate_core_window", "repeated core device-window identity")
            require(integer(row["shared_cap_bytes"], "shared_cap_bytes") == cap, "shared_cap", "core window cap differs from configured budget")
            for field in ("grant_bytes", "demand_bytes", "evidence_bytes_received"):
                integer(row[field], field)
            self.check_count(row["evidence_bytes_received"] <= row["grant_bytes"] <= row["demand_bytes"],
                             "grant_demand_service_errors", f"receipt/grant/demand inequality at {device}/{window}", arm)
            core[key] = row
        require(set(core) == {(d, w) for d in PROBES for w in range(295)},
                "core_window_coverage", "core windows do not exactly cover 3 devices x 295 windows")
        for window in range(295):
            rows = [core[d, window] for d in PROBES]
            cap_ok = sum(r["grant_bytes"] for r in rows) <= cap
            self.check_count(cap_ok, "aggregate_grant_cap_errors", f"summed grants exceed cap in window {window}", arm)
            self.counts["checked_rounds"] += 1
            if cap_ok and all(r["evidence_bytes_received"] <= r["grant_bytes"] <= r["demand_bytes"] for r in rows):
                self.counts["verified_rounds"] += 1
        return core

    def probe_windows(self, folder: Path, arm: str, device: str, core: dict) -> None:
        windows = self.rows(folder / "probe_windows.jsonl")
        indices = [integer(r["window_index"], "window_index") for r in windows]
        require(indices == list(range(295)), "probe_window_coverage", "probe windows must be ordered, unique, and exactly 0..294")
        queue = 0
        for window, row in enumerate(windows):
            self.identity(row, arm, device, "probe_window")
            drain = boolean(row.get("drain_window", False), "drain_window")
            if drain:
                require(integer(row["generated_events"], "generated_events") == 0, "drain_generation", "drain window generated events")
                generated, sent = 0, integer(row["application_payload_bytes"], "application_payload_bytes")
            else:
                generated = integer(row["payload_generated_bytes"], "payload_generated_bytes")
                sent = integer(row["payload_delivered_bytes"], "payload_delivered_bytes")
            current = integer(row["queue_bytes"], "queue_bytes")
            self.check_count(queue + generated - sent == current, "queue_residuals", f"queue recurrence at {device}/{window}", arm)
            self.check_count(sent == core[device, window]["evidence_bytes_received"], "receipt_disagreements", f"probe/core receipt at {device}/{window}", arm)
            queue = current
        self.counts["final_queue_bytes"] += queue

    def events(self, folder: Path, arm: str, device: str) -> None:
        events = [e for e in self.rows(folder / "event_ledger.jsonl") if e.get("window_phase") == "measured"]
        origins = [integer(e["origin_window_index"], "origin_window_index") for e in events]
        require(len(origins) == 90 and set(origins) == set(range(5, 95)),
                "event_origin_coverage", "measured origins must occur exactly once each at 5..94")
        for event in events:
            require(event["device_id"] == device and event["run_id"] == arm,
                    "event_identity", "measured event device/run differs from its enclosing identity")
            deadline = integer(event["deadline_ns"], "deadline_ns")
            require(deadline == 10**9, "event_deadline", "primary measured deadline must be one second")
            key = text(event["event_key"], "event_key")
            # The original primary reviewer treats event_key as opaque and
            # checks uniqueness within each arm/probe. Do not import a key
            # grammar from the separate CRFA export into this private schema.
            namespaced_key = arm, device, key
            if namespaced_key in self.event_keys:
                self.counts["duplicate_events"] += 1
                raise InvalidRecord("duplicate_event_key", "event key is repeated within an arm/probe")
            self.event_keys.add(namespaced_key)
            self.counts["event_key_opaque_format"] += 1
            fields = ("payload_bytes", "unique_payload_received_bytes", "queued_remaining_bytes",
                      "inflight_payload_bytes", "cancelled_discarded_bytes", "duplicate_wire_bytes")
            for field in fields:
                integer(event[field], field)
            self.check_count(event["payload_bytes"] == sum(event[f] for f in fields[1:5]),
                             "event_balance_errors", f"measured event byte balance at {device}/{event['origin_window_index']}", arm)
            for field in fields[2:]:
                self.counts[field] += event[field]
            self.counts["generated"] += 1
            if boolean(event["requires_core"], "requires_core"):
                self.counts["core_required"] += 1
                created = integer(event["created_probe_monotonic_ns"], "created_probe_monotonic_ns")
                returned = event["result_received_monotonic_ns"]
                if returned is None:
                    self.counts["missing_return"] += 1
                else:
                    returned = integer(returned, "result_received_monotonic_ns")
                    self.counts["returned_core"] += 1
                    self.check_count(returned >= created, "negative_latency", f"negative origin-clock return duration at {device}/{event['origin_window_index']}", arm)
                    self.counts["timely_core"] += 0 <= returned - created <= deadline

    def audit_arm(self, arm: str, tree: str, models: dict) -> None:
        session, method, capacity, attempt = ARM_PATTERN.fullmatch(arm).groups()
        base = self.campaign / session / ("attempt_" + attempt) / (method + "_" + capacity)
        deployed = self.document(base / "manifests/deployment.json")
        require(isinstance(deployed, dict) and set(deployed) == ROLES, "deployment_roles", "deployment roles must be exactly core/P1/P2/P3")
        folders = {role: self.manifest(base, arm, role, deployed[role], tree, models, CAPS[capacity]) for role in sorted(ROLES)}
        core = self.core_windows(folders["core"], arm, CAPS[capacity])
        for device in PROBES:
            self.probe_windows(folders[device], arm, device, core)
            self.events(folders[device], arm, device)
        self.counts["arms_completed"] += 1

    def run(self) -> dict:
        try:
            self.check_cohort()
            tree = load_runtime_tree(self.runtime)
            model_hashes = {p.stem: sha256(self.read(p)) for p in sorted((self.runtime / "artifacts/portable_models").glob("*.npz"))}
            require(len(model_hashes) == 3, "model_roster", "archived primary runtime must supply three model weight files")
            for path in sorted((self.runtime / "netshield").rglob("*.py")):
                self.read(path)
            for arm in self.private_arms:
                before, first_error = self.counts.copy(), len(self.errors)
                completed = False
                try:
                    self.audit_arm(arm, tree, model_hashes)
                    completed = True
                except (InvalidRecord, KeyError, TypeError, ValueError, OSError) as exc:
                    self.error(getattr(exc, "code", "input_schema_or_io"), str(exc), arm)
                self.arm_reports.append({"arm": arm, "scan_completed": completed,
                                         "error_count": len(self.errors) - first_error,
                                         "counts": dict(self.counts - before)})
        except (InvalidRecord, KeyError, TypeError, ValueError, OSError, ImportError, AttributeError) as exc:
            self.error(getattr(exc, "code", "input_schema_or_io"), str(exc))
        pending = any(self.counts[k] for k in ("queued_remaining_bytes", "inflight_payload_bytes", "final_queue_bytes", "missing_return"))
        status = "FAIL" if self.errors else "PENDING_TERMINAL_STATE" if pending else "PASS_RECORDED_FIELDS_ONLY"
        terminal = "UNQUALIFIED_DUE_TO_ERRORS" if self.errors else "PENDING" if pending else "CLOSED_WITH_CANCELLATIONS" if self.counts["cancelled_discarded_bytes"] else "RECORDED_QUEUES_DRAINED_AND_REQUIRED_RETURNS_PRESENT"
        return {
            "schema_version": 1, "status": status, "terminal_state": terminal,
            "scope": "PARTIAL_ARCHIVED_RECORD_QUALIFICATION_NOT_PRIMITIVE_TRANSPORT_OR_CLOCK_PROOF",
            "expected_index_is_repository_default": self.expected_index.resolve() == DEFAULT_INDEX.resolve(),
            "expected_index_sha256": self.registry.get(str(self.expected_index.resolve())),
            "private_index_sha256": self.registry.get(str((self.campaign / "ATTEMPT_INDEX.json").resolve())),
            "expected_arm_count": len(self.expected_arms), "input_arm_count": len(self.private_arms),
            "counts": dict(self.counts), "errors": self.errors, "arms": self.arm_reports,
            "limitations": LIMITATIONS,
            "checker_sha256": sha256(Path(__file__).read_bytes()),
            "legacy_checker_sha256": sha256(LEGACY.read_bytes()),
            "private_sources": self.registry,
        }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("campaign", type=Path)
    parser.add_argument("runtime", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--expected-index", type=Path, default=DEFAULT_INDEX,
                        help="explicit alternative cohort, primarily for synthetic fixtures; default is the public 216-arm index")
    args = parser.parse_args(argv)
    if args.output.exists():
        print("Refusing to overwrite an existing qualification report.", file=sys.stderr)
        return 1
    report = Checker(args.campaign, args.runtime, args.expected_index).run()
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")
    print(json.dumps({"status": report["status"], "expected_arm_count": report["expected_arm_count"],
                      "arms_completed": report["counts"]["arms_completed"], "errors": len(report["errors"])}))
    return 1 if report["status"] == "FAIL" else 2 if report["status"] == "PENDING_TERMINAL_STATE" else 0


if __name__ == "__main__":
    raise SystemExit(main())
