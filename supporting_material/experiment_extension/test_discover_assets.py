import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("discover_assets.py")
SPEC = importlib.util.spec_from_file_location("asset_discovery", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class AssetDiscoveryTests(unittest.TestCase):
    def test_source_is_parsed_never_executed_and_reports_candidates_not_verdicts(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sentinel = root / "must_not_exist"
            (root / "runtime.py").write_text(f"raise RuntimeError('must not execute')\nfrom pathlib import Path\nPath({str(sentinel)!r}).touch()\ndef waterfill(q, cap):\n share = cap // len(q)\n while q:\n  if share == 0:\n   break\n", encoding="utf-8")
            report = MODULE.discover([("runtime", root)], hash_max_bytes=10000, max_files=100)
            self.assertFalse(sentinel.exists())
            function = report["files"][0]["candidate_functions"][0]
            self.assertTrue(function["integer_division_and_zero_break_heuristic"])
            self.assertEqual(function["interpretation"], "SOURCE_REVIEW_REQUIRED_NOT_A_BUG_VERDICT")
            self.assertEqual(report["experiment_status"], "NOT_EXECUTED")

    def test_secrets_symlinks_and_data_values_are_not_exported(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".env").write_text("private-token")
            (root / "credentials.json").write_text('{"secret":"private-token"}')
            (root / "events.csv").write_text("episode_id,ground_truth\nprivate-episode,attack\n")
            (root / "numeric.csv").write_text("1,999999,0\n")
            (root / "text_values.csv").write_text("private-patient,private-diagnosis\n")
            (root / "linked.csv").symlink_to(root / "events.csv")
            report = MODULE.discover([("data", root)], hash_max_bytes=10000, max_files=100)
            encoded = json.dumps(report)
            self.assertNotIn("private-token", encoded)
            self.assertNotIn("private-episode", encoded)
            self.assertNotIn("999999", encoded)
            self.assertNotIn("private-patient", encoded)
            self.assertNotIn("private-diagnosis", encoded)
            self.assertNotIn("linked.csv", encoded)
            self.assertEqual(len(report["files"]), 3)

    def test_hash_limits_missing_roots_and_truncation_are_explicit(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "model.onnx").write_bytes(b"not-a-real-model")
            (root / "z.csv").write_text("label\nattack\n")
            report = MODULE.discover([("missing", root / "absent"), ("data", root)], hash_max_bytes=0, max_files=1)
            self.assertTrue(report["truncated"])
            self.assertEqual(report["roots"][0]["status"], "DIRECTORY_NOT_AVAILABLE")
            self.assertIsNone(report["files"][0]["sha256"])
            self.assertIn("REQUIRE_IDENTITY", report["model_status"])

    def test_duplicate_root_names_and_invalid_limits_rejected(self):
        with self.assertRaises(ValueError):
            MODULE.discover([("x", Path(".")), ("x", Path("."))], hash_max_bytes=1, max_files=1)
        with self.assertRaises(ValueError):
            MODULE.discover([("x", Path("."))], hash_max_bytes=-1, max_files=1)

    def test_cli_does_not_overwrite_prior_inventory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "existing.json"
            target.write_text("prior evidence")
            result = subprocess.run([sys.executable, str(SCRIPT), "--root", f"test={root}", "--output", str(target)], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(target.read_text(), "prior evidence")


if __name__ == "__main__":
    unittest.main()
