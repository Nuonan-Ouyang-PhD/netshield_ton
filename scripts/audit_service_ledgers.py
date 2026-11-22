#!/usr/bin/env python3
"""Independently reconstruct public ledger counts; never call a simulator.

The CRFA input is a public export of hardware records, not the private raw
archive. Software ledgers establish accounting conformance, not measurements
of Wi-Fi or Raspberry Pi performance. Summary 'violation' flags are not used
to decide whether a service cap was respected.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class AuditError(ValueError):
    pass


def check(condition: bool, description: str) -> None:
    if not condition:
        raise AuditError(description)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def integer(value: str, name: str) -> int:
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise AuditError(f"invalid integer {name}: {value!r}") from exc


def boolean(value: str) -> bool:
    check(value.lower() in {"true", "false", "1", "0"}, f"invalid boolean {value!r}")
    return value.lower() in {"true", "1"}


def audit_crfa(directory: Path) -> dict:
    service_path = directory / "CRFA_SERVICE_AUDIT.csv"
    occurrence_path = directory / "CRFA_OCCURRENCE_LEDGER.csv"
    services = read_csv(service_path)
    occurrences = read_csv(occurrence_path)
    caps = {"low": 131072, "mid": 262144, "high": 393216}
    groups: dict[str, list] = defaultdict(list)
    rounds = set()
    grants_by_key = {}
    expected_occurrences = set()
    service_rows_by_key = {}
    run_by_identity = {}
    for row in services:
        run = row["run_id"]
        round_index = integer(row["round_index"], "round_index")
        key = run, round_index
        check(key not in rounds, f"duplicate service round {key}")
        rounds.add(key)
        groups[run].append(row)
        identity = row["session_id"], row["attempt"], row["capacity"]
        check(identity not in run_by_identity or run_by_identity[identity] == run, f"ambiguous run identity {identity}")
        run_by_identity[identity] = run
        cap = integer(row["shared_cap_bytes"], "shared_cap_bytes")
        check(cap == caps[row["capacity"]], f"unexpected cap {key}")
        grants = [integer(row[f"{d}_grant_bytes"], f"{d}_grant_bytes") for d in ("P1", "P2", "P3")]
        demands = [integer(row[f"{d}_demand_bytes"], f"{d}_demand_bytes") for d in ("P1", "P2", "P3")]
        check(all(0 <= g <= d for g, d in zip(grants, demands)), f"grant outside demand {key}")
        check(sum(grants) <= cap, f"reconstructed cap violation {key}: {sum(grants)} > {cap}")
        check(sum(grants) == integer(row["sum_grant_bytes"], "sum_grant_bytes"), f"grant aggregate mismatch {key}")
        check(sum(demands) == integer(row["aggregate_service_demand_bytes"], "aggregate_service_demand_bytes"), f"demand aggregate mismatch {key}")
        for device, grant in zip(("P1", "P2", "P3"), grants):
            service_key = run, round_index, device
            grants_by_key[service_key] = grant
            service_rows_by_key[service_key] = row
            if row["phase"] == "measured":
                expected_occurrences.add(service_key)
    for run, rows in groups.items():
        rows.sort(key=lambda r: int(r["round_index"]))
        check([int(r["round_index"]) for r in rows] == list(range(len(rows))), f"missing service round {run}")
        after = {d: 0 for d in ("P1", "P2", "P3")}
        for row in rows:
            admitted = 0
            for device in after:
                before = integer(row[f"{device}_queue_before_bytes"], "queue_before_bytes")
                check(before == after[device], f"queue continuity {run}/{row['round_index']}/{device}")
                action = row[f"{device}_action"]
                check(action in {"H_NONE", "H_FULL"}, f"unexpected CRFA action {action}")
                new_bytes = 131072 if action == "H_FULL" else 0
                demand = integer(row[f"{device}_demand_bytes"], "demand_bytes")
                check(demand == before + new_bytes, f"queue conservation {run}/{row['round_index']}/{device}")
                after[device] = demand - int(row[f"{device}_grant_bytes"])
                admitted += new_bytes
            check(admitted == int(row["aggregate_admitted_bytes"]), f"admission aggregate {run}/{row['round_index']}")
        check(sum(after.values()) == 0, f"undrained service queue {run}")

    counts = {capacity: Counter() for capacity in caps}
    event_keys = set()
    observed_occurrences = set()
    for row in occurrences:
        key = row["event_key"]
        check(key not in event_keys, f"duplicate event {key}")
        event_keys.add(key)
        count = counts[row["capacity"]]
        count["generated"] += 1
        full = row["admitted_action_id"] == "H_FULL"
        check(full == boolean(row["requires_core"]) == boolean(row["rotation_selected"]), f"selection semantics {key}")
        check(int(row["payload_bytes"]) == (131072 if full else 0), f"payload/action mismatch {key}")
        parts = key.split("|")
        check(len(parts) == 4, f"invalid event key {key}")
        run = parts[1]
        check(parts[0] == row["campaign_id"] and parts[2] == row["device_id"]
              and int(parts[3]) == int(row["origin_window_index"]), f"event key fields differ {key}")
        identity = row["session_id"], row["attempt"], row["capacity"]
        check(run_by_identity.get(identity) == run, f"occurrence/service run identity {key}")
        service_key = run, int(row["origin_window_index"]), row["device_id"]
        check(service_key in expected_occurrences, f"missing measured occurrence service {key}")
        check(service_key not in observed_occurrences, f"duplicate run/window/device occurrence {key}")
        observed_occurrences.add(service_key)
        check(service_rows_by_key[service_key][f"{row['device_id']}_action"] == row["admitted_action_id"], f"occurrence/service action {key}")
        check(grants_by_key[service_key] == int(row["payload_bytes"]), f"CRFA occurrence/service mismatch {key}")
        returned = row["result_return_monotonic_ns"] != ""
        created = int(row["actual_event_creation_monotonic_ns"])
        scheduled = int(row["scheduled_release_monotonic_ns"])
        deadline = int(row["deadline_ns"])
        post = nominal = False
        if full:
            count["selected_full"] += 1
            if returned:
                end = int(row["result_return_monotonic_ns"])
                check(end >= created and end >= scheduled, f"negative result duration {key}")
                count["returned_full"] += 1
                post = end - created <= deadline
                nominal = end - scheduled <= deadline
                count["post_release_timely_full"] += post
                count["nominal_timely_full"] += nominal
                count["recorded_prediction_matches_label"] += row["core_prediction"] == row["label"]
        check(boolean(row["post_release_on_time_full"]) == post, f"post-release flag mismatch {key}")
        check(boolean(row["nominal_on_time_full"]) == nominal, f"nominal flag mismatch {key}")
        check(boolean(row["full_core_result_returned"]) == (full and returned), f"return flag mismatch {key}")
    check(observed_occurrences == expected_occurrences, "missing measured occurrence records")
    return {
        "status": "PASS", "scope": "public CRFA exported per-probe service and occurrence ledgers",
        "private_raw_archive_reopened": False, "hardware_rerun": False,
        "service_rounds_reconstructed": len(rounds), "service_runs": len(groups),
        "cap_violations_reconstructed": 0, "occurrences_reconstructed": len(occurrences),
        "capacity_counts": {key: dict(value) for key, value in counts.items()},
        "inputs_sha256": {p.name: digest(p) for p in (service_path, occurrence_path)},
        "interpretation": "Record consistency and application grant cap; not a physical-link/NIC measurement or an independent IDS-content comparison.",
    }


def audit_software(directory: Path) -> dict:
    summary_path = directory / "RUN_SUMMARY.csv"
    event_path = directory / "EVENT_LEDGER.csv"
    service_path = directory / "SERVICE_LEDGER.csv"
    summaries = read_csv(summary_path)
    events = read_csv(event_path)
    services = read_csv(service_path)
    runs = {}
    for row in summaries:
        check(row["run_id"] not in runs, "duplicate run summary")
        runs[row["run_id"]] = row
    by_event = {}
    for row in events:
        key = row["run_id"], row["event_id"]
        check(key not in by_event and row["run_id"] in runs, f"duplicate/orphan event {key}")
        by_event[key] = row
    round_bytes: Counter = Counter()
    event_bytes: Counter = Counter()
    last_service = {}
    seen_segments = set()
    for row in services:
        key = row["run_id"], row["event_id"]
        check(key in by_event, f"orphan service {key}")
        event = by_event[key]
        check(row["device"] == event["device"], f"wrong service device {key}")
        start, end, amount = (int(row[k]) for k in ("start_tick", "end_tick", "served_bytes"))
        round_index = int(row["service_round"])
        check(0 <= start < end and amount > 0, f"invalid service segment {key}")
        check(start // 1000 == (end - 1) // 1000 == round_index, f"service crosses round {key}")
        check(start >= int(event["network_ready_tick"]), f"service before readiness {key}")
        segment = key, round_index
        check(segment not in seen_segments, f"duplicate event/round segment {key}")
        seen_segments.add(segment)
        round_bytes[row["run_id"], round_index] += amount
        event_bytes[key] += amount
        last_service[key] = max(last_service.get(key, 0), end)
    for (run_id, round_index), amount in round_bytes.items():
        cap = int(runs[run_id]["capacity_bytes"])
        check(amount <= cap, f"reconstructed software cap violation {run_id}/{round_index}")
    reconstructed = {run: Counter() for run in runs}
    core_intervals = defaultdict(list)
    for key, event in by_event.items():
        selected, background = boolean(event["selected"]), boolean(event["is_background"])
        count = reconstructed[key[0]]
        if not background:
            count["requested"] += 1
            count["selected"] += selected
        if not selected:
            check(event_bytes[key] == 0 and not event["upload_done_tick"] and not event["result_return_tick"], f"unselected event served {key}")
            continue
        payload = int(event["payload_bytes"])
        check(event_bytes[key] == payload, f"event byte conservation {key}")
        upload = int(event["upload_done_tick"])
        check(upload == last_service[key], f"upload endpoint differs from service ledger {key}")
        ready, start, done, returned = (int(event[k]) for k in ("core_ready_tick", "core_start_tick", "core_done_tick", "result_return_tick"))
        check(ready == upload + int(event["uplink_extra_ticks"]), f"uplink-extra duration {key}")
        check(start >= ready and done == start + int(event["core_compute_ticks"]), f"core duration/order {key}")
        check(returned == done + int(event["return_ticks"]), f"return duration {key}")
        created, deadline = int(event["creation_tick"]), int(event["deadline_ticks"])
        upload_on_time = 0 <= upload - created <= deadline
        result_on_time = 0 <= returned - created <= deadline
        if background:
            check(event["upload_on_time"] == event["result_on_time"] == "", f"background deadline must be unscored {key}")
        else:
            expected_ready = created + int(event["detector_compute_ticks"]) + int(event["preprocessing_ticks"])
            check(int(event["network_ready_tick"]) == expected_ready, f"detector/preprocessing duration {key}")
            check(boolean(event["upload_on_time"]) == upload_on_time, f"upload deadline flag {key}")
            check(boolean(event["result_on_time"]) == result_on_time, f"result deadline flag {key}")
        if done > start:
            core_intervals[key[0]].append((start, done, key[1]))
        if not background:
            count["timely_upload"] += upload_on_time
            count["timely_result"] += result_on_time
    for run, intervals in core_intervals.items():
        intervals.sort()
        check(all(a[1] <= b[0] for a, b in zip(intervals, intervals[1:])), f"overlapping single-core jobs {run}")
    columns = {"requested": "generated_new_events", "selected": "selected_new_events",
               "timely_upload": "timely_uploads", "timely_result": "timely_results"}
    for run, counts in reconstructed.items():
        for field, column in columns.items():
            check(counts[field] == int(runs[run][column]), f"summary differs from reconstructed {field}: {run}")
    return {
        "status": "PASS", "scope": "software-only service/event ledger reconstruction",
        "runs": len(runs), "events": len(events), "service_segments": len(services),
        "nonempty_service_rounds_reconstructed": len(round_bytes),
        "cap_violations_reconstructed": 0,
        "per_run_reconstructed": {run: dict(count) for run, count in reconstructed.items()},
        "inputs_sha256": {p.name: digest(p) for p in (summary_path, event_path, service_path)},
        "interpretation": "Independent accounting checks on simulated records; does not validate injected latency assumptions against hardware.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--crfa", type=Path)
    parser.add_argument("--software", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not args.crfa and not args.software:
        parser.error("provide --crfa and/or --software")
    result = {}
    if args.crfa:
        result["crfa"] = audit_crfa(args.crfa)
    if args.software:
        result["software"] = audit_software(args.software)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(json.dumps({key: {k: v for k, v in value.items() if k not in {"per_run_reconstructed", "inputs_sha256"}} for key, value in result.items()}, indent=2))


if __name__ == "__main__":
    main()
