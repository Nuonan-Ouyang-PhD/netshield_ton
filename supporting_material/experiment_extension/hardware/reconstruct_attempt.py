"""Reconstruct one extension attempt from its Core JSONL and three probe archives.

JSONL source references are SHA-256:line (1-based). The tool retains the input
primitives in place. A discrepancy aborts the complete-case export; raw attempt
files remain available for failure review. Output directories are exclusive.
"""

import argparse
import hashlib
import json
import tarfile
from collections import defaultdict
from pathlib import Path

ROLES = ("P1", "P2", "P3")


def require(ok, message):
    if not ok:
        raise ValueError(message)


def read_lines(data, name, sources):
    sha = hashlib.sha256(data).hexdigest()
    sources[name] = sha
    rows = []
    for i, line in enumerate(data.splitlines(), 1):
        r = json.loads(line)
        r["_src"] = f"{sha}:{i}"
        rows.append(r)
    return rows


def indexed(rows, keys):
    result = {}
    for r in rows:
        key = tuple(r[k] for k in keys)
        require(key not in result, f"duplicate {keys} {key}")
        result[key] = r
    return result


def timing(created, received, horizon, deadline):
    require(created <= horizon and deadline > 0, "origin clock order")
    if received is None:
        return "miss" if horizon - created >= deadline else "censored"
    require(created <= received <= horizon, "receipt outside origin observation")
    return "timely" if received - created <= deadline else "late"


def add_range(covered, start, end):
    """Union of half-open byte ranges; return the newly observed length."""
    require(
        type(start) is int and type(end) is int and 0 <= start < end, "chunk offsets"
    )
    previous = sum(b - a for a, b in covered)
    merged = []
    for a, b in sorted([*covered, (start, end)]):
        if merged and a <= merged[-1][1]:
            merged[-1] = merged[-1][0], max(b, merged[-1][1])
        else:
            merged.append((a, b))
    covered[:] = merged
    return sum(b - a for a, b in covered) - previous


