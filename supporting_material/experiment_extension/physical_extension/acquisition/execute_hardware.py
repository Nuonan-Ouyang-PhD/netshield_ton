"""Execute a qualified extension plan using RC1's actual Core, Probe and preflight.

Private layout: deployment.json gives the local RC1 formal_tools directory, its
Python executable, a port and blocks keyed by session_id. Each block supplies
one workload session, seed, and a bundle directory per condition. A bundle
contains netshield/, config.json, actions.json, artifacts/portable_models/ and
window_plans/<workload_session>/{manifest.json,P1.jsonl,P2.jsonl,P3.jsonl}.
All bundle files and this launcher are bound by freeze_inputs before execution.
The registry is a private directory on the external project volume.
"""

import argparse
import csv
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
import tarfile
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

from plan_hardware import make_plan

EXT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EXT))
from freeze_inputs import freeze, verify

ROLES = ("P1", "P2", "P3")


def write(path, obj):
    with path.open("x") as f:
        json.dump(obj, f, indent=2)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def files(root):
    paths = sorted(root.rglob("*"))
    require(not any(p.is_symlink() for p in paths), "bundle contains a symbolic link")
    return {p.relative_to(root).as_posix(): p for p in paths if p.is_file()}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def execute(args):
    plan = json.loads((args.plan / "plan.json").read_bytes())
    from pilot_mapping import PROTOCOL, ROOT, PROTOCOL_PATH, HOST_KEYS, backup_volume, copy_evidence
    mapping_hash=digest(PROTOCOL_PATH)
    contract=json.loads(Path(__file__).with_name("protocol.json").read_bytes())["physical_campaign"]
    require(contract["protocol_sha256"]==mapping_hash and plan["campaign_id"]==PROTOCOL["campaign_id"]
            and plan["study"]=="allocator" and plan["phase"]=="pilot"
            and plan["requested_complete_blocks"]==1 and plan["order_seed"]==PROTOCOL["order_seed"]
            and not plan["include_mid_control"],"replacement campaign scope")
    role_names={role:record["hostname"] for role,record in PROTOCOL["roles"].items()}
    rule = args.rule
    rebuilt, rows, qualification = make_plan(
        Path(__file__).with_name("protocol.json"),
        study=plan["study"],
        phase=plan["phase"],
        blocks=plan["requested_complete_blocks"],
        order_seed=plan["order_seed"],
        campaign_id=plan["campaign_id"],
        include_mid_control=plan["include_mid_control"],
        qualification_path=args.qualification,
        sample_size_path=rule,
    )
    require(
        plan == rebuilt
        and qualification["status"] == "QUALIFIED_FOR_EXECUTION_BY_EXTERNAL_RUNNER",
        "plan or current evidence does not qualify for deployment",
    )
    with (args.plan / "condition_order.csv").open() as f:
        actual = list(csv.DictReader(f))
    require(
        actual == [{k: str(v) for k, v in r.items()} for r in rows], "order mismatch"
    )
    cfg = json.loads(args.deployment.read_bytes())
    identity_path = Path(__file__).with_name("candidate_identity.json")
    identities = json.loads(identity_path.read_bytes())
    bound = dict(
        plan=args.plan / "plan.json",
        order=args.plan / "condition_order.csv",
        qualification=args.qualification,
        deployment=args.deployment,
        launcher=Path(__file__),
        candidate_identity=identity_path,
    )
    bound.update(probe_protocol=PROTOCOL_PATH, host_keys=HOST_KEYS, protocol_text=ROOT/"PROTOCOL.md",
                 design=Path(__file__).with_name("protocol.json"), plan_builder=Path(__file__).with_name("plan_hardware.py"),
                 freeze_tool=EXT/"freeze_inputs.py", paired_summary=Path(__file__).with_name("summarize_blocks.py"),
                 resume=ROOT/"run_pilot.py")
    for record in json.loads(args.qualification.read_bytes())["evidence"].values():
        path=(args.qualification.parent / record["path"]).resolve(strict=True)
        require(digest(path)==record["sha256"],"private qualification evidence changed")
        bound["evidence/"+path.name]=path
    if rule:
        bound["sample_size_rule"] = rule
    tools = Path(cfg["formal_tools"]).resolve(strict=True)
    require(tools == ROOT/"code/formal_tools","unexpected deployment transport")
    for p in tools.glob("*.py"):
        bound["tools/" + p.name] = p
    bound["analysis"] = Path(__file__).with_name("reconstruct_attempt.py")
    bundles = {}
    for r in rows:
        session, condition = r["session_id"], r["condition_id"]
        block = cfg["blocks"][session]
        root = Path(block["bundles"][condition]).resolve(strict=True)
        members = files(root)
        workload = block["workload_session"]
        require(re.fullmatch(r"[A-Za-z0-9_-]+", workload), "invalid workload session")
        require(workload==PROTOCOL["workload_session"],"unexpected workload")
        settings = json.loads(members["config.json"].read_bytes())
        method = "independent_dpp" if plan["study"] == "allocator" else r["policy"]
        require(
            settings["method"] == method
            and settings["experiment_id"] == plan["campaign_id"]
            and settings["windows"] == 95
            and settings["warmup_windows"] == 5
            and settings["drain_windows"] == 200
            and settings["window_seconds"] == 1
            and settings["deadline_ms"] == 1000
            and settings["strict_telemetry"] is True
            and settings["synthetic"] is False
            and settings["shared_efficiency"] == 1
            and settings["expected_devices"] == list(ROLES)
            and settings["app_capacity_bps"] == 8 * r["capacity_bytes_per_round"]
            and settings["seed"] == block["seed"],
            "bundle differs from protocol",
        )
        if plan["study"] == "allocator":
            require(settings["dpp_v"] == 1, "allocator queue weight")
        else:
            require(
                settings["stage_initial_backlog_bytes"] == r["initial_backlog_bytes"],
                "initial backlog",
            )
            if plan["phase"] == "calibration":
                require(
                    ",".join(settings["stage_capture_devices"])
                    == r["stage_capture_devices"],
                    "forced subset",
                )
        for role in ROLES:
            require(
                len(
                    members[f"window_plans/{workload}/{role}.jsonl"]
                    .read_bytes()
                    .splitlines()
                )
                == 95,
                "workload generation count",
            )
        # Use RC1's filename/length/content tree format, including every Python file.
        tree = hashlib.sha256()
        for filename, p in sorted(members.items()):
            if filename.startswith("netshield/") and filename.endswith(".py"):
                name = filename.removeprefix("netshield/").encode()
                data = p.read_bytes()
                for part in (name, data):
                    tree.update(len(part).to_bytes(8, "big"))
                    tree.update(part)
        variant = (
            "corrected"
            if r["allocator_variant"] == "integer_remainder_fix"
            else "original"
        )
        require(
            tree.hexdigest() == identities[variant],
            "variant differs from reviewed instrumented tree",
        )
        manifest = json.loads(
            members[
                "artifacts/portable_models/runtime_identity_manifest.json"
            ].read_bytes()
        )
        require(
            manifest["package_tree_sha256"] == tree.hexdigest(),
            "unbound runtime identity",
        )
        for model in ("light", "medium", "heavy"):
            require(
                digest(members[f"artifacts/portable_models/{model}.npz"])
                == manifest["models"][model]["sha256"],
                "model bytes differ from runtime identity",
            )
        for name, p in members.items():
            bound[f"{session}/{condition}/{name}"] = p
        bundles[r["arm_id"]] = root
    # Matching workloads, models, actions, and instrumentation within each paired block.
    for session in {r["session_id"] for r in rows}:
        group = [r for r in rows if r["session_id"] == session]
        baseline = files(bundles[group[0]["arm_id"]])

        def hashes(members):
            return {
                n: digest(p)
                for n, p in members.items()
                if n.startswith(
                    ("window_plans/", "artifacts/portable_models/", "netshield/")
                )
                and n
                not in (
                    "netshield/core.py",
                    "artifacts/portable_models/runtime_identity_manifest.json",
                )
            }

        for r in group:
            member = files(bundles[r["arm_id"]])
            require(
                hashes(member) == hashes(baseline)
                and digest(member["actions.json"]) == digest(baseline["actions.json"]),
                "non-permitted paired input differences",
            )
            if plan["study"] == "shared_stage":
                require(
                    digest(member["netshield/core.py"])
                    == digest(baseline["netshield/core.py"]),
                    "stage runtime differs",
                )
    if args.freeze_only:
        freeze(bound, args.freeze, plan["campaign_id"])
        return
    verify(bound, args.freeze)
    sys.path.insert(0, str(tools))
    from hardware_ops import Operations
    from preflight import BASE, collect, collect_probe, ssh_command

    registry = args.registry.resolve(strict=True)
    require(
        registry.is_relative_to(BASE.resolve(strict=True)),
        "registry must reside on the external project volume",
    )
    campaign = registry / plan["campaign_id"]
    volume, uuid = backup_volume()
    backup_root=volume/"NetShield_Backup"/plan["campaign_id"]
    require(not campaign.exists() and not backup_root.exists(),"campaign or backup already registered")
    os.environ["TON_EXT_BACKUP_UUID"]=uuid
    from tempfile import mkdtemp
    gate_path=Path(mkdtemp(prefix="launch_",dir=ROOT/"checks"))/"gate"
    require(collect(gate_path)["status"]=="PASS","hardware or backup qualification failed before launch")
    backup_root.mkdir(parents=True,exist_ok=False)
    for name in ("code","plan","bundles","evidence","enrollment"):
        copy_evidence(ROOT/name,backup_root/name)
    for name in ("run_pilot.py","ALLOCATOR_PILOT_PROTOCOL.json","INPUT_FREEZE.json","QUALIFICATION.json","PROTOCOL.md","SHA256SUMS.txt"):
        source=ROOT/name
        target=backup_root/name
        target.write_bytes(source.read_bytes())
        require(digest(target)==digest(source),"failed backup readback")
    campaign.mkdir()
    (campaign/PROTOCOL_PATH.name).write_bytes(PROTOCOL_PATH.read_bytes())
    write(
        campaign / "before_first_arm.json",
        dict(
            freeze_sha256=digest(args.freeze),
            plan_sha256=digest(args.plan / "plan.json"),
            copy_type="same physical research disk",registered_ns=time.time_ns(),role_map=role_names,protocol_sha256=mapping_hash,backup_uuid=uuid,
        ),
    )
    for row in rows:
        verify(bound, args.freeze)
        attempt = row["arm_id"] + "_A001"
        output = campaign / attempt
        output.mkdir()
        write(
            output / "started.json",
            dict(
                row=row,role_map=role_names,protocol_sha256=mapping_hash,
                attempt=attempt,
                started_ns=time.time_ns(),
                started_utc=datetime.now(timezone.utc).isoformat(),
                runtime_manifest_sha256=digest(
                    bundles[row["arm_id"]]
                    / "artifacts/portable_models/runtime_identity_manifest.json"
                ),
                plan_sha256=digest(args.plan / "plan.json"),
                formal_freeze_sha256=(qualification.get("formal_bindings") or {}).get(
                    "freeze_artifact_sha256"
                ),
            ),
        )
        procs, handles, logs, remote_dirs = {}, [], {}, {}
        status = "interrupted"
        try:
            report = collect(output / "preflight")
            require(
                report["status"] == "PASS",
                "RC1 pre-arm infrastructure qualification failed",
            )
            root = bundles[row["arm_id"]]
            layout = cfg["blocks"][row["session_id"]]
            common = [
                "--config",
                "config.json",
                "--actions",
                "actions.json",
                "--models-dir",
                "artifacts/portable_models",
                "--run-id",
                attempt,
                "--session-id",
                row["session_id"],
                "--seed",
                str(layout["seed"]),
                "--capacity-level",
                row["capacity"],
                "--port",
                str(cfg["port"]),
            ]
            # Immutable per-attempt copies avoid sharing queue/process state between arms.
            archive = output / "deployment.tar"
            members = files(root)
            with tarfile.open(archive, "x") as tar:
                for name, p in members.items():
                    require(
                        re.fullmatch(r"[A-Za-z0-9_. /-]+", name), "unsafe bundle member"
                    )
                    tar.add(p, arcname=name, recursive=False)
            verify(bound, args.freeze)
            with tarfile.open(archive) as tar:
                for m in tar.getmembers():
                    require(
                        hashlib.sha256(tar.extractfile(m).read()).hexdigest()
                        == digest(members[m.name]),
                        "bundle changed",
                    )
            for role in ROLES:
                remote = "netshield_extensions/" + attempt
                with archive.open("rb") as f:
                    subprocess.run(
                        ssh_command(
                            role,
                            f"umask 077 && mkdir -p netshield_extensions && mkdir {remote} && cd {remote} && tar xf -",
                        ),
                        stdin=f,
                        check=True,
                        timeout=180,
                    )
                remote_dirs[role] = remote
                check = "".join(f"{digest(p)}  {name}\n" for name, p in members.items())
                subprocess.run(
                    ssh_command(role, f"cd {remote} && sha256sum --check --status"),
                    input=check.encode(),
                    check=True,
                    timeout=90,
                )
            verify(bound, args.freeze)
            write(
                output / "deployment_verified.json",
                dict(
                    roles=list(ROLES),role_map=role_names,protocol_sha256=mapping_hash,
                    members={n: digest(p) for n, p in members.items()},
                    archive_sha256=digest(archive),
                ),
            )

            def start(role, argv, cwd):
                logs[role] = output / (role + ".log")
                h = logs[role].open("xb")
                handles.append(h)
                procs[role] = subprocess.Popen(
                    argv,
                    cwd=cwd,
                    stdout=h,
                    stderr=subprocess.STDOUT,
                    start_new_session=True,
                    env=dict(
                        os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONUNBUFFERED="1"
                    ),
                )

            ip = subprocess.check_output(
                ["ipconfig", "getifaddr", "en1"], text=True
            ).strip()
            start(
                "core",
                [
                    cfg["core_python"],
                    "-B",
                    "-u",
                    "-m",
                    "netshield.core",
                    *common,
                    "--host",
                    ip,
                    "--output",
                    str(output / "core"),
                ],
                root,
            )
            until = time.monotonic() + 60
            while "CORE_READY " not in logs["core"].read_text(errors="replace"):
                require(
                    procs["core"].poll() is None and time.monotonic() < until,
                    "Core readiness failed",
                )
                time.sleep(0.2)
            for role in ROLES:
                argv = [
                    "python3",
                    "-B",
                    "-u",
                    "-m",
                    "netshield.probe",
                    *common,
                    "--device-id",
                    role,
                    "--core-host",
                    ip,
                    "--interface",
                    "wlan0",
                    "--window-plan-dir",
                    "window_plans",
                    "--window-plan-session-id",
                    layout["workload_session"],
                    "--output",
                    "raw",
                ]
                command = (
                    f"cd {remote_dirs[role]} && export PATH=/usr/sbin:/sbin:$PATH && echo NETSHIELD_OWNED_PID=$$ >&2 && exec "
                    + shlex.join(argv)
                )
                start(role, ssh_command(role, command), root)
            next_gate = time.monotonic() + 30
            until = time.monotonic() + 1800
            while any(p.poll() is None for p in procs.values()):
                require(
                    all(p.poll() in (0, None) for p in procs.values())
                    and time.monotonic() < until,
                    "process exit or timeout",
                )
                if time.monotonic() >= next_gate:
                    with ThreadPoolExecutor(max_workers=3) as pool:
                        observations = dict(zip(ROLES, pool.map(collect_probe, ROLES)))
                    write(output / f"health_{time.monotonic_ns()}.json", observations)
                    for role, obs in observations.items():
                        require(
                            all(
                                obs["checks"].get(k)
                                for k in (
                                    "commands_success",
                                    "identity",
                                    "ntp",
                                    "temperature",
                                    "power",
                                    "memory",
                                    "disk",
                                    "wifi",
                                    "workload_route_wlan0",
                                    "route",
                                )
                            )
                            and all(
                                attempt in line
                                for line in obs.get("competing_processes", [])
                            ),
                            "in-run health/identity failure on " + role,
                        )
                    next_gate = time.monotonic() + 30
                time.sleep(1)
            require(
                all(p.returncode == 0 for p in procs.values()), "nonzero process exit"
            )
            status = "processes_completed_pending_raw_audit"
        finally:
            try:
                if any(p.poll() is None for p in procs.values()):
                    Operations().stop_owned(procs, logs, attempt)
            finally:
                for h in handles:
                    h.close()
                write(
                    output / "exits.json",
                    dict(
                        status=status,
                        ended_ns=time.time_ns(),
                        ended_utc=datetime.now(timezone.utc).isoformat(),
                        returncodes={k: p.poll() for k, p in procs.items()},
                    ),
                )
                collection_errors = []
                for role, remote in remote_dirs.items():
                    # Keep partial logs and record missing/failed collections, including on error.
                    try:
                        with (output / (role + ".tar")).open("xb") as f:
                            p = subprocess.run(
                                ssh_command(role, f"cd {remote} && tar cf - raw"),
                                stdout=f,
                                timeout=180,
                            )
                        require(
                            p.returncode == 0, "remote tar exit " + str(p.returncode)
                        )
                        result = {
                            "status": "collected",
                            "sha256": digest(output / (role + ".tar")),
                        }
                    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
                        collection_errors.append(role)
                        result = {"status": "collection_failed", "error": str(exc)}
                    write(output / (role + "_collection.json"), result)
                if status.startswith("processes_completed"):
                    require(
                        not collection_errors,
                        "raw collection failed: " + str(collection_errors),
                    )
        from reconstruct_attempt import reconstruct

        reconstruct(output, output / "reconstructed")
        copy_evidence(output,backup_root/output.name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("plan", "deployment", "qualification", "freeze", "registry", "rule"):
        parser.add_argument("--" + name, type=Path, required=name != "rule")
    parser.add_argument(
        "--freeze-only",
        action="store_true",
        help="Write a new input manifest without deployment",
    )
    sys.path.insert(0,str(EXT/"formal_tools"))
    execute(parser.parse_args())
