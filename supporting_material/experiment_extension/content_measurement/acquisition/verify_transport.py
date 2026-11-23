"""Reconcile every registered observation against physical byte service and origin-clock results."""
import csv, hashlib, itertools, json, shutil, sys
from collections import Counter
from pathlib import Path

def readfile(p):return json.loads(p.read_bytes())
def writefile(p,obj):
    with p.open('x') as f:json.dump(obj,f,indent=2,allow_nan=False);f.write('\n')

def setup(source,dest):
    dest.mkdir()
    proto=readfile(source/'protocol.json')
    for f in ('groups.csv','corpus.csv','occurrences.csv','consumer.json','threshold.json','alert.json','summary.json','full.json','overlap.json'):
        shutil.copyfile(source/f,dest/f)
    proto.update(phase='transport_measured',transport=dict(deadline_ns=10**9,anchor='event_creation',horizon_semantics='continuous_observation_through_inclusive_horizon',wire_accounting='measured_uplink_evidence_headers_and_retransmissions'))
    proto['analysis']['primary_metric']='timely_correct_per_generated'
    writefile(dest/'protocol.json',proto)

def analyze(repo,dest,attempt):
    sys.path.insert(0,str(repo/'supporting_material/experiment_extension/evidence_value'))
    import score_evidence_value as score
    proto=readfile(dest/'protocol.json');art=proto['artifacts']
    plan=readfile(Path('schedule.json'));scheduled={a['id']:a for a in plan['arms']}
    events={e['occurrence_id']:e for e in csv.DictReader((dest/'occurrences.csv').open())}
    assert set(events)==set(plan['ids'])
    led=[json.loads(l) for l in (attempt/'ledger.jsonl').read_text().splitlines()];assert led[-1]=={'completed':True}
    boots=led[0]['boot'];assert len(set(boots.values()))==3
    created={};returned={};horizon={};metrics=Counter();completed=[];sent=Counter()
    for row in led[1:-1]:
        if 'finished' in row:completed.append(row['finished']);continue
        arm=scheduled[row['arm']];level=arm['level'];tick=row['tick'];n=0
        for role,v in row['requests'].items():
            c=v['created'];expected=arm['rounds'][tick].get(role) if tick<len(arm['rounds']) else None
            assert (c['id'] if c else None)==expected
            if c:
                key=(c['id'],level);assert key not in created;created[key]=(role,c)
            gs=row['grants'][role];assert gs==sum(k[2] for k in row['segments'][role])<=v['demand'];n+=gs
            for ident,off,size in row['segments'][role]:
                k=ident,level;assert created[k][0]==role and sent[k]==off;sent[k]+=size
            rr=row['receipts'][role];horizon[(arm['id'],role)]=rr['horizon']
            for z in rr['receipts']:
                k=z['id'],level
                assert created[k][0]==role and k not in returned and sent[k]==plan['sizes'][level]
                returned[k]=arm['id'],z
        assert n==min(sum(v['demand'] for v in row['requests'].values()),131072)
        metrics['service_rounds']+=1;metrics['application_bytes']+=n
    assert completed==[a['id'] for a in plan['arms']]
    assert set(created)==set(returned)==set(itertools.product(events,score.LEVELS))
    with (dest/'predictions.csv').open('x',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=score.PREDICTION_FIELDS);writer.writeheader()
        for (ident,level),(role,c) in created.items():
            arm,res=returned[ident,level];item=events[ident];clk=role+'-'+boots[role];width={'alert':1,'summary':33,'full':313}[level];padded=plan['sizes'][level];cutoff=proto['decision_rule']['threshold']
            writer.writerow(dict(occurrence_id=ident,representation=level,split='test',truth_label=item['truth_label'],model_id=art['model']['id'],threshold_id=art['threshold']['id'],encoder_id=art['encoders'][level]['id'],source_feature_sha256=item['source_feature_sha256'],status='returned',predicted_label=proto['labels'][int(res['score']>=cutoff)],positive_score=res['score'],representation_sha256=c['hash'],payload_sha256=c['padded_hash'],information_bytes=width,padding_bytes=padded-width,payload_bytes=padded,created_ns=c['created'],created_clock_domain=clk,result_ns=res['returned'],result_clock_domain=clk,observed_until_ns=horizon[arm,role],observation_clock_domain=clk,time_source='measured'))
    results=score.score_study(dest/'protocol.json',{k:dest/(k+'.csv') for k in ('groups','corpus','occurrences','predictions')})
    writefile(dest/'score.json',results);writefile(dest/'service_audit.json',dict(**metrics,completed_miniblock_arms=len(completed),cap_violations=0,unreturned=len(created)-len(returned),evidence_wire_bytes_including_link_retransmissions='unobserved'))
if __name__=='__main__':
    if sys.argv[1]=='setup':setup(Path('information'),Path('transport'))
    else:analyze(Path(sys.argv[1]),Path('transport'),Path(sys.argv[2]))
