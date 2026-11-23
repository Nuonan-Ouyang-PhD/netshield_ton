"""Bind completed first-batch reconstructions to their private primitive files and build the profile."""

import argparse
import csv
import json
import shutil
import sys
import tarfile
from pathlib import Path

from build_profile import build, digest, require

HARDWARE = Path(__file__).resolve().parents[1] / "hardware"
sys.path.insert(0, str(HARDWARE))
from reconstruct_attempt import reconstruct


def assemble(plan_dir, campaign, review, margin, out):
    plan_path = plan_dir / "plan.json"
    plan = json.loads(plan_path.read_bytes())
    require(
        plan["study"] == "shared_stage"
        and plan["phase"] == "calibration"
        and plan["execution_qualification"]
        == "QUALIFIED_FOR_EXECUTION_BY_EXTERNAL_RUNNER",
        "qualified independent calibration required",
    )
    require(campaign.name == plan["campaign_id"], "campaign identity")
    register = json.loads((campaign / "before_first_arm.json").read_bytes())
    require(register["plan_sha256"] == digest(plan_path), "registered plan identity")
    with (plan_dir / "condition_order.csv").open() as f:
        order = {r["arm_id"]: r for r in csv.DictReader(f)}
    require(len(order) == plan["planned_arms"], "incomplete planned order")
    adapter = HARDWARE / "reconstruct_attempt.py"
    approved = json.loads(review.read_bytes())
    require(
        approved["status"] == "REVIEWED_PHYSICAL_CAPTURE_FIELD_MAP"
        and approved["campaign_id"] == campaign.name
        and approved["frozen_margin_ns"] == margin
        and approved["adapter_source"]["sha256"] == digest(adapter),
        "reviewed mapping/adapter binding",
    )
    out.mkdir()
    sources, records, seen = [], [], set()
    for start in sorted(campaign.glob("*/started.json")):
        source = start.parent
        receipt = json.loads(start.read_bytes())
        attempt = receipt["attempt"]
        arm = receipt["row"]["arm_id"]
        require(
            attempt == source.name
            and arm in order
            and receipt["plan_sha256"] == register["plan_sha256"]
            and all(str(v) == order[arm][k] for k, v in receipt["row"].items()),
            "attempt differs from registered schedule",
        )
        # Keep interrupted/unreviewed attempts visible. Never select a faster replacement.
        previous = json.loads((source / "reconstructed" / "attempt.jsonl").read_bytes())
        if previous["attempt_state"] == "infrastructure_excluded":
            require(
                previous["attempt_id"] == attempt
                and previous["exclusion_reason_code"]
                and previous["exclusion_evidence_ids"]
                and not previous["scientific_outcomes_used_for_exclusion_or_retry"],
                "unsubstantiated infrastructure exclusion",
            )
            continue
        require(
            arm not in seen and previous["attempt_state"] == "completed",
            "ambiguous calibration attempts",
        )
        seen.add(arm)
        work = out / attempt
        reconstruct(source, work)
        core_root = source / "core" / attempt
        tree = json.loads((core_root / "manifest.json").read_bytes())["software"][
            "package_tree_sha256"
        ]
        require(
            tree == approved["runtime_tree_sha256"], "calibration uses another runtime"
        )
        capture = json.loads((work / "first_batch.jsonl").read_bytes())
        for name, sha in json.loads((work / "sources.json").read_bytes()).items():
            if name == "core_windows":
                path = core_root / "core_windows.jsonl"
            else:
                role, filename = name.split("/")
                path = work / role / filename
                path.parent.mkdir(exist_ok=True)
                with (
                    tarfile.open(source / (role + ".tar")) as tar,
                    path.open("xb") as data,
                ):
                    member = tar.getmember(f"raw/{attempt}/{filename}")
                    require(member.isfile(), "nonregular primitive source")
                    shutil.copyfileobj(tar.extractfile(member), data)
            require(digest(path) == sha, "primitive source identity changed")
            sources.append(
                dict(
                    source_id=attempt + "/" + name, path=str(path.resolve()), sha256=sha
                )
            )
        records.append(capture)
    require(seen == set(order), "missing planned calibration arms")
    mapping = dict(
        approved,
        raw_files=sources,
        adapter_source=dict(path=str(adapter), sha256=digest(adapter)),
        mapping_review=dict(path=str(review.resolve()), sha256=digest(review)),
    )
    field_map = out / "field_map.json"
    field_map.write_text(json.dumps(mapping, indent=2) + "\n")
    inputs = out / "records.jsonl"
    inputs.write_text("".join(json.dumps(r) + "\n" for r in records))
    profile = build(inputs, plan_path, field_map, margin)
    with (out / "profile.json").open("x") as f:
        json.dump(profile, f, indent=2)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    for k in ("plan", "campaign", "review", "output"):
        p.add_argument("--" + k, type=Path, required=True)
    p.add_argument("--margin-ns", type=int, required=True)
    a = p.parse_args()
    assemble(a.plan, a.campaign, a.review, a.margin_ns, a.output)
