"""Small synthetic records only: no private runtime, model, or hardware input."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


EXTENSION = Path(__file__).resolve().parents[2]
SCRIPT = EXTENSION / "qualify_private_records.py"
LEGACY = EXTENSION / "private_record_qualification/legacy/qualify_private_records_dc5269c.py"
LEGACY_SHA = "5b193c43e476df783837b51b49d40750222dd8acb3723ada16cd89f8ce81affd"
ARM = "F12_S01_E_mid_a01"
TREE = "e" * 64
CAP = 262144


class Fixture:
    def __init__(self, root):
        self.root = Path(root)
        self.campaign = self.root / "campaign"
        self.runtime = self.root / "runtime"
        self.expected = self.root / "expected.json"
        self.index = self.campaign / "ATTEMPT_INDEX.json"
        self.base = self.campaign / "F12_S01/attempt_a01/E_mid"
        index = {"accepted": [{"session_id": "F12_S01", "attempt": "a01", "arms": [ARM]}]}
        self.dump(self.expected, index)
        self.dump(self.index, index)
        package = self.runtime / "netshield"
        package.mkdir(parents=True)
        (package / "__init__.py").write_text("")
        (package / "common.py").write_text(f"def package_tree_sha256():\n    return {TREE!r}\n")
        model_dir = self.runtime / "artifacts/portable_models"
        model_dir.mkdir(parents=True)
        models = {}
        for name in ("light", "medium", "heavy"):
            data = ("synthetic-weight-bytes-" + name).encode()
            (model_dir / (name + ".npz")).write_bytes(data)
            models[name] = hashlib.sha256(data).hexdigest()
        self.dump(self.base / "manifests/deployment.json", {
            role: {"identity": {"package_tree_sha256": TREE}, "models": models}
            for role in ("core", "P1", "P2", "P3")})
        self.core = self.folder("core") / "core_windows.jsonl"
        core_rows = []
        self.event_paths, self.window_paths = {}, {}
        for role in ("core", "P1", "P2", "P3"):
            folder = self.folder(role)
            self.dump(folder / "manifest.json", {
                "run_id": ARM, "device_id": role,
                "software": {"package_tree_sha256": TREE, "hostname": role + "-synthetic"},
                "config": {"app_capacity_bps": CAP * 8, "window_seconds": 1.0,
                           "windows": 95, "warmup_windows": 5, "drain_windows": 200}})
            if role == "core":
                continue
            self.dump(self.base / "preflight" / (role + ".json"), {
                "data": {"hostname": {"stdout": role + "-synthetic\n"}}})
            windows = []
            for window in range(295):
                count = int(5 <= window < 95)
                windows.append({"run_id": ARM, "device_id": role, "window_index": window,
                                "drain_window": window >= 95, "generated_events": count,
                                "payload_generated_bytes": count, "payload_delivered_bytes": count,
                                "application_payload_bytes": count, "queue_bytes": 0})
                core_rows.append({"record_type": "core_window", "run_id": ARM, "device_id": role,
                                  "window_index": window, "shared_cap_bytes": CAP,
                                  "grant_bytes": count, "demand_bytes": count, "evidence_bytes_received": count})
            events = [{"window_phase": "measured", "run_id": ARM, "device_id": role,
                       "origin_window_index": w, "event_key": f"SYNTHETIC|{ARM}|{role}|{w}",
                       "campaign_id": "SYNTHETIC", "deadline_ns": 10**9,
                       "payload_bytes": 1, "unique_payload_received_bytes": 1,
                       "queued_remaining_bytes": 0, "inflight_payload_bytes": 0,
                       "cancelled_discarded_bytes": 0, "duplicate_wire_bytes": 0,
                       "requires_core": True, "created_probe_monotonic_ns": w * 10**9,
                       "result_received_monotonic_ns": w * 10**9 + 500_000_000}
                      for w in range(5, 95)]
            self.event_paths[role] = folder / "event_ledger.jsonl"
            self.window_paths[role] = folder / "probe_windows.jsonl"
            self.jsonl(self.event_paths[role], events)
            self.jsonl(self.window_paths[role], windows)
        self.jsonl(self.core, core_rows)
        self.output_count = 0

    def folder(self, role):
        return self.base / "raw" / ("core" if role == "core" else "probe/" + role) / ARM

    @staticmethod
    def dump(path, data):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data))

    @staticmethod
    def jsonl(path, data):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("".join(json.dumps(row) + "\n" for row in data))

    def mutate(self, path, mutate):
        rows = [json.loads(line) for line in path.read_text().splitlines()]
        mutate(rows)
        self.jsonl(path, rows)

    def run(self, optimized=False, repository_index=False):
        self.output_count += 1
        output = self.root / f"report-{self.output_count}.json"
        cmd = [sys.executable] + (["-O"] if optimized else [])
        cmd += [str(SCRIPT), str(self.campaign), str(self.runtime), str(output)]
        if not repository_index:
            cmd += ["--expected-index", str(self.expected)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if not output.exists():
            raise AssertionError(f"Expected retained report, got exit={result.returncode}: {result.stderr}")
        return result, json.loads(output.read_text())


class QualificationTests(unittest.TestCase):
    def fixture(self):
        temp = tempfile.TemporaryDirectory(prefix="netshield_qualification_test_")
        self.addCleanup(temp.cleanup)
        return Fixture(temp.name)

    def assert_failed(self, result, report, code):
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(report["status"], "FAIL")
        self.assertIn(code, {e["code"] for e in report["errors"]})

    def test_valid_baseline_and_legacy_bytes(self):
        f = self.fixture()
        result, report = f.run()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(report["status"], "PASS_RECORDED_FIELDS_ONLY")
        self.assertFalse(report["expected_index_is_repository_default"])
        self.assertEqual(report["expected_arm_count"], 1)
        self.assertEqual(report["counts"]["runtime_manifest_matches"], 4)
        self.assertEqual(report["counts"]["verified_rounds"], 295)
        self.assertEqual(report["counts"]["generated"], 270)
        self.assertEqual(report["counts"]["timely_core"], 270)
        self.assertEqual(hashlib.sha256(LEGACY.read_bytes()).hexdigest(), LEGACY_SHA)
        self.assertEqual(report["legacy_checker_sha256"], LEGACY_SHA)
        self.assertTrue(report["limitations"])

    def test_import_does_not_read_argv_or_private_runtime(self):
        spec = importlib.util.spec_from_file_location("qualification_import_only", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertTrue(callable(module.main))
        self.assertNotIn("netshield.common", sys.modules)

    def test_both_original_counter_errors_fail_and_are_retained(self):
        f = self.fixture()
        f.mutate(f.event_paths["P1"], lambda rows: rows[0].update(unique_payload_received_bytes=0))
        f.mutate(f.core, lambda rows: rows[5].update(grant_bytes=2))
        result, report = f.run()
        self.assert_failed(result, report, "event_balance_errors")
        self.assertIn("grant_demand_service_errors", {e["code"] for e in report["errors"]})
        self.assertEqual(report["counts"]["event_balance_errors"], 1)
        self.assertEqual(report["counts"]["grant_demand_service_errors"], 1)
        self.assertEqual(report["counts"]["verified_rounds"], 294)

    def test_capacity_failure_cannot_be_disabled_by_optimized_python(self):
        f = self.fixture()
        f.mutate(f.core, lambda rows: rows[0].update(shared_cap_bytes=0))
        for optimized in (False, True):
            with self.subTest(optimized=optimized):
                result, report = f.run(optimized=optimized)
                self.assert_failed(result, report, "shared_cap")

    def test_noninteger_and_negative_bytes_are_rejected(self):
        for field, value in (("grant_bytes", -1), ("grant_bytes", 0.5),
                             ("grant_bytes", True), ("queued_remaining_bytes", -1),
                             ("payload_bytes", 1.0), ("duplicate_wire_bytes", False)):
            with self.subTest(field=field, value=value):
                f = self.fixture()
                path = f.core if field == "grant_bytes" else f.event_paths["P1"]
                f.mutate(path, lambda rows: rows[0].update({field: value}))
                result, report = f.run()
                self.assert_failed(result, report, "invalid_integer")

    def test_cohort_empty_duplicate_missing_extra_and_wrong_attempt(self):
        cases = (
            ([], "empty_cohort"),
            ([ARM, ARM], "duplicate_arm"),
            (["F12_S01_E_mid_a02"], "cohort_mismatch"),
            ([ARM, "F12_S01_E_low_a01"], "cohort_mismatch"),
        )
        for arms, code in cases:
            with self.subTest(arms=arms):
                f = self.fixture()
                f.dump(f.index, {"accepted": [{"arms": arms}]})
                result, report = f.run()
                self.assert_failed(result, report, code)
        f = self.fixture()
        f.dump(f.expected, {"accepted": [{"arms": [ARM, "F12_S01_E_low_a01"]}]})
        result, report = f.run()
        self.assert_failed(result, report, "cohort_mismatch")
        f = self.fixture()
        result, report = f.run(repository_index=True)
        self.assert_failed(result, report, "cohort_mismatch")
        self.assertEqual(report["expected_arm_count"], 216)

    def test_duplicate_event_and_wrong_explicit_identity_fail(self):
        for kind in ("duplicate", "run", "origin", "core_run", "probe_device"):
            with self.subTest(kind=kind):
                f = self.fixture()
                if kind == "duplicate":
                    f.mutate(f.event_paths["P1"], lambda rows: rows[1].update(event_key=rows[0]["event_key"]))
                    expected = "duplicate_event_key"
                elif kind == "run":
                    f.mutate(f.event_paths["P1"], lambda rows: rows[0].update(run_id="another-run"))
                    expected = "event_identity"
                elif kind == "origin":
                    f.mutate(f.event_paths["P1"], lambda rows: rows[0].update(origin_window_index=6))
                    expected = "event_origin_coverage"
                elif kind == "core_run":
                    f.mutate(f.core, lambda rows: rows[0].update(run_id="another-run"))
                    expected = "identity_mismatch"
                else:
                    f.mutate(f.window_paths["P1"], lambda rows: rows[0].update(device_id="P2"))
                    expected = "identity_mismatch"
                result, report = f.run()
                self.assert_failed(result, report, expected)

    def test_opaque_keys_do_not_assume_a_crfa_grammar_or_global_namespace(self):
        f = self.fixture()
        for device in ("P1", "P2", "P3"):
            def local_keys(rows):
                for row in rows:
                    row["event_key"] = f"opaque|historical|key|{row['origin_window_index']}"
            f.mutate(f.event_paths[device], local_keys)
        result, report = f.run()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(report["counts"]["event_key_opaque_format"], 270)

    def test_pending_bytes_and_missing_return_are_not_success(self):
        for pending_field in ("queued_remaining_bytes", "inflight_payload_bytes", "missing_return"):
            with self.subTest(pending_field=pending_field):
                f = self.fixture()
                if pending_field == "missing_return":
                    f.mutate(f.event_paths["P1"], lambda rows: rows[0].update(result_received_monotonic_ns=None))
                else:
                    f.mutate(f.event_paths["P1"], lambda rows: rows[0].update({
                        "unique_payload_received_bytes": 0, pending_field: 1,
                        "result_received_monotonic_ns": None}))
                result, report = f.run()
                self.assertEqual(result.returncode, 2)
                self.assertEqual(report["status"], "PENDING_TERMINAL_STATE")
                self.assertEqual(report["terminal_state"], "PENDING")
                self.assertEqual(report["counts"]["event_balance_errors"], 0)
                self.assertGreater(report["counts"][pending_field], 0)

    def test_queue_receipt_and_negative_return_arithmetic_fail(self):
        for kind, code in (("queue", "queue_residuals"), ("receipt", "receipt_disagreements"),
                           ("time", "negative_latency")):
            with self.subTest(kind=kind):
                f = self.fixture()
                if kind == "queue":
                    f.mutate(f.window_paths["P1"], lambda rows: rows[5].update(queue_bytes=1))
                elif kind == "receipt":
                    f.mutate(f.core, lambda rows: rows[5].update(evidence_bytes_received=0))
                else:
                    f.mutate(f.event_paths["P1"], lambda rows: rows[0].update(result_received_monotonic_ns=0))
                result, report = f.run()
                self.assert_failed(result, report, code)

    def test_missing_windows_and_missing_required_time_fail(self):
        for kind, code in (("window", "core_window_coverage"), ("time", "input_schema_or_io")):
            with self.subTest(kind=kind):
                f = self.fixture()
                if kind == "window":
                    f.mutate(f.core, lambda rows: rows.pop())
                else:
                    f.mutate(f.event_paths["P1"], lambda rows: rows[0].pop("result_received_monotonic_ns"))
                result, report = f.run()
                self.assert_failed(result, report, code)


if __name__ == "__main__":
    unittest.main()
