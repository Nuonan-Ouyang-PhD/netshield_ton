#!/usr/bin/env python3
"""Check recorded source counts or prepare a declared parent-capture split.

This binds supplied acquisition-evidence bytes and checks a mapping; it cannot
discover parent captures from filenames or establish statistical independence.
It never changes the archived corpus, fits a model, or generates observations.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
EXTENSION = HERE.parent
SPEC = importlib.util.spec_from_file_location(
    "netshield_evidence_contract", EXTENSION / "evidence_value/score_evidence_value.py")
CONTRACT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CONTRACT)
require = CONTRACT.require


def read_trace(path):
    rows = CONTRACT.read_json(path)
    require(isinstance(rows, list) and rows, "source trace must be a nonempty list")
    original, labelled = set(), set()
    for row in rows:
        CONTRACT.exact_keys(row, {"split", "matched", "original_csv_sha256",
                                  "labelled_csv_sha256"}, "source trace row")
        require(row["split"] in CONTRACT.SPLITS, "unknown archived split")
        require(CONTRACT.natural(row["matched"], "matched source rows") > 0,
                "a traced source must contain matched rows")
        for key, seen in (("original_csv_sha256", original),
                          ("labelled_csv_sha256", labelled)):
            value = CONTRACT.content_hash(row[key], key)
            require(value not in seen, f"duplicate source identity: {key}")
            seen.add(value)
    return rows


def verify_public(trace_path=EXTENSION / "SOURCE_ROW_TRACE.json"):
    """Recompute exported arithmetic, not the private feature-row comparison."""
    rows = read_trace(Path(trace_path))
    split_rows, split_files = Counter(), Counter()
    for row in rows:
        split_rows[row["split"]] += row["matched"]
        split_files[row["split"]] += 1
    prior = CONTRACT.read_json(EXTENSION / "formal_record_reconciliation/results/SPLIT_COUNTS.json")
    rounded = CONTRACT.read_json(EXTENSION / "ROUNDED_OVERLAP.json")
    expected = {split: item["rows"] for split, item in prior["splits"].items()}
    require(dict(split_rows) == expected, "trace totals differ from retained split counts")
    require(dict(split_rows) == {split: item["rows"] for split, item in rounded.items()},
            "trace totals differ from rounded-overlap denominator")
    require(dict(split_files) == {"train": 18, "validation": 6, "test": 7},
            "retained source-file cohort differs")
    require(sum(split_rows.values()) == 5141673 and len(rows) == 31,
            "retained source-row cohort differs")
    return {
        "status": "PUBLIC_SOURCE_TRACE_COUNTS_CONSISTENT",
        "source_files": len(rows), "split_source_files": dict(split_files),
        "split_rows": dict(split_rows), "total_rows": sum(split_rows.values()),
        "source_trace_sha256": CONTRACT.sha256(Path(trace_path)),
        "private_feature_rows_rechecked": False,
        "parent_capture_mapping_qualified": False,
        "scope": "Exported counts and hash formats/uniqueness; original/labelled CSV bytes and private frozen rows not opened.",
    }


def csv_bytes(fields, rows):
    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue().encode("utf-8")


def prepare(mapping_path, splits_path, output, trace_path=EXTENSION / "SOURCE_ROW_TRACE.json",
            allow_fixture=False):
    mapping_path, splits_path, output, trace_path = map(
        Path, (mapping_path, splits_path, output, trace_path))
    require(not output.exists(), "output already exists; choose a new directory")
    traces = read_trace(trace_path)
    expected = {row["original_csv_sha256"]: row for row in traces}
    mapping = CONTRACT.read_json(mapping_path)
    CONTRACT.exact_keys(mapping, {"schema_version", "data_origin", "group_definition",
                                  "evidence", "sources"}, "capture mapping")
    require(mapping["schema_version"] == "netshield.source_capture_mapping.v1",
            "unsupported capture mapping schema")
    require(mapping["data_origin"] in ("actual_provenance", "SYNTHETIC_FIXTURE"),
            "invalid provenance origin")
    require(mapping["data_origin"] != "SYNTHETIC_FIXTURE" or allow_fixture,
            "synthetic mapping refused without --allow-synthetic-fixture")
    CONTRACT.nonempty(mapping["group_definition"], "group definition")
    require(isinstance(mapping["evidence"], list) and mapping["evidence"],
            "actual acquisition-evidence artifacts are required")
    evidence = {}
    for spec in mapping["evidence"]:
        record, _ = CONTRACT.verify_artifact(spec, mapping_path.parent, "capture provenance")
        require(record["id"] not in evidence, "duplicate acquisition-evidence ID")
        evidence[record["id"]] = record
    require(isinstance(mapping["sources"], list) and mapping["sources"],
            "source-to-parent mapping required")
    sources, used_evidence = {}, set()
    for source in mapping["sources"]:
        CONTRACT.exact_keys(source, {"original_csv_sha256", "parent_capture_id", "evidence_ids"},
                            "source mapping")
        key = CONTRACT.content_hash(source["original_csv_sha256"], "mapped source SHA-256")
        require(key in expected and key not in sources, "unknown or duplicate mapped source")
        parent = CONTRACT.nonempty(source["parent_capture_id"], "parent capture ID")
        refs = source["evidence_ids"]
        require(isinstance(refs, list) and refs and
                all(isinstance(ref, str) and ref in evidence for ref in refs),
                "each source needs valid acquisition-evidence references")
        require(len(set(refs)) == len(refs), "duplicate evidence reference")
        used_evidence.update(refs)
        sources[key] = parent
    require(set(sources) == set(expected), "mapping must cover every traced source exactly once")
    require(used_evidence == set(evidence), "unused acquisition-evidence artifact")
    splits = {}
    for row in CONTRACT.read_csv(splits_path, ("parent_capture_id", "split")):
        parent = CONTRACT.nonempty(row["parent_capture_id"], "split parent capture ID")
        require(parent not in splits, "a parent capture may have only one split assignment")
        require(row["split"] in CONTRACT.SPLITS, "unknown assigned split")
        splits[parent] = row["split"]
    require(set(splits) == set(sources.values()), "split inventory and mapped parents differ")
    require(set(splits.values()) == set(CONTRACT.SPLITS),
            "train, validation and test must all contain declared parent groups")
    groups = [{"group_id": parent, "split": splits[parent]} for parent in sorted(splits)]
    source_rows = [{"original_csv_sha256": key, "parent_capture_id": parent,
                    "split": splits[parent]} for key, parent in sorted(sources.items())]
    group_data = csv_bytes(CONTRACT.GROUP_FIELDS, groups)
    source_data = csv_bytes(("original_csv_sha256", "parent_capture_id", "split"), source_rows)
    totals = Counter()
    for key, parent in sources.items():
        totals[splits[parent]] += expected[key]["matched"]
    report = {
        "schema_version": 1,
        "status": "DECLARED_PARENT_SPLIT_CONSISTENT",
        "data_origin": mapping["data_origin"],
        "group_definition": mapping["group_definition"],
        "source_files": len(sources), "declared_parent_captures": len(splits),
        "declared_parent_groups_by_split": dict(Counter(splits.values())),
        "retained_traced_rows_under_declared_new_assignment": dict(totals),
        "verified_evidence": list(evidence.values()),
        "input_sha256": {"source_trace": CONTRACT.sha256(trace_path),
                         "mapping": CONTRACT.sha256(mapping_path),
                         "split_assignment": CONTRACT.sha256(splits_path)},
        "output_sha256": {"groups.csv": hashlib.sha256(group_data).hexdigest(),
                          "source_groups.csv": hashlib.sha256(source_data).hexdigest()},
        "checker_sha256": CONTRACT.sha256(Path(__file__)),
        "evidence_contract_sha256": CONTRACT.sha256(EXTENSION / "evidence_value/score_evidence_value.py"),
        "parent_identity_meaning_verified_by_this_tool": False,
        "statistical_independence_proved_by_this_tool": False,
        "feature_leakage_checked_by_this_tool": False,
        "models_fitted_or_predictions_generated": False,
        "scope": "Verified declared evidence-file bytes and complete parent-level split assignment. Read the acquisition evidence to establish the parent identities before using these groups; qualify exact/near overlap, class support and training provenance separately.",
    }
    output.mkdir(parents=True, exist_ok=False)
    (output / "groups.csv").write_bytes(group_data)
    (output / "source_groups.csv").write_bytes(source_data)
    (output / "CAPTURE_MAPPING_REPORT.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    public = sub.add_parser("verify-public")
    public.add_argument("--output", type=Path)
    plan = sub.add_parser("prepare")
    plan.add_argument("--mapping", type=Path, required=True)
    plan.add_argument("--splits", type=Path, required=True)
    plan.add_argument("--output", type=Path, required=True)
    plan.add_argument("--trace", type=Path, default=EXTENSION / "SOURCE_ROW_TRACE.json")
    plan.add_argument("--allow-synthetic-fixture", action="store_true")
    args = parser.parse_args()
    try:
        if args.command == "verify-public":
            result = verify_public()
            if args.output:
                with args.output.open("x", encoding="utf-8") as stream:
                    json.dump(result, stream, indent=2)
                    stream.write("\n")
        else:
            result = prepare(args.mapping, args.splits, args.output, args.trace,
                             args.allow_synthetic_fixture)
        print(json.dumps(result, indent=2))
        return 0
    except (CONTRACT.ContractError, OSError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
