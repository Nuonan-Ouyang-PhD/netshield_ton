"""Verify distribution bytes, paired names and source capture time boundaries."""
from pathlib import Path
import hashlib, json, subprocess, csv, re
def read(p):return json.loads(Path(p).read_bytes())
def norm(s):return re.sub('[^a-z0-9]','',s.lower())
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
v=read('distribution/selected.json');a=read('input_audit.json');out=[]
for parent in a['register']:
    orig=[x for x in v if x['sha256']==parent['sha256']]
    name=Path(parent['member']).name.removesuffix('.csv');prefix=name.rsplit('.',1)[0]
    cand=[x for x in v if Path(x['member']).suffix.lower() in ('.pcap','.pcapng') and norm(Path(x['member']).stem)==norm(prefix)]
    if not orig or len({x['sha256'] for x in cand})!=1:
        raise ValueError((parent['parent'],len(orig),[x['member'] for x in cand]))
    orig.sort(key=lambda x:('!' in x['member'],x['member']));cand.sort(key=lambda x:('!' in x['member'],x['member']));c=cand[0]; fields=subprocess.check_output(['./capture_bounds',c['path']],text=True).rstrip().split('\t')
    n,first,last,lo,hi=map(int,fields[1:]);assert n>0 and lo<=first<=hi and lo<=last<=hi
    out.append(dict(parent=parent['parent'],split=parent['split'],csv_member=orig[0]['member'],csv_byte_identical_members=[x['member'] for x in orig],csv_sha256=orig[0]['sha256'],rows=parent['rows'],capture_member=c['member'],capture_byte_identical_members=[x['member'] for x in cand],capture_sha256=c['sha256'],capture_bytes=c['bytes'],packets=n,first_us=first,last_us=last,min_us=lo,max_us=hi))
overlaps=[]
for i,x in enumerate(out):
    for y in out[:i]:
        if x['split']!=y['split'] and max(x['min_us'],y['min_us'])<=min(x['max_us'],y['max_us']):overlaps.append([x['parent'],y['parent']])
report=dict(passed=not overlaps,between_split_time_overlaps=overlaps,source_url='https://www.unb.ca/cic/datasets/iomt-dataset-2024.html',distribution_mirror='https://www.kaggle.com/datasets/cyberdeeplearning/ciciomt2024',distribution_sha256=sha('original.zip'),paper='https://www.sciencedirect.com/science/article/pii/S2542660524002920',protocol_reference='Dadkhah et al., Wi-Fi power experiments and data processing; seven devices powered individually with remaining devices disconnected; attack conditions are separately defined experiments. Each selected feature file is for one named PCAP. Whole device/scenario capture kept in a single split. Absolute inter-packet time and filenames are excluded as predictors; IAT is a frozen field.',sources=out)
with Path('parent_evidence.json').open('x') as f:json.dump(report,f,indent=2)
print('registered',len(out),'overlap',overlaps);assert not overlaps
