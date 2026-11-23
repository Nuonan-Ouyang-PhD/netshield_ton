"""Empirically calibrated, one-round admission for the three-probe extension.

A measured maximum is not a hard physical bound. Inputs are causal snapshots.
Unsupported queue states reject new work; the runtime still serves old work.
"""
import hashlib
import itertools
import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import platform
import re
import subprocess
import sys
from types import MappingProxyType


DEVICES = ("P1", "P2", "P3")
PAYLOAD = 131072
CAPACITY = 262144
DEADLINE_NS = 1_000_000_000
BACKLOGS = ((0, 0, 0), (43691, 43691, 43690))
TIMINGS = ("proposal_transit_ns", "dispatch_compute_upload_ns", "fallback_compute_ns", "core_per_job_ns", "return_ns")


@dataclass(frozen=True)
class CompiledProfile:
    margin_ns: int
    envelopes: object


@lru_cache(maxsize=1)
def clock_epoch():
    """Read the actual local boot epoch once; never substitute a run label."""
    if sys.platform.startswith("linux"):
        value = Path("/proc/sys/kernel/random/boot_id").read_text().strip()
        require(bool(re.fullmatch(r"[0-9a-fA-F-]{36}", value)), "invalid Linux boot identity")
        return "linux:" + value
    if sys.platform == "darwin":
        value = subprocess.check_output(["sysctl", "-n", "kern.boottime"], text=True)
        match = re.search(r"sec\s*=\s*(\d+)\s*,\s*usec\s*=\s*(\d+)", value)
        require(match is not None, "macOS boot epoch unavailable")
        return "darwin:" + platform.node() + ":" + match[1] + ":" + match[2]
    raise ValueError("no reviewed boot-epoch adapter for this host")


def require(ok, message):
    if not ok:
        raise ValueError(message)


def integer(value, name, minimum=None):
    require(type(value) is int and (minimum is None or value >= minimum), name)
    return value


def identity(value, name):
    require(isinstance(value, str) and bool(value.strip()), name)
    return value


def sha256_identity(value, name):
    require(isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value), name)
    return value


def subsets():
    return [tuple(c) for n in range(4) for c in itertools.combinations(DEVICES, n)]


def envelope_key(backlog, selected):
    require(set(backlog) == set(DEVICES), "backlog device set")
    require(isinstance(selected, (list, tuple)) and len(set(selected)) == len(selected)
            and set(selected) <= set(DEVICES), "selected device set")
    return tuple(integer(backlog[d], "backlog bytes", 0) for d in DEVICES), tuple(sorted(selected))


def validate_profile(profile, campaign=None):
    require(profile.get("schema_version") == 2 and profile.get("phase") == "calibration",
            "schema v2 calibration profile required")
    source_campaign = identity(profile["campaign"], "calibration campaign")
    require(source_campaign.startswith("TON_EXT_STAGE_") and source_campaign != campaign,
            "independent calibration campaign required")
    require(type(profile["workers"]) is int and profile["workers"] == 1,
            "single synchronous core required")
    require(profile["basis"] in ("physical_capture", "synthetic_fixture"), "calibration basis")
    if profile["basis"] == "physical_capture":
        sha256_identity(profile["runtime_tree_sha256"], "calibrated runtime identity")
        for name in ("records_sha256", "plan_sha256", "field_map_sha256", "adapter_sha256", "mapping_review_sha256"):
            sha256_identity(profile["source_identity"][name], "calibration " + name)
    if profile["basis"] == "synthetic_fixture" and campaign is not None:
        require(campaign.startswith("TON_EXT_STAGE_TEST_"), "synthetic timing forbidden in physical campaign")
    require(profile["clock_policy"] == "within_host_intervals_only", "calibration clock policy")
    require(profile["estimator"] == "per_condition_componentwise_observed_maximum",
            "unsupported calibration estimator")
    require(profile["controller_sha256"] == hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "calibration belongs to another controller source")
    integer(profile["margin_ns"], "frozen margin", 0)
    require(profile["scope"] == {"devices": list(DEVICES), "payload_bytes": PAYLOAD,
            "capacity_bytes_per_round": CAPACITY, "deadline_ns": DEADLINE_NS,
            "initial_core_executing_jobs": 0, "initial_core_queued_complete_jobs": 0},
            "calibration scope mismatch")
    envelopes = {}
    for row in profile["envelopes"]:
        key = envelope_key(row["backlog_by_probe_bytes"], row["selected_devices"])
        require(key not in envelopes, "duplicate calibration condition")
        for name in TIMINGS:
            integer(row[name], name, 0)
        integer(row["observed_batches"], "observed batches", 1)
        envelopes[key] = row
    require(set(envelopes) == {(b, s) for b in BACKLOGS for s in subsets()},
            "all 16 backlog/selection conditions must be retained")
    return envelopes


def load_profile(config_path, campaign, runtime_tree_sha256=None):
    cfg = json.loads(Path(config_path).read_bytes())["stage_profile"]
    raw = (Path(config_path).parent / cfg["file"]).read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    require(digest == cfg["sha256"], "stage calibration identity mismatch")
    profile = json.loads(raw)
    envelopes = validate_profile(profile, campaign)
    if profile["basis"] == "physical_capture":
        require(sha256_identity(runtime_tree_sha256, "running runtime identity") == profile["runtime_tree_sha256"],
                "running runtime differs from calibrated runtime")
    # Source/digest/schema verification runs once at load time, outside every
    # admission round. Freeze the scalar envelope inputs against later edits.
    compiled = CompiledProfile(profile["margin_ns"], MappingProxyType({
        key: MappingProxyType(dict(value)) for key, value in envelopes.items()}))
    return compiled, digest


