#!/usr/bin/env python3
"""Score actual matched evidence-value observations without running any model.

The contract is intentionally binary and fail closed. Synthetic data are
accepted only through an explicit fixture opt-in and remain labelled synthetic.
See README.md for denominator, censoring, clock and bootstrap semantics.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

SCHEMA = "netshield.evidence_value.v1"
LEVELS = ("alert", "summary", "full")
SPLITS = ("train", "validation", "test")
STATUSES = ("returned", "rejected", "missing", "censored")
GROUP_FIELDS = ("group_id", "split")
CORPUS_FIELDS = ("source_record_id", "group_id", "split", "truth_raw", "source_feature_sha256")
OCCURRENCE_FIELDS = ("occurrence_id", "source_record_id", "group_id", "split", "truth_label", "source_feature_sha256")
PREDICTION_FIELDS = (
    "occurrence_id", "representation", "split", "truth_label", "model_id", "encoder_id", "threshold_id",
    "status", "status_detail", "predicted_label", "positive_score", "source_feature_sha256",
    "representation_sha256", "payload_sha256", "information_bytes", "padding_bytes", "payload_bytes", "wire_bytes",
    "created_ns", "created_clock_domain", "result_ns", "result_clock_domain",
    "observed_until_ns", "observation_clock_domain", "time_source",
)
HASH_RE = re.compile(r"[0-9a-f]{64}\Z")
MAX_INT = (1 << 63) - 1


class ContractError(ValueError):
    """Input is inconsistent with the predeclared scoring contract."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def exact_keys(value: Any, keys: set[str], context: str) -> dict:
    require(isinstance(value, dict), f"{context}: expected an object")
    require(set(value) == keys, f"{context}: expected keys {sorted(keys)}, got {sorted(value)}")
    return value


def nonempty(value: Any, context: str) -> str:
    require(isinstance(value, str) and bool(value.strip()) and value == value.strip(), f"{context}: expected nonempty unpadded string")
    return value


def natural(value: Any, context: str) -> int:
    require(type(value) is int and 0 <= value <= MAX_INT, f"{context}: expected nonnegative 64-bit integer")
    return value


def csv_int(value: str, context: str, *, optional: bool = False) -> int | None:
    if value == "" and optional:
        return None
    require(len(value) <= 19 and bool(re.fullmatch(r"[0-9]+", value)), f"{context}: expected nonnegative 64-bit integer, not {value!r}")
    return natural(int(value), context)


def finite(value: Any, context: str) -> float:
    require(type(value) in (float, int), f"{context}: expected a number")
    result = float(value)
    require(math.isfinite(result), f"{context}: nonfinite number")
    return result


def content_hash(value: str, context: str, *, optional: bool = False) -> str:
    require((optional and value == "") or (isinstance(value, str) and bool(HASH_RE.fullmatch(value))), f"{context}: expected lowercase SHA-256")
    return value


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def reject_json_constant(value: str) -> None:
    raise ContractError(f"JSON nonfinite constant is forbidden: {value}")


def unique_json_object(pairs: list[tuple[str, Any]]) -> dict:
    result = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"), parse_constant=reject_json_constant, object_pairs_hook=unique_json_object)
    except (OSError, UnicodeError, ValueError) as exc:
        raise ContractError(f"Cannot read JSON {path.name}: {exc}") from exc


def read_csv(path: Path, fields: tuple[str, ...]) -> list[dict[str, str]]:
    try:
        with path.open(encoding="utf-8", newline="") as stream:
            reader = csv.DictReader(stream)
            require(reader.fieldnames is not None and len(reader.fieldnames) == len(set(reader.fieldnames)), f"{path.name}: absent/duplicate headers")
            require(set(reader.fieldnames) == set(fields), f"{path.name}: headers must be {list(fields)}")
            rows = []
            for number, row in enumerate(reader, start=2):
                require(None not in row and all(value is not None for value in row.values()), f"{path.name}:{number}: malformed row")
                require(all(value == value.strip() for value in row.values()), f"{path.name}:{number}: leading/trailing whitespace")
                rows.append(row)
            return rows
    except (OSError, UnicodeError, csv.Error) as exc:
        raise ContractError(f"Cannot read CSV {path.name}: {exc}") from exc


