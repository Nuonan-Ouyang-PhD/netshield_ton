"""Offline-only planner gates and balance tests; never connect to hardware."""

import copy
import json
import tempfile
import unittest
from collections import Counter
from pathlib import Path

import plan_hardware as planner


HERE = Path(__file__).resolve().parent


class HardwarePlanTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ton_hw_plan_test_")
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.protocol_path = HERE / "protocol.json"
        self.protocol = planner.read_json(self.protocol_path)

    def save_json(self, name, value):
        path = self.directory / name
        path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
        return path

    def draft(self, **changes):
        args = dict(study="shared_stage", phase="pilot", blocks=1,
                    order_seed=17, campaign_id="TON_EXT_STAGE_UNIT_TEST")
        args.update(changes)
        return planner.make_plan(self.protocol_path, **args)

    def test_fixed_study_matrices_and_invalid_numerical_configuration(self):
        self.assertEqual(len(planner.conditions_for(self.protocol, "allocator", "pilot", False)), 2)
        self.assertEqual(len(planner.conditions_for(self.protocol, "allocator", "pilot", True)), 4)
        self.assertEqual(len(planner.conditions_for(self.protocol, "shared_stage", "pilot", False)), 6)
        self.assertEqual(len(planner.conditions_for(self.protocol, "shared_stage", "calibration", False)), 16)
        for mutation in ("float_capacity", "wrong_backlog", "wrong_window_count"):
            with self.subTest(mutation=mutation):
                protocol = copy.deepcopy(self.protocol)
                if mutation == "float_capacity":
                    protocol["capacity_bytes_per_round"]["mid"] = 262144.0
                elif mutation == "wrong_backlog":
                    protocol["shared_stage"]["backlog_by_probe_bytes"]["131072"]["P3"] += 1
                else:
                    protocol["measured_rounds"] = 89
                with self.assertRaises(planner.PlanError):
                    planner.validate_protocol(protocol)
        with self.assertRaises(planner.PlanError):
            self.draft(blocks=0)
        with self.assertRaises(planner.PlanError):
            self.draft(campaign_id="NSF12_CRFA_20260913")

    def test_complete_crossover_cycles_balance_every_position_and_directed_pair(self):
        for size in (2, 4, 6, 16):
            with self.subTest(size=size):
                names = [f"C{i}" for i in range(size)]
                conditions = [{"condition_id": name} for name in names]
                schedules = planner.ordered_blocks(conditions, 2 * size, 37)
                self.assertEqual(schedules, planner.ordered_blocks(conditions, 2 * size, 37))
                for order in schedules:
                    self.assertEqual(Counter(order), Counter(names))
                for position in range(size):
                    self.assertEqual(Counter(order[position] for order in schedules), Counter({name: 2 for name in names}))
                pairs = Counter(pair for order in schedules for pair in zip(order, order[1:]))
                self.assertEqual(pairs, Counter({(a, b): 2 for a in names for b in names if a != b}))

    def test_calibration_covers_every_selection_without_dropping_fallback_probes(self):
        conditions = planner.conditions_for(self.protocol, "shared_stage", "calibration", False)
        expected = {(), ("P1",), ("P2",), ("P3",), ("P1", "P2"),
                    ("P1", "P3"), ("P2", "P3"), ("P1", "P2", "P3")}
        self.assertEqual(len({row["condition_id"] for row in conditions}), 16)
        for backlog in (0, 131072):
            rows = [row for row in conditions if row["backlog_bytes"] == backlog]
            self.assertEqual({tuple(row["stage_capture_devices"]) for row in rows}, expected)
            self.assertTrue(all(row["candidate_probes"] == ["P1", "P2", "P3"] for row in rows))
        plan, order, _ = self.draft(phase="calibration")
        self.assertEqual(len(order), 16)
        self.assertTrue(all(row["planned_new_measured_occurrences"] == 270 for row in order))
        self.assertEqual(sorted(row["planned_forced_full_requests"] for row in order),
                         sorted([0, 90, 90, 90, 180, 180, 180, 270] * 2))
        self.assertEqual(plan["physical_arms_executed"], 0)
        incomplete = copy.deepcopy(self.protocol)
        incomplete["shared_stage"]["calibration_capture_batches"].remove(["P1", "P2"])
        with self.assertRaises(planner.PlanError):
            planner.validate_protocol(incomplete)

    def test_partial_cycles_report_partial_balance_without_inventing_replicates(self):
        plan, order, qualification = self.draft(blocks=5)
        self.assertEqual(plan["status"], "PLANNED_NOT_EXECUTED")
        self.assertFalse(plan["ordering_balance"]["exact_position_and_transition_balance"])
        self.assertEqual(plan["ordering_balance"]["partial_cycle_blocks"], 5)
        self.assertLessEqual(plan["ordering_balance"]["maximum_within_condition_position_count_spread"], 1)
        self.assertEqual(len(order), 30)
        self.assertEqual(len({row["session_id"] for row in order}), 5)
        self.assertTrue(all(row["session_id"].startswith("TON_EXT_STAGE_UNIT_TEST_PILOT_") for row in order))
        self.assertEqual(plan["physical_arms_executed"], 0)
        self.assertIsNone(plan["observed_results"])
        self.assertTrue(qualification["status"].startswith("BLOCKED"))

    def test_boolean_attestations_without_valid_artifact_hashes_do_not_qualify(self):
        template = planner.read_json(HERE / "qualification_template.json")
        template["facts"] = dict.fromkeys(template["facts"], True)
        qpath = self.save_json("qualification.json", template)
        report = planner.qualification_report(qpath, "shared_stage", "pilot")
        self.assertTrue(report["status"].startswith("BLOCKED"))
        evidence = self.directory / "review.txt"
        evidence.write_text("UNIT TEST artifact; no hardware/source review occurred.\n")
        template["evidence"]["runtime_inventory"] = {"path": evidence.name, "sha256": planner.digest(evidence)}
        self.save_json("qualification.json", template)
        report = planner.qualification_report(qpath, "shared_stage", "pilot")
        self.assertTrue(next(r for r in report["checks"] if r["evidence_name"] == "runtime_inventory")["artifact_hash_verified"])
        evidence.write_text("UNIT TEST changed content\n")
        report = planner.qualification_report(qpath, "shared_stage", "pilot")
        self.assertFalse(next(r for r in report["checks"] if r["evidence_name"] == "runtime_inventory")["artifact_hash_verified"])

    def test_unaffected_private_allocator_requires_evidence_and_schedules_no_runs(self):
        template = planner.read_json(HERE / "qualification_template.json")
        template["facts"]["deployed_allocator_affected"] = False
        qpath = self.save_json("qualification.json", template)
        plan, order, _ = self.draft(study="allocator", campaign_id="TON_EXT_ALLOC_UNIT_TEST", qualification_path=qpath)
        self.assertTrue(plan["execution_qualification"].startswith("BLOCKED"))
        self.assertEqual(len(order), 2)
        evidence = self.directory / "inspection.txt"
        evidence.write_text("UNIT TEST only: pretend inspected allocator is unaffected.\n")
        template["evidence"]["deployed_allocator_inspection"] = {"path": evidence.name, "sha256": planner.digest(evidence)}
        self.save_json("qualification.json", template)
        plan, order, _ = self.draft(study="allocator", campaign_id="TON_EXT_ALLOC_UNIT_TEST", qualification_path=qpath)
        self.assertEqual(plan["execution_qualification"], "NOT_NEEDED_DEPLOYED_ALLOCATOR_UNAFFECTED")
        self.assertEqual(order, [])
        self.assertEqual(plan["physical_arms_executed"], 0)

    def formal_fixture(self, study="shared_stage"):
        # All artifacts below exist only in a disposable unit-test directory.
        # They test binding mechanics; they are never real qualifications.
        template = planner.read_json(HERE / "qualification_template.json")
        template["facts"] = dict.fromkeys(template["facts"], True)
        for name in template["evidence"]:
            if name == "formal_freeze":
                continue
            path = self.directory / f"{name}.txt"
            path.write_text(f"UNIT TEST binding artifact {name}; no real study.\n")
            template["evidence"][name] = {"path": path.name, "sha256": planner.digest(path)}
        pilot_sha = template["evidence"]["pilot_report"]["sha256"]
        campaign = "TON_EXT_STAGE_UNIT_TEST" if study == "shared_stage" else "TON_EXT_ALLOC_UNIT_TEST"
        rule = {
            "schema_version": 1, "status": "FROZEN_SAMPLE_SIZE_RULE", "study": study, "rule": "fixed_complete_blocks", "formal_blocks": 6,
            "rationale": "UNIT TEST: fixed count used only to test bindings, not a scientific recommendation.",
            "pilot_campaign_id": campaign + "_PILOT", "pilot_report_sha256": pilot_sha,
            "formal_outcome_peeking_for_stopping": False, "independent_unit": "fresh_physical_complete_condition_block",
        }
        rule_path = self.save_json("sample_rule.json", rule)
        conditions = planner.conditions_for(self.protocol, study, "formal", False)
        schedule = planner.ordered_blocks(conditions, 6, 17)
        freeze = {
            "schema_version": 1, "status": "FROZEN_FOR_FORMAL_EXECUTION", "study": study,
            "campaign_id": campaign, "formal_blocks": 6, "order_seed": 17, "include_mid_control": False,
            "planner_source_sha256": planner.digest(HERE / "plan_hardware.py"),
            "raw_schema_sha256": planner.digest(HERE / "raw_ledger_schema.json"),
            "condition_order_sha256": planner.canonical_digest(schedule),
            "protocol_sha256": planner.digest(self.protocol_path), "sample_size_rule_sha256": planner.digest(rule_path),
            "pilot_campaign_id": rule["pilot_campaign_id"], "pilot_report_sha256": pilot_sha,
            "qualification_evidence_sha256": {name: record["sha256"] for name, record in template["evidence"].items() if name != "formal_freeze"},
        }
        freeze_path = self.save_json("formal_freeze.json", freeze)
        template["evidence"]["formal_freeze"] = {"path": freeze_path.name, "sha256": planner.digest(freeze_path)}
        qpath = self.save_json("qualification.json", template)
        return qpath, rule_path, freeze_path, template, freeze

    def test_formal_plan_binds_exact_rule_pilot_protocol_and_review_artifacts(self):
        qpath, rule_path, freeze_path, template, freeze = self.formal_fixture()
        args = dict(phase="formal", blocks=6, qualification_path=qpath, sample_size_path=rule_path)
        plan, _, qualification = self.draft(**args)
        self.assertEqual(plan["execution_qualification"], "QUALIFIED_FOR_EXECUTION_BY_EXTERNAL_RUNNER")
        self.assertTrue(qualification["formal_bindings"]["qualified"])
        self.assertEqual(plan["physical_arms_executed"], 0)
        self.assertIsNone(plan["observed_results"])
        freeze["campaign_id"] = "TON_EXT_STAGE_STALE_OTHER_STUDY"
        self.save_json(freeze_path.name, freeze)
        template["evidence"]["formal_freeze"]["sha256"] = planner.digest(freeze_path)
        self.save_json(qpath.name, template)
        plan, _, qualification = self.draft(**args)
        self.assertEqual(plan["execution_qualification"], "BLOCKED_FORMAL_FREEZE_BINDINGS")
        self.assertIn("campaign_id", qualification["formal_bindings"]["mismatched_bindings"])
        with self.assertRaises(planner.PlanError):
            self.draft(**{**args, "blocks": 5})
        rule = planner.read_json(rule_path)
        rule["formal_outcome_peeking_for_stopping"] = True
        self.save_json(rule_path.name, rule)
        with self.assertRaises(planner.PlanError):
            self.draft(**args)

    def test_formal_schedule_seed_and_optional_control_cannot_change_after_freeze(self):
        qpath, rule_path, _, _, _ = self.formal_fixture("allocator")
        args = dict(study="allocator", campaign_id="TON_EXT_ALLOC_UNIT_TEST", phase="formal", blocks=6,
                    qualification_path=qpath, sample_size_path=rule_path)
        plan, _, _ = self.draft(**args)
        self.assertEqual(plan["execution_qualification"], "QUALIFIED_FOR_EXECUTION_BY_EXTERNAL_RUNNER")
        for change in ({"order_seed": 18}, {"include_mid_control": True}):
            with self.subTest(change=change):
                plan, _, report = self.draft(**{**args, **change})
                self.assertEqual(plan["execution_qualification"], "BLOCKED_FORMAL_FREEZE_BINDINGS")
                self.assertIn(next(iter(change)), report["formal_bindings"]["mismatched_bindings"])

    def test_existing_plan_or_evidence_directory_is_never_overwritten(self):
        plan, order, qualification = self.draft()
        output = self.directory / "plan"
        planner.write_plan(output, plan, order, qualification)
        before = {path.name: path.read_bytes() for path in output.iterdir()}
        with self.assertRaises(planner.PlanError):
            planner.write_plan(output, plan, order, qualification)
        self.assertEqual(before, {path.name: path.read_bytes() for path in output.iterdir()})

    def test_raw_contract_keeps_clock_domains_and_attempts_explicit(self):
        schema = planner.read_json(HERE / "raw_ledger_schema.json")
        self.assertEqual(set(schema["$defs"]), {"event", "service", "transport_chunk", "admission", "attempt"})
        event = schema["$defs"]["event"]["properties"]
        self.assertIn("origin_clock_id", event)
        self.assertIn("core_clock_id", event)
        self.assertIn("result_received_origin_ns", event)
        self.assertIn("observed_through_origin_ns", event)
        self.assertIn("missing_timestamp_reasons", event)
        service = schema["$defs"]["service"]["properties"]
        self.assertIn("service_granted_bytes", service)
        self.assertIn("actual_unique_application_service_bytes", service)


if __name__ == "__main__":
    unittest.main()
