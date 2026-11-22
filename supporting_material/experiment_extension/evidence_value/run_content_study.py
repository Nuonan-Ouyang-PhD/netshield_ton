"""Fit and execute the information-only study on a provenance-qualified split."""

import argparse
import csv
import hashlib
import json
import math
import sqlite3
import struct
import sys
import time
from collections import Counter
from contextlib import ExitStack
from pathlib import Path

import numpy as np

import score_evidence_value as scorer

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "source_lineage"))
from prepare_capture_split import prepare, read_trace

WIDTHS = {"alert": 0, "summary": 4, "full": 39}
LABELS = ["benign", "attack"]
CUTOFFS = (0.25, 0.5, 0.75)
require = scorer.require


def save(path, value):
    with path.open("x") as stream:
        json.dump(value, stream, sort_keys=True, indent=2, allow_nan=False)
        stream.write("\n")


def writer(stack, path, fields):
    stream = stack.enter_context(path.open("x", newline=""))
    out = csv.DictWriter(stream, fieldnames=fields)
    out.writeheader()
    return out


def digest(data):
    return hashlib.sha256(data).hexdigest()


def add_sources(db, output, dataset, trace, bindings):
    meta = scorer.read_json(dataset / "dataset_manifest.json")
    names = meta["feature_names"]
    require(
        len(names) == len(set(names)) == 39, "expected 39 distinct ordered features"
    )
    by_labelled = {row["labelled_csv_sha256"]: row for row in read_trace(trace)}
    groups = {
        row["original_csv_sha256"]: row
        for row in scorer.read_csv(
            output / "source_groups.csv",
            ("original_csv_sha256", "parent_capture_id", "split"),
        )
    }
    files = {row["group_id"]: row for row in meta["inputs"]}
    require(
        len(files) == len(meta["inputs"]) == len(by_labelled)
        and {row["sha256"] for row in files.values()} == set(by_labelled),
        "frozen file inventory differs from trace",
    )
    db.execute(
        "CREATE TABLE samples (id TEXT PRIMARY KEY, parent TEXT, split TEXT, y INT, x BLOB, exact TEXT, rounded TEXT)"
    )
    counts = Counter()
    with ExitStack() as stack:
        corpus = writer(stack, output / "corpus.csv", scorer.CORPUS_FIELDS)
        events = writer(stack, output / "occurrences.csv", scorer.OCCURRENCE_FIELDS)
        for archived_split in scorer.SPLITS:
            path = dataset / (archived_split + ".jsonl")
            checksum = hashlib.sha256()
            with path.open("rb") as source:
                for line in source:
                    checksum.update(line)
                    row = json.loads(line)
                    src = files[row["group_id"]]
                    old = by_labelled[src["sha256"]]
                    key = old["original_csv_sha256"]
                    assignment = groups[key]
                    parent, split = assignment["parent_capture_id"], assignment["split"]
                    y, number = row["label"], row["row_number"]
                    require(
                        old["split"] == archived_split == src["split"]
                        and type(y) is int
                        and y in (0, 1)
                        and y == src["binary_label"]
                        and type(number) is int
                        and number >= 2,
                        "source row identity mismatch",
                    )
                    values = [float(v) or 0.0 for v in row["features"]]
                    require(
                        len(values) == 39 and all(map(math.isfinite, values)),
                        "invalid feature vector",
                    )
                    packed = struct.pack(">39d", *values)
                    exact = digest(packed)
                    rounded = digest(
                        struct.pack(">39d", *(float(format(v, ".3g")) for v in values))
                    )
                    identifier = f"{key}-{number}"
                    db.execute(
                        "INSERT INTO samples VALUES (?,?,?,?,?,?,?)",
                        (identifier, parent, split, y, packed, exact, rounded),
                    )
                    base = dict(
                        source_record_id=identifier,
                        group_id=parent,
                        split=split,
                        source_feature_sha256=exact,
                    )
                    corpus.writerow(dict(base, truth_raw=str(y)))
                    if split == "test":
                        events.writerow(
                            dict(base, occurrence_id=identifier, truth_label=LABELS[y])
                        )
                    counts[src["sha256"]] += 1
            require(
                checksum.hexdigest() == bindings[path.name],
                "frozen row stream digest mismatch",
            )
    require(
        counts == {k: v["matched"] for k, v in by_labelled.items()},
        "incomplete traced cohort",
    )
    db.execute("CREATE INDEX split_index ON samples(split)")
    db.commit()
    return names