def verify_artifact(spec: dict, root: Path, role: str) -> tuple[dict, Path]:
    exact_keys(spec, {"id", "path", "sha256"}, f"artifact {role}")
    identifier = nonempty(spec["id"], f"artifact {role} id")
    relative = nonempty(spec["path"], f"artifact {role} path")
    digest = content_hash(spec["sha256"], f"artifact {role} sha256")
    path = Path(relative)
    path = path if path.is_absolute() else root / path
    require(path.is_file(), f"artifact {role}: file does not exist")
    require(sha256(path) == digest, f"artifact {role}: SHA-256 mismatch")
    return {"role": role, "id": identifier, "sha256": digest, "bytes_verified": path.stat().st_size}, path


def validate_protocol(protocol_path: Path, inputs: dict[str, Path], allow_fixture: bool) -> tuple[dict, list[dict]]:
    protocol = read_json(protocol_path)
    exact_keys(protocol, {
        "schema_version", "study_id", "data_origin", "phase", "independence_unit", "group_definition",
        "labels", "label_mapping", "dataset", "artifacts", "decision_rule", "analysis", "transport", "near_duplicate_audit",
    }, "protocol")
    require(protocol["schema_version"] == SCHEMA, "unsupported protocol schema")
    nonempty(protocol["study_id"], "study_id")
    require(protocol["data_origin"] in ("actual_runtime", "SYNTHETIC_FIXTURE"), "data_origin must be actual_runtime or SYNTHETIC_FIXTURE")
    require(protocol["data_origin"] != "SYNTHETIC_FIXTURE" or allow_fixture, "Synthetic fixture refused without explicit --allow-synthetic-fixture")
    require(protocol["phase"] in ("information_only", "transport_measured"), "phase must be information_only or transport_measured")
    require(protocol["independence_unit"] in ("capture", "episode"), "independence_unit must be capture or episode")
    nonempty(protocol["group_definition"], "group_definition")
    labels = protocol["labels"]
    require(isinstance(labels, list) and len(labels) == 2 and len(set(labels)) == 2, "This scorer requires exactly two distinct predeclared labels")
    for label in labels:
        nonempty(label, "class label")
    mapping = protocol["label_mapping"]
    require(isinstance(mapping, dict) and mapping, "label_mapping must be nonempty")
    for raw, label in mapping.items():
        nonempty(raw, "raw label")
        require(label in labels, "label_mapping points outside declared classes")
    require(set(mapping.values()) == set(labels), "label_mapping must cover both binary classes")
    dataset = exact_keys(protocol["dataset"], {"id", "version", "groups_sha256", "corpus_sha256", "occurrences_sha256", "population"}, "dataset")
    nonempty(dataset["id"], "dataset id")
    nonempty(dataset["version"], "dataset version")
    require(dataset["population"] == "all_generated_held_out_occurrences", "dataset population must retain every generated held-out occurrence")
    for name in ("groups", "corpus", "occurrences"):
        content_hash(dataset[f"{name}_sha256"], f"frozen {name} hash")
        require(sha256(inputs[name]) == dataset[f"{name}_sha256"], f"Frozen {name} manifest SHA-256 mismatch")
    artifacts = exact_keys(protocol["artifacts"], {"model", "encoders", "threshold"}, "artifacts")
    exact_keys(artifacts["encoders"], set(LEVELS), "encoders")
    provenance = []
    threshold_path = None
    for role, spec in [("model", artifacts["model"]), ("threshold", artifacts["threshold"])] + [(f"encoder:{level}", artifacts["encoders"][level]) for level in LEVELS]:
        item, path = verify_artifact(spec, protocol_path.parent, role)
        provenance.append(item)
        if role == "threshold":
            threshold_path = path
    decision = exact_keys(protocol["decision_rule"], {"kind", "negative_label", "positive_label", "threshold"}, "decision_rule")
    require(decision["kind"] == "positive_score_greater_than_or_equal", "unsupported decision rule")
    require({decision["negative_label"], decision["positive_label"]} == set(labels), "decision rule labels mismatch")
    threshold = finite(decision["threshold"], "decision threshold")
    require(0 <= threshold <= 1, "decision threshold must lie in [0,1]")
    require(read_json(threshold_path) == decision, "threshold artifact must exactly encode decision_rule")
    analysis = exact_keys(protocol["analysis"], {"primary_metric", "primary_comparison", "comparisons", "weighting", "bootstrap"}, "analysis")
    allowed_metrics = {"correct_per_generated"}
    if protocol["phase"] == "transport_measured":
        allowed_metrics.add("timely_correct_per_generated")
    require(analysis["primary_metric"] in allowed_metrics, "primary metric is not valid for this phase")
    require(analysis["weighting"] == "equal_group", "Only predeclared equal_group bootstrap weighting is implemented")
    comparisons = analysis["comparisons"]
    require(isinstance(comparisons, list) and comparisons, "comparisons must be nonempty")
    seen = set()
    for pair in comparisons:
        require(isinstance(pair, list) and len(pair) == 2 and all(level in LEVELS for level in pair) and pair[0] != pair[1], "Each comparison must be [treatment, control] with distinct levels")
        require(tuple(pair) not in seen, "duplicate comparison")
        seen.add(tuple(pair))
    require(analysis["primary_comparison"] in comparisons, "primary_comparison must be predeclared in comparisons")
    bootstrap = exact_keys(analysis["bootstrap"], {"samples", "seed", "confidence"}, "bootstrap")
    samples = natural(bootstrap["samples"], "bootstrap samples")
    require(200 <= samples <= 100000, "bootstrap samples must be between 200 and 100000")
    natural(bootstrap["seed"], "bootstrap seed")
    require(0 < finite(bootstrap["confidence"], "bootstrap confidence") < 1, "bootstrap confidence must lie in (0,1)")
    if protocol["phase"] == "information_only":
        require(protocol["transport"] is None, "information_only transport metadata must be null")
    else:
        transport = exact_keys(protocol["transport"], {"deadline_ns", "anchor", "horizon_semantics", "wire_accounting"}, "transport")
        require(natural(transport["deadline_ns"], "deadline_ns") > 0, "deadline_ns must be positive")
        require(transport["anchor"] == "event_creation", "transport anchor must be event_creation")
        require(transport["horizon_semantics"] == "continuous_observation_through_inclusive_horizon", "unsupported observation horizon semantics")
        require(transport["wire_accounting"] == "measured_uplink_evidence_headers_and_retransmissions", "unsupported wire-byte accounting scope")
    near = exact_keys(protocol["near_duplicate_audit"], {"status", "method", "threshold", "artifact"}, "near_duplicate_audit")
    require(near["status"] in ("not_performed", "completed"), "invalid near-duplicate audit status")
    if near["status"] == "not_performed":
        require(all(near[k] is None for k in ("method", "threshold", "artifact")), "unperformed near-duplicate audit details must be null")
    else:
        nonempty(near["method"], "near-duplicate audit method")
        finite(near["threshold"], "near-duplicate audit threshold")
        item, _ = verify_artifact(near["artifact"], protocol_path.parent, "near_duplicate_audit")
        provenance.append(item)
    return protocol, provenance


