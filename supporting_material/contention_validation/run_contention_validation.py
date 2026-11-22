#!/usr/bin/env python3
"""Deterministic shared-link / returned-result sensitivity, not a hardware run.

Only public constants and explicit synthetic latency inputs are used.  The
one-millisecond server discards idle capacity; it does not bank a whole
round's byte budget for a later arrival.  Admission uses a separate preview
of the same declared model, so its success is model conformance, not an
independent measurement of real Wi-Fi or a runtime safety guarantee.
"""

from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import sys
from collections import defaultdict, deque
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "methodology_repair"))
from simulation_primitives import waterfill, upload_on_time

TICKS_PER_SECOND = 1000
FULL_BYTES = 131072
DEADLINE_TICKS = 1000
METHODS = ("isolated_precheck", "new_bytes_only", "backlog_aware", "deadline_reservation")
AUDITED_BASE_COMMIT = "fe09ee0eca28dc666dd9c729ac266b8426c055b9"
METHOD_DEFINITIONS = {
    "isolated_precheck": "Admit every candidate whose configured no-competition returned-result estimate is <=1000ms.",
    "new_bytes_only": "Isolated precheck, then fixed-order new full payload sum <=C; backlog ignored.",
    "backlog_aware": "Isolated precheck, then fixed-order existing remaining bytes plus new full payload sum <=C.",
    "deadline_reservation": "Fixed-order greedy admission; exact shared network/core rollout must keep every admitted new result <=1000ms.",
}
PROFILES = {
    "zero": {
        "detector_compute_ticks": [0], "preprocessing_ticks": [0],
        "uplink_extra_ticks": [0], "core_compute_ticks": [0], "return_ticks": [0],
    },
    "assumed_homogeneous": {
        "detector_compute_ticks": [40], "preprocessing_ticks": [20],
        "uplink_extra_ticks": [15], "core_compute_ticks": [35], "return_ticks": [10],
    },
    "assumed_heterogeneous": {
        "detector_compute_ticks": [20, 80, 140], "preprocessing_ticks": [10, 20, 30],
        "uplink_extra_ticks": [5, 25, 50], "core_compute_ticks": [10, 40, 100],
        "return_ticks": [5, 15, 30],
    },
}


def ceil_div(a: int, b: int) -> int:
    return (a + b - 1) // b


def components(profile: str, device_index: int) -> dict[str, int]:
    return {name: values[device_index % len(values)] for name, values in PROFILES[profile].items()}


