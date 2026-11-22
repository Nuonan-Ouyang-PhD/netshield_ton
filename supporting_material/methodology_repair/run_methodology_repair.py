#!/usr/bin/env python3
"""Corrected software analyses; frozen V1.3 outputs remain historical inputs.

Tasks A/B report payload-upload completion only.  They do not simulate or
measure full core-result return.  Task C reconstructs returned-result timing
from private hardware ledgers.  Importing this module requires no private
paths: configure_actions() supports explicit public/synthetic test fixtures.
The complete private-input workflow writes a new output directory and ZIP.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import platform
import random
import shutil
import sys
import traceback
import zipfile
from collections import Counter, deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from .simulation_primitives import (
        admission_budget, isolated_latency_ms, same_round_upload_feasible,
        upload_on_time, waterfill,
    )
except ImportError:  # Direct execution from this directory.
    from simulation_primitives import (
        admission_budget, isolated_latency_ms, same_round_upload_feasible,
        upload_on_time, waterfill,
    )


HERE = Path(__file__).resolve().parent


def required_path(name: str) -> Path:
    value = os.environ.get(name)
    if not value:
        raise SystemExit(f"Set {name} to the retained local evidence path before running")
    return Path(value).expanduser().resolve()


AUDIT: Path | None = None
RAW_ROOT: Path | None = None
PROTOCOL: Path | None = None
AUDIT_RESULTS: Path | None = None
RUNTIME: Path | None = None
RAW_ZIP: Path | None = None
OUTPUT: Path | None = None
ZIP_PATH: Path | None = None

DEVICES = ("P1", "P2", "P3")
CAPACITY_BPS = {"low": 1048576, "mid": 2097152, "high": 3145728}
CAPACITY_BYTES = {key: value // 8 for key, value in CAPACITY_BPS.items()}
V_VALUES = (1, 3, 10, 30, 100, 168, 300, 1000, 3000, 10000, 30000, 100000)
DESYNC_SEEDS = tuple(range(2026090901, 2026090921))
WINDOWS = 95
WARMUP = 5
MEASURED = WINDOWS - WARMUP
DEADLINE_TICKS = 1000
TICKS_PER_SECOND = 1000
MAX_DRAIN_WINDOWS = 200
B_FULL = 131072
S_SUMMARY = 16384

ACTION_FILES = ("L_NONE", "L_ALERT", "L_SUMMARY", "M_NONE", "M_ALERT", "M_SUMMARY", "H_NONE", "H_ALERT", "H_SUMMARY", "H_FULL")
EVIDENCE_RANK = {"none": 0, "alert": 1, "summary": 2, "full": 3}
DETECTOR_RANK = {"light": 0, "medium": 1, "heavy": 2}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


def csv_value(value: Any) -> Any:
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return value


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    if not fields:
        fields = ["status"]
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=fields,
            extrasaction="ignore",
            lineterminator="\n",
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({key: csv_value(row.get(key, "")) for key in fields})


def quantile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    position = (len(ordered) - 1) * q
    low = int(math.floor(position))
    high = int(math.ceil(position))
    if low == high:
        return ordered[low]
    return ordered[low] + (ordered[high] - ordered[low]) * (position - low)


def action_table() -> list[dict[str, Any]]:
    if PROTOCOL is None:
        raise RuntimeError("configure_private_inputs() is required to read the retained action table")
    raw = read_json(PROTOCOL / "inputs" / "actions.json")["actions"]
    return [
        {
            "id": item["id"],
            "detector": item["detector"],
            "execution": item["execution"],
            "evidence": item["evidence"],
            "payload": int(item["payload_bytes"]),
            "utility": float(item["utility"]),
            "compute_ms": item["compute_ms"],
            "core_ms": item["core_ms"],
        }
        for item in raw
    ]


ACTIONS: list[dict[str, Any]] = []
ACTION_BY_ID: dict[str, dict[str, Any]] = {}
ACTION_IDS: tuple[str, ...] = ()


def configure_actions(actions: list[dict[str, Any]]) -> None:
    """Set an explicit action table; input provenance belongs in run metadata."""
    global ACTIONS, ACTION_BY_ID, ACTION_IDS
    if not actions or len({action["id"] for action in actions}) != len(actions):
        raise ValueError("actions must be nonempty with unique ids")
    ACTIONS = [dict(action) for action in actions]
    ACTION_BY_ID = {row["id"]: row for row in ACTIONS}
    ACTION_IDS = tuple(row["id"] for row in ACTIONS)


def configure_private_inputs() -> None:
    """Load retained inputs only for a requested complete rerun."""
    global AUDIT, RAW_ROOT, PROTOCOL, AUDIT_RESULTS, RUNTIME, RAW_ZIP, OUTPUT, ZIP_PATH
    AUDIT = required_path("TON_AUDIT_ROOT")
    RAW_ROOT = AUDIT / "extracted_sessions"
    PROTOCOL = AUDIT / "protocol"
    AUDIT_RESULTS = AUDIT / "results"
    RUNTIME = required_path("TON_RUNTIME_ROOT")
    RAW_ZIP = required_path("TON_RAW_ZIP")
    default_output = HERE.parent / "methodology_corrected_runs" / datetime.now(timezone.utc).strftime("run_%Y%m%dT%H%M%S_%fZ")
    OUTPUT = Path(os.environ.get("TON_OUTPUT_DIR", str(default_output))).expanduser().resolve()
    ZIP_PATH = Path(os.environ.get("TON_OUTPUT_ZIP", str(OUTPUT.with_suffix(".zip")))).expanduser().resolve()
    if OUTPUT == HERE or OUTPUT.is_relative_to(HERE) or any(OUTPUT.is_relative_to(p) for p in (AUDIT, RUNTIME)):
        raise ValueError("TON_OUTPUT_DIR must be separate from frozen inputs and the methodology snapshot")
    if ZIP_PATH.is_relative_to(HERE) or any(ZIP_PATH.is_relative_to(p) for p in (AUDIT, RUNTIME)):
        raise ValueError("TON_OUTPUT_ZIP must be separate from frozen inputs and the methodology snapshot")
    if ZIP_PATH.is_relative_to(OUTPUT):
        raise ValueError("TON_OUTPUT_ZIP must be outside TON_OUTPUT_DIR")
    if OUTPUT.exists() or ZIP_PATH.exists():
        raise FileExistsError("Use a new output directory and ZIP path; existing results are never overwritten")
    configure_actions(action_table())
    OUTPUT.mkdir(parents=True)


def passes_isolated_latency_precheck(action: dict[str, Any], device: str, capacity_bps: int) -> bool:
    """Optimistic single-device screening; does not account for shared contention."""
    compute = float(action["compute_ms"][device])
    core_raw = action["core_ms"]
    core = float(core_raw[device] if isinstance(core_raw, dict) else core_raw)
    if capacity_bps <= 0 or capacity_bps % 8:
        raise ValueError("capacity_bps must be positive and divisible by eight")
    return isolated_latency_ms(action["payload"], capacity_bps // 8, compute_ms=compute, core_ms=core) <= 1000.0


def select_local(device: str, capacity_bps: int, v: float, queue_bytes: int, safe_only: bool) -> dict[str, Any]:
    if not ACTIONS:
        raise RuntimeError("Call configure_actions() with an explicit action table first")
    pool = [action for action in ACTIONS if (not safe_only or passes_isolated_latency_precheck(action, device, capacity_bps))]
    if not pool:
        pool = [action for action in ACTIONS if action["evidence"] == "none"] or ACTIONS
    return max(pool, key=lambda action: v * action["utility"] - queue_bytes * action["payload"] / 1_000_000.0)


def degradation_key(action: dict[str, Any]) -> tuple[int, int, int]:
    return (
        EVIDENCE_RANK[action["evidence"]],
        1 if action["execution"] == "core" else 0,
        DETECTOR_RANK[action["detector"]],
    )


def degrade(current: dict[str, Any], device: str, capacity_bps: int, safe_only: bool) -> dict[str, Any]:
    pool = [action for action in ACTIONS if (not safe_only or passes_isolated_latency_precheck(action, device, capacity_bps))]
    lower = [action for action in pool if degradation_key(action) < degradation_key(current)]
    if not lower:
        fallback = [action for action in pool if action["evidence"] == "none"]
        return min(fallback or pool, key=lambda action: (action["payload"], float(action["compute_ms"][device])))
    return max(
        lower,
        key=lambda action: (
            action["detector"] == current["detector"],
            action["execution"] == current["execution"],
            degradation_key(action),
            action["utility"],
        ),
    )


def priority(seed: int, window: int, devices: tuple[str, ...]) -> list[str]:
    base = sorted(devices, key=lambda device: hashlib.sha256(f"{seed}|{device}".encode()).digest())
    shift = window % len(base)
    return base[shift:] + base[:shift]


def joint_admit(
    chosen: dict[str, dict[str, Any]], capacity_bytes: int, capacity_bps: int,
    safe_only: bool, seed: int, window: int, existing_queues: dict[str, int],
) -> dict[str, dict[str, Any]]:
    """Degrade new payloads to a backlog-reserved application byte budget.

    This does not certify detector/core/result-return deadlines.  Existing
    backlog above capacity is reported separately by the simulation.
    """
    chosen = dict(chosen)
    available = admission_budget(capacity_bytes, existing_queues)
    while sum(action["payload"] for action in chosen.values()) > available:
        options: list[tuple[float, str, dict[str, Any]]] = []
        for device, current in chosen.items():
            replacement = degrade(current, device, capacity_bps, safe_only)
            released = current["payload"] - replacement["payload"]
            if released > 0:
                loss = max(0.0, current["utility"] - replacement["utility"])
                options.append((loss / released, device, replacement))
        if not options:
            raise ValueError("No degradation satisfies the backlog-reserved upload budget")
        minimum = min(item[0] for item in options)
        tied = [item for item in options if item[0] == minimum]
        if len(tied) == 1:
            _, victim, replacement = tied[0]
        else:
            order = priority(seed, window, tuple(chosen))
            position = {device: index for index, device in enumerate(order)}
            _, victim, replacement = max(tied, key=lambda item: position[item[1]])
        chosen[victim] = replacement
    return chosen


def consume_fifo(queue: deque[dict[str, Any]], amount: int, completion_marker: int) -> list[dict[str, Any]]:
    completed: list[dict[str, Any]] = []
    remaining = amount
    while remaining > 0 and queue:
        item = queue[0]
        sent = min(remaining, item["remaining"])
        item["remaining"] -= sent
        remaining -= sent
        if item["remaining"] == 0:
            item["completion"] = completion_marker
            completed.append(queue.popleft())
    return completed


def action_mix(counter: Counter[str]) -> dict[str, int]:
    return {action: int(counter.get(action, 0)) for action in ACTION_IDS}


def detect_period(sequence: list[tuple[Any, ...]], max_period: int = 30) -> tuple[int | None, int | None, int]:
    """Find the earliest exact suffix cycle with at least three repeats."""
    for start in range(min(31, len(sequence))):
        suffix = sequence[start:]
        for period in range(1, min(max_period, len(suffix) // 3) + 1):
            if all(suffix[index] == suffix[index % period] for index in range(len(suffix))):
                return period, start, len(suffix) // period
    return None, None, 0


def simulate_synchronous(method: str, capacity: str, seed: int, v: float) -> dict[str, Any]:
    """Round-granularity upload model; completion is conservatively at round end."""
    cap = CAPACITY_BYTES[capacity]
    bps = CAPACITY_BPS[capacity]
    queues = {device: deque() for device in DEVICES}
    qbytes = {device: 0 for device in DEVICES}
    mixes: Counter[str] = Counter()
    payload = 0
    full_events = 0
    timely_full = 0
    max_queue = 0
    trajectory: list[dict[str, int]] = []
    signatures: list[tuple[Any, ...]] = []
    cap_violations = 0
    overfull_backlog_rounds = 0
    upload_infeasible_rounds = 0

    for window in range(WINDOWS):
        safe_only = method == "shielded_coordinated"
        chosen = {device: select_local(device, bps, v, qbytes[device], safe_only) for device in DEVICES}
        if method in {"central_coordinated", "shielded_coordinated"}:
            chosen = joint_admit(chosen, cap, bps, safe_only, seed, window, existing_queues=qbytes)
        overfull_backlog_rounds += int(sum(qbytes.values()) > cap)
        upload_infeasible_rounds += int(not same_round_upload_feasible(qbytes, {d: a["payload"] for d, a in chosen.items()}, cap))
        measured = window >= WARMUP
        for device, action in chosen.items():
            if measured:
                mixes[action["id"]] += 1
                payload += action["payload"]
            if action["payload"]:
                item = {
                    "remaining": action["payload"], "action": action["id"],
                    "origin_tick": window * TICKS_PER_SECOND, "measured": measured, "core": action["execution"] == "core",
                }
                queues[device].append(item)
                qbytes[device] += action["payload"]
                if measured and item["core"]:
                    full_events += 1
        grants = waterfill(qbytes, cap, tie_offset=window)
        if sum(grants.values()) > cap:
            cap_violations += 1
        for device in DEVICES:
            completed = consume_fifo(queues[device], grants[device], (window + 1) * TICKS_PER_SECOND)
            qbytes[device] -= grants[device]
            for item in completed:
                if item["measured"] and item["core"] and upload_on_time(item["origin_tick"], item["completion"], DEADLINE_TICKS):
                    timely_full += 1
        max_queue = max(max_queue, *qbytes.values())
        trajectory.append(dict(qbytes))
        if measured:
            signatures.append(tuple(chosen[device]["id"] for device in DEVICES) + tuple(qbytes[device] for device in DEVICES))

    drain = 0
    while any(qbytes.values()) and drain < MAX_DRAIN_WINDOWS:
        grants = waterfill(qbytes, cap, tie_offset=WINDOWS + drain)
        for device in DEVICES:
            consume_fifo(queues[device], grants[device], (WINDOWS + drain + 1) * TICKS_PER_SECOND)
            qbytes[device] -= grants[device]
        drain += 1
    period, start, repeats = detect_period(signatures)
    return {
        "action_counts": action_mix(mixes),
        "core_required_fraction": full_events / (MEASURED * len(DEVICES)),
        "payload_bytes": payload,
        "queue_trajectory_bytes": trajectory,
        "max_queue_bytes": max_queue,
        "upload_on_time_fraction_of_core_required": None if full_events == 0 else timely_full / full_events,
        "core_required_events": full_events,
        "on_time_core_required_uploads": timely_full,
        "completion_endpoint": "payload_upload_only",
        "completion_resolution_ms": 1000,
        "completion_quantization": "round_end_upper_bound",
        "deadline_origin": "modeled_payload_release_at_round_start",
        "deadline_ms": 1000,
        "includes_detector_compute_core_inference_or_wifi_jitter": False,
        "detected_period_windows": period,
        "period_start_measured_window": start,
        "complete_period_repeats": repeats,
        "drain_windows_used": drain,
        "final_queue_bytes": sum(qbytes.values()),
        "allocator_cap_check_failures": cap_violations,
        "cap_check_scope": "implementation_invariant_only",
        "preexisting_backlog_exceeds_capacity_rounds": overfull_backlog_rounds,
        "same_round_upload_infeasible_rounds": upload_infeasible_rounds,
        "admission_policy": "backlog_reserved_upload_budget" if method in {"central_coordinated", "shielded_coordinated"} else "independent_no_joint_admission",
        "shield_precheck_scope": "isolated_service_only" if method == "shielded_coordinated" else "not_used",
    }


def task_a(session_schedule: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """One deterministic case per (v, capacity), with session labels as metadata.

    The independent synchronized controller never consults the seed.  The
    twelve historical session labels therefore do not define replicates.
    """
    rows: list[dict[str, Any]] = []
    for v in V_VALUES:
        for capacity in CAPACITY_BPS:
            base = {
                "status": "PASS", "v": v, "capacity": capacity,
                "case_id": f"v{v}_{capacity}",
                "experimental_unit": "deterministic_parameter_case",
                "evaluations_per_case": 1,
                "independent_random_replicates": 0,
                "seed_affects_decisions": False,
                "formal_session_ids": [session["session_id"] for session in session_schedule],
                "formal_seed_labels": [session["seed"] for session in session_schedule],
                "method": "synchronized_independent_dpp_corrected_service_simulation",
            }
            try:
                base.update(simulate_synchronous("synchronized_independent", capacity, 0, v))
            except Exception as exc:  # retain every failed case
                base.update(status="FAIL", error=repr(exc), traceback=traceback.format_exc())
            rows.append(base)
    return rows


def annotate_formal_v1_identity(v_rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Compare corrected service with frozen hardware; equality is not a gate."""
    aggregate = read_json(AUDIT_RESULTS / "REBUILT_AGGREGATE_EVENT_METRICS.json")
    reference = {
        (item["session"], item["capacity"]): item
        for item in aggregate["arm_metrics"] if item["method"] == "D"
    }
    checks: list[bool] = []
    for row in v_rows:
        if row.get("status") != "PASS" or row["v"] != 1:
            continue
        comparisons = []
        for session_id in row["formal_session_ids"]:
            item = reference[(session_id, row["capacity"])]
            metrics = item["metrics"]
            raw_max_queue = max(
                phase["sampled_max_queue_bytes"]
                for probe in item["window_diagnostics"]["per_probe"].values()
                for phase in probe.values()
            )
            comparison = {
                "session_id": session_id,
                "action_mix_match": {key: value for key, value in row["action_counts"].items() if value} == metrics["action_mix"],
                "payload_match": row["payload_bytes"] == metrics["payload_generated_bytes"],
                "core_fraction_match": math.isclose(row["core_required_fraction"], metrics["core"]["required"] / metrics["n_generated"], abs_tol=1e-15),
                "queue_max_match": row["max_queue_bytes"] == raw_max_queue,
                "hardware_post_release_coverage_reference": metrics["core"]["on_time_rate"],
            }
            comparisons.append(comparison)
            checks.extend(comparison[key] for key in ("action_mix_match", "payload_match", "core_fraction_match", "queue_max_match"))
        row["formal_v1_descriptive_comparisons"] = comparisons
        row["formal_v1_exact_match_required"] = False
    return {
        "cells_checked": len(checks) // 4,
        "checks_per_cell": 4,
        "all_match": all(checks) and bool(checks),
        "failed_checks": sum(not value for value in checks),
        "exact_match_required": False,
        "scope": "descriptive_comparison_only_corrected_allocator_differs_from_frozen_service",
    }