def validate_snapshot(proposals, priority, cap, now_ns, partial_buffers):
    """Validate recorded identity, queue and same-core-clock reception state."""
    require(type(cap) is int and cap == CAPACITY, "stage capacity")
    integer(now_ns, "core decision clock", 0)
    require(set(proposals) == set(DEVICES) and len(priority) == 3
            and set(priority) == set(DEVICES), "stage device/priority configuration")
    pending, fresh, known = [], {}, {}
    backlog = {}
    for device in priority:
        proposal = proposals[device]
        received = integer(proposal["stage_received_ns"], "core receive clock", 0)
        require(received <= now_ns, "core reception after decision")
        stage = proposal["stage"]
        identity(stage["origin_clock_id"], "origin clock/boot identity")
        integer(stage["sample_probe_ns"], "origin snapshot clock", 0)
        key = identity(stage["key"], "fresh event identity")
        require(key not in known, "duplicate fresh/FIFO event identity")
        known[key] = None
        fresh[device] = {"device": device, "key": key, "remaining": PAYLOAD,
                         "slack_ns": integer(stage["slack_ns"], "fresh remaining slack"),
                         "residence_ns": now_ns - received}
        require(fresh[device]["slack_ns"] <= DEADLINE_NS, "fresh slack exceeds original deadline")
        backlog[device] = integer(proposal["queue_bytes"], "queue bytes", 0)
        require(isinstance(stage["fifo"], list), "FIFO list required")
        remaining = 0
        for job in stage["fifo"]:
            key = identity(job["key"], "FIFO event identity")
            require(key not in known, "duplicate fresh/FIFO event identity")
            rem = integer(job["remaining"], "remaining payload bytes", 1)
            require(rem <= PAYLOAD, "remaining payload exceeds full representation")
            known[key] = PAYLOAD - rem
            pending.append({"device": device, "key": key, "remaining": rem,
                            "slack_ns": integer(job["slack_ns"], "FIFO remaining slack"),
                            "residence_ns": now_ns - received})
            require(pending[-1]["slack_ns"] <= DEADLINE_NS, "FIFO slack exceeds original deadline")
            remaining += rem
        require(remaining == backlog[device], "FIFO sum differs from queue bytes")
    observed = {}
    for key, value in partial_buffers.items():
        identity(key, "core buffer event identity")
        value = integer(value, "core received prefix", 0)
        require(value < PAYLOAD, "complete input unexpectedly remains in reassembly")
        require(key in known and known[key] is not None and known[key] == value,
                "core buffer identity/prefix differs from FIFO")
        if value:
            observed[key] = value
    require({k: v for k, v in known.items() if v is not None and v > 0} == observed,
            "probe FIFO and core reassembly disagree")
    return pending, fresh, backlog


def select(proposals, priority, cap, now_ns, profile, partial_buffers):
    """Recheck every queued/selected job under each prospective batch envelope."""
    if isinstance(profile, CompiledProfile):
        envelopes, margin_ns = profile.envelopes, profile.margin_ns
    else:
        envelopes, margin_ns = validate_profile(profile), profile["margin_ns"]
    pending, fresh, backlog = validate_snapshot(proposals, priority, cap, now_ns, partial_buffers)
    queue_shape = tuple(backlog[d] for d in DEVICES)
    # A B fixture is one old full request per probe, not many tiny requests.
    expected_jobs = 0 if queue_shape == BACKLOGS[0] else 3
    supported = queue_shape in BACKLOGS and len(pending) == expected_jobs
    baseline_margin = None
    if supported and pending:
        baseline = envelopes[(queue_shape, ())]
        baseline_completion = (baseline["dispatch_compute_upload_ns"] + baseline["fallback_compute_ns"]
                               + len(pending) * baseline["core_per_job_ns"]
                               + baseline["return_ns"] + margin_ns)
        baseline_margin = min(job["slack_ns"] - job["residence_ns"] - baseline["proposal_transit_ns"]
                              for job in pending) - baseline_completion
    admitted, trace = [], []
    for device in priority:
        selected = admitted + [device]
        trial = pending + [fresh[device]]
        byte_sum = sum(job["remaining"] for job in trial)
        if not supported:
            trace.append(dict(device=device, bytes=byte_sum, accepted=False,
                              reason="out_of_calibrated_backlog", min_slack_after_service_ns=None,
                              backlog_only_predicted_margin_ns=baseline_margin))
            continue
        envelope = envelopes[(queue_shape, tuple(sorted(selected)))]
        completion = (envelope["dispatch_compute_upload_ns"]
                      + envelope["fallback_compute_ns"]
                      + len(trial) * envelope["core_per_job_ns"]
                      + envelope["return_ns"] + margin_ns)
        margin = min(job["slack_ns"] - job["residence_ns"] - envelope["proposal_transit_ns"]
                     for job in trial) - completion
        accepted = byte_sum <= cap and margin >= 0
        trace.append(dict(device=device, bytes=byte_sum, accepted=accepted,
                          selected_if_accepted=sorted(selected), estimated_completion_ns=completion,
                          min_slack_after_service_ns=margin,
                          backlog_only_predicted_margin_ns=baseline_margin,
                          reason="accepted" if accepted else ("capacity" if byte_sum > cap else "remaining_slack")))
        if accepted:
            admitted.append(device)
            pending = trial
    return admitted, trace
