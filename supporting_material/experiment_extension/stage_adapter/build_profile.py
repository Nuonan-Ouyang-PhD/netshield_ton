"""Derive scoped empirical stage envelopes from hash-bound physical captures.

Consumes first-measured-batch records from the complete prospective 16-condition
calibration plan. The private adapter and its reviewed raw-field mapping remain
separate evidence; this tool checks their identities, not their physical truth.
"""
import argparse
import hashlib
import json
from pathlib import Path

from stage_admission import (BACKLOGS, CAPACITY, DEADLINE_NS, DEVICES, PAYLOAD,
                             TIMINGS, envelope_key, identity, integer, require,
                             sha256_identity, subsets, validate_profile)


MAPPED_FIELDS = (
    "proposal_sample_origin_ns", "decision_received_origin_ns", "fallback_complete_origin_ns",
    "decision_core_ns", "last_decision_sent_core_ns", "core_payload_ready_core_ns",
    "core_start_core_ns", "core_end_core_ns", "core_result_send_core_ns",
    "result_received_origin_ns", "origin_clock_id", "core_clock_id",
    "backlog_by_probe_bytes", "received_prefix_bytes", "payload_sha256", "core_state_before",
)


def digest(path):
    value = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def artifact(entry, directory):
    path = directory / entry["path"]
    actual = digest(path)
    require(actual == entry["sha256"], "calibration artifact hash mismatch")
    return actual


def interval(start, end, label):
    integer(start, label + " start", 0)
    integer(end, label + " end", 0)
    require(end >= start, label + " reversed")
    return end - start


def batch_components(row, condition):
    key = envelope_key(row["backlog_by_probe_bytes"], row["selected_devices"])
    expected = envelope_key(condition["backlog_by_probe_bytes"], condition["stage_capture_devices"])
    require(key == expected, "measured initial state/selection differs from frozen condition")
    require(row["analysis_stratum"] == "first_measured_generation_batch", "calibration batch stratum")
    require(row["basis"] == "physical_capture", "synthetic rows cannot build a physical profile")
    require(row["core_state_before"] == {"executing_jobs": 0, "queued_complete_jobs": 0},
            "core not observed idle before calibration batch")
    for value in row["core_state_before"].values():
        integer(value, "observed core state count", 0)
    integer(row["workers"], "observed workers", 1)
    require(row["workers"] == 1, "single-worker capture required")
    core_clock = identity(row["core_clock_id"], "core clock/boot identity")
    require(set(row["probes"]) == set(DEVICES), "all three probe records required")
    proposal_allowance, fallback_allowance = 0, 0
    for device, probe in row["probes"].items():
        identity(probe["origin_clock_id"], "probe clock/boot identity")
        proposal_allowance = max(proposal_allowance, interval(probe["proposal_sample_origin_ns"],
            probe["decision_received_origin_ns"], "probe-local proposal round trip"))
        if device in row["selected_devices"]:
            require(probe["fallback_complete_origin_ns"] is None, "selected job has unexpected fallback")
        else:
            fallback_allowance = max(fallback_allowance, interval(probe["decision_received_origin_ns"],
                probe["fallback_complete_origin_ns"], "observed H-NONE fallback"))
    decision = integer(row["decision_core_ns"], "core decision", 0)
    dispatch_end = integer(row["last_decision_sent_core_ns"], "core decision dispatch", 0)
    require(dispatch_end >= decision, "decision dispatch precedes decision")
    expected_jobs = {(d, "new") for d in row["selected_devices"]}
    expected_jobs |= {(d, "background") for d in DEVICES if row["backlog_by_probe_bytes"][d]}
    seen, event_ids, core_intervals = set(), set(), []
    upload_end, core_allowance, return_allowance = dispatch_end, 0, 0
    for job in row["jobs"]:
        device = job["device_id"]
        kind = job["origin_kind"]
        pair = (device, kind)
        require(pair in expected_jobs and pair not in seen, "unexpected/duplicate calibration job")
        seen.add(pair)
        event_id = identity(job["event_id"], "calibration event identity")
        require(event_id not in event_ids, "duplicate calibration event identity")
        event_ids.add(event_id)
        remaining = PAYLOAD if kind == "new" else row["backlog_by_probe_bytes"][device]
        require(integer(job["remaining_before_bytes"], "remaining bytes", 1) == remaining,
                "observed remaining tail mismatch")
        require(integer(job["received_prefix_bytes"], "received prefix", 0) == PAYLOAD - remaining,
                "observed received prefix mismatch")
        sha = job["payload_sha256"]
        require(isinstance(sha, str) and len(sha) == 64 and all(c in "0123456789abcdef" for c in sha),
                "actual payload digest required")
        require(job["core_clock_id"] == core_clock
                and job["origin_clock_id"] == row["probes"][device]["origin_clock_id"],
                "job crossed a recorded clock epoch")
        ready = integer(job["core_payload_ready_core_ns"], "core full payload ready", 0)
        start = integer(job["core_start_core_ns"], "core inference start", 0)
        end = integer(job["core_end_core_ns"], "core inference end", 0)
        sent = integer(job["core_result_send_core_ns"], "core result send", 0)
        require(decision <= ready <= start <= end <= sent, "core pipeline ordering")
        upload_end = max(upload_end, ready)
        core_allowance = max(core_allowance, end - start)
        core_intervals.append((start, end))
        # This local suffix covers preparation, upload, waiting, compute and
        # return; it is a conservative return allowance, NOT one-way latency.
        return_allowance = max(return_allowance, interval(
            row["probes"][device]["decision_received_origin_ns"],
            job["result_received_origin_ns"], "probe-local post-decision result suffix"))
    require(seen == expected_jobs, "incomplete result capture; cannot silently drop missing jobs")
    core_intervals.sort()
    require(all(a[1] <= b[0] for a, b in zip(core_intervals, core_intervals[1:])),
            "observed core work overlaps single-worker assumption")
    return {"proposal_transit_ns": proposal_allowance,
            "dispatch_compute_upload_ns": upload_end - decision,
            "fallback_compute_ns": fallback_allowance,
            "core_per_job_ns": core_allowance, "return_ns": return_allowance}


