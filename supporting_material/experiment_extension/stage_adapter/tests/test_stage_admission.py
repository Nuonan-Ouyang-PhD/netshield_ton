"""Synthetic control/clock/capture cases; no private runtime or devices used."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
import stage_admission as stage
import build_profile

spec = importlib.util.spec_from_file_location("private_stage_fixture",
    HERE.parent / "hardware/test_stage_runtime_adapter.py")
fixture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixture)


def snapshot(backlog=stage.BACKLOGS[0], slack=(10**9,) * 3, old_slack=None):
    proposals, buffers = {}, {}
    for index, device in enumerate(stage.DEVICES):
        remaining = backlog[index]
        fifo = []
        if remaining:
            key = device + "_old"
            fifo = [{"key": key, "remaining": remaining,
                     "slack_ns": 10**9 if old_slack is None else old_slack[index]}]
            buffers[key] = stage.PAYLOAD - remaining
        proposals[device] = {"queue_bytes": remaining, "stage_received_ns": 0,
            "stage": {"key": device + "_new", "sample_probe_ns": 999999999,
                      "origin_clock_id": device + "_synthetic_epoch",
                      "slack_ns": slack[index], "fifo": fifo}}
    return proposals, buffers


class AdmissionTests(unittest.TestCase):
    def setUp(self):
        self.profile = fixture.fixture_profile(stage)

    def select(self, backlog=stage.BACKLOGS[0], slack=(10**9,) * 3, old_slack=None, now=0):
        proposals, buffers = snapshot(backlog, slack, old_slack)
        return stage.select(proposals, list(stage.DEVICES), stage.CAPACITY, now, self.profile, buffers)

    def test_capacity_and_existing_queue_are_reserved(self):
        self.assertEqual(self.select()[0], ["P1", "P2"])
        self.assertEqual(self.select(stage.BACKLOGS[1])[0], ["P1"])

    def test_prior_reservation_is_rechecked_for_every_new_request(self):
        selected, trace = self.select(slack=(300, 1000, 1000))
        self.assertEqual(selected, ["P1"])
        self.assertEqual([t["reason"] for t in trace], ["accepted", "remaining_slack", "remaining_slack"])
        self.assertGreater(trace[0]["min_slack_after_service_ns"], 0)
        self.assertLess(trace[1]["min_slack_after_service_ns"], 0)

    def test_expired_old_work_rejects_new_work_without_erasing_old_bytes(self):
        selected, trace = self.select(stage.BACKLOGS[1], old_slack=(200, 1000, 1000))
        self.assertEqual(selected, [])
        self.assertTrue(all(t["bytes"] == 262144 for t in trace))
        self.assertTrue(all(t["backlog_only_predicted_margin_ns"] < 0 for t in trace))

    def test_zero_slack_and_core_residence_reduce_admission(self):
        self.assertEqual(self.select(slack=(0, 0, 0))[0], [])
        self.assertEqual(self.select(slack=(300, 300, 300), now=100)[0], [])

    def test_uncalibrated_organic_backlog_rejects_new_requests(self):
        selected, trace = self.select((1, 0, 0))
        self.assertEqual(selected, [])
        self.assertTrue(all(t["reason"] == "out_of_calibrated_backlog" for t in trace))

    def test_identity_prefix_and_typed_clock_corruptions_are_rejected(self):
        for mutation in ("duplicate_new", "duplicate_old", "queue", "prefix", "float", "nan", "future_clock", "future_origin"):
            with self.subTest(mutation=mutation):
                proposals, buffers = snapshot(stage.BACKLOGS[1])
                if mutation == "duplicate_new":
                    proposals["P2"]["stage"]["key"] = "P1_new"
                elif mutation == "duplicate_old":
                    proposals["P2"]["stage"]["key"] = "P1_old"
                elif mutation == "queue":
                    proposals["P1"]["queue_bytes"] += 1
                elif mutation == "prefix":
                    buffers["P1_old"] += 1
                elif mutation == "float":
                    proposals["P1"]["stage"]["slack_ns"] = 1e9
                elif mutation == "nan":
                    proposals["P1"]["stage"]["slack_ns"] = float("nan")
                elif mutation == "future_origin":
                    proposals["P1"]["stage"]["slack_ns"] = 1000000001
                else:
                    proposals["P1"]["stage_received_ns"] = 1
                with self.assertRaises(ValueError):
                    stage.select(proposals, list(stage.DEVICES), stage.CAPACITY, 0, self.profile, buffers)

    def test_profile_coverage_identity_and_fixture_isolation(self):
        for mutation in ("missing", "duplicate", "source", "same_campaign", "real_campaign"):
            with self.subTest(mutation=mutation):
                profile = copy.deepcopy(self.profile)
                campaign = "TON_EXT_STAGE_TEST_RUN"
                if mutation == "missing": profile["envelopes"].pop()
                elif mutation == "duplicate": profile["envelopes"].append(profile["envelopes"][0])
                elif mutation == "source": profile["controller_sha256"] = "0" * 64
                elif mutation == "same_campaign": campaign = profile["campaign"]
                else: campaign = "TON_EXT_STAGE_FORMAL"
                with self.assertRaises(ValueError):
                    stage.validate_profile(profile, campaign)

    def test_loader_binds_bytes_and_freezes_runtime_envelopes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            raw = json.dumps(self.profile).encode()
            (root / "profile.json").write_bytes(raw)
            config = root / "config.json"
            config.write_text(json.dumps({"stage_profile": {"file": "profile.json",
                "sha256": hashlib.sha256(raw).hexdigest()}}))
            profile, _ = stage.load_profile(config, "TON_EXT_STAGE_TEST_RUN")
            proposals, buffers = snapshot()
            self.assertEqual(stage.select(proposals, list(stage.DEVICES), stage.CAPACITY, 0, profile, buffers)[0],
                             ["P1", "P2"])
            with self.assertRaises(TypeError):
                profile.envelopes[(stage.BACKLOGS[0], ())]["return_ns"] = 0
            (root / "profile.json").write_bytes(raw + b" ")
            with self.assertRaises(ValueError):
                stage.load_profile(config, "TON_EXT_STAGE_TEST_RUN")
            physical = copy.deepcopy(self.profile)
            physical.update(basis="physical_capture", runtime_tree_sha256="1" * 64,
                source_identity={k: "1" * 64 for k in ("records_sha256", "plan_sha256", "field_map_sha256",
                    "adapter_sha256", "mapping_review_sha256")})
            raw = json.dumps(physical).encode()
            (root / "profile.json").write_bytes(raw)
            config.write_text(json.dumps({"stage_profile": {"file": "profile.json",
                "sha256": hashlib.sha256(raw).hexdigest()}}))
            with self.assertRaises(ValueError):
                stage.load_profile(config, "TON_EXT_STAGE_FORMAL", "2" * 64)
            compiled, _ = stage.load_profile(config, "TON_EXT_STAGE_FORMAL", "1" * 64)
            self.assertIsInstance(compiled, stage.CompiledProfile)

    def test_optimized_python_does_not_disable_snapshot_checks(self):
        code = "import stage_admission as s; s.validate_snapshot({}, [], 262144, 0, {})"
        result = subprocess.run([sys.executable, "-B", "-O", "-c", code], cwd=HERE,
                                capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ValueError: stage device/priority configuration", result.stderr)


class CaptureTests(unittest.TestCase):
    """Fake measurements test parsing/accounting only, never physical validity."""
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.plan = {"study": "shared_stage", "phase": "calibration", "campaign_id": "TON_EXT_STAGE_UNIT_FIXTURE",
            "execution_qualification": "QUALIFIED_FOR_EXECUTION_BY_EXTERNAL_RUNNER",
            "requested_complete_blocks": 1, "planned_arms": 16, "conditions": []}
        self.rows = []
        for backlog in stage.BACKLOGS:
            for selected in stage.subsets():
                cid = "fixture_" + str(len(self.rows))
                condition = {"condition_id": cid, "backlog_by_probe_bytes": dict(zip(stage.DEVICES, backlog)),
                    "stage_capture_devices": list(selected), "candidate_probes": list(stage.DEVICES),
                    "capacity_bytes_per_round": stage.CAPACITY, "policy": "instrumented_fixed_full_capture"}
                self.plan["conditions"].append(condition)
                row = dict(campaign_id=self.plan["campaign_id"], block=1, condition_id=cid,
                    attempt_id=cid+"_attempt", analysis_stratum="first_measured_generation_batch",
                    basis="physical_capture", core_state_before={"executing_jobs": 0, "queued_complete_jobs": 0},
                    workers=1, core_clock_id="synthetic_core_epoch", decision_core_ns=10**12,
                    last_decision_sent_core_ns=10**12+5, backlog_by_probe_bytes=condition["backlog_by_probe_bytes"],
                    selected_devices=list(selected), probes={}, jobs=[], raw_source_ids=["synthetic_only"])
                for device in stage.DEVICES:
                    # Large unrelated offsets deliberately prevent cross-host subtraction.
                    row["probes"][device] = dict(origin_clock_id="synthetic_origin_"+device,
                        proposal_sample_origin_ns=9*10**15, decision_received_origin_ns=9*10**15+10,
                        fallback_complete_origin_ns=None if device in selected else 9*10**15+20)
                for device in stage.DEVICES:
                    for kind in ("background", "new"):
                        if (kind == "background" and not condition["backlog_by_probe_bytes"][device]) or (
                            kind == "new" and device not in selected):
                            continue
                        index = len(row["jobs"])
                        remaining = stage.PAYLOAD if kind == "new" else condition["backlog_by_probe_bytes"][device]
                        row["jobs"].append(dict(device_id=device, origin_kind=kind, event_id=cid+device+kind,
                            remaining_before_bytes=remaining, received_prefix_bytes=stage.PAYLOAD-remaining,
                            payload_sha256="0"*64, core_clock_id=row["core_clock_id"],
                            origin_clock_id=row["probes"][device]["origin_clock_id"],
                            core_payload_ready_core_ns=10**12+10+index*30,
                            core_start_core_ns=10**12+11+index*30, core_end_core_ns=10**12+15+index*30,
                            core_result_send_core_ns=10**12+16+index*30,
                            result_received_origin_ns=9*10**15+40+index*30))
                self.rows.append(row)
        raw = self.root / "fake_raw.jsonl"
        raw.write_text("SYNTHETIC TEST ONLY; no physical data.\n")
        stub = {"path": raw.name, "sha256": build_profile.digest(raw)}
        self.mapping = dict(status="REVIEWED_PHYSICAL_CAPTURE_FIELD_MAP", campaign_id=self.plan["campaign_id"],
            runtime_tree_sha256="1"*64,
            frozen_margin_ns=50, mapped_fields={k: "fixture field " + k for k in build_profile.MAPPED_FIELDS},
            raw_files=[dict(source_id="synthetic_only", **stub)], adapter_source=stub, mapping_review=stub)

    def build(self):
        records, plan, mapping = [self.root/name for name in ("records.jsonl", "plan.json", "map.json")]
        records.write_text("".join(json.dumps(row)+"\n" for row in self.rows))
        plan.write_text(json.dumps(self.plan))
        mapping.write_text(json.dumps(self.mapping))
        return build_profile.build(records, plan, mapping, 50)

    def test_complete_first_batch_grid_uses_only_same_clock_durations(self):
        profile = self.build()
        self.assertEqual(len(profile["envelopes"]), 16)
        self.assertTrue(all(e["proposal_transit_ns"] == 10 for e in profile["envelopes"]))
        self.assertEqual(profile["margin_ns"], 50)
        self.assertEqual(profile["calibration_complete_blocks"], 1)
        self.assertIn("not deterministic bounds", profile["interpretation"])

    def test_missing_condition_or_missing_job_is_not_silently_dropped(self):
        for mutation in ("condition", "job"):
            with self.subTest(mutation=mutation):
                original = copy.deepcopy(self.rows)
                if mutation == "condition": self.rows.pop()
                else: self.rows[-1]["jobs"].pop()
                with self.assertRaises(ValueError): self.build()
                self.rows = original

    def test_actual_backlog_wrong_batch_and_clock_epoch_are_rejected(self):
        for mutation in ("backlog", "stratum", "epoch", "overlap"):
            with self.subTest(mutation=mutation):
                original = copy.deepcopy(self.rows)
                row = self.rows[-1]
                if mutation == "backlog": row["backlog_by_probe_bytes"]["P1"] += 1
                elif mutation == "stratum": row["analysis_stratum"] = "all_measured_generation_batches"
                elif mutation == "epoch": row["jobs"][0]["core_clock_id"] = "other_boot"
                else:
                    row["jobs"][0]["core_end_core_ns"] = row["jobs"][1]["core_start_core_ns"] + 1
                    row["jobs"][0]["core_result_send_core_ns"] = row["jobs"][0]["core_end_core_ns"]
                with self.assertRaises(ValueError): self.build()
                self.rows = original

    def test_unqualified_plan_unmapped_fields_or_changed_raw_artifact_are_rejected(self):
        for mutation in ("plan", "mapping", "raw"):
            with self.subTest(mutation=mutation):
                plan, mapping = copy.deepcopy(self.plan), copy.deepcopy(self.mapping)
                if mutation == "plan": self.plan["execution_qualification"] = "BLOCKED_MISSING_OR_UNVERIFIED_PREREQUISITES"
                elif mutation == "mapping": self.mapping["mapped_fields"].pop("core_clock_id")
                else: self.mapping["raw_files"][0]["sha256"] = "f" * 64
                with self.assertRaises(ValueError): self.build()
                self.plan, self.mapping = plan, mapping

    def test_slow_observations_are_retained_in_component_maxima(self):
        self.rows[-1]["jobs"][-1]["result_received_origin_ns"] += 10**12
        profile = self.build()
        self.assertGreater(max(e["return_ns"] for e in profile["envelopes"]), 10**12)

    def test_fallback_only_cost_is_retained_and_budgeted(self):
        self.rows[0]["probes"]["P1"]["fallback_complete_origin_ns"] += 10**12
        profile = self.build()
        envelope = next(e for e in profile["envelopes"] if not e["selected_devices"]
                        and sum(e["backlog_by_probe_bytes"].values()) == 0)
        self.assertGreater(envelope["fallback_compute_ns"], 10**12)
        # A candidate must reserve the recorded fallback cost of its unselected
        # peers; it cannot discard that component when computing full deadlines.
        fixture_profile = fixture.fixture_profile(stage)
        for row in fixture_profile["envelopes"]:
            row["fallback_compute_ns"] = 1000
        proposals, buffers = snapshot(slack=(500, 500, 500))
        self.assertEqual(stage.select(proposals, list(stage.DEVICES), stage.CAPACITY, 0,
                                      fixture_profile, buffers)[0], [])


if __name__ == "__main__":
    unittest.main()
