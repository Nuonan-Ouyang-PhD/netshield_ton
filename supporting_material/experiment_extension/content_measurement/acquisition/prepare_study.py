"""Bind independent acquisitions and a predetermined workload to the existing adapter."""
from pathlib import Path
import csv,hashlib,itertools,json,sys
def read(p):return json.loads(Path(p).read_bytes())
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def put(p,v):
    with Path(p).open('x') as f:json.dump(v,f,indent=2,allow_nan=False);f.write('\n')
def schedule():
    rows=read('cohort.json');test=[q for q in rows if q['split']=='test'];roles=['P1','P2','P3']
    parents=sorted({q['parent'] for q in test})
    byparent=[sorted([q for q in test if q['parent']==p],key=lambda q:q['rank']) for p in parents]
    seq=[v for triple in itertools.zip_longest(*byparent) for v in triple if v]
    ids=[v['source']+'-'+str(v['row']) for v in seq];rounds=[]
    for i in range(0,len(ids),3):
        rounds.append({roles[(j+i//3)%3]:v for j,v in enumerate(ids[i:i+3])})
    arms=[]
    for b,order in enumerate(itertools.permutations(sorted(['alert','summary','full']))):
        subset=rounds[b*len(rounds)//6:(b+1)*len(rounds)//6];assert subset
        for level in order:arms.append(dict(id=f'B{b+1:02d}_{level}',level=level,rounds=subset))
    put('schedule.json',dict(ids=ids,arms=arms,sizes=dict(alert=256,summary=16384,full=131072)))
def prepare(repo):
    root=Path('new_inputs');root.mkdir()
    a=read('input_audit.json');ev=read('parent_evidence.json');assert ev['passed']
    assert all(not v['rows'] for v in a['overlap']['frozen_sample'].values())
    cfg=read('design.json');rows=read('cohort.json');files=[];trace=[];sources=[]
    for rec in a['register']:
        p=rec['parent'];rs=[v for v in rows if v['parent']==p]
        labelled=root/(p+'.labelled.jsonl')
        with labelled.open('x') as f:
            for row in rs:print(json.dumps(dict(group_id=p,row_number=row['row'],label=row['y'],features=row['values'])),file=f)
        h=sha(labelled);files.append(dict(group_id=p,sha256=h,split=rec['split'],binary_label=rs[0]['y']))
        trace.append(dict(split=rec['split'],matched=len(rs),original_csv_sha256=rec['sha256'],labelled_csv_sha256=h))
        sources.append(dict(original_csv_sha256=rec['sha256'],parent_capture_id=p,evidence_ids=['parent_evidence']))
    for s in ('train','validation','test'):
        with (root/(s+'.jsonl')).open('xb') as f:
            for rec in files:
                if rec['split']==s:f.write((root/(rec['group_id']+'.labelled.jsonl')).read_bytes())
    put(root/'dataset_manifest.json',dict(feature_names=a['features'],inputs=files))
    put('trace.json',trace);put('mapping.json',dict(schema_version='netshield.source_capture_mapping.v1',data_origin='actual_provenance',group_definition='Each named isolated-device power-on or single short-window attack-scenario capture on the source testbed. All windows of a capture stay together.',evidence=[dict(id='parent_evidence',path='parent_evidence.json',sha256=sha('parent_evidence.json'))],sources=sources))
    with open('splits.csv','x',newline='') as f:
        ww=csv.writer(f);ww.writerow(['parent_capture_id','split']);ww.writerows((r['parent'],r['split']) for r in a['register'])
    paths=dict(trace='trace.json',mapping='mapping.json',split_assignment='splits.csv');put('spec.json',dict(study_id=cfg['study_id'],dataset_directory=str(root),**paths,provenance_sha256={k:sha(v) for k,v in paths.items()},frozen_inputs_sha256={n:sha(root/n) for n in ['dataset_manifest.json','train.jsonl','validation.jsonl','test.jsonl']}))
    paths=['design.json','schedule.json','audit_windows.py','input_audit.json','parent_evidence.json','spec.json','cohort.json','launch_transport.py','stream_probe.py','verify_transport.py','qualify.py','prepare_study.py']
    put('before_fit.json',dict(files={p:sha(p) for p in paths},model_runner=sha(repo/'supporting_material/experiment_extension/evidence_value/run_content_study.py')))
if __name__=='__main__':
    if sys.argv[1]=='schedule':schedule()
    else:prepare(Path(sys.argv[1]))
