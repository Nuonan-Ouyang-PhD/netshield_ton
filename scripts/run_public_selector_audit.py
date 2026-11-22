#!/usr/bin/env python3
"""Audit deterministic repeats and allocator sensitivity using public inputs.

The ten rounded utilities and payloads are transcribed from the manuscript,
not recovered from the private actions.json. Timing fields are deliberately
absent: this unshielded selector does not read them. This is a public
reconstruction, not a rerun of the frozen private workload or hardware.
"""
from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import math
import sys
from collections import Counter, defaultdict, deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "supporting_material/methodology_repair"
sys.path.insert(0, str(PACKAGE))
import run_methodology_repair as corrected

PUBLIC_VALUES = (
    ("L_NONE", 0, 0.758501), ("L_ALERT", 256, 0.825168),
    ("L_SUMMARY", 4096, 0.891835), ("M_NONE", 0, 0.766968),
    ("M_ALERT", 256, 0.833635), ("M_SUMMARY", 8192, 0.900302),
    ("H_NONE", 0, 0.768378), ("H_ALERT", 256, 0.835044),
    ("H_SUMMARY", 16384, 0.901711), ("H_FULL", 131072, 0.968378),
)
COMPARE_FIELDS = ("action_counts", "core_required_fraction", "payload_bytes",
                  "queue_trajectory_bytes", "max_queue_bytes")
SIMULATION_FIELDS = COMPARE_FIELDS + (
    "post_release_on_time_core_result_coverage", "core_required_events",
    "on_time_core_results", "detected_period_windows", "period_start_measured_window",
    "complete_period_repeats", "drain_windows_used", "final_queue_bytes", "shared_cap_violations",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def public_actions() -> list[dict]:
    return [{"id": name, "payload": payload, "utility": utility,
             "detector": {"L": "light", "M": "medium", "H": "heavy"}[name[0]],
             "execution": "core" if name == "H_FULL" else "local",
             "evidence": name.split("_")[1].lower()}
            for name, payload, utility in PUBLIC_VALUES]


def legacy_functions(path: Path, actions: list[dict]) -> dict:
    """Load only the audited pure function definitions, not private I/O setup."""
    wanted = {"select_local", "waterfill", "consume_fifo", "action_mix", "detect_period", "simulate_synchronous"}
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    definitions = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in wanted]
    if {node.name for node in definitions} != wanted:
        raise ValueError("historical source does not contain expected pure functions")
    namespace = {"Counter": Counter, "deque": deque, "Any": object, "math": math,
                 "ACTIONS": actions, "ACTION_IDS": tuple(a["id"] for a in actions)}
    for name in ("DEVICES", "CAPACITY_BYTES", "CAPACITY_BPS", "WINDOWS", "WARMUP", "MEASURED", "MAX_DRAIN_WINDOWS"):
        namespace[name] = getattr(corrected, name)
    exec(compile(ast.Module(body=definitions, type_ignores=[]), str(path), "exec"), namespace)
    return namespace


