"""The model is fitted and called only on explicitly synthetic observations."""

import csv
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import run_content_study as study


def fixture(root, overlap=False):
    traces, sources, meta = [], [], []
    streams = {s: [] for s in study.scorer.SPLITS}
    assignments = []
    for g, split in enumerate(("validation", "train", "test", "test")):
        parent = f"fixture-{g}"
        assignments.append(f"{parent},{split}")
        for label in (0, 1):
            i = 2 * g + label
            archived = ("train", "validation", "test")[i % 3]
            orig, tagged = [
                hashlib.sha256(f"{name}{i}".encode()).hexdigest()
                for name in ("raw", "labelled")
            ]
            traces.append(
                dict(
                    split=archived,
                    matched=2,
                    original_csv_sha256=orig,
                    labelled_csv_sha256=tagged,
                )
            )
            sources.append(
                dict(
                    original_csv_sha256=orig,
                    parent_capture_id=parent,
                    evidence_ids=["fixture"],
                )
            )
            meta.append(
                dict(group_id=str(i), sha256=tagged, split=archived, binary_label=label)
            )
            for n in (2, 3):
                base = 0 if overlap else i * 0.1
                v = [1 + j + n + base + label * 5.0 for j in range(39)]
                streams[archived].append(
                    json.dumps(
                        dict(group_id=str(i), row_number=n, label=label, features=v)
                    )
                )
    study.save(root / "trace.json", traces)
    study.save(
        root / "dataset_manifest.json",
        dict(inputs=meta, feature_names=[f"x{i}" for i in range(39)]),
    )
    for s, rows in streams.items():
        (root / (s + ".jsonl")).write_text("\n".join(rows) + "\n")
    (root / "groups.txt").write_text(
        "parent_capture_id,split\n" + "\n".join(assignments) + "\n"
    )
    (root / "evidence.txt").write_text("SYNTHETIC_FIXTURE generated groups")
    study.save(
        root / "mapping.json",
        dict(
            schema_version="netshield.source_capture_mapping.v1",
            data_origin="SYNTHETIC_FIXTURE",
            group_definition="Artificial test capture groups",
            evidence=[
                dict(
                    id="fixture",
                    path="evidence.txt",
                    sha256=study.scorer.sha256(root / "evidence.txt"),
                )
            ],
            sources=sources,
        ),
    )
    study.save(
        root / "spec.json",
        dict(
            study_id="SYNTHETIC_FIXTURE",
            dataset_directory=".",
            trace="trace.json",
            provenance_sha256={
                k: study.scorer.sha256(root / v)
                for k, v in {
                    "mapping": "mapping.json",
                    "trace": "trace.json",
                    "split_assignment": "groups.txt",
                }.items()
            },
            mapping="mapping.json",
            split_assignment="groups.txt",
            frozen_inputs_sha256={
                n: study.scorer.sha256(root / n)
                for n in (
                    "dataset_manifest.json",
                    "train.jsonl",
                    "validation.jsonl",
                    "test.jsonl",
                )
            },
        ),
    )
    return root / "spec.json"


class ContentStudyTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.out = self.root / "run"

    def test_fit_encode_infer_score_and_decode_all_payloads(self):
        report = study.run(fixture(self.root), self.out, True)
        self.assertEqual(report["data_origin"], "SYNTHETIC_FIXTURE")
        with (self.out / "predictions.csv").open() as stream:
            rows = list(csv.DictReader(stream))
        self.assertEqual(len(rows), 24)
        payloads = (self.out / "payloads.bin").read_bytes()
        model = json.loads((self.out / "consumer.json").read_bytes())
        calls = list(
            map(json.loads, (self.out / "calls.jsonl").read_text().splitlines())
        )
        self.assertEqual(len(calls), len(rows))
        for row, call in zip(rows, calls):
            n = int(row["payload_bytes"])
            self.assertEqual(n, 1 + 8 * study.WIDTHS[row["representation"]])
            payload = payloads[call["offset"] : call["offset"] + n]
            self.assertEqual(study.digest(payload), row["representation_sha256"])
            self.assertEqual(
                study.consume(payload, model), float(row["positive_score"])
            )

    def test_cross_split_duplicate_blocks_fitting(self):
        with self.assertRaisesRegex(ValueError, "overlap"):
            study.run(fixture(self.root, overlap=True), self.out, True)
        self.assertTrue((self.out / "overlap.json").exists())
        self.assertFalse((self.out / "consumer.json").exists())

    def test_fixture_cannot_run_as_real(self):
        with self.assertRaisesRegex(ValueError, "synthetic mapping"):
            study.run(fixture(self.root), self.out)

    def test_changed_input_fails_before_fit(self):
        spec = fixture(self.root)
        with (self.root / "train.jsonl").open("a") as f:
            f.write(" ")
        with self.assertRaises(ValueError):
            study.run(spec, self.out, True)
        self.assertFalse((self.out / "consumer.json").exists())

    def test_missing_consumer_result_keeps_denominator(self):
        original = study.consume

        def fail_one(payload, model):
            if (self.out / "protocol.json").exists() and len(payload) == 313:
                raise ValueError("synthetic consumer fault")
            return original(payload, model)

        with patch.object(study, "consume", fail_one):
            result = study.run(fixture(self.root), self.out, True)
        self.assertEqual(result["pooled_by_representation"]["full"]["scored"], 0)
        self.assertEqual(result["pooled_by_representation"]["full"]["generated"], 8)
