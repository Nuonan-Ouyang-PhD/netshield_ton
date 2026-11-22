"""Opt-in integration check against a patched RC1 runtime. Synthetic inputs."""
import asyncio
import hashlib
import json
import sys
import tempfile
from dataclasses import replace
from pathlib import Path


def exercise(runtime, scratch):
    sys.path.insert(0,str(runtime))
    from netshield.config import load_experiment
    from netshield.core import Coordinator
    from netshield.common import package_tree_sha256
    cfg = replace(load_experiment(runtime/"configs/hr01_low.json"),experiment_id="TON_EXT_STAGE_TEST_ONLY",
                  app_capacity_bps=2097152,window_seconds=1,deadline_ms=1000,shared_efficiency=1)
    roles=["P1","P2","P3"]
    profile=dict(phase="calibration",campaign="TON_EXT_STAGE_FIXTURE_CAL",workers=1,
                 proposal_transit_ns=10,dispatch_compute_upload_ns=100,core_per_job_ns=100,
                 return_ns=10,margin_ns=10)
    data=json.dumps(profile).encode()
    (scratch/"fixture.json").write_bytes(data)
    conf=scratch/"args.json"
    conf.write_text(json.dumps({"stage_profile":{"file":"fixture.json","sha256":hashlib.sha256(data).hexdigest()}}))
    def trial(mode,queued,slack,expected):
        core=Coordinator(replace(cfg,method=mode,stage_capture_devices=roles),scratch,config_path=str(conf))
        async def go():
            calls=[]
            for i,d in enumerate(roles):
                candidates=[dict(action_id=aid,utility=1,predicted_compute_ms=0,predicted_core_ms=0,
                                 detector="heavy",execution=ex,evidence=ev,safe=True,unsafe_reasons=[],
                                 payload_bytes=n) for aid,ex,ev,n in (
                                     ("H_FULL","core","full",131072),("H_NONE","local","none",0))]
                rem=queued[i]
                fifo=[]
                if rem:
                    fifo=[dict(key=d,remaining=rem,slack_ns=slack)]
                    core.segment_buffers[d]={"received":131072-rem}
                calls.append(core.submit(dict(device_id=d,window_index=0,queue_bytes=rem,
                    candidates=candidates,stage={"slack_ns":slack,"fifo":fifo})))
            return await asyncio.gather(*calls)
        results=asyncio.run(go())
        if sum(r["action"]["action_id"]=="H_FULL" for r in results)!=expected:
            raise ValueError(mode)
        if sum(r["grant_bytes"] for r in results)>262144:
            raise ValueError("grant cap")
    for mode,z,b in (("instrumented_fixed_full_capture",3,3),("isolated_precheck_new_bytes",2,2),
                     ("backlog_aware_bytes",2,1),("causal_shared_stage",2,1)):
        trial(mode,[0]*3,10**9,z)
        trial(mode,[43691,43691,43690],10**9,b)
    trial("causal_shared_stage",[0]*3,0,0)
    # The second candidate fits the byte budget but would invalidate the first.
    from netshield.stage_admission import select
    props={d:dict(queue_bytes=0,stage_received_ns=0,stage={"fifo":[],"slack_ns":s})
           for d,s in zip(roles,[300,1000,1000])}
    selected,_=select(props,roles,262144,0,profile,{})
    if selected!=["P1"]:
        raise ValueError("prior reservation invalidated")
    print(json.dumps(dict(status="PASS_SYNTHETIC_ADAPTER_ONLY",cases=10,tree=package_tree_sha256())))


if __name__=="__main__":
    with tempfile.TemporaryDirectory(dir=sys.argv[2]) as d:
        exercise(Path(sys.argv[1]).resolve(),Path(d))
