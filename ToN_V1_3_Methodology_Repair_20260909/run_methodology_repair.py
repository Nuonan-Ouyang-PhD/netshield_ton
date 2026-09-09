#!/usr/bin/env python3
"""Independent ToN V1.3 methodology-repair analyses.

This program treats the accepted V1.2 campaign, protocol, action table, and
runtime source as read-only inputs.  It never contacts Raspberry Pis and never
writes outside its own output directory (plus the sibling final ZIP).
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import platform
import random
import sys
import traceback
import zipfile
from collections import Counter, deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent


def required_path(name: str) -> Path:
    value = os.environ.get(name)
    if not value:
        raise SystemExit(f"Set {name} to the retained local evidence path before running")
    return Path(value).expanduser().resolve()


AUDIT = required_path("TON_AUDIT_ROOT")
RAW_ROOT = AUDIT / "extracted_sessions"
PROTOCOL = AUDIT / "protocol"
AUDIT_RESULTS = AUDIT / "results"
RUNTIME = required_path("TON_RUNTIME_ROOT")
RAW_ZIP = required_path("TON_RAW_ZIP")
ZIP_PATH = Path(
    os.environ.get(
        "TON_OUTPUT_ZIP",
        str(HERE.parent / "ToN_V1_3_Methodology_Repair_20260909.zip"),
    )
).expanduser().resolve()

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


ACTIONS = action_table()
ACTION_BY_ID = {row["id"]: row for row in ACTIONS}


def is_safe(action: dict[str, Any], device: str, capacity_bps: int) -> bool:
    compute = float(action["compute_ms"][device])
    core_raw = action["core_ms"]
    core = float(core_raw[device] if isinstance(core_raw, dict) else core_raw)
    network = action["payload"] * 8 / capacity_bps * 1000.0 if action["payload"] else 0.0
    return compute + core + network <= 1000.0


def select_local(device: str, capacity_bps: int, v: float, queue_bytes: int, safe_only: bool) -> dict[str, Any]:
    pool = [action for action in ACTIONS if (not safe_only or is_safe(action, device, capacity_bps))]
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
    pool = [action for action in ACTIONS if (not safe_only or is_safe(action, device, capacity_bps))]
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
    safe_only: bool, seed: int, window: int,
) -> dict[str, dict[str, Any]]:
    chosen = dict(chosen)
    while sum(action["payload"] for action in chosen.values()) > capacity_bytes:
        options: list[tuple[float, str, dict[str, Any]]] = []
        for device, current in chosen.items():
            replacement = degrade(current, device, capacity_bps, safe_only)
            released = current["payload"] - replacement["payload"]
            if released > 0:
                loss = max(0.0, current["utility"] - replacement["utility"])
                options.append((loss / released, device, replacement))
        if not options:
            break
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


def waterfill(demands: dict[str, int], cap: int) -> dict[str, int]:
    devices = sorted(demands)
    remaining = int(cap)
    grants: dict[str, int] = {}
    unserved = [device for device in devices if demands[device] > 0]
    while remaining > 0 and unserved:
        share = remaining // len(unserved)
        if share == 0:
            break
        progressed = False
        for device in list(unserved):
            want = demands[device] - grants.get(device, 0)
            give = min(want, share, remaining)
            if give > 0:
                grants[device] = grants.get(device, 0) + give
                remaining -= give
                progressed = True
            if grants.get(device, 0) >= demands[device]:
                unserved.remove(device)
        if not progressed:
            break
    for device in devices:
        grants.setdefault(device, 0)
    return grants


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


ACTION_IDS = tuple(action["id"] for action in ACTIONS)


def detect_period(sequence: list[tuple[Any, ...]], max_period: int = 30) -> tuple[int | None, int | None, int]:
    """Find the earliest exact suffix cycle with at least three repeats."""
    for start in range(min(31, len(sequence))):
        suffix = sequence[start:]
        for period in range(1, min(max_period, len(suffix) // 3) + 1):
            if all(suffix[index] == suffix[index % period] for index in range(len(suffix))):
                return period, start, len(suffix) // period
    return None, None, 0


def simulate_synchronous(method: str, capacity: str, seed: int, v: float) -> dict[str, Any]:
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

    for window in range(WINDOWS):
        safe_only = method == "shielded_coordinated"
        chosen = {device: select_local(device, bps, v, qbytes[device], safe_only) for device in DEVICES}
        if method in {"central_coordinated", "shielded_coordinated"}:
            chosen = joint_admit(chosen, cap, bps, safe_only, seed, window)
        measured = window >= WARMUP
        for device, action in chosen.items():
            if measured:
                mixes[action["id"]] += 1
                payload += action["payload"]
            if action["payload"]:
                item = {
                    "remaining": action["payload"], "action": action["id"],
                    "origin": window, "measured": measured, "core": action["execution"] == "core",
                }
                queues[device].append(item)
                qbytes[device] += action["payload"]
                if measured and item["core"]:
                    full_events += 1
        grants = waterfill(qbytes, cap)
        if sum(grants.values()) > cap:
            cap_violations += 1
        for device in DEVICES:
            completed = consume_fifo(queues[device], grants[device], window)
            qbytes[device] -= grants[device]
            for item in completed:
                if item["measured"] and item["core"] and item["completion"] == item["origin"]:
                    timely_full += 1
        max_queue = max(max_queue, *qbytes.values())
        trajectory.append(dict(qbytes))
        if measured:
            signatures.append(tuple(chosen[device]["id"] for device in DEVICES) + tuple(qbytes[device] for device in DEVICES))

    drain = 0
    while any(qbytes.values()) and drain < MAX_DRAIN_WINDOWS:
        grants = waterfill(qbytes, cap)
        for device in DEVICES:
            consume_fifo(queues[device], grants[device], WINDOWS + drain)
            qbytes[device] -= grants[device]
        drain += 1
    period, start, repeats = detect_period(signatures)
    return {
        "action_counts": action_mix(mixes),
        "core_required_fraction": full_events / (MEASURED * len(DEVICES)),
        "payload_bytes": payload,
        "queue_trajectory_bytes": trajectory,
        "max_queue_bytes": max_queue,
        "post_release_on_time_core_result_coverage": None if full_events == 0 else timely_full / full_events,
        "core_required_events": full_events,
        "on_time_core_results": timely_full,
        "detected_period_windows": period,
        "period_start_measured_window": start,
        "complete_period_repeats": repeats,
        "drain_windows_used": drain,
        "final_queue_bytes": sum(qbytes.values()),
        "shared_cap_violations": cap_violations,
    }


def task_a(session_schedule: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for v in V_VALUES:
        for capacity in CAPACITY_BPS:
            for session in session_schedule:
                base = {
                    "status": "PASS", "v": v, "capacity": capacity,
                    "session_id": session["session_id"], "seed": session["seed"],
                    "method": "synchronized_independent_dpp_offline_replay",
                }
                try:
                    base.update(simulate_synchronous("synchronized_independent", capacity, session["seed"], v))
                except Exception as exc:  # retain every failed run
                    base.update(status="FAIL", error=repr(exc), traceback=traceback.format_exc())
                rows.append(base)
    return rows


def annotate_formal_v1_identity(v_rows: list[dict[str, Any]]) -> dict[str, Any]:
    aggregate = read_json(AUDIT_RESULTS / "REBUILT_AGGREGATE_EVENT_METRICS.json")
    reference = {
        (item["session"], item["capacity"]): item
        for item in aggregate["arm_metrics"] if item["method"] == "D"
    }
    checks: list[bool] = []
    for row in v_rows:
        if row.get("status") != "PASS" or row["v"] != 1:
            continue
        item = reference[(row["session_id"], row["capacity"])]
        metrics = item["metrics"]
        raw_max_queue = max(
            phase["sampled_max_queue_bytes"]
            for probe in item["window_diagnostics"]["per_probe"].values()
            for phase in probe.values()
        )
        expected_core_fraction = metrics["core"]["required"] / metrics["n_generated"]
        nonzero_mix = {key: value for key, value in row["action_counts"].items() if value}
        row["formal_v1_action_mix_match"] = nonzero_mix == metrics["action_mix"]
        row["formal_v1_payload_match"] = row["payload_bytes"] == metrics["payload_generated_bytes"]
        row["formal_v1_core_fraction_match"] = math.isclose(row["core_required_fraction"], expected_core_fraction, abs_tol=1e-15)
        row["formal_v1_queue_max_match"] = row["max_queue_bytes"] == raw_max_queue
        row["formal_v1_hardware_post_release_coverage_reference"] = metrics["core"]["on_time_rate"]
        row["formal_v1_hardware_coverage_exact_match_expected"] = False
        checks.extend([
            row["formal_v1_action_mix_match"], row["formal_v1_payload_match"],
            row["formal_v1_core_fraction_match"], row["formal_v1_queue_max_match"],
        ])
    return {
        "cells_checked": sum(row.get("v") == 1 and row.get("status") == "PASS" for row in v_rows),
        "checks_per_cell": 4,
        "all_match": all(checks) and bool(checks),
        "failed_checks": sum(not value for value in checks),
    }


def phase_map(seed: int) -> dict[str, int]:
    rng = random.Random(seed)
    return {device: phase for device, phase in zip(DEVICES, rng.sample(range(TICKS_PER_SECOND), len(DEVICES)))}


def simulate_tick_baseline(method: str, capacity: str, seed: int) -> dict[str, Any]:
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
    last_arrival = max(arrivals)
    final_tick = last_arrival + MAX_DRAIN_WINDOWS * TICKS_PER_SECOND
    drain_complete_tick: int | None = None

    for tick in range(final_tick + 1):
        if tick % TICKS_PER_SECOND == 0:
            # The frozen allocator may leave fewer than n bytes unused at the
            # end of a one-second round.  Within the round, however, sub-tick
            # integer remainders must carry forward or 1 ms discretisation
            # would invent systematic capacity loss.
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
                chosen = joint_admit(chosen, cap, bps, method == "shielded_coordinated", seed, batch[0][1])
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
        grants = waterfill(qbytes, service_credit)
        granted = sum(grants.values())
        service_credit -= granted
        allocated_in_bucket += granted
        if service_credit < 0 or allocated_in_bucket > cap:
            cap_violations += 1
        for device in DEVICES:
            completed = consume_fifo(queues[device], grants[device], tick + 1)
            qbytes[device] -= grants[device]
            for item in completed:
                if item["measured"] and item["core"] and item["completion"] - item["origin_tick"] <= DEADLINE_TICKS:
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
        "post_release_on_time_core_result_coverage": None if full_events == 0 else timely_full / full_events,
        "core_required_events": full_events,
        "on_time_core_results": timely_full,
        "drain_ticks_used": drain_ticks,
        "final_queue_bytes": sum(qbytes.values()),
        "shared_cap_violations": cap_violations,
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
                row = {"status": "PASS", "seed": seed, "capacity": capacity, "method": method, "v": 1.0}
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
                    shared_cap_violation=sum(grants.values()) > cap,
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
        item.update(n=len(values), mean=sum(values) / len(values), minimum=min(values), maximum=max(values))
        output.append(item)
    return output


def build_report(
    v_rows: list[dict[str, Any]], desync_rows: list[dict[str, Any]],
    nominal_rows: list[dict[str, Any]], diagnostic_rows: list[dict[str, Any]],
    release_finding: dict[str, Any], scaling_rows: list[dict[str, Any]],
    formal_v1_identity: dict[str, Any],
) -> str:
    failures = {
        "A": sum(row.get("status") != "PASS" for row in v_rows),
        "B": sum(row.get("status") != "PASS" for row in desync_rows),
        "C": sum(row.get("status") != "PASS" for row in nominal_rows),
        "D": sum(row.get("status") != "PASS" for row in scaling_rows),
    }
    scaling_match = all(row.get("theory_simulation_match") is True for row in scaling_rows if row.get("status") == "PASS")
    v_summary = compact_summary(v_rows, ("v", "capacity"), "core_required_fraction")
    b_summary = compact_summary(desync_rows, ("method", "capacity"), "core_required_fraction")
    nominal_delta = []
    for row in nominal_rows:
        if row.get("status") == "PASS" and row.get("core_required_events", 0):
            nominal_delta.append(float(row["post_release_on_time_coverage"]) - float(row["nominal_on_time_coverage"]))
    lines = [
        "# ToN V1.3 Methodology Repair Validation Report",
        "",
        f"Generated UTC: `{utc_now()}`",
        "",
        "## Scope and evidence boundary",
        "",
        "The accepted V1.2 raw evidence, protocol, actions, runtime source, manuscript, GitHub, Overleaf, and Raspberry Pis were not modified. Tasks A, B, and D are offline replay/simulation results; only Task C is a reconstruction from measured formal raw timestamps. Simulated deadline coverage must not be described as a new hardware measurement.",
        "",
        "## Run completeness",
        "",
        f"- Task A: {len(v_rows)} planned rows, {failures['A']} retained failures.",
        f"- Task B: {len(desync_rows)} planned rows (20 fixed seeds x 3 capacities x 4 methods), {failures['B']} retained failures.",
        f"- Task C: {len(nominal_rows)} planned session/method/capacity/device rows, {failures['C']} retained failures.",
        f"- Task D: {len(scaling_rows)} planned n/rho rows, {failures['D']} retained failures; theory/simulation all-match={scaling_match}.",
        "",
        "## Task A — v sensitivity",
        "",
        "The exact frozen objective `v*utility - queue_bytes*payload_bytes/1,000,000`, frozen action order, and exact integer max-min allocator were replayed for all 12 formal seeds. `queue_trajectory_bytes` contains every generation-window post-service queue for P1/P2/P3. Period detection is exact and automatic: it reports the earliest suffix (within the first 30 measured windows) repeated at least three times.",
        "",
        f"The v=1 replay was checked against all {formal_v1_identity['cells_checked']} accepted formal D session-capacity cells for exact nonzero action mix, payload bytes, core fraction, and sampled max queue: all-match={formal_v1_identity['all_match']}, failed checks={formal_v1_identity['failed_checks']}. Hardware post-release coverage is retained as a reference column but is not an identity criterion: the service replay has no Pi runtime/network jitter and exact equality is not expected.",
        "",
        "Core-required-fraction ranges by v/capacity:",
        "",
        "```json",
        json.dumps(v_summary, indent=2, sort_keys=True),
        "```",
        "",
        "## Task B — desynchronised independent baseline",
        "",
        "Each desynchronised probe uses a seed-fixed independent initial phase in [0,1) s. It observes only its own queue when selecting; there is no action/queue exchange and no joint admission. A 1 ms discrete-event clock makes exactly C/8 application bytes available per second (integer cumulative accounting) and applies the frozen deterministic max-min shared service to current queues. Synchronized independent, central coordinated, and shielded coordinated use the same simulator, workload count, action table, and service rule; coordinated methods alone use the frozen joint degradation rule.",
        "",
        "Shield safety uses the frozen deadline calculation under a nominal healthy state: retry delta 0, no thermal guard trigger, and no memory guard trigger. This is a software sensitivity baseline, not replayed hardware telemetry.",
        "",
        "Core-required-fraction ranges by method/capacity:",
        "",
        "```json",
        json.dumps(b_summary, indent=2, sort_keys=True),
        "```",
        "",
        "## Task C — nominal deadline reconstruction",
        "",
        "For core-required measured events, `post_release_latency=result_received-created_probe` and `nominal_latency=result_received-scheduled_release`. Missing results remain in the denominator and are not counted on time. Release-lateness quantiles use all measured events in each session/method/capacity/device cell.",
        "",
        f"Across cells with a core-required endpoint, post-release minus nominal coverage ranged from {min(nominal_delta) if nominal_delta else None} to {max(nominal_delta) if nominal_delta else None}.",
        "",
        f"Observed aggregate p50 ordering: `{release_finding['observed_p50_descending']}`; P1>P2>P3={release_finding['p1_gt_p2_gt_p3']}.",
        "",
        "The source/log-supported mechanism is recorded in `RELEASE_LATENESS_DIAGNOSTIC.csv`: independent per-probe nominal clocks are created before window 0; the core decision is a three-probe barrier; raw window-0 decision latency and window-1 release lateness expose unequal first-iteration waiting; and the probe loop sleeps relative to the completed iteration without absolute catch-up. The exact OS/network reason for the recurring proposal-arrival order and residual per-session variation are explicitly UNKNOWN.",
        "",
        "## Task D — scaling validation",
        "",
        "The independent simulator starts all n probes at H_FULL and repeatedly applies the frozen H_FULL-to-H_SUMMARY capacity degradation until total admitted payload fits C. For every requested n and rho, the simulated full count is compared with `clip_[0,n](floor((C-nS)/(B-S)))`, B=131072 and S=16384.",
        "",
        f"All {len(scaling_rows)} theory/simulation comparisons match: **{scaling_match}**.",
        "",
        "## Validation verdict",
        "",
        ("PASS — all planned runs are present, the v=1 formal identity gate passed, no shared-cap violation occurred, and scaling theory matches simulation."
         if not any(failures.values()) and formal_v1_identity["all_match"] and scaling_match and all(row.get("shared_cap_violations", 0) == 0 for row in v_rows + desync_rows if row.get("status") == "PASS")
         else "PASS_WITH_ISSUES — inspect retained FAIL rows or invariant fields before use."),
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    started = utc_now()
    failures: list[dict[str, Any]] = []
    session_schedule = read_json(PROTOCOL / "inputs" / "SESSION_SCHEDULE.json")
    accepted = read_json(AUDIT_RESULTS / "ACCEPTED_EXCLUDED_ATTEMPTS.json")["accepted_attempts"]

    v_rows = task_a(session_schedule)
    formal_v1_identity = annotate_formal_v1_identity(v_rows)
    write_csv(HERE / "V_SWEEP_RESULTS.csv", v_rows)
    desync_rows = task_b()
    write_csv(HERE / "DESYNC_BASELINE_RESULTS.csv", desync_rows)
    nominal_rows, diagnostics, release_finding = task_c(accepted, session_schedule)
    write_csv(HERE / "NOMINAL_DEADLINE_RESULTS.csv", nominal_rows)
    write_csv(HERE / "RELEASE_LATENESS_DIAGNOSTIC.csv", diagnostics)
    scaling_rows = task_d()
    write_csv(HERE / "SCALING_RESULTS.csv", scaling_rows)

    for task, rows in (("A", v_rows), ("B", desync_rows), ("C", nominal_rows), ("D", scaling_rows)):
        for row in rows:
            if row.get("status") != "PASS":
                failures.append({"task": task, **row})
    write_json(HERE / "FAILED_RUNS.json", failures)

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
    }
    metadata = {
        "schema": "ton_v1_3_methodology_repair_run_metadata_v1",
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
        "task_a": {"v_values": V_VALUES, "capacities_bps": CAPACITY_BPS, "formal_session_seeds": [item["seed"] for item in session_schedule]},
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
    write_json(HERE / "RUN_METADATA.json", metadata)
    report = build_report(v_rows, desync_rows, nominal_rows, diagnostics, release_finding, scaling_rows, formal_v1_identity)
    (HERE / "VALIDATION_REPORT.md").write_text(report, encoding="utf-8")

    invariants_pass = (
        formal_v1_identity["all_match"]
        and all(row.get("theory_simulation_match") is True for row in scaling_rows if row.get("status") == "PASS")
        and all(row.get("shared_cap_violations", 0) == 0 for row in v_rows + desync_rows if row.get("status") == "PASS")
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
    (HERE / "run.log").write_text(json.dumps(run_summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    hash_targets = sorted(path for path in HERE.iterdir() if path.is_file() and path.name != "SHA256SUMS.txt")
    with (HERE / "SHA256SUMS.txt").open("w", encoding="utf-8") as stream:
        for path in hash_targets:
            stream.write(f"{sha256(path)}  {path.name}\n")

    if ZIP_PATH.exists():
        ZIP_PATH.unlink()
    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(HERE.iterdir()):
            if path.is_file():
                archive.write(path, arcname=f"{HERE.name}/{path.name}")
    print(json.dumps({
        "status": "PASS" if overall_pass else "PASS_WITH_ISSUES",
        "output_directory": str(HERE), "zip": str(ZIP_PATH),
        "zip_sha256": sha256(ZIP_PATH), "failures": len(failures),
    }, indent=2))
    return 0 if overall_pass else 2


if __name__ == "__main__":
    raise SystemExit(main())
