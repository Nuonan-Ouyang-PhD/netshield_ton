"""Collect extension arm outcomes by scheduled physical block with explicit missing pairs."""

import argparse
import csv
import json
from itertools import combinations
from pathlib import Path


def summarize(plan_dir, campaign_dir, output):
    plan = json.loads((plan_dir / "plan.json").read_bytes())
    if campaign_dir.name != plan["campaign_id"]:
        raise ValueError("wrong campaign")
    with (plan_dir / "condition_order.csv").open() as f:
        schedule = list(csv.DictReader(f))
    by_arm = {}
    for start in sorted(campaign_dir.glob("*/started.json")):
        meta = json.loads(start.read_bytes())
        arm = meta["row"]["arm_id"]
        by_arm.setdefault(arm, []).append((start.parent, meta))
    if set(by_arm) - {r["arm_id"] for r in schedule}:
        raise ValueError("unscheduled attempts")
    results = []
    contrasts = []
    groups = {}
    for r in schedule:
        attempts = by_arm.get(r["arm_id"], [])
        accepted = []
        for d, meta in attempts:
            source = d / "reconstructed"
            completed = source / "attempt.jsonl"
            if not completed.exists():
                continue
            a = json.loads(completed.read_bytes())
            if (
                a["attempt_id"] != meta["attempt"]
                or a["attempt_state"] != "completed"
                or a["campaign_id"] != plan["campaign_id"]
                or a["condition_id"] != r["condition_id"]
                or a["phase"] != plan["phase"]
                or a["arm_id"] != r["arm_id"]
                or a["session_id"] != r["session_id"]
            ):
                raise ValueError("inconsistent attempt identity")
            if plan["phase"] == "formal" and not a["included_in_formal_analysis"]:
                continue
            accepted.append(source)
        entry = dict(
            block=int(r["block"]),
            arm=r["arm_id"],
            condition=r["condition_id"],
            attempts=[meta["attempt"] for _, meta in attempts],
            complete=False,
        )
        if len(accepted) > 1:
            raise ValueError("more than one included attempt")
        if accepted:
            timeline = json.loads((accepted[0] / "timing_by_stratum.json").read_bytes())
            summary = json.loads((accepted[0] / "summary.json").read_bytes())
            entry.update(
                complete=True,
                strata=timeline,
                unused_serviceable_bytes=summary["unused_serviceable_bytes"],
            )
        results.append(entry)
        groups.setdefault(
            (entry["block"], r["capacity"], r["initial_backlog_bytes"]), []
        ).append(entry)
    for (block, capacity, backlog), group in groups.items():
        for a, b in combinations(sorted(group, key=lambda x: x["condition"]), 2):
            q = dict(
                block=block,
                capacity=capacity,
                backlog=backlog,
                left=a["condition"],
                right=b["condition"],
                complete_pair=a["complete"] and b["complete"],
            )
            if q["complete_pair"]:
                q["difference_bounds"] = {}
                for stratum in a["strata"]:
                    lo, hi = a["strata"][stratum]["post_release"]["coverage_bounds"]
                    other_lo, other_hi = b["strata"][stratum]["post_release"][
                        "coverage_bounds"
                    ]
                    q["difference_bounds"][stratum] = [lo - other_hi, hi - other_lo]
                q["unused_serviceable_difference_bytes"] = (
                    a["unused_serviceable_bytes"] - b["unused_serviceable_bytes"]
                )
            contrasts.append(q)
    with output.open("x") as f:
        json.dump(
            dict(
                campaign=plan["campaign_id"],
                arms=results,
                paired_blocks=contrasts,
                interval_scope="Within-block censoring bounds. Sampling uncertainty requires the formal freeze.",
            ),
            f,
            indent=2,
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ("plan", "campaign", "output"):
        parser.add_argument(key, type=Path)
    args = parser.parse_args()
    summarize(args.plan, args.campaign, args.output)