def reconstruct(root, out):
    out.mkdir()
    receipt = json.loads((root / "started.json").read_bytes())
    row, attempt = receipt["row"], receipt["attempt"]
    ids = {
        k: row[k]
        for k in (
            "study",
            "phase",
            "campaign_id",
            "session_id",
            "arm_id",
            "condition_id",
        )
    }
    ids.update(schema_version=1, attempt_id=attempt)
    sources = {}
    core_root = root / "core" / attempt
    core = read_lines(
        (core_root / "core_windows.jsonl").read_bytes(), "core_windows", sources
    )
    core_windows = indexed(
        (r for r in core if r["record_type"] == "core_window"),
        ("device_id", "window_index"),
    )
    dispatch = indexed(
        (r for r in core if r["record_type"] == "decision_dispatched"),
        ("device_id", "window_index"),
    )
    stage = indexed(
        (r for r in core if r["record_type"] == "stage_decision"), ("window_index",)
    )
    initial = [r for r in core if r["record_type"] == "stage_initial_state"]
    completed = {}
    sends = {}
    for r in core:
        if r["record_type"] == "results_dispatched":
            for key in r["keys"]:
                sends.setdefault(key, r)
        if r["record_type"] == "core_window":
            for job in r["completed_events"]:
                if job.get("core_inference_complete") and not job.get(
                    "replayed_cached_result"
                ):
                    key = job["event_key"]
                    require(key not in completed, "duplicate first Core completion")
                    completed[key] = (job, r["_src"])
    events, service, chunks = [], [], []
    admissions = []
    info, total_grant, total_service = {}, defaultdict(int), defaultdict(int)
    totals = defaultdict(int)
    for role in ROLES:
        with tarfile.open(root / (role + ".tar")) as archive:

            def load(name):
                member = archive.getmember(f"raw/{attempt}/{name}")
                require(member.isfile(), "nonregular raw input")
                return read_lines(
                    archive.extractfile(member).read(), role + "/" + name, sources
                )

            # RC1 writes pretty-printed JSON for the status, JSONL for the primitives.
            status_data = archive.extractfile(f"raw/{attempt}/run_status.json").read()
            status = json.loads(status_data)
            status_sha = hashlib.sha256(status_data).hexdigest()
            sources[role + "/run_status.json"] = status_sha
            require(
                status["status"] == "complete" and status["valid"] is True,
                "incomplete observation",
            )
            windows = load("probe_windows.jsonl")
            ledger = [v for v in load("event_ledger.jsonl") if "event_key" in v]
        frames = indexed(
            (r for r in windows if r["record_type"] == "transport_frame"),
            ("window_index",),
        )
        samples = indexed(
            (r for r in windows if r["record_type"] == "probe_stage"), ("window_index",)
        )
        decisions = indexed(
            (
                r
                for r in windows
                if r["record_type"] in ("probe_window", "probe_drain_window")
            ),
            ("window_index",),
        )
        require(
            set(frames) == set(decisions) == {(i,) for i in range(len(frames))}
            and 95 <= len(frames) <= 295,
            "missing service rounds",
        )
        by_generation = indexed(ledger, ("origin_window_index",))
        require(
            set(by_generation) == set(samples) == {(i,) for i in range(95)},
            "missing generated occurrence",
        )
        require(
            all(
                e["run_id"] == attempt
                and e["device_id"] == role
                and e["campaign_id"] == row["campaign_id"]
                for e in ledger
            ),
            "wrong raw identity",
        )
        known = {e["event_key"]: e for e in ledger}
        require(len(known) == 95, "event keys not unique")
        ranges = defaultdict(list)
        submitted = defaultdict(list)
        before = 0
        epoch = status["origin_clock_id"]
        for i in range(len(frames)):
            f, p, c = frames[i,], decisions[i,], core_windows[role, i]
            require(
                f["origin_clock_id"] == epoch
                and f["device_id"] == role
                and c["run_id"] == attempt,
                "frame identity",
            )
            new = p["payload_generated_bytes"] if i < 95 else 0
            demand = before + new
            require(c["demand_bytes"] == demand, "queue continuity at admission")
            grant, cap = c["grant_bytes"], c["shared_cap_bytes"]
            require(
                0 <= grant <= demand and cap == row["capacity_bytes_per_round"],
                "service decision",
            )
            used, wire_payload, chunk_ids = 0, 0, []
            for j, seg in enumerate(f["sent_segments"]):
                key, start, n = seg["event_key"], seg["offset"], seg["length"]
                require(
                    key in known and start + n <= known[key]["payload_bytes"],
                    "unknown/out-of-range segment",
                )
                submitted[key].append(f)
                end = start + n
                boundaries = sorted(
                    {start, end}
                    | {
                        point
                        for interval in ranges[key]
                        for point in interval
                        if start < point < end
                    }
                )
                for part, (left, right) in enumerate(zip(boundaries, boundaries[1:])):
                    unique = add_range(ranges[key], left, right)
                    cid = f"{attempt}/{role}/{i}/{j}/{part}"
                    chunks.append(
                        dict(
                            ids,
                            record_type="transport_chunk",
                            chunk_id=cid,
                            event_id=key,
                            device_id=role,
                            service_round_index=i,
                            transport_host_id=role,
                            transport_clock_id=epoch,
                            transport_observed_ns=f["sent_ns"],
                            payload_offset_start=left,
                            payload_offset_end=right,
                            observed_payload_bytes=right - left,
                            accounting_point="queue_to_transport_unique_service"
                            if unique
                            else "duplicate_wire_send",
                            charged_unique_service=bool(unique),
                            application_wire_bytes=None,
                            raw_source_record_id=f["_src"],
                        )
                    )
                    used += unique
                    chunk_ids.append(cid)
                wire_payload += n
            require(
                wire_payload == p["application_payload_bytes"],
                "actual payload vs frame",
            )
            ack = f["receipt_ack"]
            require(
                sum(v["unique_bytes_added"] for v in ack["segments"]) == used,
                "Core unique receipts disagree",
            )
            totals["service_above_grant_device_rounds"] += int(used > grant)
            after = p["queue_bytes"]
            require(after == demand - used, "unexplained queue change")
            service.append(
                dict(
                    ids,
                    record_type="service",
                    service_round_index=i,
                    device_id=role,
                    service_period_kind="warmup"
                    if i < 5
                    else "measured"
                    if i < 95
                    else "drain",
                    service_host_id=role,
                    service_clock_id=epoch,
                    service_start_ns=f["send_ns"],
                    service_end_ns=f["sent_ns"],
                    shared_cap_bytes=cap,
                    queue_before_bytes=before,
                    new_admitted_bytes=new,
                    cancelled_from_queue_bytes=0,
                    service_granted_bytes=grant,
                    actual_unique_application_service_bytes=used,
                    queue_after_bytes=after,
                    initial_state_fixture_id=None,
                    transport_chunk_ids=chunk_ids,
                    raw_source_record_ids=[f["_src"], c["_src"], p["_src"]],
                )
            )
            before = after
            total_grant[i] += grant
            total_service[i] += used
        require(before == status["queued_remaining_bytes"], "final queue")
        info[role] = (samples, known)
        for e in ledger:
            i, key = e["origin_window_index"], e["event_key"]
            p = samples[i,]
            h = status["observation_end_monotonic_ns"]
            created = e["created_probe_monotonic_ns"]
            result = e["result_received_monotonic_ns"] if e["requires_core"] else None
            core_job, core_ref = completed.get(key, ({}, None))
            sent = sends.get(key, {})
            if result is not None:
                require(
                    key in sends
                    and core_job.get("contract_hash_ok")
                    and core_job.get("application_payload_sha256")
                    == e["payload_sha256"],
                    "unmatched returned Core result",
                )
            require(
                epoch == p["origin_clock_id"] and p["event_key"] == key,
                "probe epoch or occurrence mismatch",
            )
            selected = e["admitted_action_id"] == "H_FULL"
            anchors = timing(created, result, h, e["deadline_ns"])
            if 5 <= i < 95:
                totals["generated"] += 1
                totals["selected"] += int(selected)
                totals["timely_full"] += int(selected and anchors == "timely")
                totals["censored_full"] += int(selected and anchors == "censored")
                totals["returned_full"] += int(selected and result is not None)
                nominal = e["scheduled_release_monotonic_ns"]
                totals["nominal_timely_full"] += int(
                    selected
                    and result is not None
                    and result - nominal <= e["deadline_ns"]
                )
                totals["nominal_censored_full"] += int(
                    selected and result is None and h < nominal + e["deadline_ns"]
                )
            cohort = "warmup" if i < 5 else "measured"
            strata = ["warmup"] if i < 5 else ["all_measured_generation_batches"]
            if i == 5:
                strata.append("first_measured_generation_batch")
            fragments = submitted[key]
            if e["cancelled_discarded_bytes"] == 0:
                require(
                    e["payload_bytes"]
                    == e["unique_payload_received_bytes"]
                    + e["queued_remaining_bytes"]
                    + e["inflight_payload_bytes"],
                    "event byte disposition mismatch",
                )
            result_row = dict(
                ids,
                record_type="event",
                device_id=role,
                event_id=key,
                origin_cohort=cohort,
                generation_round=i,
                analysis_strata=strata,
                source_sample_id=e["source_sample_id"],
                requested_action="H_FULL"
                if row["study"] == "shared_stage"
                else e["admitted_action_id"],
                admitted_action=e["admitted_action_id"],
                requires_core=e["requires_core"],
                selected_for_full=selected,
                payload_bytes=e["payload_bytes"],
                payload_sha256=e["payload_sha256"],
                origin_host_id=role,
                origin_clock_id=epoch,
                core_host_id="Core",
                core_clock_id=dispatch[role, i]["core_clock_id"],
                scheduled_release_origin_ns=e["scheduled_release_monotonic_ns"],
                actual_event_creation_origin_ns=created,
                detector_start_origin_ns=p["local_start_ns"],
                detector_end_origin_ns=p["local_end_ns"],
                preprocess_start_origin_ns=p["encode_start_ns"],
                preprocess_end_origin_ns=p["encode_end_ns"],
                network_enqueue_origin_ns=None,
                payload_submit_start_origin_ns=fragments[0]["send_ns"]
                if fragments
                else None,
                payload_submit_end_origin_ns=fragments[-1]["sent_ns"]
                if fragments
                else None,
                evidence_ack_received_origin_ns=e["transfer_complete_monotonic_ns"],
                core_payload_ready_core_ns=core_job.get("payload_ready_core_ns"),
                core_enqueue_core_ns=None,
                core_start_core_ns=core_job.get("core_inference_start_monotonic_ns"),
                core_end_core_ns=core_job.get("core_inference_end_monotonic_ns"),
                core_result_send_core_ns=sent.get("core_ns"),
                result_received_origin_ns=result,
                deadline_ns=e["deadline_ns"],
                observed_through_origin_ns=h,
                deadline_matured=h - created >= e["deadline_ns"],
                terminal_state=e["state"]
                if e["state"].startswith("terminal_")
                else "pending",
                prediction=(
                    str(e["core_prediction"])
                    if e["core_prediction"] is not None
                    else None
                ),
                ground_truth=str(e["label"]) if e["label"] is not None else None,
                queued_remaining_bytes=e["queued_remaining_bytes"],
                inflight_remaining_bytes=e["inflight_payload_bytes"],
                discarded_payload_bytes=e["cancelled_discarded_bytes"],
                raw_source_record_ids=[
                    r
                    for r in [
                        e["_src"],
                        p["_src"],
                        core_ref,
                        sent.get("_src"),
                        status_sha,
                    ]
                    if r
                ],
            )
            result_row["missing_timestamp_reasons"] = {
                k: "no corresponding event-specific boundary in raw record"
                for k, v in result_row.items()
                if k.endswith("_ns") and v is None
            }
            events.append(result_row)
    require(
        len(events) == 285
        and totals["generated"] == 270
        and len({r["event_id"] for r in events}) == 285,
        "cohort",
    )
    require(
        all(
            sum(r["service_round_index"] == i for r in service) == 3
            for i in total_grant
        ),
        "incomplete round",
    )
    # Keep actual violations in the output as scientific outcomes.
    totals["cap_violation_rounds"] = sum(
        g > row["capacity_bytes_per_round"] for g in total_grant.values()
    )
    totals["actual_service_cap_violation_rounds"] = sum(
        v > row["capacity_bytes_per_round"] for v in total_service.values()
    )
    totals["unused_serviceable_bytes"] = sum(
        min(
            row["capacity_bytes_per_round"],
            sum(
                r["queue_before_bytes"] + r["new_admitted_bytes"]
                for r in service
                if r["service_round_index"] == i
            ),
        )
        - total_service[i]
        for i in total_service
    )
    totals["aggregate_service_bytes"] = sum(total_service.values())
    for (i,), decision in sorted(stage.items()):
        keys = {d: decision["snapshot"][d]["ready"]["key"] for d in ROLES}
        chosen = [keys[d] for d in ROLES if info[d][0][i,]["action_id"] == "H_FULL"]
        rejected = {}
        margins = {}
        for t in decision["decisions"]:
            key = keys[t["device"]]
            if key not in chosen:
                rejected[key] = t.get("reason") or (
                    "preparation"
                    if t.get("preparation")
                    else "forced_subset"
                    if row["phase"] == "calibration"
                    else "isolated_unsafe"
                    if t.get("isolated_safe") is False
                    else "byte_budget"
                )
            margins[key] = t.get("min_slack_after_service_ns")
        admissions.append(
            dict(
                ids,
                record_type="admission",
                decision_id=f"{attempt}/{i}",
                decision_host_id="Core",
                decision_clock_id=decision["core_clock_id"],
                decision_time_ns=decision["core_decision_ns"],
                candidate_event_ids=list(keys.values()),
                selected_event_ids=chosen,
                queue_bytes_by_probe={
                    d: core_windows[d, i]["queue_bytes_at_decision"] for d in ROLES
                },
                core_executing_jobs=decision["executing_jobs"],
                core_queued_complete_jobs=decision["queued_complete_jobs"],
                core_job_state_digest=None,
                remaining_application_budget_bytes=decision["cap"],
                fallback_by_event={key: "H_NONE" for key in rejected},
                rejection_reason_by_event=rejected,
                calibration_sha256=decision["calibration_sha256"],
                controller_source_sha256=decision["controller_source_sha256"],
                estimate_inputs_raw_record_ids=[decision["_src"]],
                predicted_result_slack_ns_by_event=margins,
            )
        )
    by_stratum = {}
    for label, first_only in (
        ("first_measured_generation_batch", True),
        ("all_measured_generation_batches", False),
    ):
        group = [
            e
            for e in events
            if e["origin_cohort"] == "measured"
            and (not first_only or e["generation_round"] == 5)
        ]
        full = [e for e in group if e["selected_for_full"]]
        strata = dict(generated=len(group), selected=len(full))
        for anchor, key in (
            ("post_release", "actual_event_creation_origin_ns"),
            ("nominal", "scheduled_release_origin_ns"),
        ):
            timely = sum(
                e["result_received_origin_ns"] is not None
                and e["result_received_origin_ns"] - e[key] <= e["deadline_ns"]
                for e in full
            )
            censored = sum(
                e["result_received_origin_ns"] is None
                and e["observed_through_origin_ns"] < e[key] + e["deadline_ns"]
                for e in full
            )
            strata[anchor] = dict(
                timely=timely,
                censored=censored,
                coverage_bounds=[timely / len(group), (timely + censored) / len(group)],
            )
        by_stratum[label] = strata
    (out / "timing_by_stratum.json").write_text(json.dumps(by_stratum, indent=2))
    for name, records in [
        ("admission", admissions),
        ("events", events),
        ("service", service),
        ("chunks", chunks),
    ]:
        (out / (name + ".jsonl")).write_text(
            "".join(json.dumps(r) + "\n" for r in records)
        )
    if row["study"] == "shared_stage" and row["phase"] == "calibration":
        deployment = json.loads((root / "deployment_verified.json").read_bytes())
        require(
            set(deployment["roles"]) == set(ROLES)
            and row["campaign_id"].startswith("TON_EXT_STAGE_")
            and "FIXTURE" not in row["campaign_id"]
            and "LOOPBACK" not in row["campaign_id"],
            "physical calibration deployment is unverified",
        )
        preflight = json.loads(
            (root / "preflight" / "PREFLIGHT_RESULT.json").read_bytes()
        )
        require(
            preflight["status"] == "PASS"
            and all(all(preflight["probes"][r].values()) for r in ROLES),
            "physical qualification missing",
        )
        require(
            len(initial) == 1 and initial[0]["window_index"] == 5,
            "initial barrier absent or duplicated",
        )
        batch = stage[5,]
        state = initial[0]
        probes, jobs, backlogs, selected = {}, [], {}, []
        by_key = {e["event_id"]: e for e in events}
        for role in ROLES:
            p = info[role][0][5,]
            ready = batch["snapshot"][role]["ready"]
            require(
                p["event_key"] == ready["key"]
                and p["origin_clock_id"] == ready["origin_clock_id"],
                "phase identity",
            )
            full = p["action_id"] == "H_FULL"
            if full:
                selected.append(role)
            probes[role] = dict(
                origin_clock_id=p["origin_clock_id"],
                proposal_sample_origin_ns=p["sample_ns"],
                decision_received_origin_ns=p["decision_received_ns"],
                fallback_complete_origin_ns=None if full else p["local_end_ns"],
            )
            backlogs[role] = sum(j["remaining"] for j in ready["fifo"])
            inputs = [
                (j["key"], "background", j["remaining"], j["payload_sha256"])
                for j in ready["fifo"]
            ]
            if full:
                inputs.append(
                    (
                        p["event_key"],
                        "new",
                        131072,
                        by_key[p["event_key"]]["payload_sha256"],
                    )
                )
            for key, kind, remaining, sha in inputs:
                event = by_key[key]
                require(
                    event["device_id"] == role
                    and event["payload_sha256"] == sha
                    and event["result_received_origin_ns"] is not None,
                    "incomplete first-batch job",
                )
                jobs.append(
                    dict(
                        event_id=key,
                        device_id=role,
                        origin_kind=kind,
                        remaining_before_bytes=remaining,
                        received_prefix_bytes=state["partial_bytes"].get(key, 0),
                        payload_sha256=sha,
                        **{
                            k: event[k]
                            for k in (
                                "core_clock_id",
                                "origin_clock_id",
                                "core_payload_ready_core_ns",
                                "core_start_core_ns",
                                "core_end_core_ns",
                                "core_result_send_core_ns",
                                "result_received_origin_ns",
                            )
                        },
                    )
                )
        capture = dict(
            campaign_id=row["campaign_id"],
            block=row["block"],
            condition_id=row["condition_id"],
            attempt_id=attempt,
            analysis_stratum="first_measured_generation_batch",
            basis="physical_capture",
            workers=1,
            core_clock_id=state["core_clock_id"],
            core_state_before={
                k: state[k] for k in ("executing_jobs", "queued_complete_jobs")
            },
            decision_core_ns=batch["core_decision_ns"],
            last_decision_sent_core_ns=max(dispatch[d, 5]["core_ns"] for d in ROLES),
            backlog_by_probe_bytes=backlogs,
            selected_devices=selected,
            raw_source_ids=[attempt + "/" + name for name in sources],
            probes=probes,
            jobs=jobs,
        )
        (out / "first_batch.jsonl").write_text(json.dumps(capture) + "\n")
    (out / "sources.json").write_text(json.dumps(sources, indent=2))
    (out / "summary.json").write_text(json.dumps(totals, indent=2))
    if (root / "exits.json").is_file():
        exits = json.loads((root / "exits.json").read_bytes())
        require(
            exits["status"] == "processes_completed_pending_raw_audit"
            and all(v == 0 for v in exits["returncodes"].values()),
            "attempt process completion is not established",
        )
        raw_map_hash = hashlib.sha256((out / "sources.json").read_bytes()).hexdigest()
        attempt_row = dict(
            ids,
            record_type="attempt",
            attempt_state="completed",
            started_utc=receipt["started_utc"],
            ended_utc=exits["ended_utc"],
            retry_of_attempt_id=None,
            exclusion_reason_code=None,
            exclusion_evidence_ids=[],
            included_in_formal_analysis=row["phase"] == "formal",
            runtime_manifest_sha256=receipt["runtime_manifest_sha256"],
            plan_sha256=receipt["plan_sha256"],
            formal_freeze_sha256=receipt["formal_freeze_sha256"],
            raw_archive_manifest_sha256=raw_map_hash,
            scientific_outcomes_used_for_exclusion_or_retry=False,
        )
        (out / "attempt.jsonl").write_text(json.dumps(attempt_row) + "\n")
    return totals


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("attempt_directory", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    print(json.dumps(reconstruct(args.attempt_directory, args.output)))
