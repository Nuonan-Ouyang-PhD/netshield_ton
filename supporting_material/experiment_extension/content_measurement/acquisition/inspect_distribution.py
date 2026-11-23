"""Read the distribution archive without executing contents. Retain selected sources and their member paths."""
import hashlib, json, os, re, shutil, sys, tarfile, zipfile
from pathlib import Path
ROOT=Path('distribution');ROOT.mkdir(exist_ok=False)
register=json.loads(Path('input_audit.json').read_bytes())['register']
def stem(s):
    return re.sub('[^a-z0-9]','',re.sub(r'\.(pcapng|pcap)(\.csv)?$','',Path(s).name,flags=re.I).lower())
wanted={stem(r['member']) for r in register}
def consume(name,stream):
    lower=name.lower();base=Path(name).name
    relevant=stem(name) in wanted or ('readme' in base.lower() and lower.endswith(('.txt','.pdf','.md')))
    nested=lower.endswith('.zip') and not lower.startswith('bluetooth')
    if not (nested or relevant):return
    dest=ROOT/(hashlib.sha256(name.encode()).hexdigest()[:16]+'_'+base)
    with dest.open('xb') as out:shutil.copyfileobj(stream,out,4*1024*1024)
    if nested:
        with zipfile.ZipFile(dest) as z:
            for info in z.infolist():
                child=name+'!'+info.filename
                index.write(child+'\t'+str(info.file_size)+'\n')
                if not info.is_dir() and not Path(info.filename).name.startswith('._'):
                    with z.open(info) as f:consume(child,f)
    else:
        with dest.open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
        selected.append(dict(member=name,path=str(dest),sha256=digest,bytes=dest.stat().st_size))
selected=[]
with (ROOT/'members.tsv').open('x') as index,tarfile.open('source.tar.xz','r|xz') as t:
    for info in t:
        index.write(info.name+'\t'+str(info.size)+'\n');index.flush()
        if info.isfile() and not Path(info.name).name.startswith('._'):
            consume(info.name,t.extractfile(info))
(ROOT/'selected.json').write_text(json.dumps(selected,indent=2)+'\n')
