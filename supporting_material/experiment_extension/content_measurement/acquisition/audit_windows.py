import csv, hashlib, io, json, math, struct, zipfile
from collections import Counter, defaultdict
from pathlib import Path

def sha(data): return hashlib.sha256(data).hexdigest()

def main():
    design=json.loads(Path('design.json').read_bytes())
    manifest=next(Path('/Volumes/RESEARCH_DATA/10_PROJECTS/COMPLETE_RESEARCH_BY_SOURCE_PATH/ToN').glob('*/netshield-real-experiments/data/frozen/dataset_manifest.json'))
    names=json.loads(manifest.read_bytes())['feature_names']
    srcnames=['Duration' if n=='Time_To_Live' else n for n in names]
    register=[]; samples=[]; counts=defaultdict(Counter); subsets=defaultdict(Counter)
    with zipfile.ZipFile('profilling.zip') as benign, zipfile.ZipFile('attacks.zip') as attack:
        parents=[Path(n).name.removesuffix('.pcap.csv') for n in benign.namelist() if n.endswith('_Power.pcap.csv')]
        assert len(parents)==7
        parents.sort(key=lambda n:sha(('TON-IOMT-20261123|'+n).encode()))
        files=[(benign,'profilling_CSV/'+n+'.pcap.csv',n,split,0) for n,split in zip(parents,['train']*3+['validation']*2+['test']*2)]
        for n,split in [('ARP_Spoofing','train'),('Recon-Port_Scan','validation'),('MQTT-Malformed_Data','test')]:
            files.append((attack,'csv/train/'+n+'_train.pcap.csv',n,split,1))
        for z,path,parent,split,y in files:
            data=z.read(path);rows=csv.DictReader(io.StringIO(data.decode('utf-8-sig')));assert set(srcnames)<=set(rows.fieldnames)
            valid=[];invalid=0
            for i,row in enumerate(rows,2):
                try:
                    v=[float(row[n]) or 0.0 for n in srcnames]
                    if not all(map(math.isfinite,v)):raise ValueError
                except (ValueError,TypeError):invalid+=1;continue
                exact=sha(struct.pack('>39d',*v));near=sha(struct.pack('>39d',*(float(format(n,'.3g')) for n in v)))
                counts['exact'][exact,split]+=1;counts['rounded'][near,split]+=1
                rank=sha(f'TON-IOMT-20261123|{Path(path).name}|{i}'.encode())
                valid.append((rank,i,v,exact,near))
            chosen=sorted(valid)[:24];digest=sha(data)
            for rank,i,v,exact,near in chosen:
                subsets['exact'][exact,split]+=1;subsets['rounded'][near,split]+=1
                samples.append(dict(parent=parent,split=split,y=y,source=digest,row=i,values=v,exact=exact,rounded=near,rank=rank))
            register.append(dict(parent=parent,split=split,archive=z.filename,member=path,sha256=digest,rows=len(valid)+invalid,nonfinite=invalid,selected=len(chosen)))
    def matches(c):
        by_sig=defaultdict(dict)
        for (key,split),n in c.items():by_sig[key][split]=n
        return {k:v for k,v in by_sig.items() if len(v)>1}
    r={}
    for scope,cs in [('all_rows',counts),('frozen_sample',subsets)]:
        r[scope]={}
        for kind,c in cs.items():
            m=matches(c);Path(scope+'_'+kind+'_matches.json').write_text(json.dumps(m,sort_keys=True))
            r[scope][kind]=dict(signatures=len(m),rows=sum(sum(x.values()) for x in m.values()),compared_rows=c.total())
    Path('cohort.json').write_text(json.dumps(samples));Path('input_audit.json').write_text(json.dumps(dict(design=sha(Path('design.json').read_bytes()),features=names,register=register,overlap=r),indent=2))
    print(r)
if __name__=='__main__':main()
