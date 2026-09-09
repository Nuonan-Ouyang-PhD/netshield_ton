#!/usr/bin/env python3
"""Verify the committed path-free V1.3 methodology-repair review package."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "ToN_V1_3_Methodology_Repair_20260909"
EXPECTED_ROWS = {
    "V_SWEEP_RESULTS.csv": 432,
    "DESYNC_BASELINE_RESULTS.csv": 240,
    "NOMINAL_DEADLINE_RESULTS.csv": 648,
    "RELEASE_LATENESS_DIAGNOSTIC.csv": 3,
    "SCALING_RESULTS.csv": 20,
}


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    listed: set[Path] = set()
    for line in (PACKAGE / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines():
        expected, name = line.split("  ", 1)
        path = PACKAGE / name
        listed.add(path)
        if not path.is_file() or sha256(path) != expected:
            fail(f"SHA-256 mismatch: {name}")

    actual = {path for path in PACKAGE.iterdir() if path.is_file()}
    actual.remove(PACKAGE / "SHA256SUMS.txt")
    if listed != actual:
        fail("manifest file list does not match methodology-repair contents")

    for name, expected in EXPECTED_ROWS.items():
        with (PACKAGE / name).open(newline="", encoding="utf-8") as handle:
            if sum(1 for _ in csv.DictReader(handle)) != expected:
                fail(f"row count: {name}")

    metadata = json.loads((PACKAGE / "RUN_METADATA.json").read_text(encoding="utf-8"))
    guards = metadata["scope_guards"]
    if any(guards.values()) or metadata["planned_and_retained"] != {
        "failed_rows": 0,
        "task_a_rows": 432,
        "task_b_rows": 240,
        "task_c_rows": 648,
        "task_d_rows": 20,
    }:
        fail("scope guards or planned row counts")
    if json.loads((PACKAGE / "FAILED_RUNS.json").read_text(encoding="utf-8")) != []:
        fail("retained failure ledger")

    forbidden = re.compile(r"/Users/|/Volumes/|192\.168\.|(?:pi5|pi4b|pi3bplus)\.local|nuonanouyang")
    for path in PACKAGE.iterdir():
        if path.is_file() and path.suffix.lower() in {".json", ".csv", ".md", ".txt", ".py", ".log"}:
            if forbidden.search(path.read_text(encoding="utf-8", errors="ignore")):
                fail(f"private host/path token in {path.relative_to(ROOT)}")

    print("PASS: V1.3 hashes, 1343 result rows, scope guards, and privacy scan")


if __name__ == "__main__":
    try:
        main()
    except (KeyError, ValueError, OSError, json.JSONDecodeError) as error:
        fail(str(error))
