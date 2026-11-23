"""Prepare, bind, and run one prospectively identified physical phase."""
import argparse, csv, datetime, hashlib, json, os, shutil, subprocess, sys
from pathlib import Path

def read(p): return json.loads(p.read_bytes())
def put(p,data):
    with p.open('x') as f: json.dump(data,f,indent=2,allow_nan=False)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def replace(p,a,b):
    text=p.read_text()
    if text.count(a)!=1: raise ValueError((p,a))
    p.write_text(text.replace(a,b))

def main(a):
    base=a.base.resolve(); root=base.parent/a.campaign
    repo=a.repo.resolve(); study=a.study; phase=a.phase
    eng=a.backlog_qualification
    if eng and (study!='shared_stage' or phase!='calibration' or 'QUAL' not in a.campaign or len(a.workloads)!=1): raise ValueError('engineering qualification scope')
    root.mkdir(mode=0o700)
    for n in ('checks','raw','evidence'): (root/n).mkdir()
    for n in ('code','enrollment'): shutil.copytree(base/n,root/n,ignore=shutil.ignore_patterns('__pycache__'))
    for n in ('run_pilot.py',):shutil.copyfile(base/n,root/n)
    ext=repo/'supporting_material/experiment_extension'; hw=root/'code/hardware'; ev=root/'evidence'
    for n in ('deployment_qualification.json','allocator_only.diff','allocator_original.json','prior_transport.json','storage_amendment.json'):
        shutil.copyfile(base/'evidence'/n,ev/n)
    proto=read(base/'ALLOCATOR_PILOT_PROTOCOL.json')
    contract={k:proto[k] for k in ('roles','known_hosts_sha256','backup','warmup_rounds','measured_rounds','max_drain_rounds','deadline_seconds','remote_transport')}
    contract.update(campaign_id=a.campaign,study=study,phase=phase,blocks=len(a.workloads),workloads=a.workloads,order_seed=a.seed,engineering_qualification=eng,primary_anchor=proto['primary_anchor'],base_git=a.git)
    if study=='shared_stage':contract.update(profile_margin_ns=0,margin_basis='No additional margin beyond componentwise observed maxima and overlapping allowances; predeclared before formal observations.')
    if a.management_map:
        import ipaddress
        hosts=read(a.management_map)
        if set(hosts)!=set(contract["roles"]) or len(set(hosts.values()))!=3:raise ValueError("invalid enrolled address map")
        for address in hosts.values(): ipaddress.IPv4Address(address)
        contract["management_ipv4"]=hosts
        contract["management_policy"]="Observed Wi-Fi address with pinned registered HostKeyAlias; workload still routes through wlan0."
        preflight=root/'code/formal_tools/preflight.py'
        replace(preflight,"'-o','ServerAliveCountMax=3',TARGETS[role],command]", """
            '-o','ServerAliveCountMax=3','-o','HostKeyAlias='+TARGETS[role].split('@')[1],
            TARGETS[role].split('@')[0]+'@'+PROTOCOL['management_ipv4'][role],command]""")
    put(root/'ALLOCATOR_PILOT_PROTOCOL.json',contract)
    (root/'PROTOCOL.md').write_text('Physical '+study+' '+phase+' '+a.campaign+'\n\n'+('Engineering qualification only. ' if eng else '')+'See frozen campaign mapping, per-condition schedule and input hashes. Within each block all conditions use the same frozen workload, methods, windows and deadline as the extension protocol. A fresh runtime, verified bundle, three-probe preflight and exclusive registration precede each arm. Every attempt and every outcome is retained. Same-disk copy with SHA-256 readback.\n')
    hp=hw/'protocol.json'; design=read(hp); design['physical_campaign']=dict(id=a.campaign,protocol_sha256=sha(root/'ALLOCATOR_PILOT_PROTOCOL.json'),study=study,phase=phase); hp.write_text(json.dumps(design,indent=2))
    exe=hw/'execute_hardware.py'; rec=hw/'reconstruct_attempt.py'
    replace(exe,'plan["study"]=="allocator" and plan["phase"]=="pilot"','plan["study"]==PROTOCOL["study"] and plan["phase"]==PROTOCOL["phase"]')
    replace(exe,'plan["requested_complete_blocks"]==1','plan["requested_complete_blocks"]==PROTOCOL["blocks"]')
    replace(exe,'workload==PROTOCOL["workload_session"]','workload==PROTOCOL["workloads"][r["block"]-1]')
    replace(rec,'row["phase"]=="pilot"','row["phase"]==json.loads(Path(__file__).with_name("protocol.json").read_bytes())["physical_campaign"]["phase"]')
    runner=root/'run_pilot.py'
    if phase=='formal':
        replace(exe,'for name in ("run_pilot.py","ALLOCATOR_PILOT_PROTOCOL.json","INPUT_FREEZE.json","QUALIFICATION.json","PROTOCOL.md","SHA256SUMS.txt"):', 'for name in ("run_pilot.py","ALLOCATOR_PILOT_PROTOCOL.json","INPUT_FREEZE.json","QUALIFICATION.json","PROTOCOL.md","SHA256SUMS.txt","sample_size.json"):')
    if phase=='formal': replace(runner,'"--registry",registry)','"--registry",registry,"--rule",ROOT/"sample_size.json")')
    if eng:
        # Two isolated qualification runs establish the missing physical readiness fact.
        # This executable can never execute or qualify a scientific calibration plan.
        planner=hw/'plan_hardware.py'
        replace(planner,'schedules = ordered_blocks(conditions, blocks, order_seed)','require(campaign_id == '+repr(a.campaign)+' and study=="shared_stage" and phase=="calibration" and blocks==1, "engineering runs only")\n    conditions = [c for c in conditions if c["stage_capture_devices"]==["P1"]]\n    schedules = ordered_blocks(conditions, blocks, order_seed)')
        replace(planner,'gates.append(("actual_backlog_and_core_state_verified", "backlog_core_fixture_audit"))','require(phase=="calibration", "engineering acquisition only")')
        replace(planner,'"execution_qualification": qualification["status"]','"engineering_qualification_only": True, "execution_qualification": qualification["status"]')
    rows=len(a.workloads)
    def cli(script,*args):
        subprocess.run([sys.executable,'-B',str(script),*map(str,args)],check=True,cwd=root)
    params=['--study',study,'--phase',phase,'--blocks',rows,'--campaign-id',a.campaign,'--order-seed',a.seed]
    if phase=='formal':
        pil=read(a.pilot)
        if not pil['arms'] or not all(x['complete'] for x in pil['arms']): raise ValueError('incomplete pilot')
        notes=a.rationale
        durations=[]
        for x in pil['arms']:
            d=a.pilot.parent/x['attempts'][0]
            durations.append((read(d/'exits.json')['ended_ns']-read(d/'started.json')['started_ns'])/1e9)
        put(root/'sample_size.json',dict(schema_version=1,study=study,rule='fixed_complete_blocks',status='FROZEN_SAMPLE_SIZE_RULE',formal_blocks=rows,formal_outcome_peeking_for_stopping=False,independent_unit='fresh_physical_complete_condition_block',pilot_campaign_id=pil['campaign'],pilot_report_sha256=sha(a.pilot),rationale=notes+' Pilot wall seconds per arm: '+str([round(x,1) for x in durations])+'. A single pilot block cannot estimate between-block variance. No power or precision guarantee.',analysis_script_sha256=sha(ext/'physical_extension/verify_results.py'),analysis='Enumerate all n^n paired physical-block bootstrap samples for the two endpoints of the censoring bounds; nearest-rank 2.5 and 97.5 percentiles. Only complete fixed sets of 2 to 6 blocks receive this small-sample descriptive interval. Report every block and corrected minus original or policy contrasts in the preregistered strata, calendar order, censoring endpoints and descriptive range. Small block counts limit inference.'))
        params+=['--sample-size-rule-file',root/'sample_size.json']
    cli(hw/'plan_hardware.py',*params,'--output',root/'draft')
    bundleargs=['--rc1',a.rc1,'--original',a.original,'--corrected',a.corrected,'--tools',root/'code/formal_tools','--plan',root/'draft','--output',root/'bundles','--workloads',*a.workloads]
    if a.profile:bundleargs+=['--profile',a.profile]
    cli(hw/'prepare_bundles.py',*bundleargs)
    inp={}
    for d in sorted((root/'bundles').iterdir()):
        if d.is_dir(): inp[d.name]={f.relative_to(d).as_posix():sha(f) for f in sorted(d.rglob('*')) if f.is_file()}
    put(ev/'inputs.json',inp)
    put(ev/'launcher.json',dict(protocol=sha(root/'ALLOCATOR_PILOT_PROTOCOL.json'),launcher=sha(exe),analysis=sha(rec),planner=sha(hw/'plan_hardware.py'),order=sha(root/'draft/condition_order.csv'),source='fresh runtime, in-run health gates, recorded origin-clock returns and Core-local observations'))
    put(ev/'registry.json',dict(campaign=a.campaign,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),prior_entries=list((root/'raw').iterdir())))
    facts={}; evidence={}
    def bind(f,k,p):
        if not p.is_file(): raise FileNotFoundError(p)
        facts[f]=True; evidence[k]=dict(path=os.path.relpath(p,root),sha256=sha(p))
    for f,k,n in [('private_runtime_identity_verified','runtime_inventory','deployment_qualification.json'),('frozen_inputs_verified','input_manifest','inputs.json'),('launcher_and_anchors_frozen','launcher_anchor_review','launcher.json'),('window_counts_compatible','window_compatibility_review','inputs.json'),('event_and_service_logging_verified','instrumentation_audit','prior_transport.json'),('attempt_recording_verified','attempt_protocol','launcher.json'),('fresh_campaign_registry_checked','campaign_registry_review','registry.json')]:
        bind(f,k,ev/n)
    if study=='allocator':
        bind('deployed_allocator_affected','deployed_allocator_inspection',ev/'allocator_original.json')
        bind('allocator_only_patch_verified','allocator_patch_audit',ev/'allocator_only.diff')
    elif not eng:
        proof=read(a.backlog)
        if {tuple(x['backlog_by_probe_bytes'][k] for k in ('P1','P2','P3')) for x in proof} != {(0,0,0),(43691,43691,43690)} or any(any(x['core_state_before'].values()) for x in proof):raise ValueError('physical initial states unqualified')
        shutil.copyfile(a.backlog,ev/'physical_backlog.json')
        bind('actual_backlog_and_core_state_verified','backlog_core_fixture_audit',ev/'physical_backlog.json')
        if phase!='calibration':
            shutil.copyfile(a.profile,ev/'profile.json')
            shutil.copyfile(ext/'stage_adapter/final_runtime_26.json',ev/'stage_control.json')
            bind('calibration_disjoint_and_frozen','calibration_freeze',ev/'profile.json')
            bind('controller_causal_and_implemented','controller_source_and_causality_audit',ev/'stage_control.json')
    qual=dict(schema_version=1,facts=facts,evidence=evidence)
    if phase=='formal':
        shutil.copyfile(a.pilot,ev/'completed_pilot.json'); bind('pilot_report_retained','pilot_report',ev/'completed_pilot.json')
        put(root/'QUALIFICATION_DRAFT.json',qual)
        cli(hw/'plan_hardware.py',*params,'--qualification',root/'QUALIFICATION_DRAFT.json','--output',root/'formal_draft')
        draft=read(root/'formal_draft/plan.json')
        if draft['execution_qualification'].startswith('QUALIFIED'):raise ValueError('formal draft unexpectedly executable')
        rule=read(root/'sample_size.json')
        freeze={k:draft[k] for k in ('campaign_id','study','order_seed','include_mid_control','condition_order_sha256','planner_source_sha256','raw_schema_sha256','protocol_sha256')}
        freeze.update(schema_version=1,status='FROZEN_FOR_FORMAL_EXECUTION',formal_blocks=rows,sample_size_rule_sha256=sha(root/'sample_size.json'),pilot_report_sha256=sha(a.pilot),pilot_campaign_id=rule['pilot_campaign_id'],qualification_evidence_sha256={k:v['sha256'] for k,v in evidence.items()})
        put(ev/'formal_freeze.json',freeze);bind('pilot_completed_and_formal_freeze_recorded','formal_freeze',ev/'formal_freeze.json')
    put(root/'QUALIFICATION.json',qual)
    cli(hw/'plan_hardware.py',*params,'--qualification',root/'QUALIFICATION.json','--output',root/'plan')
    if read(root/'plan/plan.json')['execution_qualification']!='QUALIFIED_FOR_EXECUTION_BY_EXTERNAL_RUNNER':raise ValueError('qualification failed')
    extra=['--rule',root/'sample_size.json'] if phase=='formal' else []
    cli(exe,'--plan',root/'plan','--deployment',root/'bundles/deployment.json','--qualification',root/'QUALIFICATION.json','--freeze',root/'INPUT_FREEZE.json','--registry',root/'raw','--freeze-only',*extra)
    allfiles=sorted(p for p in root.rglob('*') if p.is_file())
    with (root/'SHA256SUMS.txt').open('x') as f:
        for p in allfiles:f.write(sha(p)+'  '+str(p.relative_to(root))+'\n')
    print('Frozen',root,flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser()
    for k in ('base','repo','rc1','original','corrected','profile','backlog','pilot'):p.add_argument('--'+k,type=Path,required=k in ('base','repo','rc1','original','corrected'))
    for k in ('phase','study','campaign','git'):p.add_argument('--'+k,required=True)
    p.add_argument('--management-map',type=Path)
    p.add_argument('--seed',type=int,required=True);p.add_argument('--workloads',nargs='+',required=True);p.add_argument('--rationale')
    p.add_argument('--backlog-qualification',action='store_true');main(p.parse_args())