def validate_inventory(protocol: dict, inputs: dict[str, Path]) -> tuple[dict[str, dict], dict]:
    groups = {}
    for row in read_csv(inputs["groups"], GROUP_FIELDS):
        identifier = nonempty(row["group_id"], "group_id")
        require(identifier not in groups, f"Duplicate/multiple-split group_id: {identifier}")
        require(row["split"] in SPLITS, "unknown group split")
        groups[identifier] = row["split"]
    require(set(groups.values()) == set(SPLITS), "group manifest must enumerate train, validation and test groups")
    corpus = {}
    hash_splits = defaultdict(set)
    hash_counts = Counter()
    split_counts = Counter()
    split_hashed = Counter()
    for row in read_csv(inputs["corpus"], CORPUS_FIELDS):
        identifier = nonempty(row["source_record_id"], "source_record_id")
        require(identifier not in corpus, f"Duplicate corpus source_record_id: {identifier}")
        require(row["group_id"] in groups and groups[row["group_id"]] == row["split"], f"Corpus group/split mismatch: {identifier}")
        require(row["truth_raw"] in protocol["label_mapping"], f"Unknown raw ground truth: {identifier}")
        digest = content_hash(row["source_feature_sha256"], f"source feature hash {identifier}", optional=True)
        split_counts[row["split"]] += 1
        if digest:
            hash_splits[digest].add(row["split"])
            hash_counts[(row["split"], digest)] += 1
            split_hashed[row["split"]] += 1
        corpus[identifier] = row
    require(all(split_counts[split] > 0 for split in SPLITS), "corpus must enumerate records from train, validation and test")
    require(not any(len(splits) > 1 for splits in hash_splits.values()), "Exact source-feature content hash occurs across dataset splits")
    occurrences = {}
    for row in read_csv(inputs["occurrences"], OCCURRENCE_FIELDS):
        identifier = nonempty(row["occurrence_id"], "occurrence_id")
        require(identifier not in occurrences, f"Duplicate generated occurrence: {identifier}")
        require(row["source_record_id"] in corpus, f"Occurrence absent from corpus: {identifier}")
        source = corpus[row["source_record_id"]]
        require(row["split"] == "test" and source["split"] == "test", f"Generated occurrence is not held out: {identifier}")
        require(row["group_id"] == source["group_id"], f"Occurrence group mismatch: {identifier}")
        require(row["truth_label"] == protocol["label_mapping"][source["truth_raw"]], f"Occurrence truth mapping mismatch: {identifier}")
        require(row["source_feature_sha256"] == source["source_feature_sha256"], f"Occurrence source hash mismatch: {identifier}")
        occurrences[identifier] = row
    require(bool(occurrences), "No generated held-out occurrences were enumerated")
    leakage = {
        "exact_source_hash_cross_split_conflicts": 0,
        "source_hashes_are_declared_record_hashes_not_recomputed_feature_bytes": True,
        "coverage_by_split": {s: {"records": split_counts[s], "hashed": split_hashed[s], "coverage": split_hashed[s] / split_counts[s]} for s in SPLITS},
        "within_split_duplicate_hash_records": {s: sum(count - 1 for (split, _), count in hash_counts.items() if split == s) for s in SPLITS},
        "near_duplicate_audit": {k: protocol["near_duplicate_audit"][k] for k in ("status", "method", "threshold")},
        "scope": "No cross-split exact duplicates among supplied raw source-feature hashes. Missing hashes, near duplicates and group independence are not certified by this check; encoded representation hashes are not leakage keys.",
    }
    return occurrences, leakage