def make_jobs(n: int, cap: int, backlog_bytes: int, profile: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Create one new full request per probe and optional partial old requests.

    A background request's payload_bytes is its remaining upload at tick zero,
    not the original event's complete payload.  Its detector work already
    happened; pending network and core work is retained.
    """
    if n <= 0 or cap <= 0 or backlog_bytes < 0:
        raise ValueError("positive n/cap and nonnegative backlog are required")
    if profile not in PROFILES:
        raise ValueError("unknown explicit latency profile")
    background, candidates = [], []
    for index in range(n):
        device = f"P{index + 1:02d}"
        delays = components(profile, index)
        candidates.append({
            "event_id": f"new_{device}", "device": device, "is_background": 0,
            "selected": 0, "payload_bytes": FULL_BYTES, "creation_tick": 0,
            "network_ready_tick": delays["detector_compute_ticks"] + delays["preprocessing_ticks"],
            "deadline_ticks": DEADLINE_TICKS, **delays,
        })
        remaining = backlog_bytes // n + int(index < backlog_bytes % n)
        if remaining:
            background.append({
                "event_id": f"old_{device}", "device": device, "is_background": 1,
                "selected": 1, "payload_bytes": remaining, "creation_tick": -1000,
                "network_ready_tick": 0, "deadline_ticks": DEADLINE_TICKS,
                **delays, "admission_reason": "preexisting_remaining_work",
            })
    return background, candidates


def simulate(jobs: list[dict[str, Any]], cap: int, *, ledger: bool = True) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Serve FIFO per probe at shared rate, then FIFO on one independent core.

    A service tick is [t,t+1).  floor((t+1)C/1000)-floor(tC/1000)
    integer bytes become available in that tick and expire if idle.  An
    upload ending at tick t arrives at the core after uplink_extra_ticks;
    core jobs are ordered by that arrival and event_id.  Return delay is a
    configured latency with no modeled return-link contention.
    """
    if cap <= 0:
        raise ValueError("capacity must be positive")
    results = copy.deepcopy(jobs)
    active_jobs = [job for job in results if job["selected"]]
    if not active_jobs:
        return results, []
    arrivals: dict[int, list[dict[str, Any]]] = defaultdict(list)
    devices = sorted({job["device"] for job in active_jobs})
    queues: dict[str, deque] = {device: deque() for device in devices}
    queued = dict.fromkeys(devices, 0)
    for job in active_jobs:
        job["remaining"] = job["payload_bytes"]
        arrivals[job["network_ready_tick"]].append(job)
    total = sum(job["payload_bytes"] for job in active_jobs)
    max_ready = max(arrivals)
    # After the last release all remaining work drains by this conservative
    # bound; it is not an event deadline or a data-dependent retry policy.
    stop = max_ready + ceil_div(total * TICKS_PER_SECOND, cap) + 2
    segments: dict[tuple[int, str], dict[str, Any]] = {}
    unfinished = len(active_jobs)
    for tick in range(stop):
        # Already queued work precedes newly ready work on the same probe,
        # including when both are represented at tick zero in this replay.
        for job in sorted(arrivals.get(tick, []), key=lambda row: (row["creation_tick"], row["event_id"])):
            queues[job["device"]].append(job)
            queued[job["device"]] += job["remaining"]
        allowance = (tick + 1) * cap // TICKS_PER_SECOND - tick * cap // TICKS_PER_SECOND
        grants = waterfill(queued, allowance, tie_offset=tick)
        for device, amount in grants.items():
            queued[device] -= amount
            while amount:
                job = queues[device][0]
                served = min(amount, job["remaining"])
                job["remaining"] -= served
                amount -= served
                if ledger:
                    key = (tick // TICKS_PER_SECOND, job["event_id"])
                    if key not in segments:
                        segments[key] = {
                            "event_id": job["event_id"], "device": device,
                            "service_round": key[0], "start_tick": tick,
                            "end_tick": tick + 1, "served_bytes": 0,
                        }
                    segments[key]["end_tick"] = tick + 1
                    segments[key]["served_bytes"] += served
                if not job["remaining"]:
                    job["upload_done_tick"] = tick + 1
                    queues[device].popleft()
                    unfinished -= 1
        if not unfinished:
            break
    if unfinished:
        raise AssertionError("conservative drain bound failed")
    for job in active_jobs:
        job["core_ready_tick"] = job["upload_done_tick"] + job["uplink_extra_ticks"]
    server_free = 0
    for job in sorted(active_jobs, key=lambda row: (row["core_ready_tick"], row["event_id"])):
        job["core_start_tick"] = max(server_free, job["core_ready_tick"])
        job["core_done_tick"] = job["core_start_tick"] + job["core_compute_ticks"]
        server_free = job["core_done_tick"]
        job["result_return_tick"] = server_free + job["return_ticks"]
        if not job["is_background"]:
            job["upload_on_time"] = int(upload_on_time(job["creation_tick"], job["upload_done_tick"], job["deadline_ticks"]))
            job["result_on_time"] = int(upload_on_time(job["creation_tick"], job["result_return_tick"], job["deadline_ticks"]))
        del job["remaining"]
    return results, sorted(segments.values(), key=lambda row: (row["service_round"], row["event_id"]))


def select_jobs(background: list[dict[str, Any]], candidates: list[dict[str, Any]], cap: int, method: str) -> list[dict[str, Any]]:
    if method not in METHODS:
        raise ValueError("unknown admission method")
    chosen = copy.deepcopy(candidates)
    old_bytes = sum(job["payload_bytes"] for job in background)
    selected_bytes = 0
    # Fixed identifier order is transparent, deterministic and not claimed
    # to optimize throughput or fairness.  Every rollout rechecks all new
    # admitted requests, since adding a competitor can delay earlier ones.
    for job in chosen:
        solo = job["network_ready_tick"] + ceil_div(job["payload_bytes"] * TICKS_PER_SECOND, cap)
        solo += job["uplink_extra_ticks"] + job["core_compute_ticks"] + job["return_ticks"]
        job["isolated_result_estimate_ticks"] = solo
        if solo > job["deadline_ticks"]:
            job["admission_reason"] = "isolated_estimate_exceeds_deadline"
            continue
        if method == "new_bytes_only" and selected_bytes + job["payload_bytes"] > cap:
            job["admission_reason"] = "new_payload_budget_exceeded"
            continue
        if method == "backlog_aware" and old_bytes + selected_bytes + job["payload_bytes"] > cap:
            job["admission_reason"] = "backlog_plus_new_budget_exceeded"
            continue
        if method == "deadline_reservation":
            job["selected"] = 1
            trial, _ = simulate(background + chosen, cap, ledger=False)
            if any(not row["result_on_time"] for row in trial if row["selected"] and not row["is_background"]):
                job["selected"] = 0
                job["admission_reason"] = "shared_pipeline_deadline_exceeded"
                continue
        job["selected"] = 1
        job["admission_reason"] = "admitted"
        selected_bytes += job["payload_bytes"]
    return chosen


def run_case(case: dict[str, Any], method: str) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    cap = case["capacity_bytes"]
    background, candidates = make_jobs(case["n"], cap, case["backlog_bytes"], case["profile"])
    chosen = select_jobs(background, candidates, cap, method)
    events, service = simulate(background + chosen, cap)
    run_id = case["case_id"] + "__" + method
    for row in events + service:
        row["run_id"] = run_id
    new = [row for row in events if not row["is_background"]]
    admitted = [row for row in new if row["selected"]]
    per_round: dict[int, int] = defaultdict(int)
    for row in service:
        per_round[row["service_round"]] += row["served_bytes"]
    summary = {
        "run_id": run_id, **case, "method": method, "evidence_type": "deterministic_software_sensitivity",
        "deadline_ticks": DEADLINE_TICKS, "tick_milliseconds": 1, "full_bytes": FULL_BYTES,
        "generated_new_events": len(new), "selected_new_events": len(admitted),
        "timely_uploads": sum(row["upload_on_time"] for row in admitted),
        "timely_results": sum(row["result_on_time"] for row in admitted),
        "selected_result_misses": sum(not row["result_on_time"] for row in admitted),
        "selection_fraction": len(admitted) / len(new),
        "timely_result_per_generated": sum(row["result_on_time"] for row in admitted) / len(new),
        "new_payload_bytes": sum(row["payload_bytes"] for row in admitted),
        "total_service_bytes": sum(row["served_bytes"] for row in service),
        "service_rounds": len(per_round),
        "max_round_service_bytes": max(per_round.values(), default=0),
        "cap_violation_counter": sum(value > cap for value in per_round.values()),
        "max_upload_tick": max((row["upload_done_tick"] for row in admitted), default=None),
        "max_result_tick": max((row["result_return_tick"] for row in admitted), default=None),
    }
    return summary, events, service


def cases() -> list[dict[str, Any]]:
    result = []
    for n in (3, 8, 16, 32):
        ratios = (("low", 1, 3), ("mid", 2, 3), ("high", 1, 1)) if n == 3 else (("mid", 2, 3),)
        profiles = tuple(PROFILES) if n == 3 else ("zero", "assumed_homogeneous")
        for capacity, numerator, denominator in ratios:
            cap = n * FULL_BYTES * numerator // denominator
            for backlog_name, backlog in (("empty", 0), ("half_round", cap // 2)):
                for profile in profiles:
                    result.append({
                        "case_id": f"n{n:02d}_{capacity}_{backlog_name}_{profile}",
                        "n": n, "capacity": capacity, "capacity_bytes": cap,
                        "capacity_ratio_numerator": numerator, "capacity_ratio_denominator": denominator,
                        "backlog": backlog_name, "backlog_bytes": backlog, "profile": profile,
                    })
    return result


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = list(dict.fromkeys(key for row in rows for key in row))
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=HERE / "results")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    summaries, events, service = [], [], []
    for case in cases():
        for method in METHODS:
            summary, new_events, new_service = run_case(case, method)
            summaries.append(summary)
            events.extend(new_events)
            service.extend(new_service)
    for name, rows in (("RUN_SUMMARY.csv", summaries), ("EVENT_LEDGER.csv", events), ("SERVICE_LEDGER.csv", service)):
        write_csv(args.output / name, rows)
    config = {
        "schema_version": 1, "evidence_type": "deterministic_software_sensitivity",
        "audited_repository_base_commit": AUDITED_BASE_COMMIT,
        "repository": "https://github.com/Nuonan-Ouyang-PhD/netshield_ton",
        "latencies_are_measured": False, "tick_milliseconds": 1,
        "full_bytes": FULL_BYTES, "deadline_ticks": DEADLINE_TICKS,
        "profiles": PROFILES, "cases": cases(), "methods": METHODS,
        "method_definitions": METHOD_DEFINITIONS,
        "assumptions": [
            "Shared fixed-rate application-byte proxy; unused per-tick service expires.",
            "FIFO per probe with integer max-min allocation across ready probes.",
            "One FIFO core; result return has configured delay but no competing return-byte queue.",
            "All new events created at tick zero; deterministic detector/preprocessing precedes upload readiness.",
            "Uplink-extra and return delays are declared sensitivity inputs, not real Wi-Fi measurements.",
            "Background payload is the remaining byte count of an old request; its core processing is pending.",
            "Fixed admission identifier order; no optimality or long-run fairness claim.",
            "Deadline reservation previews this exact model; not a proof for unmodeled runtime jitter.",
            "Alert/summary detection utility and detection accuracy are not evaluated.",
        ],
        "source_sha256": {
            "run_contention_validation.py": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "../methodology_repair/simulation_primitives.py": hashlib.sha256((HERE.parent / "methodology_repair/simulation_primitives.py").read_bytes()).hexdigest(),
        },
        "run_count": len(summaries), "event_rows": len(events), "service_rows": len(service),
    }
    (args.output / "CONFIG.json").write_text(json.dumps(config, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    digest_rows = []
    for path in sorted(args.output.iterdir()):
        if path.name in {"RUN_SUMMARY.csv", "EVENT_LEDGER.csv", "SERVICE_LEDGER.csv", "CONFIG.json"}:
            digest_rows.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}")
    (args.output / "SHA256SUMS.txt").write_text("\n".join(digest_rows) + "\n", encoding="utf-8")
    print(json.dumps({"runs": len(summaries), "event_rows": len(events), "service_rows": len(service), "output": str(args.output)}, sort_keys=True))


if __name__ == "__main__":
    main()
