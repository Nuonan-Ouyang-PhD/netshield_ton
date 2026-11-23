"""Opt-in submit/decide checks against a private patched RC1 runtime.

All times, proposals and calibration values below are synthetic. No devices
are contacted. The archived 72cc05d receipt belongs to its archived source.
"""
import asyncio
import hashlib
import itertools
import json
import sys
import tempfile
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch


def fixture_profile(module):
    return dict(schema_version=2, phase="calibration", campaign="TON_EXT_STAGE_TEST_FIXTURE_CAL",
        workers=1, basis="synthetic_fixture", clock_policy="within_host_intervals_only",
        estimator="per_condition_componentwise_observed_maximum", margin_ns=10,
        controller_sha256=hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest(),
        scope=dict(devices=list(module.DEVICES), payload_bytes=131072, capacity_bytes_per_round=262144,
                   deadline_ns=1000000000, initial_core_executing_jobs=0, initial_core_queued_complete_jobs=0),
        envelopes=[dict(backlog_by_probe_bytes=dict(zip(module.DEVICES, backlog)), selected_devices=list(selected),
            observed_batches=1, proposal_transit_ns=10, dispatch_compute_upload_ns=100,
            fallback_compute_ns=0, core_per_job_ns=100, return_ns=10)
            for backlog in module.BACKLOGS for selected in module.subsets()])


def exercise(runtime, scratch):
    sys.path.insert(0, str(runtime))
    import netshield.core as core_module
    from netshield import stage_admission
    from netshield.config import load_experiment
    from netshield.core import Coordinator
    from netshield.common import package_tree_sha256
    cfg = replace(load_experiment(runtime / "configs/hr01_low.json"),
        experiment_id="TON_EXT_STAGE_TEST_ONLY", app_capacity_bps=2097152,
        window_seconds=1, deadline_ms=1000, shared_efficiency=1)
    roles = ["P1", "P2", "P3"]
    data = json.dumps(fixture_profile(stage_admission)).encode()
    (scratch / "fixture.json").write_bytes(data)
    conf = scratch / "args.json"
    conf.write_text(json.dumps({"stage_profile": {"file": "fixture.json",
        "sha256": hashlib.sha256(data).hexdigest()}}))
    cases = []

    def trial(mode, queued, slack, expected, *, capture=roles, old_slack=None):
        output = scratch / ("case_" + str(len(cases)))
        output.mkdir()
        core = Coordinator(replace(cfg, method=mode, stage_capture_devices=capture),
                           output, config_path=str(conf))
        # Fixed priority and one synthetic core clock make the small-ns
        # reservation counterexample exercise the real submit/decide path.
        core._tiebreak_base_order = lambda devices: roles[:]

        async def go():
            calls = []
            for i, device in enumerate(roles):
                candidates = [dict(action_id=aid, utility=1, predicted_compute_ms=0, predicted_core_ms=0,
                    detector="heavy", execution=ex, evidence=ev, safe=True, unsafe_reasons=[], payload_bytes=n)
                    for aid, ex, ev, n in (("H_FULL", "core", "full", 131072), ("H_NONE", "local", "none", 0))]
                rem = queued[i]
                fifo = []
                if rem:
                    key = device + "_old"
                    fifo = [dict(key=key, remaining=rem,
                                 slack_ns=(old_slack[i] if old_slack is not None else 10**9))]
                    core.segment_buffers[key] = {"received": 131072 - rem}
                calls.append(core.submit(dict(device_id=device, window_index=0, queue_bytes=rem,
                    candidates=candidates, stage={"key": device + "_new", "sample_probe_ns": 0,
                    "origin_clock_id": device + "_synthetic_epoch", "slack_ns": slack[i], "fifo": fifo})))
            return await asyncio.wait_for(asyncio.gather(*calls), timeout=5)

        with patch.object(core_module, "monotonic_ns", return_value=0):
            results = asyncio.run(go())
        selected = [d for d, result in zip(roles, results) if result["action"]["action_id"] == "H_FULL"]
        if selected != expected:
            raise ValueError(f"{mode}: got {selected}, expected {expected}")
        if sum(result["grant_bytes"] for result in results) > 262144:
            raise ValueError("grant cap")
        if mode == "causal_shared_stage":
            demand = [rem + (131072 if d in selected else 0) for rem, d in zip(queued, roles)]
            if sum(demand) <= 262144 and [r["grant_bytes"] for r in results] != demand:
                raise ValueError("in-scope accepted/backlog bytes were not fully granted")
        cases.append(dict(method=mode, queued=queued, selected=selected, submit_decide=True))

    for backlog in ([0, 0, 0], [43691, 43691, 43690]):
        for size in range(4):
            for selected in itertools.combinations(roles, size):
                trial("instrumented_fixed_full_capture", backlog, [10**9]*3, list(selected), capture=selected)
    for mode in ("isolated_precheck_new_bytes", "backlog_aware_bytes", "causal_shared_stage"):
        trial(mode, [0]*3, [10**9]*3, roles[:2])
        trial(mode, [43691,43691,43690], [10**9]*3,
              roles[:2] if mode == "isolated_precheck_new_bytes" else roles[:1])
    trial("causal_shared_stage", [0]*3, [0]*3, [])
    trial("causal_shared_stage", [0]*3, [300,1000,1000], ["P1"])
    trial("causal_shared_stage", [43691,43691,43690], [10**9]*3, [], old_slack=[200,1000,1000])
    trial("causal_shared_stage", [1,0,0], [10**9]*3, [])
    print(json.dumps(dict(status="PASS_SYNTHETIC_PRIVATE_RUNTIME_ADAPTER_ONLY",
        submit_decide_cases=len(cases), direct_selector_only_cases=0,
        synthetic_clock_and_profile=True, tree=package_tree_sha256(),
        runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), cases=cases)))


if __name__ == "__main__":
    with tempfile.TemporaryDirectory(dir=sys.argv[2]) as d:
        exercise(Path(sys.argv[1]).resolve(), Path(d))
