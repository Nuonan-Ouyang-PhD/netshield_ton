"""Public regressions for allocator, admission and upload-metric semantics.

Only transparent synthetic action fixtures are used. These tests do not
replay a hardware campaign or certify Wi-Fi/core-result deadlines.
"""

from __future__ import annotations

import itertools
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from supporting_material.methodology_repair import run_methodology_repair as driver
from supporting_material.methodology_repair.simulation_primitives import (
    admission_budget, isolated_latency_ms, same_round_upload_feasible,
    upload_on_time, waterfill,
)


def synthetic_actions() -> list[dict]:
    return [
        {"id": name, "detector": "heavy", "execution": "core" if evidence == "full" else "local",
         "evidence": evidence, "payload": payload, "utility": utility,
         "compute_ms": dict.fromkeys(driver.DEVICES, 0), "core_ms": 0}
        for name, evidence, payload, utility in (
            ("H_NONE", "none", 0, 0.8),
            ("H_SUMMARY", "summary", 16384, 0.9),
            ("H_FULL", "full", 131072, 1.0),
        )
    ]


class IntegerServiceTests(unittest.TestCase):
    def test_residual_bytes_are_not_lost(self):
        demands = {"P1": 131072, "P2": 131072, "P3": 131072}
        for cap in (1, 2, 131072, 262144, 393216):
            grants = waterfill(demands, cap)
            self.assertEqual(sum(grants.values()), cap)
            self.assertLessEqual(max(grants.values()) - min(grants.values()), 1)

    def test_saturation_redistributes_unused_shares(self):
        self.assertEqual(waterfill({"A": 1, "B": 100, "C": 100}, 100), {"A": 1, "B": 50, "C": 49})
        self.assertEqual(waterfill({"A": 0, "B": 2}, 99), {"A": 0, "B": 2})
        self.assertEqual(waterfill({}, 10), {})

    def test_rotated_residual_priority_balances_three_intervals(self):
        totals = dict.fromkeys(("P1", "P2", "P3"), 0)
        for interval in range(3):
            for device, grant in waterfill(dict.fromkeys(totals, 10), 2, tie_offset=interval).items():
                totals[device] += grant
        self.assertEqual(totals, {"P1": 2, "P2": 2, "P3": 2})

    def test_exhaustive_integer_conservation_and_max_min_fairness(self):
        # Demand saturation and all residual counts are checked independently
        # of the implementation using conservation and max-min conditions.
        for values in itertools.product(range(5), repeat=4):
            demands = dict(zip(("A", "B", "C", "D"), values))
            for cap in range(22):
                grants = waterfill(demands, cap, tie_offset=cap)
                self.assertEqual(sum(grants.values()), min(cap, sum(values)))
                self.assertEqual(set(grants), set(demands))
                for device, grant in grants.items():
                    self.assertGreaterEqual(grant, 0)
                    self.assertLessEqual(grant, demands[device])
                    if grant < demands[device]:
                        self.assertTrue(all(other <= grant + 1 for other in grants.values()))

    def test_invalid_byte_inputs_fail_explicitly(self):
        for demands, cap in (({"P": -1}, 10), ({"P": 1.5}, 10), ({"P": 1}, -1), ({"P": 1}, 2.5), ({"P": True}, 10)):
            with self.assertRaises(ValueError):
                waterfill(demands, cap)
        with self.assertRaises(ValueError):
            waterfill({"P": 1}, 1, tie_offset=0.5)


