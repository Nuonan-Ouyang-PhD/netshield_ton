#!/usr/bin/env python3
"""Analytical counterexamples and endpoint checks for the explicit model."""

import unittest

from run_contention_validation import FULL_BYTES, make_jobs, run_case, select_jobs, simulate


def case(profile="zero", backlog=0, cap=2 * FULL_BYTES):
    return {
        "case_id": "unit", "n": 3, "capacity": "mid", "capacity_bytes": cap,
        "capacity_ratio_numerator": 2, "capacity_ratio_denominator": 3,
        "backlog": "test", "backlog_bytes": backlog, "profile": profile,
    }


class ModelCounterexamples(unittest.TestCase):
    def test_three_isolated_safe_uploads_exceed_shared_deadline(self):
        summary, events, _ = run_case(case(), "isolated_precheck")
        self.assertEqual(summary["selected_new_events"], 3)
        self.assertEqual({event["isolated_result_estimate_ticks"] for event in events}, {500})
        self.assertEqual({event["upload_done_tick"] for event in events}, {1500})
        self.assertEqual(summary["timely_results"], 0)

    def test_exact_byte_boundary_is_inclusive_without_overheads(self):
        summary, events, _ = run_case(case(), "new_bytes_only")
        self.assertEqual(summary["selected_new_events"], 2)
        self.assertEqual({event["result_return_tick"] for event in events if event["selected"]}, {1000})
        self.assertEqual(summary["timely_results"], 2)

    def test_backlog_breaks_new_bytes_only_condition(self):
        new_only, _, _ = run_case(case(backlog=FULL_BYTES), "new_bytes_only")
        backlog_aware, _, _ = run_case(case(backlog=FULL_BYTES), "backlog_aware")
        self.assertEqual(new_only["selected_new_events"], 2)
        self.assertEqual(new_only["timely_results"], 0)
        self.assertEqual(new_only["max_result_tick"], 1500)
        self.assertEqual(backlog_aware["selected_new_events"], 1)
        self.assertEqual(backlog_aware["timely_results"], 1)
        self.assertEqual(backlog_aware["max_result_tick"], 1000)

    def test_compute_and_serial_core_are_not_upload_completion(self):
        summary, events, _ = run_case(case("assumed_homogeneous"), "new_bytes_only")
        selected = [event for event in events if event["selected"]]
        self.assertEqual(summary["selected_new_events"], 2)
        self.assertEqual({event["upload_done_tick"] for event in selected}, {1060})
        self.assertEqual([event["result_return_tick"] for event in selected], [1120, 1155])
        self.assertEqual(summary["timely_results"], 0)

    def test_deadline_reservation_rechecks_shared_pipeline(self):
        summary, events, _ = run_case(case("assumed_homogeneous"), "deadline_reservation")
        self.assertEqual(summary["selected_new_events"], 1)
        self.assertEqual(summary["timely_results"], 1)
        self.assertEqual([event["result_return_tick"] for event in events if event["selected"]], [620])
        self.assertEqual([event["admission_reason"] for event in events if not event["selected"]],
                         ["shared_pipeline_deadline_exceeded", "shared_pipeline_deadline_exceeded"])

    def test_idle_service_is_not_banked(self):
        _, candidates = make_jobs(1, FULL_BYTES, 0, "zero")
        job = candidates[0]
        job["selected"] = 1
        job["network_ready_tick"] = 600
        job["detector_compute_ticks"] = 600
        events, _ = simulate([job], FULL_BYTES)
        self.assertEqual(events[0]["upload_done_tick"], 1600)

    def test_heterogeneous_core_runs_in_arrival_order_without_overlap(self):
        _, events, _ = run_case(case("assumed_heterogeneous"), "isolated_precheck")
        selected = sorted((e for e in events if e["selected"]), key=lambda e: (e["core_ready_tick"], e["event_id"]))
        for event in selected:
            self.assertGreaterEqual(event["core_start_tick"], event["core_ready_tick"])
            self.assertEqual(event["core_done_tick"] - event["core_start_tick"], event["core_compute_ticks"])
            self.assertEqual(event["result_return_tick"] - event["core_done_tick"], event["return_ticks"])
        for before, after in zip(selected, selected[1:]):
            self.assertGreaterEqual(after["core_start_tick"], before["core_done_tick"])

    def test_backlog_over_one_round_admits_no_new_work(self):
        summary, _, _ = run_case(case(backlog=2 * FULL_BYTES + 1), "backlog_aware")
        self.assertEqual(summary["selected_new_events"], 0)

    def test_unmodeled_extra_latency_invalidates_a_model_deadline_pass(self):
        background, candidates = make_jobs(3, 2 * FULL_BYTES, 0, "zero")
        chosen = select_jobs(background, candidates, 2 * FULL_BYTES, "deadline_reservation")
        self.assertEqual(sum(job["selected"] for job in chosen), 2)
        # The modeled jobs finish exactly at the deadline. An unmodeled
        # one-ms return delay is enough to break the result guarantee.
        for job in chosen:
            job["return_ticks"] = 1
        actual, _ = simulate(background + chosen, 2 * FULL_BYTES)
        admitted = [job for job in actual if job["selected"]]
        self.assertEqual([job["result_return_tick"] for job in admitted], [1001, 1001])
        self.assertEqual(sum(job["result_on_time"] for job in admitted), 0)


if __name__ == "__main__":
    unittest.main()
