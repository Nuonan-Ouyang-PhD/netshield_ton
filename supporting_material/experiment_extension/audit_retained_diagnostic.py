"""Reconcile archived prediction records and search the actual selected rows."""
import argparse
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np


def require(condition, message):
    if not condition:
        raise ValueError(message)


def fingerprint(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(2**20), b""):
            h.update(block)
    return h.hexdigest()


def signatures(rows):
    a = np.asarray([r["features"] for r in rows], dtype=float)
    require(a.shape == (len(rows),39) and np.isfinite(a).all(), "bad feature matrix")
    a[a == 0] = 0
    scale = 10 ** (2 - np.floor(np.log10(np.where(a == 0, 1, abs(a)))))
    q = np.rint(a * scale) / scale
    require(np.isfinite(q).all(), "nonfinite bucket")
    q[q == 0] = 0
    return zip(a.astype(">f8").view("V312").ravel().tolist(),
               q.astype(">f8").view("V312").ravel().tolist())


def batches(path):
    with path.open("rb") as f:
        while lines := list(itertools.islice(f, 8192)):
            yield [json.loads(line) for line in lines]


def run(root, retained, runtime, output):
    corpus = root/"data/frozen"
    modeldir = runtime/"artifacts/portable_models"
    inputs = {n:corpus/(n+".jsonl") for n in ("train","validation","test")}
    inputs.update({p.name:p for p in retained.iterdir() if p.is_file()})
    inputs.update({p.name:p for p in modeldir.iterdir() if p.is_file()})
    inputs.update({p.name:p for p in (root/"artifacts/models").iterdir() if p.is_file()})
    inputs["dataset_manifest.json"] = corpus/"dataset_manifest.json"
    for name in ("content_diagnostic.py","CONTENT_PROTOCOL.md"):
        inputs[name] = Path(__file__).with_name(name)
    hashes = {k:fingerprint(p) for k,p in inputs.items()}
    portable = json.loads(inputs["portable_manifest.json"].read_bytes())
    training = json.loads(inputs["model_manifest.json"].read_bytes())
    require(portable["source_model_manifest_sha256"]==hashes["model_manifest.json"],"training manifest")
    for k in ("train","validation"):
        require(training[k+"_sha256"]==hashes[k], k)
    for k, m in portable["models"].items():
        require(hashes[k+".npz"]==m["sha256"] and hashes[k+".pkl"]==m["source_pickle_sha256"],k)
    occurrences = [json.loads(l) for l in inputs["occurrences.jsonl"].read_bytes().splitlines()]
    keys = {r["event_id"]:(r["group_id"],r["label"]) for r in occurrences}
    require(len(keys)==len(occurrences)==896,"occurrence census")
    groups = sorted({g for g,y in keys.values()})
    selected = {}
    prefixes = Counter()
    for batch in batches(inputs["test"]):
        for r in batch:
            g = r["group_id"]
            if prefixes[g]<128:
                key = r["event_id"]
                require(key not in selected and keys.get(key)==(g,r["label"]),"prefix identity")
                selected[key]=r
            prefixes[g]+=1
    require(set(selected)==set(keys) and len(groups)==len(prefixes)==7,"test coverage")
    pairs = dict(zip(selected,signatures(list(selected.values()))))
    lookup = [{p[i]:0 for p in pairs.values()} for i in range(2)]
    for bit,split in enumerate(("train","validation")):
        for batch in batches(inputs[split]):
            for pair in signatures(batch):
                for i,v in enumerate(pair):
                    if v in lookup[i]:
                        lookup[i][v] |= 1<<bit
    seen=set()
    conf=defaultdict(lambda:defaultdict(Counter))
    for line in inputs["predictions.jsonl"].read_bytes().splitlines():
        r=json.loads(line)
        e,l=r["event"],r["level"]
        require(l in ("alert","summary","full") and (e,l) not in seen,"prediction identity")
        seen.add((e,l))
        g,y=keys[e]
        require(y in (0,1) and r["predicted"] in (0,1),"label")
        conf[l][g][("TN","FP","FN","TP")[2*y+r["predicted"]]]+=1
    require(len(seen)==2688,"incomplete pairing")
    old=json.loads(inputs["results.json"].read_bytes())
    result=[]
    for j,g in enumerate(groups):
        ids=[e for e,(file,y) in keys.items() if file==g]
        require(len(ids)==128,"file size")
        record=dict(group=f"G{j+1:02d}",generated=len(ids))
        for i,name in enumerate(("exact","rounded")):
            flags=Counter(lookup[i][pairs[e][i]] for e in ids)
            record[name]=dict(train_only=flags[1], validation_only=flags[2],
                              both=flags[3],neither=flags[0],
                              unique_within_file=len({pairs[e][i] for e in ids}))
        for l in ("alert","summary","full"):
            require(dict(conf[l][g])==old[l]["groups"][g],"per-file result")
            record[l]=dict(conf[l][g])
        result.append(record)
    for l in conf:
        require(dict(sum(conf[l].values(),Counter()))==old[l]["pooled"],"pooled result")
    with output.open("x") as f:
        json.dump(dict(files=result,sha256=hashes,unique_vectors_in_subset=[
            len(lookup[0]),len(lookup[1])]),f,indent=2)


if __name__=="__main__":
    p=argparse.ArgumentParser()
    for name in ("root","retained","runtime","output"):
        p.add_argument(name,type=Path)
    run(**vars(p.parse_args()))