def audit(db, output):
    overlaps = {}
    for kind in ("exact", "rounded"):
        matches = db.execute(
            f"SELECT {kind},split,count(*) FROM samples WHERE {kind} IN "
            f"(SELECT {kind} FROM samples GROUP BY {kind} HAVING count(DISTINCT split)>1) "
            f"GROUP BY {kind},split ORDER BY {kind},split"
        )
        count = 0
        with (output / (kind + "_matches.csv")).open("x", newline="") as stream:
            out = csv.writer(stream)
            out.writerow(("signature", "split", "rows"))
            for row in matches:
                out.writerow(row)
                count += row[2]
        overlaps[kind] = count
    save(
        output / "overlap.json",
        dict(
            cross_split_rows=overlaps,
            method="SHA-256 of 39 ordered big-endian binary64 values, signed zero normalized. "
            "Near candidates use Python .3g decimal rounding per raw coordinate before packing. "
            "All rows and splits searched. Rounding-boundary neighbours can be missed. "
            "A cross-split signature blocks fitting; no rows are dropped.",
            tables={k: scorer.sha256(output / (k + "_matches.csv")) for k in overlaps},
        ),
    )
    require(
        not any(overlaps.values()), "cross-split overlap; see retained match tables"
    )
    support = list(
        db.execute(
            "SELECT split,y,count(distinct parent) FROM samples GROUP BY split,y"
        )
    )
    require(len(support) == 6, "both binary classes required in every split")
    require(
        db.execute(
            "SELECT count(DISTINCT parent) FROM samples WHERE split='test'"
        ).fetchone()[0]
        >= 2,
        "need at least two independent test captures",
    )


def batches(db, split):
    cursor = db.execute(
        "SELECT x,y FROM samples WHERE split=? ORDER BY rowid", (split,)
    )
    while rows := cursor.fetchmany(2048):
        x = np.frombuffer(b"".join(blob for blob, _ in rows), dtype=">f8").reshape(
            -1, 39
        )
        yield x, np.array([y for _, y in rows])


def train(db):
    # Pooled population moments combine batches without subtracting large raw squares.
    counts = np.zeros(2, dtype=int)
    means, sums = np.zeros((2, 39)), np.zeros((2, 39))
    for x, y in batches(db, "train"):
        for label in (0, 1):
            a = x[y == label]
            if len(a):
                n = counts[label] + len(a)
                delta = a.mean(axis=0) - means[label]
                sums[label] += (
                    a.var(axis=0) * len(a) + delta**2 * counts[label] * len(a) / n
                )
                means[label] += delta * (len(a) / n)
                counts[label] = n
    center = np.average(means, axis=0, weights=counts)
    scale = np.sqrt(
        np.sum(sums + counts[:, None] * (means - center) ** 2, axis=0) / counts.sum()
    )
    scale[scale == 0] = 1
    weights, intercept = np.zeros(39), 0.0
    for _ in range(32):
        gradient, bias = np.zeros(39), 0.0
        for x, y in batches(db, "train"):
            z = (x - center) / scale
            error = np.exp(-np.logaddexp(0, -(z @ weights + intercept))) - y
            gradient += z.T @ error
            bias += error.sum()
        weights -= 0.05 * (gradient / counts.sum() + 0.0001 * weights)
        intercept -= 0.05 * bias / counts.sum()
    light = dict(
        center=center.tolist(),
        scale=scale.tolist(),
        weights=weights.tolist(),
        intercept=intercept,
    )
    ones = np.zeros(2)
    for x, y in batches(db, "train"):
        bits = ((x - center) / scale) @ weights + intercept >= 0
        ones += np.bincount(y[bits], minlength=2)
    model = dict(
        prior=(counts / counts.sum()).tolist(),
        bit=((ones + 1) / (counts + 2)).tolist(),
        mean=means.tolist(),
        variance=np.maximum(sums / counts[:, None], 1e-8).tolist(),
    )
    return light, model


