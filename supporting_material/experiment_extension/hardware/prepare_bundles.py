"""Materialize private launch inputs from RC1, patch-qualified runtimes and a prospective plan."""

import argparse
import csv
import hashlib
import json
import shutil
import sys
from pathlib import Path


def prepare(args):
    sources = json.loads((args.rc1 / "inputs/SESSION_SCHEDULE.json").read_bytes())
    seeds = {r["session_id"]: r["seed"] for r in sources}
    with (args.plan / "condition_order.csv").open() as handle:
        order = list(csv.DictReader(handle))
    plan = json.loads((args.plan / "plan.json").read_bytes())
    if len(args.workloads) != plan["requested_complete_blocks"] or any(
        w not in seeds for w in args.workloads
    ):
        raise ValueError("supply one archived workload session per planned block")
    args.output.mkdir()
    layout = dict(
        formal_tools=str(args.tools.resolve()),
        core_python=sys.executable,
        port=args.port,
        blocks={},
    )
    for row in order:
        workload = args.workloads[int(row["block"]) - 1]
        block = layout["blocks"].setdefault(
            row["session_id"],
            dict(workload_session=workload, seed=seeds[workload], bundles={}),
        )
        root = args.output / row["arm_id"]
        runtime = (
            args.corrected
            if row["allocator_variant"] == "integer_remainder_fix"
            else args.original
        )
        root.mkdir()
        shutil.copytree(
            runtime / "netshield",
            root / "netshield",
            ignore=shutil.ignore_patterns("__pycache__", "*.rej", "*.orig"),
        )
        shutil.copytree(
            runtime / "artifacts/portable_models", root / "artifacts/portable_models"
        )
        shutil.copytree(
            args.rc1 / "window_plans" / workload, root / "window_plans" / workload
        )
        shutil.copyfile(args.rc1 / "inputs/actions.json", root / "actions.json")
        cfg = json.loads(
            (args.rc1 / "configs" / f"formal_v1_2_{row['capacity']}.json").read_bytes()
        )
        cfg.update(experiment_id=row["campaign_id"], seed=seeds[workload])
        if row["study"] == "allocator":
            cfg["method"] = "independent_dpp"
        else:
            cfg.update(
                method=row["policy"],
                stage_initial_backlog_bytes=int(row["initial_backlog_bytes"]),
            )
            if row["phase"] == "calibration":
                devices = row["stage_capture_devices"]
                cfg["stage_capture_devices"] = devices.split(",") if devices else []
            if row["policy"] == "causal_shared_stage":
                if not args.profile:
                    raise ValueError(
                        "independent physical calibration profile required"
                    )
                profile = json.loads(args.profile.read_bytes())
                if (
                    profile["basis"] != "physical_capture"
                    or profile["campaign"] == row["campaign_id"]
                ):
                    raise ValueError("profile qualification")
                shutil.copyfile(args.profile, root / "profile.json")
                cfg["stage_profile"] = dict(
                    file="profile.json",
                    sha256=hashlib.sha256(args.profile.read_bytes()).hexdigest(),
                )
        (root / "config.json").write_text(json.dumps(cfg, indent=2) + "\n")
        block["bundles"][row["condition_id"]] = str(root.resolve())
    (args.output / "deployment.json").write_text(json.dumps(layout, indent=2) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("rc1", "original", "corrected", "tools", "plan", "output", "profile"):
        parser.add_argument("--" + name, type=Path, required=name != "profile")
    parser.add_argument("--workloads", nargs="+", required=True)
    parser.add_argument("--port", type=int, default=18940)
    prepare(parser.parse_args())
