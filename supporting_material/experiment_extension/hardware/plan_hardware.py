#!/usr/bin/env python3
"""Draft qualified-or-blocked hardware plans; never contact or run hardware."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
import re
from collections import Counter
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
STUDIES = ("allocator", "shared_stage")
PHASES = ("calibration", "pilot", "formal")


class PlanError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise PlanError(message)


def positive_integer(value: Any, name: str) -> int:
    require(type(value) is int and value > 0, f"{name} must be a positive integer")
    return value


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    require(isinstance(value, dict), f"{path.name} must contain a JSON object")
    return value


def digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def canonical_digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def validate_protocol(protocol: dict) -> None:
    require(protocol.get("schema_version") == 1, "unsupported protocol schema")
    require(protocol.get("devices") == ["P1", "P2", "P3"], "this diagnostic requires the three declared probes")
    for name in ("full_payload_bytes", "round_ns", "deadline_ns", "warmup_rounds", "measured_rounds"):
        positive_integer(protocol.get(name), name)
    require(protocol.get("full_payload_bytes") == 131072, "full payload must be 131072 bytes")
    require(protocol.get("capacity_bytes_per_round") == {"low": 131072, "mid": 262144}, "low/mid capacity mismatch")
    for capacity, value in protocol["capacity_bytes_per_round"].items():
        positive_integer(value, f"capacity_{capacity}")
    require(protocol.get("round_ns") == protocol.get("deadline_ns") == 1000000000, "this protocol uses one-second rounds/deadlines")
    require(protocol.get("warmup_rounds") == 5 and protocol.get("measured_rounds") == 90,
            "window counts must remain 5 warmup and 90 measured; qualify private-runtime compatibility separately")
    positive_integer(protocol.get("max_drain_rounds"), "max_drain_rounds")
    allocator = protocol.get("allocator", {})
    positive_integer(allocator.get("queue_weight"), "queue_weight")
    require(allocator.get("queue_weight") == 1 and allocator.get("selector") == "synchronized_independent_I_QPG",
            "allocator regression must freeze synchronized independent I-QPG at v=1")
    require(allocator.get("variants") == ["deployed_original", "integer_remainder_fix"], "allocator variants changed")
    shared = protocol.get("shared_stage", {})
    require(shared.get("capacity") == "mid", "shared-stage primary capacity must be mid")
    require(shared.get("requested_action") == "H_FULL" and shared.get("unselected_action") == "H_NONE", "shared-stage action fixture changed")
    require(shared.get("candidate_probes") == protocol["devices"], "shared-stage must request all three probes")
    require(shared.get("policies") == ["isolated_precheck_new_bytes", "backlog_aware_bytes", "causal_shared_stage"], "policy set changed")
    require(shared.get("backlog_totals_bytes") == [0, 131072], "backlog totals changed")
    expected = {"0": {"P1": 0, "P2": 0, "P3": 0}, "131072": {"P1": 43691, "P2": 43691, "P3": 43690}}
    require(shared.get("backlog_by_probe_bytes") == expected, "per-probe backlog fixture changed")
    for total in shared["backlog_totals_bytes"]:
        require(type(total) is int and total >= 0, "backlog total must be a nonnegative integer")
        require(all(type(value) is int and value >= 0 for value in shared["backlog_by_probe_bytes"][str(total)].values()), "per-probe backlog must be integer bytes")
        require(sum(shared["backlog_by_probe_bytes"][str(total)].values()) == total, "backlog total does not match per-probe state")
    require(shared.get("initial_core_executing_jobs") == shared.get("initial_core_queued_complete_jobs") == 0,
            "initial core executing/complete-job queues must be empty and verified")
    require(type(shared["initial_core_executing_jobs"]) is type(shared["initial_core_queued_complete_jobs"]) is int,
            "initial core counts must be integers")
    require(shared.get("calibration_capture_batches") == [["P1"], ["P2"], ["P3"], ["P1", "P2", "P3"]], "stage-capture population changed")
    require(protocol.get("execution", {}).get("planner_executes_hardware") is False, "planner must never execute hardware")


def conditions_for(protocol: dict, study: str, phase: str, include_mid_control: bool) -> list[dict]:
    require(study in STUDIES and phase in PHASES, "invalid study or phase")
    require(not include_mid_control or study == "allocator", "--include-mid-control is only for allocator regression")
    conditions = []
    if study == "allocator":
        require(phase != "calibration", "allocator calibration is source inspection plus offline fixtures; use pilot/formal for physical regression")
        capacities = ["low", "mid"] if include_mid_control else ["low"]
        for capacity in capacities:
            for variant in protocol["allocator"]["variants"]:
                conditions.append({
                    "condition_id": f"{capacity}_{variant}", "capacity": capacity,
                    "capacity_bytes_per_round": protocol["capacity_bytes_per_round"][capacity],
                    "allocator_variant": variant, "policy": "synchronized_independent_I_QPG",
                    "queue_weight": 1, "candidate_probes": protocol["devices"],
                    "backlog_fixture": "unaltered_frozen_runtime_initialization",
                    "primary_stratum": "all_measured_generation_batches",
                })
    else:
        shared = protocol["shared_stage"]
        for backlog in shared["backlog_totals_bytes"]:
            populations = shared["calibration_capture_batches"] if phase == "calibration" else [shared["candidate_probes"]]
            policies = [shared["calibration_policy"]] if phase == "calibration" else shared["policies"]
            for population in populations:
                for policy in policies:
                    conditions.append({
                        "condition_id": f"B{backlog}_{'_'.join(population)}_{policy}",
                        "capacity": "mid", "capacity_bytes_per_round": 262144,
                        "allocator_variant": "frozen_audited_shared_service", "policy": policy,
                        "candidate_probes": population, "requested_action": "H_FULL",
                        "unselected_action": "H_NONE", "backlog_fixture": "one_time_first_measured_batch",
                        "backlog_bytes": backlog, "backlog_by_probe_bytes": shared["backlog_by_probe_bytes"][str(backlog)],
                        "initial_core_executing_jobs": 0, "initial_core_queued_complete_jobs": 0,
                        "primary_stratum": shared["primary_backlog_stratum"],
                        "secondary_stratum": shared["secondary_stratum"],
                    })
    return conditions


def williams_rows(size: int) -> list[list[int]]:
    """Even-order Latin crossover: every directed distinct pair occurs once."""
    require(type(size) is int and size >= 2 and size % 2 == 0, "Williams design needs positive even order >=2")
    base = [0]
    for position in range(1, size):
        base.append((position + 1) // 2 if position % 2 else size - position // 2)
    return [[(value + offset) % size for value in base] for offset in range(size)]


def ordered_blocks(conditions: list[dict], blocks: int, order_seed: int) -> list[list[str]]:
    positive_integer(blocks, "blocks")
    require(type(order_seed) is int, "order seed must be an integer")
    names = [condition["condition_id"] for condition in conditions]
    require(len(names) == len(set(names)), "duplicate condition identifiers")
    design = williams_rows(len(names))
    rng = random.Random(order_seed)
    schedules = []
    while len(schedules) < blocks:
        relabel = names.copy()
        rng.shuffle(relabel)
        row_order = list(range(len(names)))
        rng.shuffle(row_order)
        for row_number in row_order:
            schedules.append([relabel[index] for index in design[row_number]])
            if len(schedules) == blocks:
                break
    return schedules


def balance_report(schedules: list[list[str]], names: list[str]) -> dict:
    positions = {name: [0] * len(names) for name in names}
    transitions = Counter({(a, b): 0 for a in names for b in names if a != b})
    for order in schedules:
        require(len(order) == len(names) and set(order) == set(names), "every block must contain every condition exactly once")
        for position, name in enumerate(order):
            positions[name][position] += 1
        transitions.update(zip(order, order[1:]))
    values = list(transitions.values())
    return {
        "conditions_per_block": len(names), "blocks": len(schedules),
        "complete_design_cycles": len(schedules) // len(names),
        "partial_cycle_blocks": len(schedules) % len(names),
        "position_counts": positions,
        "maximum_within_condition_position_count_spread": max(max(row) - min(row) for row in positions.values()),
        "within_block_directed_transition_counts": [{"from": a, "to": b, "count": transitions[a, b]} for a in names for b in names if a != b],
        "directed_transition_minimum": min(values), "directed_transition_maximum": max(values),
        "exact_position_and_transition_balance": len(schedules) % len(names) == 0,
        "scope": "Within-block positions/adjacent condition transitions only. Between-block transitions are excluded; runtime resets still required. Scheduling seeds are not scientific replicates.",
    }


COMMON_GATES = (
    ("private_runtime_identity_verified", "runtime_inventory"),
    ("frozen_inputs_verified", "input_manifest"),
    ("launcher_and_anchors_frozen", "launcher_anchor_review"),
    ("window_counts_compatible", "window_compatibility_review"),
    ("event_and_service_logging_verified", "instrumentation_audit"),
    ("attempt_recording_verified", "attempt_protocol"),
    ("fresh_campaign_registry_checked", "campaign_registry_review"),
)


def qualification_report(path: Path | None, study: str, phase: str) -> dict:
    document = read_json(path) if path else {"facts": {}, "evidence": {}}
    facts, evidence = document.get("facts", {}), document.get("evidence", {})
    require(isinstance(facts, dict) and isinstance(evidence, dict), "qualification facts/evidence must be objects")
    gates = list(COMMON_GATES)
    if study == "allocator":
        gates.extend((("deployed_allocator_affected", "deployed_allocator_inspection"),
                      ("allocator_only_patch_verified", "allocator_patch_audit")))
    else:
        gates.append(("actual_backlog_and_core_state_verified", "backlog_core_fixture_audit"))
        if phase in {"pilot", "formal"}:
            gates.extend((("calibration_disjoint_and_frozen", "calibration_freeze"),
                          ("controller_causal_and_implemented", "controller_source_and_causality_audit")))
    if phase == "formal":
        gates.extend((("pilot_completed_and_formal_freeze_recorded", "formal_freeze"),
                      ("pilot_report_retained", "pilot_report")))
    checks = []
    for fact, artifact_name in gates:
        record = evidence.get(artifact_name, {})
        artifact_verified, reason, observed = False, "evidence artifact missing", None
        if isinstance(record, dict) and record.get("path") and record.get("sha256"):
            artifact = Path(record["path"]).expanduser()
            if not artifact.is_absolute():
                artifact = path.parent / artifact
            expected = record["sha256"]
            if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected):
                reason = "expected SHA-256 must be 64 lowercase hexadecimal characters"
            elif not artifact.is_file():
                reason = "evidence artifact is not a readable regular file"
            else:
                observed = digest(artifact)
                artifact_verified = observed == expected
                reason = "verified retained artifact hash" if artifact_verified else "evidence artifact SHA-256 mismatch"
        checks.append({
            "fact": fact, "asserted_value": facts.get(fact), "evidence_name": artifact_name,
            "artifact_sha256": observed, "artifact_hash_verified": artifact_verified,
            "qualified": facts.get(fact) is True and artifact_verified,
            "reason": reason if facts.get(fact) is True else f"fact not established true; {reason}",
        })
    inspection = next((row for row in checks if row["fact"] == "deployed_allocator_affected"), None)
    not_needed = bool(inspection and inspection["asserted_value"] is False and inspection["artifact_hash_verified"])
    return {
        "status": "NOT_NEEDED_DEPLOYED_ALLOCATOR_UNAFFECTED" if not_needed else ("QUALIFIED_FOR_EXECUTION_BY_EXTERNAL_RUNNER" if all(row["qualified"] for row in checks) else "BLOCKED_MISSING_OR_UNVERIFIED_PREREQUISITES"),
        "checks": checks,
        "qualification_document_sha256": digest(path) if path else None,
        "meaning": "Objective prerequisite records, not a permission request. Hash checks bind retained review artifacts; this planner cannot perform the private source/instrumentation review itself.",
    }


def sample_size_report(path: Path | None, study: str, blocks: int, phase: str) -> dict:
    if phase != "formal":
        require(path is None, "--sample-size-rule-file applies only to formal plans")
        return {"required": False, "qualified": True, "rule": "separate_nonformal_capture_or_pilot", "formal_blocks": None}
    if path is None:
        return {"required": True, "qualified": False, "reason": "fixed complete-block rule must be frozen before formal outcomes"}
    rule = read_json(path)
    require(rule.get("schema_version") == 1, "unsupported sample-size rule schema")
    require(rule.get("status") == "FROZEN_SAMPLE_SIZE_RULE", "sample-size rule is still a draft/unfrozen template")
    require(rule.get("study") == study, "sample-size study mismatch")
    require(rule.get("rule") == "fixed_complete_blocks", "this planner supports a predeclared fixed complete-block rule only")
    require(positive_integer(rule.get("formal_blocks"), "formal_blocks") == blocks, "requested blocks differ from frozen sample-size rule")
    require(rule.get("formal_outcome_peeking_for_stopping") is False, "outcome-based formal stopping is prohibited")
    require(rule.get("independent_unit") == "fresh_physical_complete_condition_block", "sample-size independent unit must be a fresh physical block")
    require(isinstance(rule.get("rationale"), str) and bool(rule["rationale"].strip()), "sample-size rationale missing")
    require(isinstance(rule.get("pilot_campaign_id"), str) and bool(rule["pilot_campaign_id"].strip()), "separate pilot identity missing")
    require(isinstance(rule.get("pilot_report_sha256"), str) and bool(re.fullmatch(r"[0-9a-f]{64}", rule["pilot_report_sha256"])), "pilot report hash missing/invalid")
    return {"required": True, "qualified": True, "rule": rule["rule"], "formal_blocks": blocks,
            "rationale": rule["rationale"], "pilot_campaign_id": rule["pilot_campaign_id"],
            "pilot_report_sha256": rule["pilot_report_sha256"], "sample_size_rule_sha256": digest(path),
            "freeze_binding": "The formal_freeze qualification artifact must bind this exact rule hash and the pilot report hash before any formal run."}


def formal_binding_report(qualification_path: Path | None, qualification: dict, sample: dict,
                          *, protocol_path: Path, study: str, campaign_id: str, blocks: int,
                          order_seed: int, include_mid_control: bool, condition_order_sha256: str) -> dict:
    """Reject stale/unrelated freeze receipts even when all fact flags are true."""
    checks = {row["evidence_name"]: row for row in qualification["checks"]}
    freeze_check = checks.get("formal_freeze", {})
    pilot_check = checks.get("pilot_report", {})
    if not qualification_path or not freeze_check.get("artifact_hash_verified") or not pilot_check.get("artifact_hash_verified") or not sample.get("qualified"):
        return {"qualified": False, "reason": "verified formal-freeze, pilot-report and fixed sample-size artifacts are required"}
    document = read_json(qualification_path)
    freeze_path = Path(document["evidence"]["formal_freeze"]["path"]).expanduser()
    if not freeze_path.is_absolute():
        freeze_path = qualification_path.parent / freeze_path
    try:
        freeze = read_json(freeze_path)
    except (OSError, json.JSONDecodeError, PlanError) as exc:
        return {"qualified": False, "reason": f"formal-freeze must be a readable binding JSON: {exc}"}
    expected = {
        "schema_version": 1, "status": "FROZEN_FOR_FORMAL_EXECUTION", "study": study,
        "campaign_id": campaign_id, "formal_blocks": blocks,
        "order_seed": order_seed, "include_mid_control": include_mid_control,
        "planner_source_sha256": digest(Path(__file__)),
        "raw_schema_sha256": digest(HERE / "raw_ledger_schema.json"),
        "condition_order_sha256": condition_order_sha256,
        "protocol_sha256": digest(protocol_path), "sample_size_rule_sha256": sample["sample_size_rule_sha256"],
        "pilot_campaign_id": sample["pilot_campaign_id"], "pilot_report_sha256": pilot_check["artifact_sha256"],
    }
    mismatches = [field for field, value in expected.items() if freeze.get(field) != value]
    if sample["pilot_report_sha256"] != pilot_check["artifact_sha256"]:
        mismatches.append("sample_size_rule.pilot_report_sha256")
    bound = freeze.get("qualification_evidence_sha256", {})
    if not isinstance(bound, dict):
        bound = {}
    for name, row in checks.items():
        if name != "formal_freeze" and bound.get(name) != row["artifact_sha256"]:
            mismatches.append(f"qualification_evidence_sha256.{name}")
    return {"qualified": not mismatches, "mismatched_bindings": mismatches,
            "reason": "exact plan/rule/pilot/qualification-artifact bindings checked",
            "freeze_artifact_sha256": freeze_check["artifact_sha256"],
            "chronology_requirement": "External runner must establish this receipt existed before the first formal run and refuse campaign/phase reuse. Hash agreement alone cannot prove wall-clock chronology."}


def make_plan(protocol_path: Path, *, study: str, phase: str, blocks: int, order_seed: int,
              campaign_id: str, include_mid_control: bool = False, qualification_path: Path | None = None,
              sample_size_path: Path | None = None) -> tuple[dict, list[dict], dict]:
    protocol = read_json(protocol_path)
    validate_protocol(protocol)
    positive_integer(blocks, "blocks")
    prefix = "TON_EXT_ALLOC_" if study == "allocator" else "TON_EXT_STAGE_"
    require(isinstance(campaign_id, str) and campaign_id.startswith(prefix), f"fresh campaign ID must start with {prefix}")
    require(bool(re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{4,95}", campaign_id)), "invalid campaign ID")
    conditions = conditions_for(protocol, study, phase, include_mid_control)
    schedules = ordered_blocks(conditions, blocks, order_seed)
    order_digest = canonical_digest(schedules)
    qualification = qualification_report(qualification_path, study, phase)
    sample = sample_size_report(sample_size_path, study, blocks, phase)
    if phase == "formal" and not sample["qualified"] and qualification["status"].startswith("QUALIFIED"):
        qualification["status"] = "BLOCKED_SAMPLE_SIZE_RULE_NOT_FROZEN"
    if phase == "formal":
        qualification["formal_bindings"] = formal_binding_report(qualification_path, qualification, sample,
            protocol_path=protocol_path, study=study, campaign_id=campaign_id, blocks=blocks,
            order_seed=order_seed, include_mid_control=include_mid_control, condition_order_sha256=order_digest)
        if not qualification["formal_bindings"]["qualified"] and qualification["status"].startswith("QUALIFIED"):
            qualification["status"] = "BLOCKED_FORMAL_FREEZE_BINDINGS"
    balance = balance_report(schedules, [row["condition_id"] for row in conditions])
    by_id = {row["condition_id"]: row for row in conditions}
    order_rows = []
    not_needed = qualification["status"] == "NOT_NEEDED_DEPLOYED_ALLOCATOR_UNAFFECTED"
    if not not_needed:
        for block, order in enumerate(schedules, 1):
            session_id = f"{campaign_id}_{phase.upper()}_B{block:04d}"
            for position, name in enumerate(order, 1):
                condition = by_id[name]
                arm_id = f"{session_id}_R{position:02d}"
                order_rows.append({
                    "status": "PLANNED_NOT_EXECUTED", "campaign_id": campaign_id, "study": study,
                    "phase": phase, "block": block, "session_id": session_id, "position": position,
                    "arm_id": arm_id, "attempt_id_pattern": arm_id + "_A{attempt:03d}", "condition_id": name,
                    "capacity": condition["capacity"], "capacity_bytes_per_round": condition["capacity_bytes_per_round"],
                    "policy": condition["policy"], "allocator_variant": condition["allocator_variant"],
                    "candidate_probes": ",".join(condition["candidate_probes"]),
                    "warmup_rounds": protocol["warmup_rounds"], "measured_rounds": protocol["measured_rounds"],
                    "planned_new_measured_occurrences": len(condition["candidate_probes"]) * protocol["measured_rounds"],
                    "initial_backlog_bytes": condition.get("backlog_bytes", "frozen_runtime_initialization"),
                    "primary_stratum": condition["primary_stratum"], "order_seed": order_seed,
                })
    plan = {
        "schema_version": 1, "status": "PLANNED_NOT_EXECUTED", "study": study, "phase": phase,
        "campaign_id": campaign_id, "requested_complete_blocks": blocks, "order_seed": order_seed,
        "include_mid_control": include_mid_control, "condition_order_sha256": order_digest,
        "order_seed_role": "Scheduling only; not a workload-randomness or independence claim.",
        "execution_qualification": qualification["status"], "planner_executes_hardware": False,
        "physical_arms_executed": 0, "observed_results": None,
        "planned_arms": len(order_rows), "conditions": conditions, "ordering_balance": balance,
        "sample_size": sample, "anchors": {"primary": protocol["anchor_primary"], "sensitivity": protocol["anchor_sensitivity"]},
        "protocol_sha256": digest(protocol_path), "planner_source_sha256": digest(Path(__file__)),
        "raw_schema_sha256": digest(HERE / "raw_ledger_schema.json"),
        "raw_schema_file": "raw_ledger_schema.json", "controller_contract": "CONTROLLER_AND_CAPTURE_CONTRACT.md",
        "exclusion_rule": "Retain all attempts; apply only predeclared independent infrastructure exclusions. Poor timing, zero admission, cap violations and classifier errors are outcomes, not retry grounds.",
        "scope": "Conditional supplemental campaign. No frozen campaign is altered, reclassified or silently combined with these planned data.",
    }
    return plan, order_rows, qualification


def write_plan(output: Path, plan: dict, order: list[dict], qualification: dict) -> None:
    require(not output.exists() or (output.is_dir() and not any(output.iterdir())), "output must be new or empty; never overwrite an existing plan/evidence")
    output.mkdir(parents=True, exist_ok=True)
    for name, document in (("plan.json", plan), ("qualification_report.json", qualification)):
        (output / name).write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with (output / "condition_order.csv").open("w", newline="", encoding="utf-8") as handle:
        fields = list(order[0]) if order else ["status", "reason"]
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(order)
    paths = sorted(output.iterdir())
    (output / "SHA256SUMS.txt").write_text("\n".join(f"{digest(path)}  {path.name}" for path in paths) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=HERE / "protocol.json")
    parser.add_argument("--study", choices=STUDIES, required=True)
    parser.add_argument("--phase", choices=PHASES, required=True)
    parser.add_argument("--blocks", type=int, required=True, help="Explicit complete physical blocks; no default or seed-as-replicate interpretation")
    parser.add_argument("--order-seed", type=int, required=True, help="Scheduling randomness only")
    parser.add_argument("--campaign-id", required=True)
    parser.add_argument("--include-mid-control", action="store_true")
    parser.add_argument("--qualification", type=Path)
    parser.add_argument("--sample-size-rule-file", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        plan, order, qualification = make_plan(args.config, study=args.study, phase=args.phase,
            blocks=args.blocks, order_seed=args.order_seed, campaign_id=args.campaign_id,
            include_mid_control=args.include_mid_control, qualification_path=args.qualification,
            sample_size_path=args.sample_size_rule_file)
        write_plan(args.output, plan, order, qualification)
    except (PlanError, OSError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    print(json.dumps({key: plan[key] for key in ("status", "study", "phase", "planned_arms", "execution_qualification", "physical_arms_executed")}, sort_keys=True))


if __name__ == "__main__":
    main()
