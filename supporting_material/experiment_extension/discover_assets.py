#!/usr/bin/env python3
"""Read-only discovery of candidate inputs; never imports or executes a runtime.

Paths in the report are relative to caller-named roots. No feature values,
payloads, credentials or source snippets are copied into the report. Discovery
is not a certification that any candidate is suitable for an experiment.
"""
from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import os
import re
from pathlib import Path

EXCLUDED_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".ssh", ".aws", ".cache"}
SOURCE_SUFFIXES = {".py", ".sh", ".cpp", ".cc", ".c", ".h", ".js", ".ts"}
DATA_SUFFIXES = {".csv", ".tsv", ".jsonl", ".ndjson", ".parquet", ".npz", ".npy", ".pcap", ".pcapng"}
MODEL_SUFFIXES = {".onnx", ".joblib", ".pkl", ".pickle", ".pt", ".pth", ".tflite", ".h5", ".keras"}
CONFIG_SUFFIXES = {".json", ".yaml", ".yml", ".toml", ".ini"}
TEXT_READ_LIMIT = 2 * 1024 * 1024
RECOGNIZED_COLUMNS = {
    "group_id", "capture_id", "episode_id", "session_id", "run_id", "event_id",
    "occurrence_id", "probe", "device", "split", "label", "ground_truth",
    "y_true", "attack_label", "class", "prediction", "score", "evidence_level",
    "created_probe_monotonic_ns", "generated_time", "generated_ns",
    "result_received_monotonic_ns", "result_received", "result_received_ns",
    "scheduled_release_monotonic_ns", "served_bytes", "granted_bytes",
    "service_round", "payload_bytes", "remaining_bytes", "feature_sha256",
    "representation_hash", "model_hash", "encoder_hash", "threshold_id",
    "terminal_state", "deadline", "method", "capacity", "capacity_bytes", "v", "n",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sensitive_name(path: Path) -> bool:
    name = path.name.lower()
    return (name.startswith(".env") or path.suffix.lower() in {".pem", ".key", ".p12", ".pfx"}
            or any(token in name for token in ("credential", "secret", "id_rsa", "id_ed25519")))


def source_hints(text: str, suffix: str) -> dict:
    """Heuristics are explicitly labeled; an AST finding is not deployment proof."""
    hints = []
    lower = text.lower()
    for tag, words in {
        "allocator_candidate": ("waterfill", "water_fill", "max_min"),
        "payload_encoder_candidate": ("serialize", "encode_payload", "build_payload", "summary_payload"),
        "consumer_candidate": ("predict_proba", "inference", "onnxruntime", "model.predict"),
        "clock_instrumentation_candidate": ("monotonic_ns", "result_received", "scheduled_release"),
        "service_logging_candidate": ("service_ledger", "service_audit", "served_bytes", "granted_bytes"),
    }.items():
        if any(word in lower for word in words):
            hints.append(tag)
    result = {"candidate_tags": hints}
    if suffix != ".py":
        return result
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError):
        result["python_ast"] = "UNPARSEABLE_SOURCE"
        return result
    functions = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        name = node.name.lower()
        if not any(token in name for token in ("waterfill", "water_fill", "admit", "payload", "encode", "decode", "infer", "predict", "is_safe")):
            continue
        item = {"name": node.name, "line": node.lineno}
        if "waterfill" in name or "water_fill" in name:
            floor_div = any(isinstance(n, ast.BinOp) and isinstance(n.op, ast.FloorDiv) for n in ast.walk(node))
            zero_break = any(
                isinstance(n, ast.If)
                and isinstance(n.test, ast.Compare)
                and any(isinstance(op, ast.Eq) for op in n.test.ops)
                and any(isinstance(v, ast.Constant) and v.value == 0 for v in [n.test.left, *n.test.comparators])
                and any(isinstance(v, ast.Break) for stmt in n.body for v in ast.walk(stmt))
                for n in ast.walk(node)
            )
            item["integer_division_and_zero_break_heuristic"] = floor_div and zero_break
            item["interpretation"] = "SOURCE_REVIEW_REQUIRED_NOT_A_BUG_VERDICT"
        functions.append(item)
    result["candidate_functions"] = functions
    return result


def inspect_file(path: Path, root: Path, root_id: str, hash_max_bytes: int) -> dict | None:
    suffix = path.suffix.lower()
    if suffix not in SOURCE_SUFFIXES | DATA_SUFFIXES | MODEL_SUFFIXES | CONFIG_SUFFIXES:
        return None
    if sensitive_name(path) or path.is_symlink():
        return None
    size = path.stat().st_size
    kind = "source" if suffix in SOURCE_SUFFIXES else "model" if suffix in MODEL_SUFFIXES else "data" if suffix in DATA_SUFFIXES else "configuration"
    entry = {"root_id": root_id, "path": path.relative_to(root).as_posix(), "kind": kind, "size_bytes": size}
    if size <= hash_max_bytes:
        entry["sha256"] = sha256_file(path)
    else:
        entry["sha256"] = None
        entry["hash_status"] = "NOT_COMPUTED_SIZE_LIMIT_FREEZE_SEPARATELY"
    if kind == "source" and size <= TEXT_READ_LIMIT:
        entry.update(source_hints(path.read_text(encoding="utf-8", errors="replace"), suffix))
    if suffix in {".csv", ".tsv"}:
        with path.open(encoding="utf-8-sig", errors="strict", newline="") as handle:
            # Only a bounded header is read; data rows are not disclosed.
            header_line = handle.readline(65537)
        if len(header_line) > 65536:
            entry["header_status"] = "HEADER_TOO_LONG_NOT_READ"
        else:
            columns = next(csv.reader([header_line], delimiter="\t" if suffix == ".tsv" else ","), [])
            # Headerless string data are also possible. Emit only vocabulary
            # from this fixed schema-name allowlist, never arbitrary cells.
            names = {c.lower() for c in columns}
            recognized = names & RECOGNIZED_COLUMNS
            if recognized and len(columns) <= 1024:
                entry["recognized_schema_names"] = sorted(recognized)
                entry["column_count"] = len(columns)
                entry["header_status"] = "CANDIDATE_SCHEMA_NAMES_ONLY_HEADER_NOT_CERTIFIED"
                entry["has_group_id_column"] = bool(names & {"group_id", "capture_id", "episode_id", "session_id"})
                entry["has_label_column"] = bool(names & {"label", "ground_truth", "y_true", "attack_label", "class"})
                entry["has_origin_return_clock_columns"] = bool(names & {"created_probe_monotonic_ns", "generated_time", "generated_ns"}) and bool(names & {"result_received_monotonic_ns", "result_received", "result_received_ns"})
            else:
                entry["header_status"] = "UNRECOGNIZED_OR_HEADERLESS_VALUES_NOT_REPORTED"
    return entry