def validate_predictions(protocol: dict, occurrences: dict[str, dict], path: Path) -> list[dict]:
    records = []
    seen = set()
    decision = protocol["decision_rule"]
    transport = protocol["phase"] == "transport_measured"
    for raw in read_csv(path, PREDICTION_FIELDS):
        key = (raw["occurrence_id"], raw["representation"])
        require(key not in seen, f"Duplicate prediction row: {key}")
        seen.add(key)
        require(key[0] in occurrences and key[1] in LEVELS, f"Unmatched prediction identity: {key}")
        occurrence = occurrences[key[0]]
        for field in ("split", "truth_label", "source_feature_sha256"):
            require(raw[field] == occurrence[field], f"Prediction {field} mismatch: {key}")
        require(raw["model_id"] == protocol["artifacts"]["model"]["id"], f"Model identity mismatch: {key}")
        require(raw["encoder_id"] == protocol["artifacts"]["encoders"][key[1]]["id"], f"Encoder identity mismatch: {key}")
        require(raw["threshold_id"] == protocol["artifacts"]["threshold"]["id"], f"Threshold identity mismatch: {key}")
        status = raw["status"]
        require(status in STATUSES, f"Unknown prediction status: {key}")
        record = {"occurrence_id": key[0], "representation": key[1], "group_id": occurrence["group_id"], "truth": occurrence["truth_label"], "status": status}
        if status == "returned":
            try:
                score = finite(float(raw["positive_score"]), f"positive score {key}")
            except ValueError as exc:
                raise ContractError(f"Invalid positive score: {key}") from exc
            require(0 <= score <= 1, f"Positive score outside [0,1]: {key}")
            predicted = decision["positive_label"] if score >= decision["threshold"] else decision["negative_label"]
            require(raw["predicted_label"] == predicted, f"Prediction disagrees with frozen threshold: {key}")
            record["predicted"] = predicted
            record["correct"] = int(predicted == occurrence["truth_label"])
        else:
            require(raw["positive_score"] == raw["predicted_label"] == "", f"Non-returned row must not contain a scored prediction: {key}")
            if status == "rejected":
                nonempty(raw["status_detail"], f"terminal rejection reason {key}")
            record["predicted"] = None
            record["correct"] = 0 if status == "rejected" else None
        for field in ("information_bytes", "padding_bytes", "payload_bytes"):
            record[field] = csv_int(raw[field], f"{field} {key}", optional=True)
        amounts = [record[field] for field in ("information_bytes", "padding_bytes", "payload_bytes")]
        require(all(value is None for value in amounts) or all(value is not None for value in amounts), f"Information/padding/payload accounting must be all known or all blank: {key}")
        require(status != "returned" or all(value is not None for value in amounts), f"Returned prediction requires byte accounting: {key}")
        if amounts[0] is not None:
            require(amounts[0] + amounts[1] == amounts[2], f"Information+padding != payload: {key}")
        record["wire_bytes"] = csv_int(raw["wire_bytes"], f"wire_bytes {key}", optional=True)
        content_hash(raw["representation_sha256"], f"unpadded representation hash {key}", optional=not record["information_bytes"] and status != "returned")
        content_hash(raw["payload_sha256"], f"payload hash {key}", optional=not record["payload_bytes"] and status != "returned")
        empty_digest = hashlib.sha256(b"").hexdigest()
        for amount, field in ((record["information_bytes"], "representation_sha256"), (record["payload_bytes"], "payload_sha256")):
            if amount is None:
                require(raw[field] == "", f"Unknown content length requires blank content hash: {key}")
            elif amount == 0 and raw[field]:
                require(raw[field] == empty_digest, f"Zero-length content must have the empty-byte SHA-256: {key}")
        record["timely_correct"] = None
        record["timing_category"] = "not_applicable"
        if not transport:
            require(all(raw[f] == "" for f in PREDICTION_FIELDS[PREDICTION_FIELDS.index("created_ns"):]), f"information_only forbids timing fields: {key}")
            require(raw["wire_bytes"] == "", f"information_only wire_bytes must be blank: {key}")
        else:
            expected_origin = "SYNTHETIC_FIXTURE" if protocol["data_origin"] == "SYNTHETIC_FIXTURE" else "measured"
            require(raw["time_source"] == expected_origin, f"Time source must be {expected_origin}, never simulated: {key}")
            created = csv_int(raw["created_ns"], f"created_ns {key}")
            domain = nonempty(raw["created_clock_domain"], f"creation clock domain {key}")
            returned = csv_int(raw["result_ns"], f"result_ns {key}", optional=True)
            horizon = csv_int(raw["observed_until_ns"], f"observed_until_ns {key}", optional=True)
            if horizon is None:
                require(raw["observation_clock_domain"] == "", f"Absent horizon has a clock domain: {key}")
            else:
                require(raw["observation_clock_domain"] == domain and horizon >= created, f"Invalid observation horizon/clock: {key}")
            if status == "returned":
                require(returned is not None and raw["result_clock_domain"] == domain, f"Returned prediction needs a same-domain result timestamp: {key}")
                require(returned >= created, f"Result precedes creation: {key}")
                require(horizon is None or returned <= horizon, f"Result is after the observation horizon: {key}")
                require(record["wire_bytes"] is None or record["wire_bytes"] >= record["payload_bytes"], f"Completed transport wire bytes below payload: {key}")
                timely = returned - created <= protocol["transport"]["deadline_ns"]
                record["timely_correct"] = int(timely and record["correct"])
                record["timing_category"] = "timely_result" if timely else "late_result"
            else:
                require(returned is None and raw["result_clock_domain"] == "", f"Non-returned row has result timestamp: {key}")
                if status == "rejected":
                    require(horizon is not None, f"Terminal rejection requires an observation horizon: {key}")
                    record["timely_correct"] = 0
                    record["timing_category"] = "terminal_rejection"
                elif horizon is not None and horizon - created >= protocol["transport"]["deadline_ns"]:
                    record["timely_correct"] = 0
                    record["timing_category"] = "mature_no_result"
                else:
                    record["timing_category"] = "immature_or_unknown_no_result"
        records.append(record)
    expected = {(occurrence, level) for occurrence in occurrences for level in LEVELS}
    require(seen == expected, f"Exactly three representation rows per generated occurrence are required; missing={len(expected - seen)}, unexpected={len(seen - expected)}")
    return records


