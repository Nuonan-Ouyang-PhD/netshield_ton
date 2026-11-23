"""Resume the stage workflow with a new complete calibration and authenticated Wi-Fi endpoints."""
import fcntl, json, shutil, sys, traceback
from pathlib import Path
import continue_runs as chain
from phase import read,sha,put

h=chain.here
calid='TON_EXT_STAGE_4B8_CAL_20261123_02'
def main():
    previous=chain.pilot.parent/'TON_EXT_STAGE_4B8_CAL_20261123_01'
    arm=sorted((previous/'raw'/previous.name).glob('*/started.json'))[-1].parent
    health=sorted(arm.glob('health_*.json'))[-1]
    assert read(health)['P2']['checks'].get('ssh_collection') is False
    assert all(r['registered_identity'] for r in read(h/'p2_pinned_paths.json').values())
    assert len(read(h/'physical_states.json'))==2
    put(h/'management_amendment.json',dict(previous_campaign=previous.name,interrupted_attempt=arm.name,
        reason='P2 management SSH timeout. Multicast name subsequently resolved to the switch-side address via an unavailable Mac route. Direct Wi-Fi and the enrolled wired jump path both passed pinned identity verification.',
        evidence=dict(health=sha(health),exits=sha(arm/'exits.json'),recovery=sha(h/'p2_pinned_paths.json'),additional_P2_raw=sha(h/'interrupted_recovery/P2_additional_raw.tar')),
        new_campaign=calid,scope='Complete prospective 16-condition cohort; prior partial block archived separately. Common application route, workload, order seed, stage runtime and endpoints retained. No outcome used for recovery.'))
    common=dict(backlog=h/'physical_states.json',**{'management-map':h/'pinned_wifi.json'})
    field=read(h/'field_review.json')
    field.update(campaign_id=calid,adapter_source=dict(path=str(chain.pilot.parent/calid/'code/hardware/reconstruct_attempt.py'),sha256=field['adapter_source']['sha256']))
    approval=h/'field_review_pinned.json';put(approval,field)
    c=chain.phase(calid,'shared_stage','calibration',['F12_S07'],2026112303,**common)
    adapter=h/'calibration_analysis_code';(adapter/'hardware').mkdir(parents=True)
    for f in ('reconstruct_attempt.py','plan_hardware.py','protocol.json'):
        shutil.copyfile(c/'code/hardware'/f,adapter/'hardware'/f)
    shutil.copytree(chain.ext/'stage_adapter',adapter/'stage_adapter',ignore=shutil.ignore_patterns('__pycache__','legacy','tests'))
    out=h/'calibration'
    chain.run('profile',[adapter/'stage_adapter/assemble_calibration.py','--plan',c/'plan','--campaign',c/'raw'/c.name,'--review',approval,'--output',out,'--margin-ns',0],h)
    profile=out/'profile.json'
    sp=chain.phase('TON_EXT_STAGE_4B8_PILOT_20261123_01','shared_stage','pilot',['F12_S08'],2026112304,profile=profile,**common)
    chain.phase('TON_EXT_STAGE_4B8_FORMAL_20261123_01','shared_stage','formal',['F12_S01','F12_S02','F12_S03','F12_S04','F12_S05','F12_S06'],2026112305,profile=profile,pilot=chain.paired(sp),rationale='Six fresh complete physical blocks cover a whole six-condition Williams cycle. One 36-arm fixed sample balances all within-block positions and transitions. Workloads exclude the independent stage calibration and pilot.',**common)
if __name__=='__main__':
    with (h/'physical.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        try:main()
        except Exception as exc:chain.log('stage_pinned','interrupted',reason=repr(exc));raise
