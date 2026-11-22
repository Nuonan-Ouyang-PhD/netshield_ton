"""Bind frozen source row numbers to retained unlabelled per-capture CSVs."""
import hashlib
import itertools
import json
import math
import struct
import sys
from pathlib import Path


def signature(values):
    if len(values) != 39 or not all(math.isfinite(x) for x in values):
        raise ValueError("invalid feature vector")
    return hashlib.sha256(struct.pack(">39d", *values)).digest()


def trace(frozen, sources):
    manifest = json.loads((frozen/"dataset_manifest.json").read_bytes())
    source_by_group = {i["group_id"]:i for i in manifest["inputs"]}
    found = {}
    for split in ("train","validation","test"):
        with (frozen/(split+".jsonl")).open("rb") as stream:
            for group, batch in itertools.groupby(map(json.loads,stream),key=lambda r:r["group_id"]):
                meta=source_by_group[group]
                if meta["split"]!=split or group in found:
                    raise ValueError("source group identity")
                expected={}
                for row in batch:
                    n=row["row_number"]
                    if n in expected or row["label"]!=meta["binary_label"]:
                        raise ValueError("row identity")
                    expected[n]=signature(row["features"])
                original=Path(meta["path"])
                p=sources/original.parent.name/original.name
                filehash=hashlib.sha256()
                matched=0
                with p.open("rb") as f:
                    header=f.readline()
                    filehash.update(header)
                    if header.decode().strip().split(",")!=manifest["feature_names"]:
                        raise ValueError("source schema")
                    for n,line in enumerate(f,2):
                        filehash.update(line)
                        if n in expected:
                            if signature(list(map(float,line.split(b","))))!=expected.pop(n):
                                raise ValueError(f"feature mismatch at data row {n}")
                            matched+=1
                if expected or matched!=meta["sampled_rows"]:
                    raise ValueError("incomplete source coverage")
                found[group]=dict(split=split,matched=matched,original_csv_sha256=filehash.hexdigest(),
                                  labelled_csv_sha256=meta["sha256"])
    if set(found)!=set(source_by_group):
        raise ValueError("missing source group")
    return found


if __name__=="__main__":
    frozen,sources,out=map(Path,sys.argv[1:])
    result=trace(frozen,sources)
    with out.open("x") as f:
        json.dump(list(result.values()),f,indent=2)