def discover(roots: list[tuple[str, Path]], *, hash_max_bytes: int, max_files: int) -> dict:
    if hash_max_bytes < 0 or max_files < 1:
        raise ValueError("hash_max_bytes must be nonnegative and max_files must be positive")
    if not roots or len({name for name, _ in roots}) != len(roots):
        raise ValueError("At least one root and unique root names are required")
    files, root_reports, errors = [], [], []
    visited = 0
    truncated = False
    for root_id, supplied_root in roots:
        if not re.fullmatch(r"[A-Za-z0-9_-]+", root_id):
            raise ValueError("Root names must contain only letters, digits, underscore or hyphen")
        root = supplied_root.expanduser().resolve()
        if not root.is_dir():
            root_reports.append({"root_id": root_id, "status": "DIRECTORY_NOT_AVAILABLE"})
            continue
        count_before = len(files)
        root_errors = []
        def walk_error(error):
            root_errors.append(type(error).__name__)
        for directory, subdirs, names in os.walk(root, followlinks=False, onerror=walk_error):
            parent = Path(directory)
            subdirs[:] = sorted(d for d in subdirs if d not in EXCLUDED_DIRS and not d.startswith(".") and not (parent / d).is_symlink())
            for name in sorted(names):
                path = parent / name
                if name.startswith(".") or sensitive_name(path) or path.is_symlink():
                    continue
                visited += 1
                if visited > max_files:
                    truncated = True
                    break
                try:
                    entry = inspect_file(path, root, root_id, hash_max_bytes)
                    if entry:
                        files.append(entry)
                except (OSError, UnicodeError, csv.Error) as error:
                    errors.append({"root_id": root_id, "path": path.relative_to(root).as_posix(), "error": type(error).__name__})
            if truncated:
                break
        root_reports.append({"root_id": root_id, "status": "PARTIAL_LIMIT_REACHED" if truncated else "INSPECTED_WITH_ERRORS" if root_errors else "INSPECTED", "candidate_files": len(files) - count_before, "walk_errors": root_errors})
        if truncated:
            break
    counts = {kind: sum(f["kind"] == kind for f in files) for kind in ("source", "model", "data", "configuration")}
    return {
        "schema_version": 1,
        "evidence_type": "ASSET_DISCOVERY_ONLY",
        "experiment_status": "NOT_EXECUTED",
        "scope": "Only the named roots were inspected. A candidate is not a qualified runtime, dataset, encoder, model, or primitive ledger.",
        "source_sha256": sha256_file(Path(__file__)),
        "hash_max_bytes": hash_max_bytes,
        "visited_files": min(visited, max_files),
        "truncated": truncated,
        "roots": root_reports,
        "candidate_counts": counts,
        "model_status": "CANDIDATES_REQUIRE_IDENTITY_AND_COMPATIBILITY_REVIEW" if counts["model"] else "NO_MODEL_CANDIDATE_IN_SCANNED_FILES",
        "unresolved_qualifications": [
            "Which source and allocator actually executed the frozen hardware campaign?",
            "Are actual alert, summary and full encoders and downstream consumers available?",
            "Do independent held-out captures/episodes and labels exist, with audited exact and near duplication?",
            "Are model/threshold hashes and executed configuration identities recoverable?",
            "Do primitive service records and same-origin-clock event milestones permit independent reconstruction?",
            "Are actual devices, physical transport and independently calibrated causal admission implementation available?",
        ],
        "files": files,
        "read_errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", action="append", required=True, metavar="NAME=PATH")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--hash-max-bytes", type=int, default=64 * 1024 * 1024)
    parser.add_argument("--max-files", type=int, default=100000)
    args = parser.parse_args()
    try:
        roots = []
        for value in args.root:
            name, separator, path = value.partition("=")
            if not separator or not path:
                raise ValueError("Each --root must have NAME=PATH form")
            roots.append((name, Path(path)))
        if args.output.exists():
            raise ValueError("Output already exists; choose a fresh path to preserve provenance")
        report = discover(roots, hash_max_bytes=args.hash_max_bytes, max_files=args.max_files)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8") as handle:
            json.dump(report, handle, indent=2, sort_keys=True, ensure_ascii=False)
            handle.write("\n")
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print(json.dumps({"output": str(args.output), "experiment_status": report["experiment_status"], "candidate_counts": report["candidate_counts"], "truncated": report["truncated"]}))
    return 0 if not report["truncated"] and not report["read_errors"] and all(r["status"] == "INSPECTED" for r in report["roots"]) else 2


if __name__ == "__main__":
    raise SystemExit(main())
