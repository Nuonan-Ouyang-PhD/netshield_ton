"""Failure-mode tests; all observations are temporary SYNTHETIC_FIXTURE data.

No fixture results are research observations, and no generated fixture CSV/JSON
is committed. The scorer never runs an encoder, trains a model, or starts a Pi.
"""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

MODULE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MODULE_ROOT))
import score_evidence_value as scoring


def digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


class Fixture:
    """Construct only a declared, non-research in-memory/temporary fixture."""
    def __init__(self, root: Path):
        self.root = root
        self.paths = {name: root / f"SYNTHETIC_FIXTURE_{name}.csv" for name in ("groups", "corpus", "occurrences", "predictions")}
        self.protocol_path = root / "SYNTHETIC_FIXTURE_protocol.json"
        self.groups = [{"group_id": name, "split": split} for name, split in (("SYNTHETIC_TRAIN", "train"), ("SYNTHETIC_VAL", "validation"), ("SYNTHETIC_G1", "test"), ("SYNTHETIC_G2", "test"))]
        self.corpus = []
        for index, group in enumerate(("SYNTHETIC_TRAIN", "SYNTHETIC_VAL", "SYNTHETIC_G1", "SYNTHETIC_G1", "SYNTHETIC_G2", "SYNTHETIC_G2")):
            self.corpus.append({"source_record_id": f"SYNTHETIC_SOURCE_{index}", "group_id": group, "split": self.groups[0 if index == 0 else 1 if index == 1 else 2]["split"], "truth_raw": "raw_benign" if index % 2 == 0 else "raw_attack", "source_feature_sha256": digest(f"SYNTHETIC_FEATURE_{index}")})
        self.occurrences = [
            {"occurrence_id": f"SYNTHETIC_EVENT_{index}", "source_record_id": row["source_record_id"], "group_id": row["group_id"], "split": "test", "truth_label": "benign" if row["truth_raw"] == "raw_benign" else "attack", "source_feature_sha256": row["source_feature_sha256"]}
            for index, row in enumerate(self.corpus[2:])
        ]
        decision = {"kind": "positive_score_greater_than_or_equal", "negative_label": "benign", "positive_label": "attack", "threshold": 0.5}

        def artifact(name: str, content: bytes) -> dict:
            path = root / f"SYNTHETIC_FIXTURE_{name}.bin"
            path.write_bytes(content)
            return {"id": f"SYNTHETIC_{name}", "path": path.name, "sha256": hashlib.sha256(content).hexdigest()}

        self.protocol = {
            "schema_version": scoring.SCHEMA, "study_id": "SYNTHETIC_FIXTURE_STUDY", "data_origin": "SYNTHETIC_FIXTURE", "phase": "information_only",
            "independence_unit": "capture", "group_definition": "SYNTHETIC_FIXTURE independent capture labels, not real data",
            "labels": ["benign", "attack"], "label_mapping": {"raw_benign": "benign", "raw_attack": "attack"},
            "dataset": {"id": "SYNTHETIC_FIXTURE_DATASET", "version": "fixture-v1", "groups_sha256": "", "corpus_sha256": "", "occurrences_sha256": "", "population": "all_generated_held_out_occurrences"},
            "artifacts": {"model": artifact("MODEL", b"SYNTHETIC_FIXTURE_NOT_A_MODEL"), "encoders": {level: artifact("ENCODER_" + level, b"SYNTHETIC_FIXTURE_NOT_AN_ENCODER") for level in scoring.LEVELS}, "threshold": artifact("THRESHOLD", json.dumps(decision).encode())},
            "decision_rule": decision,
            "analysis": {"primary_metric": "correct_per_generated", "primary_comparison": ["full", "summary"], "comparisons": [["full", "summary"], ["summary", "alert"]], "weighting": "equal_group", "bootstrap": {"samples": 200, "seed": 20261122, "confidence": 0.95}},
            "transport": None,
            "near_duplicate_audit": {"status": "not_performed", "method": None, "threshold": None, "artifact": None},
        }
        self.predictions = []
        for index, occurrence in enumerate(self.occurrences):
            for level in scoring.LEVELS:
                truth = occurrence["truth_label"]
                predicted = "benign" if level == "alert" else (truth if level == "full" or index < 2 else ("attack" if truth == "benign" else "benign"))
                row = dict.fromkeys(scoring.PREDICTION_FIELDS, "")
                row.update({"occurrence_id": occurrence["occurrence_id"], "representation": level, "split": "test", "truth_label": truth,
                            "model_id": self.protocol["artifacts"]["model"]["id"], "encoder_id": self.protocol["artifacts"]["encoders"][level]["id"], "threshold_id": self.protocol["artifacts"]["threshold"]["id"],
                            "status": "returned", "predicted_label": predicted, "positive_score": "0.9" if predicted == "attack" else "0.1", "source_feature_sha256": occurrence["source_feature_sha256"],
                            "representation_sha256": digest("SYNTHETIC_IDENTICAL_ENCODED_VALUE"), "payload_sha256": digest("SYNTHETIC_PADDING_PLUS_CONTENT"), "information_bytes": "16", "padding_bytes": "16", "payload_bytes": "32"})
                self.predictions.append(row)

    def transport(self) -> None:
        self.protocol["phase"] = "transport_measured"
        self.protocol["analysis"]["primary_metric"] = "timely_correct_per_generated"
        self.protocol["transport"] = {"deadline_ns": 1000000000, "anchor": "event_creation", "horizon_semantics": "continuous_observation_through_inclusive_horizon", "wire_accounting": "measured_uplink_evidence_headers_and_retransmissions"}
        for row in self.predictions:
            row.update(created_ns="10000", created_clock_domain="SYNTHETIC_PROBE_CLOCK", result_ns="1000010000", result_clock_domain="SYNTHETIC_PROBE_CLOCK", observed_until_ns="1000010000", observation_clock_domain="SYNTHETIC_PROBE_CLOCK", time_source="SYNTHETIC_FIXTURE", wire_bytes="72")

    def row(self, level: str, event: int = 0) -> dict:
        return next(row for row in self.predictions if row["representation"] == level and row["occurrence_id"] == f"SYNTHETIC_EVENT_{event}")

    @staticmethod
    def write_csv(path: Path, rows: list[dict], fields: tuple[str, ...]) -> None:
        with path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    def save(self) -> None:
        for name, fields in (("groups", scoring.GROUP_FIELDS), ("corpus", scoring.CORPUS_FIELDS), ("occurrences", scoring.OCCURRENCE_FIELDS), ("predictions", scoring.PREDICTION_FIELDS)):
            self.write_csv(self.paths[name], getattr(self, name), fields)
        for name in ("groups", "corpus", "occurrences"):
            self.protocol["dataset"][f"{name}_sha256"] = scoring.sha256(self.paths[name])
        self.protocol_path.write_text(json.dumps(self.protocol))

    def run(self) -> dict:
        self.save()
        return scoring.score_study(self.protocol_path, self.paths, allow_synthetic_fixture=True)


class EvidenceValueTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="SYNTHETIC_FIXTURE_")
        self.fixture = Fixture(Path(self.temp.name))

    def tearDown(self):
        self.temp.cleanup()

    def assert_rejected(self, phrase: str):
        with self.assertRaisesRegex(scoring.ContractError, phrase):
            self.fixture.run()

    def test_pooled_confusion_denominators_and_exact_provenance(self):
        result = self.fixture.run()
        full = result["pooled_by_representation"]["full"]
        summary = result["pooled_by_representation"]["summary"]
        self.assertEqual((full["generated"], full["scored"], full["correct"]), (4, 4, 4))
        self.assertEqual({k: summary["scored_only_binary_metrics"][k] for k in ("TP", "FP", "FN", "TN")}, {"TP": 1, "FP": 1, "FN": 1, "TN": 1})
        self.assertEqual(summary["scored_only_binary_metrics"]["f1_positive"], 0.5)
        self.assertIsNone(full["timely_correct_per_generated"])
        self.assertEqual(full["byte_costs"]["information_bytes"]["total"], 64)
        self.assertEqual(full["byte_costs"]["padding_bytes"]["total"], 64)
        self.assertEqual(full["byte_costs"]["payload_bytes"]["total"], 128)
        self.assertIsNone(full["byte_costs"]["wire_bytes"]["total"])
        self.assertEqual(result["provenance"]["scorer_source_sha256"], scoring.sha256(MODULE_ROOT / "score_evidence_value.py"))
        self.assertEqual(len(result["provenance"]["verified_artifacts"]), 5)
        self.assertEqual(result["data_origin"], "SYNTHETIC_FIXTURE")

    def test_equal_group_estimand_differs_from_pooled_occurrence_weighting(self):
        for source in self.fixture.corpus[3:]:
            source["group_id"] = "SYNTHETIC_G2"
        for occurrence in self.fixture.occurrences[1:]:
            occurrence["group_id"] = "SYNTHETIC_G2"
        for index in range(4):
            row = self.fixture.row("summary", index)
            predicted = ("attack" if row["truth_label"] == "benign" else "benign") if index == 0 else row["truth_label"]
            row.update(predicted_label=predicted, positive_score="0.9" if predicted == "attack" else "0.1")
        result = self.fixture.run()
        self.assertEqual(result["paired_group_comparisons"][0]["estimate"], 0.5)
        pooled = result["pooled_by_representation"]
        self.assertEqual(pooled["full"]["correct_per_generated"]["estimate"] - pooled["summary"]["correct_per_generated"]["estimate"], 0.25)

    def test_inclusive_deadline_and_one_nanosecond_late(self):
        self.fixture.transport()
        result = self.fixture.run()
        self.assertEqual(result["pooled_by_representation"]["full"]["timely_correct_per_generated"]["estimate"], 1.0)
        self.fixture.row("full").update(result_ns="1000010001", observed_until_ns="1000010001")
        result = self.fixture.run()
        self.assertEqual(result["pooled_by_representation"]["full"]["timely_correct_per_generated"]["estimate"], 0.75)

    def test_incomplete_followup_bounds_then_mature_miss(self):
        self.fixture.transport()
        self.fixture.row("full").update(status="censored", positive_score="", predicted_label="", result_ns="", result_clock_domain="", observed_until_ns="500010000")
        result = self.fixture.run()
        metric = result["pooled_by_representation"]["full"]["timely_correct_per_generated"]
        self.assertEqual((metric["estimate"], metric["lower"], metric["upper"], metric["generated_denominator"]), (None, 0.75, 1.0, 4))
        self.assertIsNone(result["paired_group_comparisons"][0]["percentile_interval"])
        self.assertEqual(result["paired_group_comparisons"][0]["interval_unavailable_reason"], "incomplete_outcomes_or_followup")
        self.fixture.row("full")["observed_until_ns"] = "1000010000"
        mature = self.fixture.run()["pooled_by_representation"]["full"]
        self.assertEqual(mature["timely_correct_per_generated"]["estimate"], 0.75)
        self.assertIsNone(mature["correct_per_generated"]["estimate"])
        self.assertEqual(mature["generated"], 4)

    def test_unknown_horizon_is_not_imputed_to_deadline(self):
        self.fixture.transport()
        self.fixture.row("summary").update(status="missing", positive_score="", predicted_label="", result_ns="", result_clock_domain="", observed_until_ns="", observation_clock_domain="")
        summary = self.fixture.run()["pooled_by_representation"]["summary"]
        self.assertEqual(summary["timely_correct_per_generated"]["unresolved"], 1)
        self.assertIsNone(summary["timely_correct_per_generated"]["estimate"])

    def test_terminal_rejection_stays_in_denominator_before_deadline(self):
        self.fixture.transport()
        self.fixture.row("full").update(status="rejected", status_detail="SYNTHETIC_TERMINAL_ADMISSION_REJECT", positive_score="", predicted_label="", result_ns="", result_clock_domain="", observed_until_ns="20000", wire_bytes="0")
        full = self.fixture.run()["pooled_by_representation"]["full"]
        self.assertEqual((full["generated"], full["scored"], full["correct"]), (4, 3, 3))
        self.assertEqual(full["timely_correct_per_generated"]["estimate"], 0.75)
        self.assertEqual(full["timing_categories"]["terminal_rejection"], 1)

    def test_information_only_missing_values_are_bounded_and_unknown_costs_stay_null(self):
        self.fixture.row("full").update(status="missing", positive_score="", predicted_label="", information_bytes="", padding_bytes="", payload_bytes="", representation_sha256="", payload_sha256="")
        full = self.fixture.run()["pooled_by_representation"]["full"]
        self.assertIsNone(full["correct_per_generated"]["estimate"])
        self.assertEqual((full["correct_per_generated"]["lower"], full["correct_per_generated"]["upper"]), (0.75, 1.0))
        self.assertIsNone(full["byte_costs"]["payload_bytes"]["total"])
        self.assertEqual(full["byte_costs"]["payload_bytes"]["known_total"], 96)

    def test_no_interval_with_one_independent_group_and_undefined_metrics_are_null(self):
        for source in self.fixture.corpus[2:]:
            source["group_id"] = "SYNTHETIC_G1"
        for occurrence in self.fixture.occurrences:
            occurrence["group_id"] = "SYNTHETIC_G1"
        result = self.fixture.run()
        comparison = result["paired_group_comparisons"][0]
        self.assertIsNotNone(comparison["estimate"])
        self.assertIsNone(comparison["percentile_interval"])
        self.assertEqual(comparison["interval_unavailable_reason"], "fewer_than_two_independent_groups")
        self.assertIsNone(result["pooled_by_representation"]["alert"]["scored_only_binary_metrics"]["precision"])

    def test_duplicate_or_missing_representation_rows_fail(self):
        original = [dict(row) for row in self.fixture.predictions]
        self.fixture.predictions.append(dict(original[0]))
        self.assert_rejected("Duplicate prediction")
        self.fixture.predictions = original[:-1]
        self.assert_rejected("Exactly three")

    def test_truth_source_hash_split_and_artifact_identity_mismatches_fail(self):
        for field, value, message in (("truth_label", "wrong", "truth_label"), ("split", "train", "split mismatch"), ("source_feature_sha256", digest("wrong"), "source_feature"), ("encoder_id", "wrong", "Encoder identity"), ("model_id", "wrong", "Model identity"), ("threshold_id", "wrong", "Threshold identity")):
            with self.subTest(field=field):
                row = self.fixture.row("full")
                old = row[field]
                row[field] = value
                self.assert_rejected(message)
                row[field] = old

    def test_duplicate_group_and_source_feature_leakage_fail_but_encoded_duplicates_do_not(self):
        # Every fixture row already has identical encoded hashes; that is valid.
        self.fixture.run()
        self.fixture.groups.append({"group_id": "SYNTHETIC_G1", "split": "train"})
        self.assert_rejected("Duplicate/multiple-split group")
        self.fixture.groups.pop()
        self.fixture.corpus[1]["source_feature_sha256"] = self.fixture.corpus[0]["source_feature_sha256"]
        self.assert_rejected("across dataset splits")

    def test_missing_feature_hashes_report_audit_coverage_not_no_leakage(self):
        self.fixture.corpus[0]["source_feature_sha256"] = ""
        result = self.fixture.run()
        self.assertEqual(result["leakage_audit"]["coverage_by_split"]["train"]["coverage"], 0)
        self.assertEqual(result["leakage_audit"]["near_duplicate_audit"]["status"], "not_performed")

    def test_threshold_output_and_nonfinite_scores_rejected(self):
        row = self.fixture.row("full")
        row["positive_score"] = "0.5"
        self.assert_rejected("frozen threshold")
        for value in ("nan", "inf", "-inf", "1.1"):
            row["positive_score"] = value
            self.assert_rejected("score")

    def test_same_clock_result_order_horizon_and_simulated_time_guards(self):
        self.fixture.transport()
        row = self.fixture.row("full")
        for field, value, message in (("result_clock_domain", "SYNTHETIC_OTHER_HOST", "same-domain"), ("result_ns", "9999", "precedes creation"), ("observed_until_ns", "10000", "after the observation horizon"), ("observation_clock_domain", "SYNTHETIC_OTHER_HOST", "horizon/clock"), ("time_source", "simulated", "never simulated")):
            with self.subTest(field=field):
                old = row[field]
                row[field] = value
                self.assert_rejected(message)
                row[field] = old

    def test_information_phase_cannot_accept_transport_fields(self):
        self.fixture.row("full")["created_ns"] = "1"
        self.assert_rejected("information_only forbids timing")

    def test_byte_accounting_partial_costs_and_unobserved_result_timestamps_fail(self):
        row = self.fixture.row("full")
        for field, value, message in (("payload_bytes", "99", "Information\\+padding"), ("padding_bytes", "-1", "nonnegative"), ("information_bytes", "nan", "nonnegative"), ("payload_bytes", "", "all known or all blank")):
            old = row[field]
            row[field] = value
            self.assert_rejected(message)
            row[field] = old
        self.fixture.transport()
        row.update(status="missing", positive_score="", predicted_label="")
        self.assert_rejected("Non-returned row has result timestamp")

    def test_protocol_hash_artifact_hash_unknown_schema_and_bootstrap_override_fail(self):
        self.fixture.save()
        self.fixture.paths["occurrences"].write_text(self.fixture.paths["occurrences"].read_text() + "\n")
        with self.assertRaisesRegex(scoring.ContractError, "manifest SHA-256 mismatch"):
            scoring.score_study(self.fixture.protocol_path, self.fixture.paths, allow_synthetic_fixture=True)
        self.fixture.save()
        with self.assertRaisesRegex(scoring.ContractError, "differs from frozen"):
            scoring.score_study(self.fixture.protocol_path, self.fixture.paths, allow_synthetic_fixture=True, bootstrap_seed=1)
        self.fixture.protocol["unexpected"] = "not allowed"
        self.assert_rejected("expected keys")
        self.fixture.protocol.pop("unexpected")
        artifact = self.fixture.root / self.fixture.protocol["artifacts"]["model"]["path"]
        artifact.write_bytes(b"SYNTHETIC_TAMPERED_ARTIFACT")
        self.assert_rejected("artifact model: SHA-256 mismatch")

    def test_synthetic_cli_opt_in_and_no_output_on_schema_failure(self):
        self.fixture.save()
        output = self.fixture.root / "SYNTHETIC_FIXTURE_result.json"
        command = [sys.executable, str(MODULE_ROOT / "score_evidence_value.py"), "--protocol", str(self.fixture.protocol_path), "--output", str(output)]
        for name, path in self.fixture.paths.items():
            command += ["--" + name, str(path)]
        failed = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(failed.returncode, 2)
        self.assertFalse(output.exists())
        successful = subprocess.run(command + ["--allow-synthetic-fixture"], capture_output=True, text=True)
        self.assertEqual(successful.returncode, 0, successful.stderr)
        self.assertEqual(json.loads(output.read_text())["data_origin"], "SYNTHETIC_FIXTURE")
        before = output.read_bytes()
        again = subprocess.run(command + ["--allow-synthetic-fixture"], capture_output=True, text=True)
        self.assertEqual(again.returncode, 2)
        self.assertEqual(output.read_bytes(), before)

    def test_duplicate_json_keys_and_nonfinite_protocol_numbers_fail_closed(self):
        self.fixture.save()
        original = self.fixture.protocol_path.read_text()
        self.fixture.protocol_path.write_text(original[:-1] + ', "study_id": "duplicate"}')
        with self.assertRaisesRegex(scoring.ContractError, "duplicate JSON key"):
            scoring.score_study(self.fixture.protocol_path, self.fixture.paths, allow_synthetic_fixture=True)
        self.fixture.protocol["analysis"]["bootstrap"]["confidence"] = float("nan")
        self.assert_rejected("nonfinite")


if __name__ == "__main__":
    unittest.main()
