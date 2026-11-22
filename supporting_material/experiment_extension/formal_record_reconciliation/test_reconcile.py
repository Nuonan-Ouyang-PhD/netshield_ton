"""Synthetic failure-mode fixtures only; no private logs/models are executed."""

import copy
import csv
import json
import tempfile
import unittest
from pathlib import Path

import reconcile as audit


class ReconciliationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ton_export_reconcile_test_")
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.expected = audit.accepted_arms(audit.DEFAULT_INDEX)
        self.rows = []
        for arm in sorted(self.expected):
            row = {key: 0 for key in audit.COUNTERS if key not in audit.OPTIONAL_COUNTERS}
            row.update(arm=arm, identities=[audit.IDENTITY], rounds=295, generated=270)
            self.rows.append(row)
        self.registry = {}
        for arm in self.expected:
            self.registry[f"/UNIT_TEST_NOT_REAL/raw/core/{arm}/core_windows.jsonl"] = "1" * 64
            for device in ("P1", "P2", "P3"):
                for file in ("probe_windows.jsonl", "event_ledger.jsonl"):
                    self.registry[f"/UNIT_TEST_NOT_REAL/raw/probe/{device}/{arm}/{file}"] = "1" * 64
        self.splits = {
            "train": {"rows": 20, "rows_matching_earlier_split": 0, "file_sha256": "1" * 64},
            "validation": {"rows": 8, "rows_matching_earlier_split": 2, "file_sha256": "2" * 64},
            "test": {"rows": 10, "rows_matching_earlier_split": 4, "file_sha256": "3" * 64},
        }
        self.interfaces = []
        for number, device in enumerate(("P1", "P2", "P3")):
            for line in (1, 2, 3):
                for level, size in (("alert", 16), ("summary", 13), ("full", 224)):
                    self.interfaces.append(dict(device=device, line=line, level=level, encoded_bytes=size,
                        encoded_sha256="4" * 64, model_sha256="5" * 64,
                        source_sha256=f"{number * 3 + line:064x}", prediction=line % 2))

    def write_inputs(self):
        source = self.directory / "inputs"
        source.mkdir()
        (source / "formal_records.json").write_text(json.dumps(dict(arms=self.rows, private_sources=self.registry)))
        (source / "split_overlap.json").write_text(json.dumps(self.splits))
        (source / "pilot_model_interfaces.jsonl").write_text("\n".join(json.dumps(row) for row in self.interfaces) + "\n")
        return source

    def test_exact_public_accepted_reruns_and_missing_duplicate_wrong_cohort(self):
        normalized = audit.normalize_arm_rows(self.rows, self.expected)
        attempts = audit.arm_aggregates(normalized)["accepted_attempts"]
        for session in ("F12_S03", "F12_S04", "F12_S07"):
            self.assertEqual(attempts[session], "a02")
        for mutation in ("missing", "duplicate", "wrong_attempt"):
            with self.subTest(mutation=mutation):
                rows = copy.deepcopy(self.rows)
                if mutation == "missing":
                    rows.pop()
                elif mutation == "duplicate":
                    rows.append(copy.deepcopy(rows[0]))
                else:
                    row = next(row for row in rows if row["arm"].startswith("F12_S03_"))
                    row["arm"] = row["arm"].replace("_a02", "_a01")
                with self.assertRaises(audit.ReconciliationError):
                    audit.normalize_arm_rows(rows, self.expected)

    def test_unknown_shape_negative_boolean_identity_and_counter_constraints_fail(self):
        changes = ({"new_unknown_field": 1}, {"queue_residuals": -1}, {"generated": True},
                   {"identities": ["f" * 64]}, {"timely_core": 1}, {"rounds": 294})
        for change in changes:
            with self.subTest(change=change):
                rows = copy.deepcopy(self.rows)
                rows[0].update(change)
                with self.assertRaises(audit.ReconciliationError):
                    audit.normalize_arm_rows(rows, self.expected)
        rows = copy.deepcopy(self.rows)
        del rows[0]["generated"]
        with self.assertRaises(audit.ReconciliationError):
            audit.normalize_arm_rows(rows, self.expected)

    def test_optional_counter_zero_and_nonzero_anomalies_are_retained_not_filtered(self):
        self.rows[0]["queue_residuals"] = 1
        self.rows[1]["unallocated_demanded_bytes"] = 2
        self.rows[2].update(core_required=1, missing_return=1)
        normalized = audit.normalize_arm_rows(self.rows, self.expected)
        aggregate = audit.arm_aggregates(normalized)
        self.assertEqual(len(normalized), 216)
        self.assertEqual(aggregate["totals"]["timely_core"], 0)
        self.assertEqual(aggregate["totals"]["missing_return"], 1)
        self.assertEqual(aggregate["totals"]["unallocated_demanded_bytes"], 2)
        self.assertEqual(aggregate["reported_anomaly_status"], "FAIL")

    def test_source_registry_must_cover_every_role_without_exporting_paths(self):
        result = audit.validate_source_registry(self.registry, self.expected)
        self.assertEqual(result["reported_file_hashes"], 1512)
        self.assertNotIn("UNIT_TEST", json.dumps(result))
        damaged = dict(self.registry)
        damaged.pop(next(iter(damaged)))
        with self.assertRaises(audit.ReconciliationError):
            audit.validate_source_registry(damaged, self.expected)

    def test_split_overlap_counts_and_interface_pairs_are_not_efficacy(self):
        split = audit.split_summary(self.splits)
        self.assertEqual(split["splits"]["validation"]["matching_fraction"], 0.25)
        self.assertFalse(split["held_out_efficacy_qualified"])
        broken = copy.deepcopy(self.splits)
        broken["test"]["rows_matching_earlier_split"] = 11
        with self.assertRaises(audit.ReconciliationError):
            audit.split_summary(broken)
        summary = audit.interface_summary(self.interfaces)
        self.assertEqual(summary["source_observations"], 9)
        self.assertEqual(summary["rows"], 27)
        self.assertFalse(summary["accuracy_or_detection_gain_estimated"])
        for mutation in ("missing", "duplicate", "changed_source"):
            with self.subTest(mutation=mutation):
                rows = copy.deepcopy(self.interfaces)
                if mutation == "missing":
                    rows.pop()
                elif mutation == "duplicate":
                    rows.append(copy.deepcopy(rows[0]))
                else:
                    rows[0]["source_sha256"] = "f" * 64
                with self.assertRaises(audit.ReconciliationError):
                    audit.interface_summary(rows)

    def test_export_roundtrip_is_pathfree_and_does_not_overwrite(self):
        source = self.write_inputs()
        output = self.directory / "results"
        result = audit.export_reports(source, output)
        self.assertEqual(audit.verify_public(output), result)
        text = "".join(path.read_text() for path in output.iterdir())
        self.assertNotIn("UNIT_TEST_NOT_REAL", text)
        self.assertNotIn(str(source), text)
        self.assertEqual(result["raw_window_or_event_logs_reopened"], 0)
        with self.assertRaises(audit.ReconciliationError):
            audit.export_reports(source, output)

    def test_public_verification_checks_cohort_and_math_even_after_product_hash_update(self):
        source = self.write_inputs()
        output = self.directory / "results"
        audit.export_reports(source, output)
        path = output / "SPLIT_COUNTS.json"
        split = json.loads(path.read_text())
        split["splits"]["validation"]["matching_fraction"] = 1.0
        audit.write_json(path, split)
        report_path = output / "RECONCILIATION.json"
        report = json.loads(report_path.read_text())
        report["products_sha256"][path.name] = audit.sha(path)
        audit.write_json(report_path, report)
        with self.assertRaises(audit.ReconciliationError):
            audit.verify_public(output)
        audit.write_json(path, audit.split_summary(self.splits))
        report["products_sha256"][path.name] = audit.sha(path)
        csv_path = output / "ARM_REVIEW.csv"
        with csv_path.open(newline="") as stream:
            reader = csv.DictReader(stream)
            rows = list(reader)
        with csv_path.open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=audit.ARM_FIELDS)
            writer.writeheader()
            writer.writerows(rows[:-1])
        report["products_sha256"][csv_path.name] = audit.sha(csv_path)
        audit.write_json(report_path, report)
        with self.assertRaises(audit.ReconciliationError):
            audit.verify_public(output)


if __name__ == "__main__":
    unittest.main()