def phase_map(seed: int) -> dict[str, int]:
    rng = random.Random(seed)
    return {device: phase for device, phase in zip(DEVICES, rng.sample(range(TICKS_PER_SECOND), len(DEVICES)))}


def simulate_tick_baseline(method: str, capacity: str, seed: int) -> dict[str, Any]:
    """One-millisecond payload-upload model with an application byte bucket."""
    cap = CAPACITY_BYTES[capacity]
    bps = CAPACITY_BPS[capacity]
    phases = phase_map(seed) if method == "desynchronized_independent" else {device: 0 for device in DEVICES}
    arrivals: dict[int, list[tuple[str, int]]] = {}
    for window in range(WINDOWS):
        for device in DEVICES:
            arrivals.setdefault(window * TICKS_PER_SECOND + phases[device], []).append((device, window))
    queues = {device: deque() for device in DEVICES}
    qbytes = {device: 0 for device in DEVICES}
    mixes: Counter[str] = Counter()
    payload = 0
    full_events = 0
    timely_full = 0
    max_queue = 0
    cap_violations = 0
    overfull_backlog_batches = 0
    upload_infeasible_batches = 0
    last_arrival = max(arrivals)
    final_tick = last_arrival + MAX_DRAIN_WINDOWS * TICKS_PER_SECOND
    drain_complete_tick: int | None = None

    for tick in range(final_tick + 1):
        if tick % TICKS_PER_SECOND == 0:
            # This models a one-second application byte bucket, not physical
            # Wi-Fi: unused intra-bucket credit carries to later arrivals and
            # resets at the bucket boundary. Integer residual service is now
            # work conserving whenever backlog exists.
            service_credit = 0
            allocated_in_bucket = 0
        batch = arrivals.get(tick, [])
        if batch:
            chosen: dict[str, dict[str, Any]] = {}
            for device, window in batch:
                safe_only = method == "shielded_coordinated"
                chosen[device] = select_local(device, bps, 1.0, qbytes[device], safe_only)
            if method in {"central_coordinated", "shielded_coordinated"}:
                # Coordinated baselines have a synchronized batch by design.
                chosen = joint_admit(chosen, cap - allocated_in_bucket, bps, method == "shielded_coordinated", seed, batch[0][1], existing_queues=qbytes)
            overfull_backlog_batches += int(sum(qbytes.values()) > cap - allocated_in_bucket)
            upload_infeasible_batches += int(not same_round_upload_feasible(qbytes, {d: a["payload"] for d, a in chosen.items()}, cap - allocated_in_bucket))
            for device, window in batch:
                action = chosen[device]
                measured = window >= WARMUP
                if measured:
                    mixes[action["id"]] += 1
                    payload += action["payload"]
                if action["payload"]:
                    item = {
                        "remaining": action["payload"], "action": action["id"],
                        "origin_tick": tick, "measured": measured,
                        "core": action["execution"] == "core",
                    }
                    queues[device].append(item)
                    qbytes[device] += action["payload"]
                    if measured and item["core"]:
                        full_events += 1

        # Exactly cap bytes are made available per 1000 ticks, without rounding drift.
        allowance = ((tick + 1) * cap // TICKS_PER_SECOND) - (tick * cap // TICKS_PER_SECOND)
        service_credit += allowance
        grants = waterfill(qbytes, service_credit, tie_offset=tick)
        granted = sum(grants.values())
        service_credit -= granted
        allocated_in_bucket += granted
        if service_credit < 0 or allocated_in_bucket > cap:
            cap_violations += 1
        for device in DEVICES:
            completed = consume_fifo(queues[device], grants[device], tick + 1)
            qbytes[device] -= grants[device]
            for item in completed:
                if item["measured"] and item["core"] and upload_on_time(item["origin_tick"], item["completion"], DEADLINE_TICKS):
                    timely_full += 1
        max_queue = max(max_queue, *qbytes.values())
        if tick >= last_arrival and not any(qbytes.values()):
            drain_complete_tick = tick
            break

    generated_end = (WINDOWS - 1) * TICKS_PER_SECOND + max(phases.values())
    drain_ticks = None if drain_complete_tick is None else max(0, drain_complete_tick - generated_end)
    return {
        "phase_ticks": phases,
        "phase_seconds": {device: phases[device] / TICKS_PER_SECOND for device in DEVICES},
        "action_counts": action_mix(mixes),
        "core_required_fraction": full_events / (MEASURED * len(DEVICES)),
        "payload_bytes": payload,
        "max_queue_bytes": max_queue,
        "upload_on_time_fraction_of_core_required": None if full_events == 0 else timely_full / full_events,
        "core_required_events": full_events,
        "on_time_core_required_uploads": timely_full,
        "completion_endpoint": "payload_upload_only",
        "completion_resolution_ms": 1,
        "completion_quantization": "tick_end_upper_bound",
        "deadline_origin": "modeled_payload_release_tick",
        "deadline_ms": 1000,
        "includes_detector_compute_core_inference_or_wifi_jitter": False,
        "drain_ticks_used": drain_ticks,
        "final_queue_bytes": sum(qbytes.values()),
        "allocator_cap_check_failures": cap_violations,
        "cap_check_scope": "implementation_invariant_only",
        "preexisting_backlog_exceeds_remaining_bucket_batches": overfull_backlog_batches,
        "remaining_bucket_upload_infeasible_batches": upload_infeasible_batches,
        "admission_policy": "backlog_reserved_upload_budget" if method in {"central_coordinated", "shielded_coordinated"} else "independent_no_joint_admission",
        "shield_precheck_scope": "isolated_service_only" if method == "shielded_coordinated" else "not_used",
    }


def task_b() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    methods = (
        "desynchronized_independent", "synchronized_independent",
        "central_coordinated", "shielded_coordinated",
    )
    for seed in DESYNC_SEEDS:
        for capacity in CAPACITY_BPS:
            for method in methods:
                row = {
                    "status": "PASS", "seed": seed, "capacity": capacity, "method": method, "v": 1.0,
                    "seed_role": "arrival_phase" if method == "desynchronized_independent" else ("unused_deterministic_identity" if method == "synchronized_independent" else "joint_admission_tie_break"),
                    "independent_random_replication_claimed": method == "desynchronized_independent",
                }
                try:
                    row.update(simulate_tick_baseline(method, capacity, seed))
                except Exception as exc:  # retain every failed run
                    row.update(status="FAIL", error=repr(exc), traceback=traceback.format_exc())
                rows.append(row)
    return rows


def locate_ledger(session: str, attempt: str, arm: str, capacity: str, device: str) -> Path:
    root = RAW_ROOT / session / f"attempt_{attempt}" / f"{arm}_{capacity}" / "raw" / "probe" / device
    matches = sorted(root.glob("*/event_ledger.jsonl"))
    if len(matches) != 1:
        raise FileNotFoundError(f"expected one ledger below {root}, found {len(matches)}")
    return matches[0]


def task_c(accepted: dict[str, str], session_schedule: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    method_names = {"A": "fixed_local", "B": "fixed_summary", "C": "fixed_full", "D": "independent_dpp", "E": "central_dpp", "F": "shielded_dpp"}
    nominal_rows: list[dict[str, Any]] = []
    diagnostic_source: dict[str, list[float]] = {device: [] for device in DEVICES}
    first_window_lateness: dict[str, list[float]] = {device: [] for device in DEVICES}
    second_window_lateness: dict[str, list[float]] = {device: [] for device in DEVICES}
    first_window_decision_latency: dict[str, list[float]] = {device: [] for device in DEVICES}
    first_window_completion_latency: dict[str, list[float]] = {device: [] for device in DEVICES}
    for session in session_schedule:
        session_id = session["session_id"]
        attempt = accepted[session_id]
        for arm in "ABCDEF":
            for capacity in CAPACITY_BPS:
                for device in DEVICES:
                    row: dict[str, Any] = {
                        "status": "PASS", "session_id": session_id, "attempt": attempt,
                        "seed": session["seed"], "arm": arm, "method": method_names[arm],
                        "capacity": capacity, "device": device,
                    }
                    try:
                        ledger_path = locate_ledger(session_id, attempt, arm, capacity, device)
                        records = [item for item in read_jsonl(ledger_path) if item.get("record_type") != "ledger_header"]
                        probe_windows = read_jsonl(ledger_path.parent / "probe_windows.jsonl")
                        window_zero = next(
                            (item for item in probe_windows if item.get("record_type") == "probe_window" and item.get("window_index") == 0),
                            None,
                        )
                        if window_zero is not None:
                            if window_zero.get("decision_latency_ms") is not None:
                                first_window_decision_latency[device].append(float(window_zero["decision_latency_ms"]))
                            if window_zero.get("evidence_completion_ms") is not None:
                                first_window_completion_latency[device].append(float(window_zero["evidence_completion_ms"]))
                        measured = [item for item in records if item.get("window_phase") == "measured"]
                        required = [item for item in measured if item.get("requires_core")]
                        post_values: list[float] = []
                        nominal_values: list[float] = []
                        lateness_values: list[float] = []
                        for item in measured:
                            scheduled = item.get("scheduled_release_monotonic_ns")
                            created = item.get("created_probe_monotonic_ns")
                            actual = item.get("actual_release_monotonic_ns", created)
                            if scheduled is not None and actual is not None:
                                lateness = max(0, actual - scheduled) / 1_000_000.0
                                lateness_values.append(lateness)
                                diagnostic_source[device].append(lateness)
                        all_records = sorted(records, key=lambda item: item.get("occurrence_seq", 0))
                        if all_records:
                            first_window_lateness[device].append(float(all_records[0].get("release_lateness_ns", 0)) / 1_000_000.0)
                        if len(all_records) > 1:
                            second_window_lateness[device].append(float(all_records[1].get("release_lateness_ns", 0)) / 1_000_000.0)
                        for item in required:
                            returned = item.get("result_received_monotonic_ns")
                            created = item.get("created_probe_monotonic_ns")
                            scheduled = item.get("scheduled_release_monotonic_ns")
                            if returned is not None and created is not None:
                                post_values.append((returned - created) / 1_000_000.0)
                            if returned is not None and scheduled is not None:
                                nominal_values.append((returned - scheduled) / 1_000_000.0)
                        deadline = 1000.0
                        post_timely = sum(value <= deadline for value in post_values)
                        nominal_timely = sum(value <= deadline for value in nominal_values)
                        n = len(required)
                        row.update(
                            ledger_path=str(ledger_path), ledger_sha256=sha256(ledger_path),
                            measured_events=len(measured), core_required_events=n,
                            post_release_results_observed=len(post_values),
                            post_release_on_time_count=post_timely,
                            post_release_on_time_coverage=None if n == 0 else post_timely / n,
                            nominal_results_observed=len(nominal_values), nominal_on_time_count=nominal_timely,
                            nominal_on_time_coverage=None if n == 0 else nominal_timely / n,
                            post_release_latency_ms_p50=quantile(post_values, 0.50),
                            post_release_latency_ms_p95=quantile(post_values, 0.95),
                            post_release_latency_ms_p99=quantile(post_values, 0.99),
                            nominal_latency_ms_p50=quantile(nominal_values, 0.50),
                            nominal_latency_ms_p95=quantile(nominal_values, 0.95),
                            nominal_latency_ms_p99=quantile(nominal_values, 0.99),
                            release_lateness_ms_p50=quantile(lateness_values, 0.50),
                            release_lateness_ms_p95=quantile(lateness_values, 0.95),
                            release_lateness_ms_p99=quantile(lateness_values, 0.99),
                        )
                    except Exception as exc:
                        row.update(status="FAIL", error=repr(exc), traceback=traceback.format_exc())
                    nominal_rows.append(row)

    probe_source = RUNTIME / "netshield" / "probe.py"
    core_source = RUNTIME / "netshield" / "core.py"
    diagnostics: list[dict[str, Any]] = []
    aggregate_quantiles: dict[str, dict[str, float | None]] = {}
    for device in DEVICES:
        values = diagnostic_source[device]
        q = {"p50": quantile(values, 0.50), "p95": quantile(values, 0.95), "p99": quantile(values, 0.99)}
        aggregate_quantiles[device] = q
        diagnostics.append({
            "status": "SOURCE_AND_LOG_SUPPORTED",
            "device": device,
            "measured_event_count": len(values),
            "release_lateness_ms_p50": q["p50"],
            "release_lateness_ms_p95": q["p95"],
            "release_lateness_ms_p99": q["p99"],
            "window0_lateness_ms_p50": quantile(first_window_lateness[device], 0.50),
            "window1_lateness_ms_p50": quantile(second_window_lateness[device], 0.50),
            "window0_decision_latency_ms_p50": quantile(first_window_decision_latency[device], 0.50),
            "window0_evidence_completion_ms_p50": quantile(first_window_completion_latency[device], 0.50),
            "source_probe_sha256": sha256(probe_source),
            "source_core_sha256": sha256(core_source),
            "proven_cause": (
                "Each probe defines its own nominal clock before window 0; core submit is a barrier over P1/P2/P3; "
                "raw window-0 decision latency and window-1 release lateness directly expose unequal first-iteration wait; "
                "the probe loop sleeps only relative to each completed iteration and has no absolute catch-up, so that skew persists."
            ),
            "source_evidence": "probe.py:415,422-431,469-472,943-945; core.py:448-462; manifests/process_P1.json,process_P2.json,process_P3.json",
            "unproven_residual": "The exact OS/network reason that proposals repeatedly reached the barrier in P3/P2/P1 order, and residual per-session variation, are UNKNOWN.",
        })
    ordering = sorted(DEVICES, key=lambda device: aggregate_quantiles[device]["p50"] or -1, reverse=True)
    finding = {
        "observed_p50_descending": ordering,
        "p1_gt_p2_gt_p3": ordering == ["P1", "P2", "P3"],
        "scope": "accepted formal V1.2 measured events only",
    }
    return nominal_rows, diagnostics, finding


def task_d() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seed = 20260909
    fractions = ((1, 3), (1, 2), (2, 3), (3, 4), (1, 1))
    for n in (3, 8, 16, 32):
        devices = tuple(f"P{index + 1}" for index in range(n))
        for numerator, denominator in fractions:
            rho = numerator / denominator
            cap = (n * B_FULL * numerator) // denominator
            row: dict[str, Any] = {
                "status": "PASS", "n": n, "rho": rho,
                "rho_fraction": f"{numerator}/{denominator}", "capacity_bytes": cap,
                "B_bytes": B_FULL, "S_bytes": S_SUMMARY, "seed": seed,
            }
            try:
                theoretical = max(0, min(n, math.floor((cap - n * S_SUMMARY) / (B_FULL - S_SUMMARY))))
                # Scaling simulator uses homogeneous frozen H_FULL/H_SUMMARY values.
                chosen = {device: dict(ACTION_BY_ID["H_FULL"]) for device in devices}
                while sum(item["payload"] for item in chosen.values()) > cap:
                    # Every degradation ratio is identical; seeded rotating priority is the frozen tie rule.
                    order = priority(seed, 0, tuple(chosen))
                    candidates = [device for device in order if chosen[device]["id"] == "H_FULL"]
                    if not candidates:
                        break
                    chosen[candidates[-1]] = dict(ACTION_BY_ID["H_SUMMARY"])
                simulated = sum(item["id"] == "H_FULL" for item in chosen.values())
                demand = sum(item["payload"] for item in chosen.values())
                grants = waterfill({device: item["payload"] for device, item in chosen.items()}, cap)
                row.update(
                    theoretical_admitted_full_count=theoretical,
                    theoretical_full_fraction=theoretical / n,
                    simulated_admitted_full_count=simulated,
                    simulated_full_fraction=simulated / n,
                    theory_simulation_match=theoretical == simulated,
                    admitted_payload_bytes=demand,
                    aggregate_grant_bytes=sum(grants.values()),
                    allocator_cap_check_failed=sum(grants.values()) > cap,
                    cap_check_scope="implementation_invariant_only",
                )
            except Exception as exc:
                row.update(status="FAIL", error=repr(exc), traceback=traceback.format_exc())
            rows.append(row)
    return rows


def compact_summary(rows: list[dict[str, Any]], group_fields: tuple[str, ...], metric: str) -> list[dict[str, Any]]:
    groups: dict[tuple[Any, ...], list[float]] = {}
    for row in rows:
        if row.get("status") != "PASS" or row.get(metric) is None:
            continue
        key = tuple(row[field] for field in group_fields)
        groups.setdefault(key, []).append(float(row[metric]))
    output = []
    for key, values in sorted(groups.items(), key=lambda item: str(item[0])):
        item = {field: value for field, value in zip(group_fields, key)}
        item.update(row_count=len(values), mean=sum(values) / len(values), minimum=min(values), maximum=max(values))
        output.append(item)
    return output


def build_report(
    v_rows: list[dict[str, Any]], desync_rows: list[dict[str, Any]],
    nominal_rows: list[dict[str, Any]], diagnostic_rows: list[dict[str, Any]],
    release_finding: dict[str, Any], scaling_rows: list[dict[str, Any]],
    formal_v1_identity: dict[str, Any],
) -> str:
    failures = sum(row.get("status") != "PASS" for row in v_rows + desync_rows + nominal_rows + scaling_rows)
    invariant_failures = sum(row.get("allocator_cap_check_failures", 0) for row in v_rows + desync_rows)
    scaling_match = all(row.get("theory_simulation_match") is True for row in scaling_rows if row.get("status") == "PASS")
    lines = [
        "# Corrected methodology simulation report", "",
        f"Generated UTC: `{utc_now()}`", "",
        "## Scope", "",
        "Frozen V1.3 tables and accepted hardware records are read-only. Tasks A/B use the corrected work-conserving integer allocator, with residual-byte priority rotated each service interval. Coordinated admission reserves existing queue bytes before accepting new payloads. These changes define a corrected software model and are not a rerun of the physical campaign.", "",
        "Tasks A/B end at **payload upload completion**. Detector computation, actual Wi-Fi delay, core inference/queuing, and result return are not modeled. Task A conservatively timestamps upload completion at the end of each 1000 ms round; Task B uses the end of each 1 ms tick. Both use inclusive elapsed upload time <= 1000 ms, but their time resolutions and service models are not identical.", "",
        "The shield's isolated latency precheck is an optimistic screening calculation; backlog-reserved byte admission is a separate condition and neither is a full-result deadline certificate. Shared-link/core contention experiments are reported separately.", "",
        "## Experimental units", "",
        f"- Task A: {len(v_rows)} deterministic (v, capacity) cases. The 12 formal session/seed identities are metadata, not independent replicates.",
        f"- Task B: {len(desync_rows)} rows. Only the desynchronized method randomizes phases; synchronized-independent seeds are unused, and coordinated seeds only choose tie-breaking identities. Rows are not automatically independent repetitions.",
        f"- Task C: {len(nominal_rows)} timestamp-reconstruction rows from retained hardware ledgers.",
        f"- Task D: {len(scaling_rows)} deterministic scaling-conformance cases.", "",
        "## Implementation checks and historical comparison", "",
        f"Allocator cap-check failures: {invariant_failures}. This checks a simulator invariant, not independently measured link capacity. Raw service evidence requires an external-ledger reconstruction.",
        f"Scaling theory matches: {scaling_match}; retained failed rows: {failures}.",
        "The v=1 historical comparison below is descriptive: the corrected residual-byte allocator may change queues and subsequent threshold decisions. Equality with frozen service is not a validation gate.", "",
        "```json", json.dumps(formal_v1_identity, indent=2, sort_keys=True), "```", "",
        "## Task A deterministic case summary", "",
        "```json", json.dumps(compact_summary(v_rows, ("v", "capacity"), "core_required_fraction"), indent=2, sort_keys=True), "```", "",
        "## Task B descriptive row summary", "",
        "```json", json.dumps(compact_summary(desync_rows, ("method", "capacity"), "upload_on_time_fraction_of_core_required"), indent=2, sort_keys=True), "```", "",
        "## Hardware timing reconstruction", "",
        "Task C alone uses result_received - created_probe (post-release) and result_received - scheduled_release (nominal) for core-required measured events. Missing returned results remain in the denominator. It does not replace raw per-service-byte accounting.",
        f"Release-lateness finding: {json.dumps(release_finding, sort_keys=True)}", "",
        "## Verdict", "",
        "PASS — corrected software cases and implementation checks completed." if not failures and not invariant_failures and scaling_match else "PASS_WITH_ISSUES — inspect failed cases and invariant fields.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    configure_private_inputs()
    started = utc_now()
    failures: list[dict[str, Any]] = []
    session_schedule = read_json(PROTOCOL / "inputs" / "SESSION_SCHEDULE.json")
    accepted = read_json(AUDIT_RESULTS / "ACCEPTED_EXCLUDED_ATTEMPTS.json")["accepted_attempts"]

    v_rows = task_a(session_schedule)
    formal_v1_identity = annotate_formal_v1_identity(v_rows)
    write_csv(OUTPUT / "V_SWEEP_RESULTS.csv", v_rows)
    desync_rows = task_b()
    write_csv(OUTPUT / "DESYNC_BASELINE_RESULTS.csv", desync_rows)
    nominal_rows, diagnostics, release_finding = task_c(accepted, session_schedule)
    write_csv(OUTPUT / "NOMINAL_DEADLINE_RESULTS.csv", nominal_rows)
    write_csv(OUTPUT / "RELEASE_LATENESS_DIAGNOSTIC.csv", diagnostics)
    scaling_rows = task_d()
    write_csv(OUTPUT / "SCALING_RESULTS.csv", scaling_rows)

    for task, rows in (("A", v_rows), ("B", desync_rows), ("C", nominal_rows), ("D", scaling_rows)):
        for row in rows:
            if row.get("status") != "PASS":
                failures.append({"task": task, **row})
    write_json(OUTPUT / "FAILED_RUNS.json", failures)

    source_files = {
        "raw_zip": RAW_ZIP,
        "actions": PROTOCOL / "inputs" / "actions.json",
        "session_schedule": PROTOCOL / "inputs" / "SESSION_SCHEDULE.json",
        "accepted_attempts": AUDIT_RESULTS / "ACCEPTED_EXCLUDED_ATTEMPTS.json",
        "rebuilt_aggregate_event_metrics": AUDIT_RESULTS / "REBUILT_AGGREGATE_EVENT_METRICS.json",
        "formal_low_config": PROTOCOL / "configs" / "formal_v1_2_low.json",
        "formal_mid_config": PROTOCOL / "configs" / "formal_v1_2_mid.json",
        "formal_high_config": PROTOCOL / "configs" / "formal_v1_2_high.json",
        "frozen_actions_source": RUNTIME / "netshield" / "actions.py",
        "frozen_probe_source": RUNTIME / "netshield" / "probe.py",
        "frozen_core_source": RUNTIME / "netshield" / "core.py",
        "analysis_script": Path(__file__).resolve(),
        "simulation_primitives": HERE / "simulation_primitives.py",
        "historical_script": HERE / "legacy" / "run_methodology_repair_v1_3.py",
    }
    metadata = {
        "schema": "ton_corrected_upload_simulation_v2",
        "historical_outputs_replaced": False,
        "completion_endpoint_tasks_a_b": "payload_upload_only",
        "allocator_residual_policy": "sorted_active_devices_rotated_by_service_interval",
        "cap_checks": "implementation_invariants_not_measurements",
        "started_utc": started,
        "completed_utc": utc_now(),
        "command": [sys.executable, str(Path(__file__).resolve())],
        "cwd": os.getcwd(),
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "machine": platform.machine(),
            "executable": sys.executable,
        },
        "scope_guards": {
            "raspberry_pi_campaign_rerun": False,
            "formal_v1_2_evidence_modified": False,
            "manuscript_modified": False,
            "github_modified": False,
            "overleaf_modified": False,
        },
        "task_a": {"v_values": V_VALUES, "capacities_bps": CAPACITY_BPS, "case_count": len(V_VALUES) * len(CAPACITY_BPS), "experimental_unit": "deterministic_parameter_case", "seed_affects_decisions": False, "formal_session_seeds_are_identity_labels": [item["seed"] for item in session_schedule]},
        "task_b": {
            "seeds": DESYNC_SEEDS, "ticks_per_second": TICKS_PER_SECOND,
            "phase_rule": "python random.Random(seed).sample(range(1000),3), mapped P1/P2/P3",
            "selector_v": 1.0,
            "shield_nominal_telemetry": {"tx_retries_delta": 0, "thermal_guard_triggered": False, "memory_guard_triggered": False},
        },
        "task_c": {"accepted_attempts": accepted, "cohort": "measured", "deadline_ms": 1000.0},
        "task_d": {"n": [3, 8, 16, 32], "rho": ["1/3", "1/2", "2/3", "3/4", "1"], "B": B_FULL, "S": S_SUMMARY},
        "input_sha256": {name: {"path": str(path), "sha256": sha256(path)} for name, path in source_files.items()},
        "planned_and_retained": {
            "task_a_rows": len(v_rows), "task_b_rows": len(desync_rows),
            "task_c_rows": len(nominal_rows), "task_d_rows": len(scaling_rows),
            "failed_rows": len(failures),
        },
        "release_lateness_finding": release_finding,
        "formal_v1_replay_identity": formal_v1_identity,
    }
    write_json(OUTPUT / "RUN_METADATA.json", metadata)
    report = build_report(v_rows, desync_rows, nominal_rows, diagnostics, release_finding, scaling_rows, formal_v1_identity)
    (OUTPUT / "VALIDATION_REPORT.md").write_text(report, encoding="utf-8")

    invariants_pass = (
        all(row.get("theory_simulation_match") is True for row in scaling_rows if row.get("status") == "PASS")
        and all(row.get("allocator_cap_check_failed") is False for row in scaling_rows if row.get("status") == "PASS")
        and all(row.get("allocator_cap_check_failures", 0) == 0 for row in v_rows + desync_rows if row.get("status") == "PASS")
    )
    overall_pass = not failures and invariants_pass
    run_summary = {
        "status": "PASS" if overall_pass else "PASS_WITH_ISSUES",
        "started_utc": started,
        "completed_utc": utc_now(),
        "task_a_rows": len(v_rows), "task_b_rows": len(desync_rows),
        "task_c_rows": len(nominal_rows), "task_d_rows": len(scaling_rows),
        "retained_failures": len(failures), "invariants_pass": invariants_pass,
    }
    (OUTPUT / "run.log").write_text(json.dumps(run_summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    (OUTPUT / "sources").mkdir()
    for source in (Path(__file__).resolve(), HERE / "simulation_primitives.py"):
        shutil.copy2(source, OUTPUT / "sources" / source.name)
    (OUTPUT / "sources" / "legacy").mkdir()
    shutil.copy2(HERE / "legacy" / "run_methodology_repair_v1_3.py", OUTPUT / "sources" / "legacy" / "run_methodology_repair_v1_3.py")
    hash_targets = sorted(path for path in OUTPUT.rglob("*") if path.is_file() and path.name != "SHA256SUMS.txt")
    with (OUTPUT / "SHA256SUMS.txt").open("w", encoding="utf-8") as stream:
        for path in hash_targets:
            stream.write(f"{sha256(path)}  {path.relative_to(OUTPUT).as_posix()}\n")

    ZIP_PATH.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ZIP_PATH, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(OUTPUT.rglob("*")):
            if path.is_file():
                archive.write(path, arcname=f"{OUTPUT.name}/{path.relative_to(OUTPUT).as_posix()}")
    print(json.dumps({
        "status": "PASS" if overall_pass else "PASS_WITH_ISSUES",
        "output_directory": str(OUTPUT), "zip": str(ZIP_PATH),
        "zip_sha256": sha256(ZIP_PATH), "failures": len(failures),
    }, indent=2))
    return 0 if overall_pass else 2


if __name__ == "__main__":
    raise SystemExit(main())
