"""Temporary synthetic mapping failures; no corpus/model/hardware execution."""
import copy
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("capture_split", HERE / "prepare_capture_split.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


class CaptureMappingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="netshield-synthetic-lineage-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.trace_path = self.root / "trace.json"
        self.mapping_path = self.root / "mapping.json"
        self.splits_path = self.root / "capture_splits.csv"
        self.output = self.root / "output"
        self.trace = [dict(split=split, matched=2, original_csv_sha256=digest(f"source-{i}"),
                           labelled_csv_sha256=digest(f"labelled-{i}"))
                      for i, split in enumerate(("train", "validation", "test", "train"))]
        evidence = self.root / "acquisition_record.json"
        evidence.write_text('{"data_origin":"SYNTHETIC_FIXTURE","captures":["A","B","C"]}')
        self.mapping = dict(
            schema_version="netshield.source_capture_mapping.v1",
            data_origin="SYNTHETIC_FIXTURE",
            group_definition="Synthetic acquisition parents; two source files share A.",
            evidence=[dict(id="fixture-log", path=evidence.name, sha256=MODULE.CONTRACT.sha256(evidence))],
            sources=[dict(original_csv_sha256=row["original_csv_sha256"], parent_capture_id=parent,
                          evidence_ids=["fixture-log"])
                     for row, parent in zip(self.trace, ("A", "B", "C", "A"))])
        self.splits = "parent_capture_id,split\nA,train\nB,validation\nC,test\n"

    def write_inputs(self):
        self.trace_path.write_text(json.dumps(self.trace))
        self.mapping_path.write_text(json.dumps(self.mapping))
        self.splits_path.write_text(self.splits)

    def run_fixture(self, allow=True):
        self.write_inputs()
        return MODULE.prepare(self.mapping_path, self.splits_path, self.output,
                              self.trace_path, allow_fixture=allow)

    def reject(self):
        with self.assertRaises(MODULE.CONTRACT.ContractError):
            self.run_fixture()
        self.assertFalse(self.output.exists())

    def test_current_public_trace_matches_retained_denominators(self):
        result = MODULE.verify_public()
        self.assertEqual(result["total_rows"], 5141673)
        self.assertEqual(result["split_source_files"], {"train": 18, "validation": 6, "test": 7})
        self.assertFalse(result["private_feature_rows_rechecked"])
        self.assertFalse(result["parent_capture_mapping_qualified"])

    def test_shared_parent_stays_one_group_and_scope_is_explicit(self):
        result = self.run_fixture()
        self.assertEqual(result["status"], "DECLARED_PARENT_SPLIT_CONSISTENT")
        self.assertEqual(result["declared_parent_captures"], 3)
        with (self.output / "groups.csv").open() as stream:
            groups = list(csv.DictReader(stream))
        self.assertEqual(groups, [{"group_id": "A", "split": "train"},
                                  {"group_id": "B", "split": "validation"},
                                  {"group_id": "C", "split": "test"}])
        self.assertEqual(result["retained_traced_rows_under_declared_new_assignment"],
                         {"train": 4, "validation": 2, "test": 2})
        self.assertFalse(result["parent_identity_meaning_verified_by_this_tool"])
        self.assertFalse(result["statistical_independence_proved_by_this_tool"])
        self.assertNotIn(str(self.root), json.dumps(result))
        for name, expected in result["output_sha256"].items():
            self.assertEqual(MODULE.CONTRACT.sha256(self.output / name), expected)

    def test_incomplete_duplicate_or_unknown_source_mapping_is_rejected(self):
        original = copy.deepcopy(self.mapping)
        variants = [original["sources"][:-1], original["sources"] + [original["sources"][0]],
                    original["sources"] + [dict(original_csv_sha256=digest("unknown"),
                        parent_capture_id="D", evidence_ids=["fixture-log"])]]
        for sources in variants:
            with self.subTest(sources=len(sources)):
                self.mapping = copy.deepcopy(original)
                self.mapping["sources"] = sources
                self.reject()

    def test_one_parent_cannot_be_assigned_to_two_splits(self):
        self.splits += "A,test\n"
        self.reject()

    def test_insufficient_or_mismatched_parent_inventory_is_rejected(self):
        for splits in ("parent_capture_id,split\nA,train\nB,validation\n",
                       "parent_capture_id,split\nA,train\nB,validation\nC,train\n",
                       self.splits + "D,test\n"):
            with self.subTest(splits=splits):
                self.splits = splits
                self.reject()

    def test_missing_or_altered_evidence_is_rejected(self):
        original = copy.deepcopy(self.mapping)
        self.mapping["sources"][0]["evidence_ids"] = []
        self.reject()
        self.mapping = copy.deepcopy(original)
        self.mapping["sources"][0]["evidence_ids"] = ["unknown"]
        self.reject()
        self.mapping = copy.deepcopy(original)
        (self.root / "acquisition_record.json").write_text("changed fixture")
        self.reject()

    def test_invalid_source_counts_and_duplicate_hashes_are_rejected(self):
        original = copy.deepcopy(self.trace)
        for value in (0, -1, 2.0, True):
            with self.subTest(value=value):
                self.trace = copy.deepcopy(original)
                self.trace[0]["matched"] = value
                self.reject()
        self.trace = copy.deepcopy(original)
        self.trace[1]["original_csv_sha256"] = self.trace[0]["original_csv_sha256"]
        self.reject()

    def test_fixture_opt_in_and_fresh_output_are_required(self):
        with self.assertRaises(MODULE.CONTRACT.ContractError):
            self.run_fixture(allow=False)
        self.assertFalse(self.output.exists())
        self.run_fixture()
        sentinel = self.output / "CAPTURE_MAPPING_REPORT.json"
        before = sentinel.read_bytes()
        with self.assertRaises(MODULE.CONTRACT.ContractError):
            self.run_fixture()
        self.assertEqual(sentinel.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
