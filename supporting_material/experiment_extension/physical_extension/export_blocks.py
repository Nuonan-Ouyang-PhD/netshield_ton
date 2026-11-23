"""Export role-labelled counts and trajectory rows from a retained physical campaign."""
import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


def load(path):
    return json.loads(path.read_bytes())


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def export(plan_dir, campaign, target):
    plan = load(plan_dir / "plan.json")
    registered = load(campaign / "before_first_arm.json")
    if plan["campaign_id"] != campaign.name or registered["plan_sha256"] != sha(plan_dir / "plan.json"):
        raise ValueError("Registry and prospective plan differ")
    with (plan_dir / "condition_order.csv").open() as stream:
        order = list(csv.DictReader(stream))
    scheduled = {r["arm_id"]: r for r in order}
    target.mkdir(parents=True, exist_ok=False)
    attempts = []
    with (target / "trajectory.csv").open("x", newline="") as stream:
        fields = ["attempt", "round", "device", "action", "before", "new_payload", "grant", "unique_service", "after"]
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for start in sorted(campaign.glob("*/started.json")):
            receipt = load(start)
            arm = receipt["row"]["arm_id"]
            if not all(str(v) == scheduled[arm][k] for k, v in receipt["row"].items()):
                raise ValueError("Attempt differs from schedule")
            root = start.parent
            attempt = receipt["attempt"]
            if root.name != attempt:
                raise ValueError("Attempt identity mismatch")
            row = dict(arm=arm, attempt=attempt, block=int(scheduled[arm]["block"]),
                       condition=scheduled[arm]["condition_id"], position=int(scheduled[arm]["position"]),
                       started_sha256=sha(start), completed=False)
            attempts.append(row)
            rebuilt = root / "reconstructed"
            if not (rebuilt / "attempt.jsonl").is_file():
                row["state"] = load(root / "exits.json")["status"] if (root / "exits.json").exists() else "registered_without_exit"
                continue
            a = load(rebuilt / "attempt.jsonl")
            if a["attempt_id"] != attempt or a["campaign_id"] != campaign.name:
                raise ValueError("Reconstruction belongs to another attempt")
            row["state"] = a["attempt_state"]
            if row["state"] != "completed":
                continue
            row["completed"] = True
            row["timing"] = load(rebuilt / "timing_by_stratum.json")
            row["counts"] = load(rebuilt / "summary.json")
            row["artifacts"] = {p.name: sha(p) for p in sorted(rebuilt.iterdir()) if p.is_file()}
            row["raw_artifacts"] = {p.name: sha(p) for p in sorted(root.glob("*.tar"))}
            events = [json.loads(line) for line in (rebuilt / "events.jsonl").read_bytes().splitlines()]
            actions = {(e["device_id"],e["generation_round"]):e["admitted_action"] for e in events}
            measured = [e for e in events if e["origin_cohort"] == "measured"]
            if len(actions) != len(events) or len(measured) != row["counts"]["generated"]:
                raise ValueError("Event count or round identity mismatch")
            event_path = target / (attempt + "_endpoints.csv")
            with event_path.open("x", newline="") as events_file:
                out = csv.writer(events_file, lineterminator="\n")
                out.writerow(["device", "round", "action", "deadline_ns", "release_lateness_ns", "post_latency_ns", "post_followup_ns"])
                for e in measured:
                    created = e["actual_event_creation_origin_ns"]
                    result = e["result_received_origin_ns"]
                    out.writerow([e["device_id"],e["generation_round"],e["admitted_action"],e["deadline_ns"],
                                  created-e["scheduled_release_origin_ns"],result-created if result is not None else "",
                                  e["observed_through_origin_ns"]-created])
            row["endpoint_sha256"] = sha(event_path)
            row["measured_action_mix"] = dict(Counter(e["admitted_action"] for e in measured))
            for line in (rebuilt / "service.jsonl").read_bytes().splitlines():
                s = json.loads(line)
                i, d = s["service_round_index"], s["device_id"]
                writer.writerow(dict(attempt=attempt, round=i, device=d, action=actions.get((d, i), ""),
                                     before=s["queue_before_bytes"], new_payload=s["new_admitted_bytes"],
                                     grant=s["service_granted_bytes"], unique_service=s["actual_unique_application_service_bytes"],
                                     after=s["queue_after_bytes"]))
    report = dict(campaign=campaign.name, phase=plan["phase"], study=plan["study"],
                  plan_sha256=registered["plan_sha256"], freeze_sha256=registered["freeze_sha256"],
                  planned_arms=len(order), attempts=attempts, trajectory_sha256=sha(target / "trajectory.csv"))
    with (target / "arms.json").open("x") as stream:
        json.dump(report, stream, indent=2)
        stream.write("\n")
    if (campaign / "paired_pilot.json").is_file():
        (target / "pairs.json").write_bytes((campaign / "paired_pilot.json").read_bytes())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("plan", "campaign", "output"):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    export(args.plan, args.campaign, args.output)