class AdmissionAndEndpointTests(unittest.TestCase):
    def setUp(self):
        self.saved_actions = driver.ACTIONS
        driver.configure_actions(synthetic_actions())

    def tearDown(self):
        if self.saved_actions:
            driver.configure_actions(self.saved_actions)
        else:
            driver.ACTIONS, driver.ACTION_BY_ID, driver.ACTION_IDS = [], {}, ()

    def test_backlog_changes_admission_feasibility(self):
        backlog = {"P1": 131072, "P2": 0, "P3": 0}
        new = {"P1": 131072, "P2": 131072, "P3": 0}
        self.assertLessEqual(sum(new.values()), 262144)
        self.assertFalse(same_round_upload_feasible(backlog, new, 262144))
        self.assertEqual(admission_budget(262144, backlog), 131072)
        chosen = dict.fromkeys(driver.DEVICES, driver.ACTION_BY_ID["H_FULL"])
        admitted = driver.joint_admit(chosen, 262144, 2097152, False, 1, 0, existing_queues=backlog)
        self.assertTrue(same_round_upload_feasible(backlog, {d: a["payload"] for d, a in admitted.items()}, 262144))

    def test_backlog_alone_can_already_exceed_one_round(self):
        backlog = {"P1": 262145, "P2": 0, "P3": 0}
        chosen = dict.fromkeys(driver.DEVICES, driver.ACTION_BY_ID["H_FULL"])
        admitted = driver.joint_admit(chosen, 262144, 2097152, False, 1, 0, existing_queues=backlog)
        self.assertEqual(sum(a["payload"] for a in admitted.values()), 0)
        self.assertFalse(same_round_upload_feasible(backlog, {}, 262144))

    def test_isolated_precheck_is_not_shared_link_certificate(self):
        full = driver.ACTION_BY_ID["H_FULL"]
        self.assertTrue(driver.passes_isolated_latency_precheck(full, "P1", 2097152))
        self.assertEqual(isolated_latency_ms(131072, 262144), 500.0)
        self.assertFalse(same_round_upload_feasible({}, dict.fromkeys(driver.DEVICES, full["payload"]), 262144))
        self.assertEqual(sum(dict.fromkeys(driver.DEVICES, full["payload"]).values()) / 262144, 1.5)

    def test_upload_deadline_boundary_is_inclusive(self):
        self.assertTrue(upload_on_time(37, 1037))
        self.assertFalse(upload_on_time(37, 1038))
        self.assertFalse(upload_on_time(37, None))
        self.assertFalse(upload_on_time(37, 36))
        with self.assertRaises(ValueError):
            upload_on_time(-1, 0)

    def test_task_a_deduplicates_unused_seed_identities(self):
        schedule = [{"session_id": f"S{i}", "seed": i} for i in range(12)]
        with patch.object(driver, "WINDOWS", 9), patch.object(driver, "WARMUP", 3), patch.object(driver, "MEASURED", 6):
            rows = driver.task_a(schedule)
            first = driver.simulate_synchronous("synchronized_independent", "mid", 1, 1)
            second = driver.simulate_synchronous("synchronized_independent", "mid", 9876, 1)
        self.assertEqual(len(rows), 36)
        self.assertEqual(first, second)
        self.assertTrue(all(row["status"] == "PASS" and row["evaluations_per_case"] == 1 and row["independent_random_replicates"] == 0 and not row["seed_affects_decisions"] for row in rows))
        self.assertEqual(rows[0]["formal_seed_labels"], list(range(12)))

    def test_both_models_report_upload_endpoints_with_distinct_resolutions(self):
        with patch.object(driver, "WINDOWS", 4), patch.object(driver, "WARMUP", 1), patch.object(driver, "MEASURED", 3):
            coarse = driver.simulate_synchronous("central_coordinated", "mid", 1, 1)
            fine = driver.simulate_tick_baseline("central_coordinated", "mid", 1)
        for row in (coarse, fine):
            self.assertEqual(row["completion_endpoint"], "payload_upload_only")
            self.assertEqual(row["deadline_ms"], 1000)
            self.assertFalse(row["includes_detector_compute_core_inference_or_wifi_jitter"])
            self.assertNotIn("on_time_core_results", row)
            self.assertNotIn("post_release_on_time_core_result_coverage", row)
            self.assertEqual(row["allocator_cap_check_failures"], 0)
        self.assertEqual(coarse["completion_resolution_ms"], 1000)
        self.assertEqual(fine["completion_resolution_ms"], 1)

    def test_import_does_not_require_private_inputs(self):
        result = subprocess.run(
            [sys.executable, "-c", "from supporting_material.methodology_repair import run_methodology_repair as m; assert m.ACTIONS == []"],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
