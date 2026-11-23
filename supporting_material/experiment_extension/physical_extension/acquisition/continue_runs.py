"""Serialize the predeclared ToN acquisitions and retain a receipt for every phase."""
import datetime, fcntl, hashlib, json, os, shutil, subprocess, sys
from pathlib import Path
from phase import read, put, sha

here=Path(__file__).resolve().parent
work=here.parent
base=work.parent
pilot=base/'20_EXTENSION_WORKSPACES/TON_EXT_ALLOC_4B8_PILOT_20261122_01'
repo=work/'review'
ext=repo/'supporting_material/experiment_extension'
calid='TON_EXT_STAGE_4B8_CAL_20261123_01'
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def log(step,status,**facts):
    with (here/'phases.jsonl').open('a') as out:out.write(json.dumps(dict(utc=now(),step=step,status=status,**facts))+'\n')
def run(label,args,cwd):
    with (here/(label+'.log')).open('x') as out:subprocess.run([sys.executable,'-B',*map(str,args)],cwd=cwd,stdout=out,stderr=subprocess.STDOUT,check=True)
def paired(root):return root/'raw'/root.name/'paired_pilot.json'
def phase(id,study,kind,workloads,seed,**options):
    root=pilot.parent/id
    cmd=[here/'phase.py','--base',pilot,'--repo',repo,'--rc1',base/'00_ADMIN/FORMAL_PROTOCOL_V1_2_RC1','--original',work/'closeout_07ce152/instrumented','--corrected',work/'closeout_07ce152/instrumented_corrected','--git','f9ce9bf9b25d40cdb93e07fff4f187ed992f030d','--campaign',id,'--study',study,'--phase',kind,'--workloads',*workloads,'--seed',seed]
    for k,v in options.items():cmd.extend(['--'+k,v])
    log(id,'preparing');run(id+'_freeze',cmd,here)
    return acquire(root)
def acquire(root):
    log(root.name,'starting')
    run(root.name+'_execution',[root/'run_pilot.py'],root)
    s=read(paired(root))
    if not all(a['complete'] for a in s['arms']):raise ValueError('incomplete physical blocks; see '+root.name)
    log(root.name,'completed',arms=len(s['arms']),report=sha(paired(root)));return root
def allocation():
    p=read(paired(pilot))
    if len(p['arms'])!=2 or not all(a['complete'] for a in p['arms']):raise ValueError('separate allocator pilot incomplete')
    return phase('TON_EXT_ALLOC_4B8_FORMAL_20261123_01','allocator','formal',['F12_S03','F12_S04','F12_S05','F12_S06'],2026112302,pilot=paired(pilot),rationale='Four independent physical blocks cover two full two-condition order cycles across four archived workloads. The fixed resource budget is eight individually reset arms, selected for balanced order and replication of each order. Report individual differences and their mean with the actual denominator.')
def stage():
    qual=acquire(pilot.parent/'TON_EXT_STAGE_4B8_QUAL_20261123_01')
    states=[read(p) for p in sorted((qual/'raw'/qual.name).glob('*/reconstructed/first_batch.jsonl'))]
    if len(states)!=2:raise ValueError('missing physical backlog qualification observations')
    proof=here/'physical_states.json';put(proof,states)
    # Field map and margin are registered before opening the calibration campaign.
    source=repo/'supporting_material/experiment_extension/stage_adapter'
    engine=qual/'code/hardware/reconstruct_attempt.py'
    def review(adapter):
        mapping={'proposal_sample_origin_ns':'probe_stage.sample_ns','decision_received_origin_ns':'probe_stage.decision_received_ns','fallback_complete_origin_ns':'probe_stage.local_end_ns for H_NONE','decision_core_ns':'stage_decision.core_decision_ns','last_decision_sent_core_ns':'maximum of three decision_dispatched.core_ns','core_payload_ready_core_ns':'matched event Core payload readiness','core_start_core_ns':'core_inference_start_monotonic_ns','core_end_core_ns':'core_inference_end_monotonic_ns','core_result_send_core_ns':'results_dispatched.core_ns joined by event ID','result_received_origin_ns':'origin probe result receipt, matched frame','origin_clock_id':'matching probe_stage and proposal origin epoch','core_clock_id':'initial barrier Core epoch','backlog_by_probe_bytes':'per-probe ready.fifo remaining sum','received_prefix_bytes':'stage_initial_state.partial_bytes keyed by event','payload_sha256':'matched probe and Core event identity','core_state_before':'stage_initial_state executing_jobs and queued_complete_jobs'}
        return dict(status='REVIEWED_PHYSICAL_CAPTURE_FIELD_MAP',campaign_id=calid,frozen_margin_ns=0,runtime_tree_sha256=read(qual/'code/hardware/candidate_identity.json')['original'],adapter_source=dict(path=str(adapter),sha256=sha(engine)),mapped_fields=mapping)
    calroot=pilot.parent/calid
    approval=here/'field_review.json';put(approval,review(calroot/'code/hardware/reconstruct_attempt.py'))
    c=phase(calid,'shared_stage','calibration',['F12_S07'],2026112303,backlog=proof)
    adapterdir=c/'code/stage_adapter';shutil.copytree(source,adapterdir,ignore=shutil.ignore_patterns('__pycache__','legacy','tests'))
    assembled=here/'calibration'
    run('profile',[adapterdir/'assemble_calibration.py','--plan',c/'plan','--campaign',c/'raw'/c.name,'--review',approval,'--output',assembled,'--margin-ns',0],here)
    profile=assembled/'profile.json'
    sp=phase('TON_EXT_STAGE_4B8_PILOT_20261123_01','shared_stage','pilot',['F12_S08'],2026112304,backlog=proof,profile=profile)
    phase('TON_EXT_STAGE_4B8_FORMAL_20261123_01','shared_stage','formal',['F12_S01','F12_S02','F12_S03','F12_S04','F12_S05','F12_S06'],2026112305,backlog=proof,profile=profile,pilot=paired(sp),rationale='Six fresh complete physical blocks form one entire six-condition Williams order cycle, allowing balanced positions and directed within-block transitions. Formal workloads exclude stage calibration and pilot workloads. This is a fixed 36-arm resource allocation.')
if __name__=='__main__':
    with (here/'physical.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        for fn in (allocation,stage):
            try:fn()
            except Exception as e:log(fn.__name__,'interrupted',reason=repr(e))