def decoded(row: dict, field: str):
    value = row[field]
    if value == "":
        return None
    return json.loads(value)


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def run(output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    frozen_path = PACKAGE / "V_SWEEP_RESULTS.csv"
    legacy_path = PACKAGE / "legacy/run_methodology_repair_v1_3.py"
    with frozen_path.open(newline="", encoding="utf-8") as handle:
        frozen = list(csv.DictReader(handle))
    groups = defaultdict(list)
    for row in frozen:
        groups[int(row["v"]), row["capacity"]].append(row)
    actions = public_actions()
    corrected.configure_actions(actions)
    historical = legacy_functions(legacy_path, actions)
    dedup, comparisons = [], []
    trajectory_deltas = 0
    changed_actions = 0
    frozen_matches = 0
    for (weight, capacity), records in sorted(groups.items()):
        signatures = {canonical({field: decoded(row, field) for field in SIMULATION_FIELDS}) for row in records}
        traces = {canonical(decoded(row, "queue_trajectory_bytes")) for row in records}
        dedup.append({"v": weight, "capacity": capacity, "archived_rows": len(records),
                      "distinct_seed_labels": len({row["seed"] for row in records}),
                      "distinct_simulation_outcomes": len(signatures), "distinct_trajectories": len(traces),
                      "independent_random_replicates": 0})
        old = historical["simulate_synchronous"]("synchronized_independent", capacity, 0, weight)
        new = corrected.simulate_synchronous("synchronized_independent", capacity, 0, weight)
        another_seed = corrected.simulate_synchronous("synchronized_independent", capacity, 789123, weight)
        if new != another_seed:
            raise AssertionError("unshielded synchronized selector unexpectedly depends on seed")
        matches = {field: old[field] == decoded(records[0], field) for field in COMPARE_FIELDS}
        match = all(matches.values())
        frozen_matches += match
        action_changed = old["action_counts"] != new["action_counts"]
        changed_actions += action_changed
        trajectory_changed = old["queue_trajectory_bytes"] != new["queue_trajectory_bytes"]
        trajectory_deltas += trajectory_changed
        comparisons.append({
            "v": weight, "capacity": capacity,
            "public_legacy_matches_frozen_selected_fields": match,
            "mismatched_fields": ";".join(key for key, value in matches.items() if not value),
            "action_counts_changed": action_changed, "trajectory_changed": trajectory_changed,
            "legacy_core_required_fraction": old["core_required_fraction"],
            "corrected_core_required_fraction": new["core_required_fraction"],
            "legacy_payload_bytes": old["payload_bytes"], "corrected_payload_bytes": new["payload_bytes"],
            "legacy_max_queue_bytes": old["max_queue_bytes"], "corrected_max_queue_bytes": new["max_queue_bytes"],
            "legacy_period_windows": old["detected_period_windows"], "corrected_period_windows": new["detected_period_windows"],
            "legacy_upload_proxy_count": old["on_time_core_results"],
            "corrected_timely_full_uploads": new["on_time_core_required_uploads"],
            "legacy_action_counts": canonical(old["action_counts"]),
            "corrected_action_counts": canonical(new["action_counts"]),
        })
    write_csv(output / "TASK_A_REPLICATION_AUDIT.csv", dedup)
    write_csv(output / "PUBLIC_SELECTOR_COMPARISON.csv", comparisons)
    result = {
        "evidence_type": "public_parameter_reconstruction_and_frozen_table_audit",
        "private_workload_or_action_table_loaded": False, "hardware_rerun": False,
        "archived_rows": len(frozen), "parameter_configurations": len(groups),
        "all_configs_have_one_archived_trajectory": all(r["distinct_trajectories"] == 1 for r in dedup),
        "all_configs_have_one_archived_simulation_outcome": all(r["distinct_simulation_outcomes"] == 1 for r in dedup),
        "legacy_reconstruction_matches_selected_frozen_fields_cases": frozen_matches,
        "compared_fields": list(COMPARE_FIELDS),
        "corrected_cases_with_changed_trajectory": trajectory_deltas,
        "corrected_cases_with_changed_action_counts": changed_actions,
        "corrected_seed_independence_cases": len(groups),
        "utilities_precision": "six decimals as published; not the private full-precision action file",
        "corrected_allocation_policy": "work-conserving integer max-min with round-rotating residual priority",
        "latency_scope": "round-end upload proxy; no compute, Wi-Fi, core execution or result return",
        "public_actions": actions,
        "inputs_sha256": {
            "archived_csv": sha(frozen_path), "legacy_source": sha(legacy_path),
            "corrected_source": sha(PACKAGE / "run_methodology_repair.py"),
            "primitives": sha(PACKAGE / "simulation_primitives.py"), "audit_script": sha(Path(__file__)),
        },
    }
    (output / "PUBLIC_SELECTOR_AUDIT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "supporting_material/methodology_validation")
    summary = run(parser.parse_args().output)
    print(json.dumps({key: value for key, value in summary.items() if key not in {"public_actions", "inputs_sha256"}}, indent=2))
