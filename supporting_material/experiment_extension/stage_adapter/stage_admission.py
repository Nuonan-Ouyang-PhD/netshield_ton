"""One-round shared-stage admission for the controlled three-probe extension."""
import hashlib
import json
from pathlib import Path


def load_profile(config_path, campaign):
    cfg = json.loads(Path(config_path).read_bytes())["stage_profile"]
    raw = (Path(config_path).parent / cfg["file"]).read_bytes()
    if hashlib.sha256(raw).hexdigest() != cfg["sha256"]:
        raise ValueError("stage calibration identity mismatch")
    profile = json.loads(raw)
    if (profile["phase"] != "calibration" or not profile["campaign"].startswith("TON_EXT_STAGE_")
            or profile["campaign"] == campaign or profile["workers"] != 1):
        raise ValueError("independent calibration and single synchronous core required")
    for key in ("proposal_transit_ns","dispatch_compute_upload_ns","core_per_job_ns","return_ns","margin_ns"):
        if type(profile[key]) is not int or profile[key] < 0:
            raise ValueError(key)
    return profile,cfg["sha256"]


def select(proposals, priority, cap, now_ns, profile, partial_buffers):
    """Snapshot at the barrier; reserve complete service for all jobs this round."""
    if cap!=262144 or set(proposals)!={"P1","P2","P3"} or len(priority)!=3 or set(priority)!=set(proposals):
        raise ValueError("stage configuration")
    pending = []
    known = {}
    fresh = {}
    for d in priority:
        p = proposals[d]
        s = p["stage"]
        wait = now_ns-p["stage_received_ns"]
        age = wait+profile["proposal_transit_ns"]
        if wait<0 or sum(j["remaining"] for j in s["fifo"])!=p["queue_bytes"]:
            raise ValueError("stage queue or clock")
        for j in s["fifo"]:
            rem = j["remaining"]
            if type(rem) is not int or not 0<rem<=131072 or j["key"] in known:
                raise ValueError("invalid FIFO")
            known[j["key"]]=131072-rem
            pending.append((rem,j["slack_ns"]-age))
        fresh[d]=(131072,s["slack_ns"]-age)
    if {k:v for k,v in known.items() if v}!=partial_buffers:
        raise ValueError("probe FIFO and core reassembly disagree")
    admitted=[]
    trace=[]
    for d in priority:
        trial=pending+[fresh[d]]
        byte_sum=sum(n for n,_ in trial)
        # Conservative serialized post-decision batch estimate. The independent
        # profile must cover preparation and upload of a complete in-scope batch.
        # Synchronous core inference cannot overlap another inference here.
        completion=(profile["dispatch_compute_upload_ns"]+len(trial)*profile["core_per_job_ns"]
                    +profile["return_ns"]+profile["margin_ns"])
        margin=min(slack for _,slack in trial)-completion
        accepted=byte_sum<=cap and margin>=0
        trace.append(dict(device=d,bytes=byte_sum,min_slack_after_service_ns=margin,accepted=accepted))
        if accepted:
            admitted.append(d)
            pending=trial
    return admitted,trace
