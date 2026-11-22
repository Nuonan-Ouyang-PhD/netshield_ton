"""In-memory corruption checks; no private inputs or research outputs created."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest


HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "verify_export.py"
SPEC = importlib.util.spec_from_file_location("retained_export_verifier", SCRIPT)
VERIFIER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFIER)


class ExportVerificationTests(unittest.TestCase):
    def setUp(self):
        self.report = json.loads((HERE / "diagnostic_review.json").read_text())

    def reject(self, report):
        with self.assertRaises(ValueError):
            VERIFIER.verify_diagnostic_summary(report)

    def test_current_public_snapshot_and_explicit_unique_scope(self):
        result = VERIFIER.verify_export()
        self.assertEqual((result["groups"], result["generated"]), (7, 896))
        self.assertEqual(result["reported_distinct_vectors"], [895, 863])
        self.assertEqual(result["distinct_vector_verification"],
                         "bounds_only_private_feature_scan_not_repeated")

    def test_extra_duplicate_group_preserving_overlap_totals_is_rejected(self):
        extra = copy.deepcopy(self.report["files"][0])
        for rule in ("exact", "rounded"):
            extra[rule].update(train_only=0, validation_only=0, both=0, neither=128)
        self.report["files"].append(extra)
        self.reject(self.report)

    def test_duplicate_name_with_seven_rows_is_rejected(self):
        self.report["files"][1]["group"] = self.report["files"][0]["group"]
        self.reject(self.report)

    def test_impossible_exported_distinct_counts_are_rejected(self):
        for values in ([0, 0], [897, 863], [895, 896], [127, 120], [895.0, 863]):
            with self.subTest(values=values):
                changed = copy.deepcopy(self.report)
                changed["unique_vectors_in_subset"] = values
                self.reject(changed)

    def test_negative_bucket_counts_cannot_cancel(self):
        # Keeps both per-file and published aggregate bucket sums unchanged.
        self.report["files"][0]["exact"].update(train_only=-1, validation_only=1)
        self.reject(self.report)

    def test_negative_or_noninteger_confusion_counts_are_rejected(self):
        for counts in ({"TN": 129, "FP": -1}, {"TN": 128.0}, {"TN": 128, "FP": False}):
            with self.subTest(counts=counts):
                changed = copy.deepcopy(self.report)
                changed["files"][0]["alert"] = counts
                self.reject(changed)

    def test_unknown_confusion_key_and_changed_pooled_result_are_rejected(self):
        for counts in ({"UNSCORED": 128}, {"FN": 128}):
            with self.subTest(counts=counts):
                changed = copy.deepcopy(self.report)
                changed["files"][0]["alert"] = counts
                self.reject(changed)

    def test_within_file_unique_bounds_are_checked(self):
        for value in (0, 129, 3):
            with self.subTest(value=value):
                changed = copy.deepcopy(self.report)
                # G02 has four nonempty exact-membership categories.
                changed["files"][1]["exact"]["unique_within_file"] = value
                self.reject(changed)

    def test_rounded_containment_checks_keep_inclusive_split_meaning(self):
        changed = copy.deepcopy(self.report)
        # Preserve union totals while losing exact training membership.
        changed["files"][1]["rounded"].update(train_only=0, validation_only=28, both=55)
        self.reject(changed)
        changed = copy.deepcopy(self.report)
        # Preserve union and both inclusive totals, but lose one both-split match.
        changed["files"][1]["rounded"].update(train_only=25, validation_only=4, both=54)
        self.reject(changed)

    def test_optimized_python_cannot_disable_rejection(self):
        self.report["unique_vectors_in_subset"] = [0, 0]
        code = (
            "import importlib.util,json,sys; "
            "s=importlib.util.spec_from_file_location('v',sys.argv[1]); "
            "m=importlib.util.module_from_spec(s); s.loader.exec_module(m); "
            "m.verify_diagnostic_summary(json.load(sys.stdin))"
        )
        result = subprocess.run([sys.executable, "-B", "-O", "-c", code, str(SCRIPT)],
                                input=json.dumps(self.report), text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ValueError: global exact unique bounds", result.stderr)


if __name__ == "__main__":
    unittest.main()
