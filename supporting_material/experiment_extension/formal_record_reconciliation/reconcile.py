#!/usr/bin/env python3
"""Reconcile exported review reports; never reopen raw logs or execute models."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DEFAULT_INDEX = ROOT / "supporting_material/formal_campaign_audit/results/ATTEMPT_INDEX.json"
DEFAULT_PRODUCERS = ROOT / "supporting_material/experiment_extension"
IDENTITY = "be34cdd19441e66a0042b60f9fe75eb0277a8b9a9bb8eeb8f8f87b6b393d7085"
COUNTERS = (
    "duplicate_core_windows", "window_order_errors", "queue_residuals",
    "receipt_disagreements", "final_queue_bytes", "generated", "duplicate_events",
    "unmatched_core_windows", "rounds", "receipt_cap_excess_rounds",
    "unallocated_demanded_bytes", "core_event_stages", "core_required",
    "timely_core", "missing_return", "negative_latency",
)
OPTIONAL_COUNTERS = {"core_event_stages", "core_required", "timely_core", "missing_return", "negative_latency"}
ZERO_DIAGNOSTICS = (
    "duplicate_core_windows", "window_order_errors", "queue_residuals", "receipt_disagreements",
    "final_queue_bytes", "duplicate_events", "unmatched_core_windows", "receipt_cap_excess_rounds",
    "missing_return", "negative_latency",
)
ARM_FIELDS = ("arm", "session", "attempt", "method", "capacity", "reported_package_tree_sha256") + COUNTERS
SPLITS = ("train", "validation", "test")
LEVELS = ("alert", "summary", "full")
PRODUCERS = ("review_formal_records.py", "check_split_overlap.py", "check_model_interface.py")
LIMITATIONS = [
    "Reaggregation of exported arm summaries, not an independent reread of the 1,512 private source logs.",
    "Reported package-tree identities are deployment metadata; the producer does not verify expected host roster or rehash every deployed source tree.",
    "The original private_sources registry hashes core/probe windows and event ledgers, not deployment.json or the input accepted index.",
    "Receipt-cap checks use aggregated logged core receipts and the last per-round cap field; they are not explicit grant<=cap or grant<=demand checks.",
    "The producer does not enforce all expected device/window cells, canonical per-device event keys, uniform per-event deadlines or clock epochs.",
    "Probe/core counter agreement is not primitive chunk-offset continuity, retransmission accounting, NIC delivery or independent packet measurement.",
    "Service-round counts include warmup, measured and drain periods; they are not measured wall-clock durations.",
    "core_event_stages includes non-inference evidence paths and is not a count of core inference executions.",
    "Split counts are reported exact feature-hash overlaps; source features are not reread, and near-duplicate, capture-lineage and exact training-input qualification remain open.",
    "The interface diagnostic uses nine archived observations and three new encoders derived from the same model/observation; prediction agreement is by construction, not held-out efficacy or a Raspberry Pi campaign.",
    "No corrected-allocator hardware counterfactual, calibrated Wi-Fi guarantee or evidence-level detection gain is established here.",
]


class ReconciliationError(ValueError):
    pass


def check(value, message):
    if not value:
        raise ReconciliationError(message)


def nonnegative_int(value, field):
    check(type(value) is int and value >= 0, f"{field} must be a nonnegative integer")
    return value


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest_string(value, field):
    check(isinstance(value, str) and bool(re.fullmatch(r"[0-9a-f]{64}", value)), f"invalid SHA-256 in {field}")
    return value


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        check(key not in result, "duplicate JSON object key")
        result[key] = value
    return result


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_pairs,
                      parse_constant=lambda _: (_ for _ in ()).throw(ReconciliationError("nonfinite JSON number")))


def parse_arm(arm):
    check(isinstance(arm, str), "arm must be a string")
    match = re.fullmatch(r"(F12_S(?:0[1-9]|1[0-2]))_([A-F])_(low|mid|high)_(a[0-9]{2})", arm)
    check(match is not None, "unexpected accepted arm identifier")
    session, method, capacity, attempt = match.groups()
    return session, method, capacity, attempt


def accepted_arms(index_path):
    index = load_json(index_path)
    check(isinstance(index, dict) and isinstance(index.get("accepted"), list), "accepted index shape invalid")
    expected, sessions = set(), set()
    for item in index["accepted"]:
        check(isinstance(item, dict) and set(item) == {"session_id", "attempt", "arms"}, "accepted index item shape invalid")
        check(item["session_id"] not in sessions, "duplicate accepted session")
        sessions.add(item["session_id"])
        check(isinstance(item["arms"], list) and len(item["arms"]) == 18, "accepted session must contain 18 arms")
        cells = set()
        for arm in item["arms"]:
            session, method, capacity, attempt = parse_arm(arm)
            check(session == item["session_id"] and attempt == item["attempt"], "accepted index identity mismatch")
            check(arm not in expected, "duplicate accepted arm")
            expected.add(arm)
            cells.add((method, capacity))
        check(cells == {(m, c) for m in "ABCDEF" for c in ("low", "mid", "high")}, "accepted session factorial coverage mismatch")
    check(len(expected) == 216 and len(sessions) == 12, "expected exact 12-session/216-arm accepted cohort")
    return expected


def normalize_arm_rows(rows, expected, *, exported=False):
    check(isinstance(rows, list), "arms must be a list")
    actual, normalized = set(), []
    for raw in rows:
        check(isinstance(raw, dict), "arm row must be an object")
        if exported:
            check(set(raw) == set(ARM_FIELDS), "sanitized arm CSV shape mismatch")
            row = {key: (nonnegative_int(int(value), key) if re.fullmatch(r"0|[1-9][0-9]*", value or "") else (_ for _ in ()).throw(ReconciliationError("invalid CSV counter")))
                   for key, value in raw.items() if key in COUNTERS}
            arm, identities = raw["arm"], [raw["reported_package_tree_sha256"]]
        else:
            allowed = {"arm", "identities", *COUNTERS}
            required = allowed - OPTIONAL_COUNTERS
            check(required <= set(raw) <= allowed, "unknown or missing arm-row fields")
            row = {key: nonnegative_int(raw.get(key, 0), key) for key in COUNTERS}
            arm, identities = raw["arm"], raw["identities"]
        check(arm not in actual, "duplicate arm in exported review")
        actual.add(arm)
        session, method, capacity, attempt = parse_arm(arm)
        check(identities == [IDENTITY], "reported deployment identity mismatch")
        check(row["rounds"] == 295 and row["generated"] == 270, "arm window/occurrence count mismatch")
        check(row["core_required"] <= row["generated"], "core-required exceeds generated")
        check(row["missing_return"] <= row["core_required"], "missing-return exceeds core-required")
        check(row["timely_core"] <= row["core_required"] - row["missing_return"], "timely exceeds observed returned core count")
        out = dict(arm=arm, session=session, attempt=attempt, method=method, capacity=capacity,
                   reported_package_tree_sha256=IDENTITY, **row)
        if exported:
            check(all(raw[key] == out[key] for key in ("session", "attempt", "method", "capacity")), "sanitized arm identity fields disagree")
        normalized.append(out)
    check(actual == expected, "exported arm set differs from exact public accepted index")
    return sorted(normalized, key=lambda row: row["arm"])


def validate_source_registry(registry, expected):
    check(isinstance(registry, dict), "private_sources registry must be an object")
    expected_keys = {(arm, "core", "", "core_windows.jsonl") for arm in expected}
    expected_keys |= {(arm, "probe", device, file) for arm in expected for device in ("P1", "P2", "P3")
                      for file in ("probe_windows.jsonl", "event_ledger.jsonl")}
    found = set()
    for path, value in registry.items():
        check(isinstance(path, str), "private source reference must be a string")
        digest_string(value, "private source registry")
        parts = Path(path).parts
        if len(parts) >= 4 and parts[-4:-2] == ("raw", "core"):
            key = (parts[-2], "core", "", parts[-1])
        elif len(parts) >= 5 and parts[-5:-3] == ("raw", "probe"):
            key = (parts[-2], "probe", parts[-3], parts[-1])
        else:
            raise ReconciliationError("unexpected private source registry structure")
        check(key not in found, "duplicate private source role")
        found.add(key)
    check(found == expected_keys, "private source registry role coverage mismatch")
    return {
        "reported_file_hashes": len(registry),
        "reported_roles": {"core_windows": 216, "probe_windows": 648, "event_ledger": 648},
        "role_coverage_checked_against_accepted_arms": True,
        "private_paths_exported": False, "raw_source_files_opened": 0,
        "original_registry_includes_deployment_or_accepted_index": False,
    }


def arm_aggregates(rows):
    def summarize(group):
        totals = {key: sum(row[key] for row in group) for key in COUNTERS}
        totals["arms"] = len(group)
        totals["returned_core"] = totals["core_required"] - totals["missing_return"]
        totals["returned_late_core"] = totals["returned_core"] - totals["timely_core"]
        totals["timely_per_generated"] = totals["timely_core"] / totals["generated"]
        totals["timely_per_required"] = totals["timely_core"] / totals["core_required"] if totals["core_required"] else None
        return totals
    cells = []
    for method in "ABCDEF":
        for capacity in ("low", "mid", "high"):
            cell = [row for row in rows if row["method"] == method and row["capacity"] == capacity]
            check(len(cell) == 12, "method/capacity accepted-cell size mismatch")
            cells.append(dict(method=method, capacity=capacity, **summarize(cell)))
    totals = summarize(rows)
    diagnostics = {key: {"count": totals[key], "status": "PASS" if totals[key] == 0 else "FAIL"} for key in ZERO_DIAGNOSTICS}
    return {
        "totals": totals, "method_capacity": cells,
        "accepted_attempts": {session: next(row["attempt"] for row in rows if row["session"] == session)
                              for session in sorted({row["session"] for row in rows})},
        "reported_zero_counter_diagnostics": diagnostics,
        "reported_anomaly_status": "FAIL" if any(totals[key] for key in ZERO_DIAGNOSTICS) else "PASS",
        "unallocated_demanded_bytes_observed": totals["unallocated_demanded_bytes"] > 0,
        "counter_omission_semantics": "Only the five optional producer Counter fields are filled with zero when absent; mandatory counters cannot be omitted.",
        "service_scope": "295 service indices per arm = 5 warmup + 90 measured-generation + 200 drain; event counters use measured-origin occurrences only.",
    }


def split_summary(document):
    check(isinstance(document, dict) and set(document) == set(SPLITS), "split report must contain train/validation/test only")
    counts = {}
    for name in SPLITS:
        row = document[name]
        check(isinstance(row, dict) and set(row) == {"rows", "rows_matching_earlier_split", "file_sha256"}, "split row shape mismatch")
        n = nonnegative_int(row["rows"], "split rows")
        matching = nonnegative_int(row["rows_matching_earlier_split"], "overlap rows")
        check(n > 0 and matching <= n, "invalid overlap count")
        check(name != "train" or matching == 0, "training has no earlier split")
        digest_string(row["file_sha256"], "split file")
        counts[name] = dict(row, matching_fraction=matching / n,
                            earlier_splits=list(SPLITS[:SPLITS.index(name)]))
    return {
        "schema_version": 1, "scope": "reported exact feature-overlap counts; original arrays not rehashed",
        "splits": counts, "reported_total_rows": sum(row["rows"] for row in counts.values()),
        "reported_matching_rows": sum(row["rows_matching_earlier_split"] for row in counts.values()),
        "feature_hash_method_reported": "39 source-order binary64 values, big endian, signed zeros normalized, labels excluded",
        "matching_count_unit": "rows matching any earlier split, not distinct features or independent captures",
        "exact_cross_split_overlap_reported": any(counts[name]["rows_matching_earlier_split"] for name in ("validation", "test")),
        "held_out_efficacy_qualified": False,
        "qualification_status": "BLOCKED_BY_REPORTED_EXACT_OVERLAP_AND_OPEN_LINEAGE_CHECKS" if any(counts[name]["rows_matching_earlier_split"] for name in ("validation", "test")) else "LINEAGE_NEAR_DUPLICATE_AND_TRAINING_INPUT_QUALIFICATION_STILL_OPEN",
        "new_efficacy_metrics_computed": False,
    }


def interface_summary(rows):
    fields = {"device", "encoded_bytes", "encoded_sha256", "level", "line", "model_sha256", "prediction", "source_sha256"}
    groups, models, by_level = defaultdict(dict), set(), defaultdict(list)
    source_for_position = {}
    for row in rows:
        check(isinstance(row, dict) and set(row) == fields, "interface row shape mismatch")
        check(row["device"] in {"P1", "P2", "P3"} and row["level"] in LEVELS, "unknown interface device label or level")
        line = nonnegative_int(row["line"], "source line")
        check(line in {1, 2, 3}, "unexpected pilot source line")
        size = nonnegative_int(row["encoded_bytes"], "encoded bytes")
        check(size > 0, "empty interface payload")
        check(type(row["prediction"]) is int and row["prediction"] in {0, 1}, "invalid binary interface prediction")
        for field in ("encoded_sha256", "model_sha256", "source_sha256"):
            digest_string(row[field], field)
        key = row["device"], line
        check(key not in source_for_position or source_for_position[key] == row["source_sha256"], "interface source mismatch across levels")
        source_for_position[key] = row["source_sha256"]
        check(row["level"] not in groups[key], "duplicate interface observation/level")
        groups[key][row["level"]] = row
        models.add(row["model_sha256"])
        by_level[row["level"]].append(row)
    check(set(groups) == {(device, line) for device in ("P1", "P2", "P3") for line in (1, 2, 3)}, "interface pilot observation grid mismatch")
    check(len(rows) == 27 and len(models) == 1 and len(set(source_for_position.values())) == 9, "interface cohort/model count mismatch")
    check(all(set(group) == set(LEVELS) for group in groups.values()), "missing interface representation")
    agreement = sum(len({row["prediction"] for row in group.values()}) == 1 for group in groups.values())
    levels = {}
    for level in LEVELS:
        sizes = [row["encoded_bytes"] for row in by_level[level]]
        levels[level] = {"rows": len(sizes), "encoded_bytes_total": sum(sizes), "encoded_bytes_min": min(sizes),
                         "encoded_bytes_max": max(sizes), "encoded_bytes_mean": sum(sizes) / len(sizes)}
    return {
        "schema_version": 1, "scope": "summary of exported interface diagnostic on archived observations",
        "rows": len(rows), "source_observations": len(groups), "source_device_labels": 3,
        "distinct_model_digests_reported": len(models), "complete_representation_triplets": len(groups),
        "prediction_agreement_triplets": agreement, "prediction_disagreement_triplets": len(groups) - agreement,
        "agreement_diagnostic_status": "PASS" if agreement == len(groups) else "FAIL",
        "levels": levels, "new_encoders": True, "ground_truth_present": False,
        "accuracy_or_detection_gain_estimated": False, "models_executed_by_reconciler": False,
        "physical_devices_used_by_reconciler": False, "raw_observations_or_identifiers_exported": False,
        "interpretation": "The new alert bit and summary score originate from the same heavy-model output, and full reuses the observation. Agreement is by construction; nine source observations are not nine Pi experiments or held-out efficacy tests.",
    }


def producer_hashes(directory):
    return {name: sha(directory / name) for name in PRODUCERS}


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def export_reports(audit_root, output, index_path=DEFAULT_INDEX, producer_dir=DEFAULT_PRODUCERS):
    check(not output.exists() or (output.is_dir() and not any(output.iterdir())), "output must be new or empty")
    expected = accepted_arms(index_path)
    report = load_json(audit_root / "formal_records.json")
    check(isinstance(report, dict) and set(report) == {"arms", "private_sources"}, "formal report shape mismatch")
    arms = normalize_arm_rows(report["arms"], expected)
    registry = validate_source_registry(report["private_sources"], expected)
    aggregate = arm_aggregates(arms)
    splits = split_summary(load_json(audit_root / "split_overlap.json"))
    interfaces = [json.loads(line, object_pairs_hook=unique_pairs) for line in (audit_root / "pilot_model_interfaces.jsonl").read_text().splitlines() if line.strip()]
    interface = interface_summary(interfaces)
    provenance = {
        "input_sha256": {name: sha(audit_root / name) for name in ("formal_records.json", "split_overlap.json", "pilot_model_interfaces.jsonl")},
        "accepted_index_sha256": sha(index_path), "producer_source_sha256": producer_hashes(producer_dir),
        "reconciliation_source_sha256": sha(Path(__file__)),
    }
    # All input validation precedes output creation. Nonzero observed anomaly
    # counters remain in the output and are flagged; no arm is dropped.
    output.mkdir(parents=True, exist_ok=True)
    with (output / "ARM_REVIEW.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=ARM_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(arms)
    write_json(output / "SPLIT_COUNTS.json", splits)
    write_json(output / "INTERFACE_SUMMARY.json", interface)
    result = {
        "schema_version": 1, "status": "EXPORTED_REPORT_RECONCILED",
        "evidence_scope": "exported-review reconciliation, not raw re-audit",
        "arms": aggregate, "private_source_registry_summary": registry,
        "reported_package_tree_sha256": IDENTITY, "provenance": provenance,
        "products_sha256": {name: sha(output / name) for name in ("ARM_REVIEW.csv", "SPLIT_COUNTS.json", "INTERFACE_SUMMARY.json")},
        "limitations": LIMITATIONS,
        "physical_experiments_executed": 0, "model_executions": 0, "raw_window_or_event_logs_reopened": 0,
        "public_verification_scope": "Recompute accepted-cohort and arm aggregates from sanitized CSV; check reported split/interface summary consistency, committed file hashes and source identities. Original private inputs and primitive records are not reverified.",
    }
    write_json(output / "RECONCILIATION.json", result)
    return result


def validate_interface_export(summary):
    check(isinstance(summary, dict) and set(summary) == {
        "schema_version", "scope", "rows", "source_observations", "source_device_labels",
        "distinct_model_digests_reported", "complete_representation_triplets", "prediction_agreement_triplets",
        "prediction_disagreement_triplets", "agreement_diagnostic_status", "levels", "new_encoders",
        "ground_truth_present", "accuracy_or_detection_gain_estimated", "models_executed_by_reconciler",
        "physical_devices_used_by_reconciler", "raw_observations_or_identifiers_exported", "interpretation",
    }, "interface summary shape mismatch")
    check(summary.get("schema_version") == 1 and summary.get("rows") == 27 and summary.get("source_observations") == 9,
          "interface summary cohort mismatch")
    check(summary.get("source_device_labels") == 3 and summary.get("distinct_model_digests_reported") == 1 and summary.get("complete_representation_triplets") == 9,
          "interface summary source/model counts mismatch")
    agreed = nonnegative_int(summary.get("prediction_agreement_triplets"), "agreement triplets")
    different = nonnegative_int(summary.get("prediction_disagreement_triplets"), "disagreement triplets")
    check(agreed + different == 9, "interface agreement counts mismatch")
    check(summary.get("agreement_diagnostic_status") == ("PASS" if different == 0 else "FAIL"), "interface agreement status mismatch")
    check(isinstance(summary.get("levels"), dict) and set(summary["levels"]) == set(LEVELS), "interface summary levels mismatch")
    for level in LEVELS:
        row = summary["levels"][level]
        check(set(row) == {"rows", "encoded_bytes_total", "encoded_bytes_min", "encoded_bytes_max", "encoded_bytes_mean"}, "interface byte summary shape mismatch")
        for key in ("rows", "encoded_bytes_total", "encoded_bytes_min", "encoded_bytes_max"):
            nonnegative_int(row[key], key)
        check(row["rows"] == 9 and 0 < row["encoded_bytes_min"] <= row["encoded_bytes_max"], "interface byte count/min/max mismatch")
        check(row["encoded_bytes_min"] * 9 <= row["encoded_bytes_total"] <= row["encoded_bytes_max"] * 9, "interface byte total outside bounds")
        check(row["encoded_bytes_mean"] == row["encoded_bytes_total"] / 9, "interface byte mean mismatch")
    for field in ("ground_truth_present", "accuracy_or_detection_gain_estimated", "models_executed_by_reconciler", "physical_devices_used_by_reconciler", "raw_observations_or_identifiers_exported"):
        check(summary.get(field) is False, "interface summary scope changed")
    check(summary.get("new_encoders") is True, "interface encoder scope changed")


def verify_public(output, index_path=DEFAULT_INDEX, producer_dir=DEFAULT_PRODUCERS):
    result = load_json(output / "RECONCILIATION.json")
    check(isinstance(result, dict) and set(result) == {
        "schema_version", "status", "evidence_scope", "arms", "private_source_registry_summary",
        "reported_package_tree_sha256", "provenance", "products_sha256", "limitations",
        "physical_experiments_executed", "model_executions", "raw_window_or_event_logs_reopened", "public_verification_scope",
    }, "reconciliation report shape mismatch")
    check(result.get("schema_version") == 1 and result.get("status") == "EXPORTED_REPORT_RECONCILED", "reconciliation report status/schema mismatch")
    check(result.get("evidence_scope") == "exported-review reconciliation, not raw re-audit", "report scope mismatch")
    check(result.get("limitations") == LIMITATIONS, "review limitations changed")
    check(result.get("reported_package_tree_sha256") == IDENTITY, "reported identity mismatch")
    provenance = result["provenance"]
    check(set(provenance) == {"input_sha256", "accepted_index_sha256", "producer_source_sha256", "reconciliation_source_sha256"}, "provenance shape mismatch")
    check(provenance["accepted_index_sha256"] == sha(index_path), "accepted index source hash mismatch")
    check(provenance["producer_source_sha256"] == producer_hashes(producer_dir), "producer source hash mismatch")
    check(provenance["reconciliation_source_sha256"] == sha(Path(__file__)), "reconciler source hash mismatch")
    check(set(provenance["input_sha256"]) == {"formal_records.json", "split_overlap.json", "pilot_model_interfaces.jsonl"}, "input hash inventory mismatch")
    for value in provenance["input_sha256"].values():
        digest_string(value, "retained private input digest")
    products = {"ARM_REVIEW.csv", "SPLIT_COUNTS.json", "INTERFACE_SUMMARY.json"}
    check(set(result["products_sha256"]) == products, "product inventory mismatch")
    for name in products:
        check(result["products_sha256"][name] == sha(output / name), "sanitized product hash mismatch")
    with (output / "ARM_REVIEW.csv").open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        check(reader.fieldnames == list(ARM_FIELDS), "sanitized CSV header mismatch")
        arms = normalize_arm_rows(list(reader), accepted_arms(index_path), exported=True)
    check(result["arms"] == arm_aggregates(arms), "reconciled arm aggregates mismatch")
    split = load_json(output / "SPLIT_COUNTS.json")
    raw_counts = {name: {key: split["splits"][name][key] for key in ("rows", "rows_matching_earlier_split", "file_sha256")} for name in SPLITS}
    check(split == split_summary(raw_counts), "reported split summary arithmetic/scope mismatch")
    validate_interface_export(load_json(output / "INTERFACE_SUMMARY.json"))
    check(result["private_source_registry_summary"] == {
        "reported_file_hashes": 1512, "reported_roles": {"core_windows": 216, "probe_windows": 648, "event_ledger": 648},
        "role_coverage_checked_against_accepted_arms": True, "private_paths_exported": False,
        "raw_source_files_opened": 0, "original_registry_includes_deployment_or_accepted_index": False,
    }, "source registry summary scope/count mismatch")
    check(all(result.get(field) == 0 for field in ("physical_experiments_executed", "model_executions", "raw_window_or_event_logs_reopened")), "execution scope changed")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest="command", required=True)
    export = subs.add_parser("export")
    export.add_argument("--audit-root", type=Path, required=True)
    export.add_argument("--output", type=Path, required=True)
    verify = subs.add_parser("verify-public")
    verify.add_argument("--results", type=Path, default=HERE / "results")
    for sub in (export, verify):
        sub.add_argument("--accepted-index", type=Path, default=DEFAULT_INDEX)
        sub.add_argument("--producer-dir", type=Path, default=DEFAULT_PRODUCERS)
    args = parser.parse_args()
    try:
        if args.command == "export":
            result = export_reports(args.audit_root, args.output, args.accepted_index, args.producer_dir)
        else:
            result = verify_public(args.results, args.accepted_index, args.producer_dir)
    except (ReconciliationError, OSError, ValueError, KeyError, TypeError) as exc:
        parser.error(str(exc))
    print(json.dumps({"status": result["status"], "mode": args.command,
                      "reported_anomaly_status": result["arms"]["reported_anomaly_status"],
                      "totals": result["arms"]["totals"],
                      "scope": result["evidence_scope"]}, sort_keys=True))
    if result["arms"]["reported_anomaly_status"] == "FAIL":
        sys.exit(1)


if __name__ == "__main__":
    main()