def encode(values, width, light):
    z = (values - light["center"]) / light["scale"]
    bit = int(z @ light["weights"] + light["intercept"] >= 0)
    return struct.pack(">B" + "d" * width, bit, *values[:width])


def consume(payload, model):
    width = (len(payload) - 1) // 8
    bit, *x = struct.unpack(">B" + "d" * width, payload)
    require(width in WIDTHS.values() and bit in (0, 1), "invalid encoded observation")
    logs = []
    for label in (0, 1):
        b = model["bit"][label]
        evidence = sum(
            math.log(v) + (value - m) ** 2 / v
            for value, m, v in zip(x, model["mean"][label], model["variance"][label])
        )
        logs.append(
            math.log(model["prior"][label])
            + math.log(b if bit else 1 - b)
            - evidence / 2
        )
    score = float(np.exp(-np.logaddexp(0, logs[0] - logs[1])))
    require(math.isfinite(score), "nonfinite model output")
    return score


def threshold(db, light, model):
    correct, counts = np.zeros((len(CUTOFFS), 2)), np.zeros(2)
    for x, y in batches(db, "validation"):
        for values, label in zip(x, y):
            for width in WIDTHS.values():
                score = consume(encode(values, width, light), model)
                counts[label] += 1
                for i, cutoff in enumerate(CUTOFFS):
                    correct[i, label] += (score >= cutoff) == label
    balanced = (correct / counts).mean(axis=1)
    return max(zip(balanced, CUTOFFS), key=lambda p: (p[0], -abs(p[1] - 0.5), -p[1]))[1]


def infer(db, output, artifacts, light, model, cutoff):
    with ExitStack() as stack:
        predictions = writer(
            stack, output / "predictions.csv", scorer.PREDICTION_FIELDS
        )
        calls = stack.enter_context((output / "calls.jsonl").open("x"))
        blobs = stack.enter_context((output / "payloads.bin").open("xb"))
        for identifier, blob, truth, source_hash in db.execute(
            "SELECT id,x,y,exact FROM samples WHERE split='test' ORDER BY rowid"
        ):
            x = np.frombuffer(blob, dtype=">f8")
            for level, width in WIDTHS.items():
                row = dict(
                    occurrence_id=identifier,
                    representation=level,
                    split="test",
                    truth_label=LABELS[truth],
                    source_feature_sha256=source_hash,
                    model_id=artifacts["model"]["id"],
                    threshold_id=artifacts["threshold"]["id"],
                    encoder_id=artifacts["encoders"][level]["id"],
                )
                call = dict(
                    occurrence_id=identifier, representation=level, fields=width + 1
                )
                start = time.perf_counter_ns()
                try:
                    payload = encode(x, width, light)
                    call["encode_ns"] = time.perf_counter_ns() - start
                    call["offset"] = blobs.tell()
                    blobs.write(payload)
                    h = digest(payload)
                    row.update(
                        information_bytes=len(payload),
                        payload_bytes=len(payload),
                        padding_bytes=0,
                        representation_sha256=h,
                        payload_sha256=h,
                    )
                    start = time.perf_counter_ns()
                    score = consume(payload, model)
                    call["consumer_ns"] = time.perf_counter_ns() - start
                    row.update(
                        status="returned",
                        positive_score=score,
                        predicted_label=LABELS[int(score >= cutoff)],
                    )
                except (ArithmeticError, ValueError, struct.error) as exc:
                    row.update(status="missing", status_detail=str(exc))
                    call["failed_stage_ns"] = time.perf_counter_ns() - start
                predictions.writerow(row)
                print(json.dumps(dict(call, status=row["status"])), file=calls)