def build(records_path, plan_path, field_map_path, margin_ns):
    integer(margin_ns, "margin", 0)
    plan = json.loads(plan_path.read_bytes())
    require(plan["study"] == "shared_stage" and plan["phase"] == "calibration", "calibration plan required")
    require(plan["execution_qualification"] == "QUALIFIED_FOR_EXECUTION_BY_EXTERNAL_RUNNER",
            "calibration execution prerequisites were not qualified")
    blocks = integer(plan["requested_complete_blocks"], "calibration blocks", 1)
    require(plan["planned_arms"] == 16 * blocks, "complete 16-condition calibration grid required")
    conditions = {c["condition_id"]: c for c in plan["conditions"]}
    require(len(conditions) == len(plan["conditions"]) == 16, "exact calibration condition set required")
    keys = {envelope_key(c["backlog_by_probe_bytes"], c["stage_capture_devices"]) for c in conditions.values()}
    require(keys == {(b, s) for b in BACKLOGS for s in subsets()}, "calibration coverage")
    require(all(c["candidate_probes"] == list(DEVICES) and c["capacity_bytes_per_round"] == CAPACITY
                and c["policy"] == "instrumented_fixed_full_capture" for c in conditions.values()),
            "all probes, capacity and capture policy must remain common")
    mapping = json.loads(field_map_path.read_bytes())
    require(mapping["status"] == "REVIEWED_PHYSICAL_CAPTURE_FIELD_MAP", "reviewed physical field map required")
    require(mapping["campaign_id"] == plan["campaign_id"] and mapping["frozen_margin_ns"] == margin_ns,
            "field map campaign/margin binding")
    runtime_sha = sha256_identity(mapping["runtime_tree_sha256"], "calibration runtime tree identity")
    require(set(mapping["mapped_fields"]) >= set(MAPPED_FIELDS)
            and all(isinstance(mapping["mapped_fields"][f], str) and mapping["mapped_fields"][f].strip()
                    for f in MAPPED_FIELDS), "incomplete source-field mapping")
    source_hashes = {}
    for item in mapping["raw_files"]:
        key = identity(item["source_id"], "raw source identity")
        require(key not in source_hashes, "duplicate raw source identity")
        source_hashes[key] = artifact(item, field_map_path.parent)
    require(bool(source_hashes), "raw capture files required")
    adapter_sha = artifact(mapping["adapter_source"], field_map_path.parent)
    review_sha = artifact(mapping["mapping_review"], field_map_path.parent)
    buckets, seen, attempts, events = {}, set(), set(), set()
    for line in records_path.read_text().splitlines():
        row = json.loads(line)
        require(row["campaign_id"] == plan["campaign_id"], "capture campaign mismatch")
        block = integer(row["block"], "physical block", 1)
        cid = row["condition_id"]
        require(block <= blocks and cid in conditions and (block, cid) not in seen,
                "duplicate/unplanned calibration arm")
        seen.add((block, cid))
        attempt = identity(row["attempt_id"], "attempt identity")
        require(attempt not in attempts, "reused physical attempt identity")
        attempts.add(attempt)
        require(isinstance(row["raw_source_ids"], list) and row["raw_source_ids"]
                and set(row["raw_source_ids"]) <= set(source_hashes), "missing raw capture references")
        require(not events.intersection(j["event_id"] for j in row["jobs"]), "event reused across arms")
        events.update(j["event_id"] for j in row["jobs"])
        values = batch_components(row, conditions[cid])
        key = envelope_key(row["backlog_by_probe_bytes"], row["selected_devices"])
        bucket = buckets.setdefault(key, {name: 0 for name in TIMINGS} | {"observed_batches": 0})
        bucket["observed_batches"] += 1
        for name in TIMINGS:
            bucket[name] = max(bucket[name], values[name])
    require(seen == {(b, c) for b in range(1, blocks + 1) for c in conditions},
            "calibration grid incomplete; missing results require resolution, not selection")
    envelopes = [dict(backlog_by_probe_bytes=dict(zip(DEVICES, backlog)), selected_devices=list(selected), **values)
                 for (backlog, selected), values in sorted(buckets.items())]
    profile = {"schema_version": 2, "phase": "calibration", "campaign": plan["campaign_id"],
               "runtime_tree_sha256": runtime_sha,
               "workers": 1, "basis": "physical_capture", "clock_policy": "within_host_intervals_only",
               "estimator": "per_condition_componentwise_observed_maximum", "margin_ns": margin_ns,
               "controller_sha256": digest(Path(__file__).with_name("stage_admission.py")),
               "scope": {"devices": list(DEVICES), "payload_bytes": PAYLOAD,
                   "capacity_bytes_per_round": CAPACITY, "deadline_ns": DEADLINE_NS,
                   "initial_core_executing_jobs": 0, "initial_core_queued_complete_jobs": 0},
               "envelopes": envelopes,
               "source_identity": {"records_sha256": digest(records_path), "plan_sha256": digest(plan_path),
                   "field_map_sha256": digest(field_map_path), "adapter_sha256": adapter_sha,
                   "mapping_review_sha256": review_sha, "raw_source_sha256": source_hashes},
               "calibration_complete_blocks": blocks,
               "interpretation": "Derived empirical allowances, not deterministic bounds or physical qualification. "
                   "Proposal allowance uses origin-local round trip. Return allowance uses origin-local post-decision "
                   "result suffix. Components deliberately overlap; no cross-host subtraction is used."}
    validate_profile(profile)
    return profile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--records", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--field-map", type=Path, required=True)
    parser.add_argument("--margin-ns", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    require(not args.output.exists(), "output must be new; preserve earlier calibrations")
    profile = build(args.records, args.plan, args.field_map, args.margin_ns)
    with args.output.open("x") as stream:
        json.dump(profile, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"status": "PROFILE_DERIVED_NOT_PHYSICAL_QUALIFICATION", "conditions": 16,
                      "blocks": profile["calibration_complete_blocks"], "sha256": digest(args.output)}))


if __name__ == "__main__":
    main()
