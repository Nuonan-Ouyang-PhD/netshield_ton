"""Run the preregistered archived-split diagnostic. Outputs are private."""
import argparse
import hashlib
import itertools
import json
import struct
import sys
from collections import Counter
from pathlib import Path

import numpy as np


def batches(stream, n=8192):
    while lines := list(itertools.islice(stream, n)):
        yield [json.loads(line) for line in lines]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    for arg in ("runtime", "dataset", "output"):
        parser.add_argument(arg, type=Path)
    args = parser.parse_args()
    args.output.mkdir(exist_ok=False)
    sys.path.insert(0, str(args.runtime.resolve()))
    from netshield.portable_models import load_portable_model
    from netshield.identity_manifest import validate_runtime_identity_manifest
    models = args.runtime / "artifacts/portable_models"
    validate_runtime_identity_manifest(models)
    light = load_portable_model(models / "light.npz")
    seen = {}
    overlap = {}
    selected = {}
    for bit, split in enumerate(("train", "validation", "test")):
        grouped = Counter()
        sample = []
        matches = total = 0
        with (args.dataset / (split + ".jsonl")).open("rb") as f:
            for rows in batches(f):
                x = np.asarray([r["features"] for r in rows], dtype=float)
                assert x.shape[1] == 39 and np.isfinite(x).all()
                scale = 10 ** (2 - np.floor(np.log10(np.where(x == 0, 1, abs(x)))))
                quant = np.rint(x * scale) / scale
                quant[quant == 0] = 0
                for r, v in zip(rows, quant.astype(">f8")):
                    key = hashlib.sha256(v.tobytes()).digest()
                    prev = seen.get(key, 0)
                    matches += bool(prev & ((1 << bit) - 1))
                    seen[key] = prev | (1 << bit)
                    if grouped[r["group_id"]] < 128:
                        sample.append(r)
                    grouped[r["group_id"]] += 1
                    total += 1
        overlap[split] = dict(rows=total, matching_earlier=matches)
        selected[split] = sample
    dest = args.output
    (dest / "overlap.json").write_text(json.dumps(overlap))
    training = selected["train"]
    x = np.array([r["features"] for r in training])
    y = np.array([r["label"] for r in training])
    states = []
    for label in (0, 1):
        a = x[y == label]
        prob = (1 + sum(light.predict_attack_probability(v) >= .5 for v in a)) / (2 + len(a))
        states.append((len(a)/len(x), prob, a.mean(axis=0), np.maximum(a.var(axis=0), 1e-8)))
    weights = json.dumps([[p,b,m.tolist(),v.tolist()] for p,b,m,v in states]).encode()
    (dest / "consumer.json").write_bytes(weights)

    def encode(features, n):
        bit = int(light.predict_attack_probability(features) >= .5)
        return struct.pack(">B" + "d"*n, bit, *features[:n])

    def consume(payload):
        n = (len(payload)-1)//8
        alert, *obs = struct.unpack(">B" + "d"*n, payload)
        scores = []
        for p, b, m, v in states:
            likelihood = np.log(v[:n]) + (obs-m[:n])**2/v[:n]
            scores.append(np.log(p) + np.log(b if alert else 1-b) - likelihood.sum()/2)
        return int(scores[1] >= scores[0])

    test = selected["test"]
    (dest / "occurrences.jsonl").write_text("".join(json.dumps(
        {k:r[k] for k in ("event_id","group_id","label")})+"\n" for r in test))
    results = {}
    with (dest / "predictions.jsonl").open("x") as f:
        for name, n in (("alert",0), ("summary",4), ("full",39)):
            counts = Counter()
            groups = {}
            for r in test:
                payload = encode(r["features"], n)
                pred = consume(payload)
                outcome = ("TN","FP","FN","TP")[int(r["label"])*2+pred]
                counts[outcome] += 1
                groups.setdefault(r["group_id"], Counter())[outcome] += 1
                print(json.dumps(dict(event=r["event_id"], level=name, predicted=pred,
                                      sha256=digest(payload), bytes=len(payload))), file=f)
            results[name] = dict(pooled=counts, groups=groups)
    (dest / "results.json").write_text(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