def run(spec_path, output, fixture=False):
    root = spec_path.resolve().parent
    spec = scorer.read_json(spec_path)
    dataset = root / spec["dataset_directory"]
    trace = root / spec["trace"]
    for field in ("mapping", "trace", "split_assignment"):
        require(
            scorer.sha256(root / spec[field]) == spec["provenance_sha256"][field],
            f"changed provenance input: {field}",
        )
    output.mkdir(parents=True, exist_ok=False)
    prepared = prepare(
        root / spec["mapping"],
        root / spec["split_assignment"],
        output / "split",
        trace,
        fixture,
    )
    origin = prepared["data_origin"]
    inputs = spec["frozen_inputs_sha256"]
    require(
        set(inputs)
        == {"dataset_manifest.json", *(s + ".jsonl" for s in scorer.SPLITS)},
        "invalid frozen input inventory",
    )
    require(
        scorer.sha256(dataset / "dataset_manifest.json")
        == inputs["dataset_manifest.json"],
        "dataset manifest hash",
    )
    for filename in ("groups.csv", "source_groups.csv"):
        (output / filename).write_bytes((output / "split" / filename).read_bytes())
    paths = {
        k: output / (k + ".csv")
        for k in ("groups", "corpus", "occurrences", "predictions")
    }
    with ExitStack() as stack:
        db = sqlite3.connect(output / "study.sqlite")
        stack.callback(db.close)
        names = add_sources(db, output, dataset, trace, inputs)
        audit(db, output)
        light, model = train(db)
        cutoff = threshold(db, light, model)

        def artifact(name, value):
            path = output / (name + ".json")
            save(path, value)
            h = scorer.sha256(path)
            return dict(id=name + "-" + h, path=path.name, sha256=h)

        rule = dict(
            kind="positive_score_greater_than_or_equal",
            negative_label="benign",
            positive_label="attack",
            threshold=cutoff,
        )
        encoders = {
            k: artifact(
                k,
                dict(
                    light=light,
                    features=names,
                    appended=v,
                    layout=">B then ordered binary64",
                ),
            )
            for k, v in WIDTHS.items()
        }
        artifacts = dict(
            model=artifact("consumer", model),
            threshold=artifact("threshold", rule),
            encoders=encoders,
        )
        near_path = output / "overlap.json"
        protocol = dict(
            schema_version=scorer.SCHEMA,
            study_id=spec["study_id"],
            data_origin="SYNTHETIC_FIXTURE"
            if origin == "SYNTHETIC_FIXTURE"
            else "actual_runtime",
            phase="information_only",
            independence_unit="capture",
            group_definition=prepared["group_definition"],
            labels=LABELS,
            label_mapping={"0": "benign", "1": "attack"},
            dataset=dict(
                id=spec["study_id"],
                version=scorer.sha256(spec_path),
                population="all_generated_held_out_occurrences",
                **{
                    k + "_sha256": scorer.sha256(paths[k])
                    for k in ("groups", "corpus", "occurrences")
                },
            ),
            artifacts=artifacts,
            decision_rule=rule,
            transport=None,
            analysis=dict(
                primary_metric="correct_per_generated",
                primary_comparison=["full", "alert"],
                comparisons=[["full", "alert"], ["full", "summary"]],
                weighting="equal_group",
                bootstrap=dict(samples=2000, seed=20261122, confidence=0.95),
            ),
            near_duplicate_audit=dict(
                status="completed",
                method="Three significant decimal digits, all ordered features",
                threshold=3,
                artifact=dict(
                    id="overlap", path=near_path.name, sha256=scorer.sha256(near_path)
                ),
            ),
        )
        save(output / "protocol.json", protocol)
        save(
            output / "fit_identity.json",
            dict(
                spec_sha256=scorer.sha256(spec_path),
                frozen_inputs=inputs,
                runner_sha256=scorer.sha256(Path(__file__)),
                split_report_sha256=scorer.sha256(
                    output / "split/CAPTURE_MAPPING_REPORT.json"
                ),
                protocol_sha256=scorer.sha256(output / "protocol.json"),
                python=sys.version,
                numpy=np.__version__,
            ),
        )
        infer(db, output, artifacts, light, model, cutoff)
    result = scorer.score_study(
        output / "protocol.json", paths, allow_synthetic_fixture=fixture
    )
    save(output / "score.json", result)
    save(
        output / "hashes.json",
        {p.name: scorer.sha256(p) for p in sorted(output.iterdir()) if p.is_file()},
    )
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--allow-synthetic-fixture", action="store_true")
    args = parser.parse_args()
    run(args.spec, args.output, args.allow_synthetic_fixture)
