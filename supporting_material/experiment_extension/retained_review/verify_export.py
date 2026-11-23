"""Verify the published snapshot's arithmetic, bounds and source identities.

Distinct-vector counts and bucket membership originate in the private scan.
Public group totals permit consistency/bound checks, not reconstruction of
those vectors, row-level membership, model execution or original predictions.
"""
import hashlib
import json
from pathlib import Path


BASE = Path(__file__).resolve().parent
LEVELS = ("alert", "summary", "full")
OUTCOMES = ("TP", "TN", "FP", "FN")
BUCKETS = ("train_only", "validation_only", "both", "neither")
EXPECTED_POOLED = {"TP": 768, "TN": 128, "FP": 0, "FN": 0}


def check(ok, msg):
    if not ok:
        raise ValueError(msg)


def count(value, field):
    check(type(value) is int and value >= 0,
          f"{field} must be a nonnegative integer, excluding bool/float")
    return value


def verify_diagnostic_summary(d):
    """Check the retained seven-group result without access to private rows."""
    files = d["files"]
    check(isinstance(files, list) and len(files) == 7, "exactly seven group rows required")
    names = [f["group"] for f in files]
    check(all(isinstance(name, str) and name for name in names), "invalid group name")
    check(len(set(names)) == 7, "group names must be unique")
    pooled = {level: dict.fromkeys(OUTCOMES, 0) for level in LEVELS}
    total = 0
    for group in files:
        generated = count(group["generated"], "generated")
        check(generated == 128, "file size")
        total += generated
        for level in LEVELS:
            outcomes = group[level]
            check(isinstance(outcomes, dict) and set(outcomes) <= set(OUTCOMES),
                  f"unknown confusion key for {level}")
            for key, value in outcomes.items():
                pooled[level][key] += count(value, f"{level}.{key}")
            check(sum(outcomes.values()) == generated, "outcome census")
        for rule in ("exact", "rounded"):
            buckets = group[rule]
            check(isinstance(buckets, dict) and
                  set(buckets) == {*BUCKETS, "unique_within_file"}, "bucket schema")
            for key, value in buckets.items():
                check(count(value, f"{rule}.{key}") <= generated, "bucket count exceeds group size")
            check(sum(buckets[key] for key in BUCKETS) == generated, "bucket census")
            # A distinct vector has one fixed training/validation membership.
            check(sum(buckets[key] > 0 for key in BUCKETS) <=
                  buckets["unique_within_file"] <= generated, "within-file unique bounds")
        exact, rounded = group["exact"], group["rounded"]
        check(rounded["unique_within_file"] <= exact["unique_within_file"],
              "rounding cannot increase within-file distinct vectors")
        # These are necessary aggregate conditions for exact matches to be
        # included in rounded matches, not a public per-row membership proof.
        check(rounded["neither"] <= exact["neither"], "rounded must include exact union matches")
        check(rounded["both"] >= exact["both"], "rounded must include exact matches to both splits")
        for key in ("train_only", "validation_only"):
            check(rounded[key] + rounded["both"] >= exact[key] + exact["both"],
                  f"rounded must include exact {key} inclusive matches")
    check(total == 896, "total generated denominator must be 896")
    for level in LEVELS:
        check(pooled[level] == EXPECTED_POOLED, f"{level} differs from the retained pooled result")
    for rule, expected in (("exact", 366), ("rounded", 544)):
        check(sum(f["generated"] - f[rule]["neither"] for f in files) == expected,
              f"{rule} aggregate matches")
    unique = d["unique_vectors_in_subset"]
    check(isinstance(unique, list) and len(unique) == 2, "two exported distinct-vector counts required")
    for index, rule in enumerate(("exact", "rounded")):
        reported = count(unique[index], f"global {rule} unique")
        per_group = [f[rule]["unique_within_file"] for f in files]
        check(max(per_group) <= reported <= min(total, sum(per_group)),
              f"global {rule} unique bounds")
    check(unique[1] <= unique[0], "rounding cannot increase global distinct vectors")
    return {"groups": len(files), "generated": total, "pooled": pooled,
            "reported_distinct_vectors": unique,
            "distinct_vector_verification": "bounds_only_private_feature_scan_not_repeated"}


def verify_export(base=BASE):
    base = Path(base)

    def load(name):
        return json.loads((base / name).read_bytes())

    q = load("qualification_summary.json")
    check(q["expected_index_is_repository_default"] is True and
          q["status"] == "PASS_RECORDED_FIELDS_ONLY" and q["errors"] == [],
          "qualification result")
    for key, file in (
        ("checker_sha256", base.parent / "qualify_private_records.py"),
        ("legacy_checker_sha256", base.parent / "private_record_qualification/legacy/qualify_private_records_dc5269c.py"),
        ("expected_index_sha256", base.parents[1] / "formal_campaign_audit/results/ATTEMPT_INDEX.json"),
    ):
        check(hashlib.sha256(file.read_bytes()).hexdigest() == q[key], key)
    c = q["counts"]
    for key, value in c.items():
        count(value, f"qualification.{key}")
    check(c["generated"] == 216 * 3 * 90 and c["verified_rounds"] == 216 * 295 and
          c["runtime_manifest_matches"] == 216 * 4 and
          c["returned_core"] - c["timely_core"] == 9596, "counts")
    d = load("diagnostic_review.json")
    for name in ("CONTENT_PROTOCOL.md", "content_diagnostic.py"):
        check(hashlib.sha256((base.parent / name).read_bytes()).hexdigest() ==
              d["sha256"][name], name)
    return verify_diagnostic_summary(d)


if __name__ == "__main__":
    verify_export()
    print("PASS: published source identities, cohort arithmetic and seven group summaries; "
          "distinct-vector values checked for bounds, not recomputed from private features")
