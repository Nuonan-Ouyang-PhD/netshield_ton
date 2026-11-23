"""Run the frozen padded-content queue on the three enrolled probes and the Mac Core."""
import argparse, ast, hashlib, inspect, itertools, json, math, os, secrets, socket, subprocess, sys, time
from collections import defaultdict
from contextlib import ExitStack
from pathlib import Path

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from stream_probe import send,receive

def digest(b):return hashlib.sha256(b).hexdigest()
def load(p):return json.loads(p.read_bytes())

def run(repo,hardware,lock,out):
    sys.path[:0]=[str(repo/'supporting_material/experiment_extension/evidence_value'),str(repo/'supporting_material/methodology_repair'),str(hardware/'code/formal_tools')]
    import run_content_study as study
    from simulation_primitives import waterfill
    from preflight import PROTOCOL,ssh_command
    out.mkdir(exist_ok=False)
    def log(v):
        print(json.dumps(v,separators=(',',':')),file=ledger,flush=True)
    dataset=load(ROOT/'cohort.json');x={r['source']+'-'+str(r['row']):r['values'] for r in dataset}
    plan=load(ROOT/'schedule.json');roles=['P1','P2','P3']
    assert not set(plan['ids'])-x.keys()
    model=load(ROOT/'information/consumer.json');light=load(ROOT/'information/alert.json')['light']
    probe=(ROOT/'stream_probe.py').read_text()+'\n'+inspect.getsource(study.encode)
    addr=load(ROOT/'ready/MAC.json')['wifi_ipv4']
    assert load(ROOT/'ready/PREFLIGHT_RESULT.json')['status']=='PASS'
    import fcntl
    with lock.open('a') as lease, ExitStack() as stack:
        fcntl.flock(lease,fcntl.LOCK_EX|fcntl.LOCK_NB)
        ledger=stack.enter_context((out/'ledger.jsonl').open('x'))
        listener=stack.enter_context(socket.socket());listener.bind((addr,0));listener.listen(3);listener.settimeout(45)
        processes={};tokens={r:secrets.token_hex(24) for r in roles}
        for role in roles:
            arms=[]
            for arm in plan['arms']:
                items=[{'id':group[role],'x':x[group[role]]} for group in arm['rounds'] if role in group]
                arms.append(dict(id=arm['id'],items=items,width=study.WIDTHS[arm['level']],size=plan['sizes'][arm['level']]))
            cfg=dict(role=role,address=addr,port=listener.getsockname()[1],source=PROTOCOL['management_ipv4'][role],token=tokens[role],light=light,arms=arms)
            code=probe+'\nmeasure(json.loads('+repr(json.dumps(cfg))+'))\n'
            err=stack.enter_context((out/(role+'.stderr')).open('xb'))
            proc=subprocess.Popen(ssh_command(role,'OPENBLAS_NUM_THREADS=1 python3 -B -'),stdin=subprocess.PIPE,stdout=err,stderr=err)
            processes[role]=proc
            stack.callback(lambda p=proc:p.terminate() if p.poll() is None else None)
            proc.stdin.write(code.encode());proc.stdin.close()
        ch={};boots={}
        for _ in roles:
            sock,peer=listener.accept();stack.enter_context(sock);sock.settimeout(25)
            sock.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,1);stream=stack.enter_context(sock.makefile('rwb'))
            hello=receive(stream);role=hello['role']
            assert role not in ch and hello['token']==tokens[role] and peer[0]==PROTOCOL['management_ipv4'][role]
            ch[role]=stream;boots[role]=hello['boot']
        log({'boot':boots,'wall_ns':time.time_ns(),'probe_source_sha256':digest(probe.encode())})
        for arm in plan['arms']:
            level=arm['level'];size=plan['sizes'][level];width=1+8*study.WIDTHS[level]
            buffers={};created={};done=set();tick=0
            while tick<len(arm['rounds']) or len(done)<len(created):
                assert tick<len(arm['rounds'])*4+10
                if tick:
                    time.sleep(max(0,(last_start+10**9-time.monotonic_ns())/1e9))
                last_start=time.monotonic_ns();gen=tick<len(arm['rounds'])
                for r in roles:send(ch[r],{'op':'tick','arm':arm['id'],'generate':gen})
                req={r:receive(ch[r]) for r in roles}
                for r,row in req.items():
                    c=row['created']
                    expected=arm['rounds'][tick].get(r) if gen else None
                    assert (c['id'] if c else None)==expected
                    if c:
                        assert expected not in created
                        buffers[expected]=bytearray();created[expected]=dict(c,role=r)
                grants=waterfill({r:v['demand'] for r,v in req.items()},131072,tie_offset=tick)
                for r in roles:send(ch[r],{'grant':grants[r]})
                segments={};results={}
                for r in roles:
                    pieces=receive(ch[r]);assert sum(p[2] for p in pieces)==grants[r];segments[r]=pieces
                    results[r]=[]
                    for identifier,off,n in pieces:
                        assert created[identifier]['role']==r and len(buffers[identifier])==off and 0<n<=size-off
                        data=ch[r].read(n);assert len(data)==n;buffers[identifier].extend(data)
                        if len(buffers[identifier])==size:
                            payload=bytes(buffers[identifier]);raw=payload[:width]
                            assert digest(payload)==created[identifier]['padded_hash'] and digest(raw)==created[identifier]['hash'] and not any(payload[width:])
                            start=time.monotonic_ns();score=study.consume(raw,model);end=time.monotonic_ns()
                            results[r].append(dict(id=identifier,score=score,decode_infer_ns=end-start,core_done=end));done.add(identifier)
                    for v in results[r]:send(ch[r],dict(op='result',id=v['id'],score=v['score']))
                    send(ch[r],{'op':'end'})
                receipts={r:receive(ch[r]) for r in roles}
                for r in roles:
                    assert [(v['id'],v['score']) for v in results[r]]==[(v['id'],v['score']) for v in receipts[r]['receipts']]
                log(dict(arm=arm['id'],level=level,tick=tick,start=last_start,requests=req,grants=grants,segments=segments,results=results,receipts=receipts))
                tick+=1
            for r in roles:send(ch[r],{'op':'finish'})
            for r in roles:assert receive(ch[r])=={'finished':arm['id']}
            log({'finished':arm['id'],'events':len(done)})
        for p in processes.values():assert p.wait(timeout=15)==0
        log({'completed':True})
if __name__=='__main__':
    run(*map(Path,sys.argv[1:]))
