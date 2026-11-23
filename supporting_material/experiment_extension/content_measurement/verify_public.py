"""Re-score the two phases and reconcile the published physical ledger in a temporary directory."""
from pathlib import Path
import csv, hashlib, json, os, shutil, sys, tempfile

root = Path(__file__).resolve().parent
repo = root.parents[2]
sys.path[:0] = [str(root.parent/'evidence_value'), str(root/'acquisition'), str(repo/'supporting_material/methodology_repair')]
from score_evidence_value import score_study
from verify_transport import analyze
from simulation_primitives import waterfill

def read(path): return json.loads(path.read_bytes())

def check(ok, message):
    if not ok: raise ValueError(message)

def verify_hash(path, expected):
    check(hashlib.sha256(path.read_bytes()).hexdigest() == expected, str(path))


freeze = read(root / 'before_fit.json')
for filename, expected in freeze['files'].items():
    if filename == 'cohort.json':
        continue  # Private raw feature vectors.
    folder = root / 'acquisition' if filename.endswith('.py') else root
    verify_hash(folder / filename, expected)
verify_hash(root.parent / 'evidence_value/run_content_study.py', freeze['model_runner'])
for filename, expected in read(root / 'before_transport.json').items():
    if filename != 'ready/PREFLIGHT_RESULT.json':  # Private endpoint inventory.
        verify_hash(root / filename, expected)
ledger = root / 'physical_ledger/ledger.jsonl'
verify_hash(ledger, read(root / 'identity.json')['published_ledger_sha256'])
for line in ledger.read_text().splitlines():
    record = json.loads(line)
    if 'grants' in record:
        demand = {role: request['demand'] for role, request in record['requests'].items()}
        expected = waterfill(demand, 131072, tie_offset=record['tick'])
        check(record['grants'] == expected, 'device grants differ from frozen allocator')

for phase in ('information','transport'):
    folder = root/phase
    inputs = {k:folder/(k+'.csv') for k in ('groups','corpus','occurrences','predictions')}
    actual = score_study(folder/'protocol.json', inputs)
    check(actual == read(folder/'score.json'), phase+' scoring mismatch')
    predictions = list(csv.DictReader(inputs['predictions'].open()))
    check(len(predictions)==216 and len({(v['occurrence_id'],v['representation']) for v in predictions})==216, 'incomplete matched panel')
    if phase=='information':
        keys = {(r['occurrence_id'],r['representation']):r for r in predictions}
    else:
        for r in predictions:
            ref=keys[r['occurrence_id'],r['representation']]
            for field in ('source_feature_sha256','representation_sha256','predicted_label','positive_score','truth_label','model_id','threshold_id'):
                check(ref[field]==r[field], 'on-device or consumer mismatch: '+field)
with tempfile.TemporaryDirectory() as tmp:
    out = Path(tmp)
    for p in (root/'transport').iterdir():
        if p.name not in ('predictions.csv','score.json','service_audit.json'):
            shutil.copyfile(p,out/p.name)
    os.chdir(root)
    analyze(repo,out,root/'physical_ledger')
    for name in ('predictions.csv','score.json','service_audit.json'):
        check((out/name).read_bytes()==(root/'transport'/name).read_bytes(),name)
evidence=read(root/'parent_evidence.json')['sources']
check(len({v['capture_sha256'] for v in evidence})==10,'capture identity count')
for i,a in enumerate(evidence):
    for b in evidence[:i]:
        if a['split']!=b['split']:
            check(a['max_us']<b['min_us'] or b['max_us']<a['min_us'],'overlapping capture times')
print('PASS: 10 capture identities, 72 matched windows, 216 predictions per phase, scores and measured service ledger.')
