"""Local wire/ledger regression. Uses loopback, synthetic inputs and no physical qualification."""

import argparse
import asyncio
import json
import socket
import sys
import tarfile
from pathlib import Path
from unittest.mock import patch

from reconstruct_attempt import reconstruct


async def exercise(runtime, destination, backlog, study):
    sys.path.insert(0, str(runtime))
    from netshield import core, probe

    destination.mkdir()
    attempt = "LOCAL_FIXTURE"
    method = "backlog_aware_bytes" if study == "shared_stage" else "independent_dpp"
    campaign = (
        "TON_EXT_STAGE_LOOPBACK_ONLY"
        if study == "shared_stage"
        else "TON_EXT_ALLOC_LOOPBACK_ONLY"
    )
    config = json.loads((runtime / "configs/hr01_low.json").read_bytes())
    config.update(
        experiment_id=campaign,
        method=method,
        windows=95,
        warmup_windows=5,
        drain_windows=4,
        app_capacity_bps=2097152 if study == "shared_stage" else 1048576,
        stage_initial_backlog_bytes=backlog if study == "shared_stage" else None,
        strict_telemetry=False,
        synthetic=False,
    )
    path = destination / "fixture.json"
    path.write_text(json.dumps(config))
    row = dict(
        study=study,
        phase="pilot",
        session_id="LOCAL",
        arm_id=attempt,
        campaign_id=campaign,
        condition_id="loopback",
        capacity_bytes_per_round=config["app_capacity_bps"] // 8,
    )
    (destination / "started.json").write_text(
        json.dumps(dict(row=row, attempt=attempt))
    )
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = str(s.getsockname()[1])
    common = [
        "--config",
        str(path),
        "--port",
        port,
        "--run-id",
        attempt,
        "--session-id",
        "LOCAL",
        "--seed",
        "1",
        "--models-dir",
        str(runtime / "artifacts/portable_models"),
        "--actions",
        str(runtime / "configs/actions.frozen.json"),
    ]

    def source(device_id, *args, **kwargs):
        return (
            dict(
                event_id=f"{device_id}-{i}",
                label=i % 2,
                features=[float(i % 2)] * 39,
                window_phase="warmup" if i < 5 else "measured",
                measured_window_index=i - 5 if i >= 5 else None,
            )
            for i in range(95)
        )

    snapshot = dict(
        wifi=dict(tx_retries_delta=0),
        temperature_c=40,
        mem_available_bytes=2**30,
        tcp_retransmissions={},
        throttled_hex="0x0",
    )
    sleep = asyncio.sleep

    async def accelerated(delay):
        await sleep(min(0.001, delay))

    with (
        patch.object(probe, "make_source", source),
        patch.object(probe, "telemetry_snapshot", return_value=snapshot),
        patch.object(asyncio, "sleep", accelerated),
    ):
        server = asyncio.create_task(
            core.async_main(
                core.build_parser().parse_args(
                    [
                        *common,
                        "--host",
                        "127.0.0.1",
                        "--output",
                        str(destination / "core"),
                    ]
                )
            )
        )
        for _ in range(100):
            if server.done():
                await server
            if (destination / "core" / attempt / "manifest.json").exists():
                break
            await sleep(0.01)
        await sleep(0.05)
        agents = []
        for role in ("P1", "P2", "P3"):
            argv = probe.build_parser().parse_args(
                [
                    *common,
                    "--device-id",
                    role,
                    "--core-host",
                    "127.0.0.1",
                    "--output",
                    str(destination / role / "raw"),
                ]
            )
            agents.append(probe.async_main(argv))
        await asyncio.wait_for(asyncio.gather(server, *agents), 60)
    for role in ("P1", "P2", "P3"):
        with tarfile.open(destination / (role + ".tar"), "x") as tar:
            tar.add(destination / role / "raw", arcname="raw")
    summary = reconstruct(destination, destination / "reconstructed")
    print(
        json.dumps(
            dict(
                scope="SYNTHETIC_LOOPBACK_ONLY",
                backlog=backlog,
                generated=summary["generated"],
                physical_arms=0,
            )
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("runtime", type=Path)
    parser.add_argument("destination", type=Path)
    parser.add_argument("backlog", type=int, choices=(0, 131072))
    parser.add_argument(
        "--study", choices=("shared_stage", "allocator"), default="shared_stage"
    )
    args = parser.parse_args()
    asyncio.run(
        exercise(
            args.runtime.resolve(), args.destination.resolve(), args.backlog, args.study
        )
    )