def ratio(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def bounded_fraction(values: list[int | None]) -> dict:
    n = len(values)
    successes = sum(value or 0 for value in values)
    unknown = sum(value is None for value in values)
    return {
        "generated_denominator": n, "known_successes": successes, "unresolved": unknown,
        "estimate": successes / n if n and not unknown else None,
        "lower": ratio(successes, n), "upper": ratio(successes + unknown, n),
    }


def summarize(records: list[dict], protocol: dict) -> dict:
    positive = protocol["decision_rule"]["positive_label"]
    scored = [row for row in records if row["predicted"] is not None]
    counts = Counter()
    for row in scored:
        counts[("T" if row["predicted"] == row["truth"] else "F") + ("P" if row["predicted"] == positive else "N")] += 1
    tp, fp, fn, tn = (counts[k] for k in ("TP", "FP", "FN", "TN"))
    costs = {}
    for field in ("information_bytes", "padding_bytes", "payload_bytes", "wire_bytes"):
        values = [row[field] for row in records]
        known = [value for value in values if value is not None]
        costs[field] = {"known_total": sum(known), "missing_records": len(values) - len(known), "total": sum(known) if len(known) == len(values) else None}
    return {
        "generated": len(records), "scored": len(scored), "correct": sum(row["correct"] or 0 for row in records),
        "status_counts": {status: sum(row["status"] == status for row in records) for status in STATUSES},
        "scored_coverage": ratio(len(scored), len(records)),
        "correct_per_generated": bounded_fraction([row["correct"] for row in records]),
        "scored_only_binary_metrics": {
            "scope": "Returned predictions only; missing/censored/rejected are not silently classified negative. Their outcomes remain in generated-denominator metrics.",
            "positive_label": positive, "negative_label": protocol["decision_rule"]["negative_label"],
            "TP": tp, "FP": fp, "FN": fn, "TN": tn,
            "accuracy": ratio(tp + tn, len(scored)), "precision": ratio(tp, tp + fp),
            "recall": ratio(tp, tp + fn), "specificity": ratio(tn, tn + fp),
            "false_positive_rate": ratio(fp, fp + tn), "f1_positive": ratio(2 * tp, 2 * tp + fp + fn),
        },
        "byte_costs": costs,
        "byte_cost_scope": "Information/padding/payload are constructed or offered representation bytes, including rejected rows where known; they are not granted/transmitted service. Wire bytes are separately measured actual attributed uplink bytes.",
        "timely_correct_per_generated": bounded_fraction([row["timely_correct"] for row in records]) if protocol["phase"] == "transport_measured" else None,
        "timing_categories": dict(sorted(Counter(row["timing_category"] for row in records).items())) if protocol["phase"] == "transport_measured" else None,
    }


def quantile(values: list[float], p: float) -> float:
    values = sorted(values)
    position = (len(values) - 1) * p
    lo, hi = math.floor(position), math.ceil(position)
    return values[lo] + (values[hi] - values[lo]) * (position - lo)


def paired_comparisons(group_results: dict, protocol: dict) -> list[dict]:
    groups = sorted(group_results)
    analysis = protocol["analysis"]
    metric = analysis["primary_metric"]
    options = analysis["bootstrap"]
    results = []
    for treatment, control in analysis["comparisons"]:
        cells = [(group_results[group][treatment][metric], group_results[group][control][metric]) for group in groups]
        lower = sum(a["lower"] - b["upper"] for a, b in cells) / len(groups)
        upper = sum(a["upper"] - b["lower"] for a, b in cells) / len(groups)
        resolved = all(a["estimate"] is not None and b["estimate"] is not None for a, b in cells)
        differences = [a["estimate"] - b["estimate"] for a, b in cells] if resolved else None
        interval = None
        reason = "incomplete_outcomes_or_followup" if not resolved else ("fewer_than_two_independent_groups" if len(groups) < 2 else None)
        if reason is None:
            # Reset to the same frozen RNG for every contrast, so every draw
            # uses identical paired group indices for all representations.
            rng = random.Random(options["seed"])
            draws = [sum(differences[rng.randrange(len(groups))] for _ in groups) / len(groups) for _ in range(options["samples"])]
            alpha = (1 - options["confidence"]) / 2
            interval = [quantile(draws, alpha), quantile(draws, 1 - alpha)]
        results.append({
            "treatment": treatment, "control": control, "primary_comparison": [treatment, control] == analysis["primary_comparison"],
            "metric": metric, "groups": len(groups), "weighting": "equal_group_mean_of_generated_denominator_proportions",
            "estimate": sum(differences) / len(groups) if resolved else None, "identification_bounds": [lower, upper],
            "percentile_interval": interval, "interval_confidence": options["confidence"], "interval_unavailable_reason": reason,
            "bootstrap_samples": options["samples"], "bootstrap_seed": options["seed"],
            "interval_scope": "Paired descriptive group-bootstrap interval; no multiplicity adjustment or causal guarantee. Independence of declared groups requires study-design evidence.",
        })
    return results


def score_study(protocol_path: Path, inputs: dict[str, Path], *, allow_synthetic_fixture: bool = False, bootstrap_seed: int | None = None, bootstrap_samples: int | None = None) -> dict:
    protocol, artifacts = validate_protocol(protocol_path, inputs, allow_synthetic_fixture)
    for name, override in (("seed", bootstrap_seed), ("samples", bootstrap_samples)):
        require(override is None or override == protocol["analysis"]["bootstrap"][name], f"CLI bootstrap {name} differs from frozen protocol")
    occurrences, leakage = validate_inventory(protocol, inputs)
    records = validate_predictions(protocol, occurrences, inputs["predictions"])
    grouped = defaultdict(list)
    for row in records:
        grouped[row["group_id"]].append(row)
    group_results = {group: {level: summarize([row for row in rows if row["representation"] == level], protocol) for level in LEVELS} for group, rows in sorted(grouped.items())}
    return {
        "schema_version": SCHEMA, "study_id": protocol["study_id"], "data_origin": protocol["data_origin"], "phase": protocol["phase"],
        "validation": "All supplied records satisfy the declared schema; this does not prove completeness against an unprovided acquisition log or truthful instrumentation.",
        "dataset": {key: protocol["dataset"][key] for key in ("id", "version", "population")},
        "decision_rule": protocol["decision_rule"], "label_mapping": protocol["label_mapping"],
        "independence_unit": protocol["independence_unit"], "group_definition": protocol["group_definition"],
        "generated_occurrences": len(occurrences), "independent_group_ids": sorted(grouped),
        "pooled_by_representation": {level: summarize([row for row in records if row["representation"] == level], protocol) for level in LEVELS},
        "by_group_and_representation": group_results,
        "paired_group_comparisons": paired_comparisons(group_results, protocol),
        "estimand_note": "Pooled counts weight occurrences. Bootstrap differences weight each declared capture/episode group equally. No average of per-row F1 is computed; reported F1 is positive-class F1 from each displayed confusion table.",
        "leakage_audit": leakage,
        "provenance": {
            "scorer_source_sha256": sha256(Path(__file__)), "protocol_sha256": sha256(protocol_path),
            "input_sha256": {name: sha256(path) for name, path in inputs.items()}, "verified_artifacts": artifacts,
            "content_hash_scope": "Model/encoder/threshold artifact bytes are checked. Corpus and representation hashes are declared per-record hashes; underlying feature/payload bytes are not supplied to this scorer.",
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("protocol", "groups", "corpus", "occurrences", "predictions", "output"):
        parser.add_argument(f"--{name}", required=True, type=Path)
    parser.add_argument("--bootstrap-seed", type=int, help="Optional assertion; must match frozen protocol")
    parser.add_argument("--bootstrap-samples", type=int, help="Optional assertion; must match frozen protocol")
    parser.add_argument("--allow-synthetic-fixture", action="store_true", help="For temporary SYNTHETIC_FIXTURE tests only; never relabels synthetic data as actual")
    args = parser.parse_args(argv)
    try:
        inputs = {name: getattr(args, name) for name in ("groups", "corpus", "occurrences", "predictions")}
        require(not args.output.exists(), "Output exists; choose a new report path")
        report = score_study(args.protocol, inputs, allow_synthetic_fixture=args.allow_synthetic_fixture, bootstrap_seed=args.bootstrap_seed, bootstrap_samples=args.bootstrap_samples)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8") as stream:
            json.dump(report, stream, indent=2, sort_keys=True, allow_nan=False)
            stream.write("\n")
        print(f"Validated {report['generated_occurrences']} matched occurrences; wrote {args.output}")
        return 0
    except (ContractError, OSError, UnicodeError, TypeError, OverflowError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
