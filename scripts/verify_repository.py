#!/usr/bin/env python3
"""Verify the committed RC1 audit snapshot without external dependencies."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RC1 = ROOT / "formal_rc1"
PROTOCOL = "NSF12_20260906_RC1"
SESSIONS = {f"F12_S{number:02d}" for number in range(1, 13)}
METHODS = set("ABCDEF")
CAPACITIES = {"low", "mid", "high"}


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def rows(name: str) -> list[dict[str, str]]:
    with (RC1 / "results" / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def load_json(name: str):
    return json.loads((RC1 / "results" / name).read_text(encoding="utf-8"))


def verify_manifest() -> None:
    listed: set[Path] = set()
    for line in (RC1 / "MANIFEST_SHA256.txt").read_text(encoding="utf-8").splitlines():
        expected, relative = line.split("  ./", 1)
        path = RC1 / relative
        listed.add(path)
        if not path.is_file():
            fail(f"manifest file missing: {relative}")
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            fail(f"SHA-256 mismatch: {relative}")
    actual_files = {path for path in RC1.rglob("*") if path.is_file()}
    actual_files.remove(RC1 / "MANIFEST_SHA256.txt")
    if listed != actual_files:
        fail("manifest file list does not match formal_rc1 contents")


def main() -> None:
    verify_manifest()
    status = load_json("campaign_status.json")
    activation = load_json("activation_record.json")
    index = load_json("ATTEMPT_INDEX.json")
    matrix = load_json("FULL_MATRIX_WITH_STATUS.json")
    attempts = rows("accepted_attempts.csv")
    validators = rows("validator_summary.csv")
    packages = rows("session_packages.csv")
    endpoints = rows("endpoint_summary.csv")
    contrasts = rows("contrast_summary.csv")

    accepted_ids = {arm for entry in index["accepted"] for arm in entry["arms"]}
    expected_grid = {(session, method, capacity) for session in SESSIONS for method in METHODS for capacity in CAPACITIES}
    validator_grid = {(row["session_id"], row["method"], row["capacity"]) for row in validators}
    endpoints_seen = {row["endpoint"] for row in endpoints}

    checks = {
        "campaign status": status["protocol_id"] == PROTOCOL
        and status["accepted_sessions"] == 12
        and status["accepted_arms"] == 216
        and status["collection_status"] == "FORMAL_CAMPAIGN_EXECUTION_COMPLETE_PENDING_INDEPENDENT_REVIEW",
        "submission hold": status["submission"] == "HOLD",
        "activation": activation["protocol_id"] == PROTOCOL
        and activation["formal_run_authorized"] is True
        and activation["frozen_tools"]["crc"] == activation["frozen_tools"]["restored_hashes"] == "PASS"
        and activation["backup_gate"]["status"] == "PASS"
        and activation["submission"] == "HOLD",
        "accepted index": len(index["accepted"]) == 12
        and len(accepted_ids) == 216
        and {entry["session_id"] for entry in index["accepted"]} == SESSIONS
        and sum(entry["status"] == "invalid_attempt" for entry in index["attempts"]) == 3,
        "accepted attempts summary": len(attempts) == 12
        and {row["session_id"] for row in attempts} == SESSIONS
        and sum(int(row["accepted_arm_count"]) for row in attempts) == 216,
        "matrix": len(matrix) == 216
        and {row["campaign_id"] for row in matrix} == {PROTOCOL}
        and {row["accepted_run_id"] for row in matrix} == accepted_ids
        and all(row["status"] == "VALIDATED_PASS" and row["validator"] == "PASS" for row in matrix),
        "validators": len(validators) == 216
        and {row["run_id"] for row in validators} == accepted_ids
        and validator_grid == expected_grid
        and all(row["overall"] == "PASS" and row["failed_check_count"] == "0" for row in validators),
        "session packages": len(packages) == 12
        and {row["session_id"] for row in packages} == SESSIONS
        and all(
            row["sha256"] == row["receipt_sha256"]
            and row["crc"] == row["restored_hashes"] == "PASS"
            for row in packages
        ),
        "endpoint summaries": len(endpoints) == 144
        and len(endpoints_seen) == 8
        and len({(row["capacity"], row["method"], row["endpoint"]) for row in endpoints}) == 144
        and {(row["capacity"], row["method"], row["endpoint"]) for row in endpoints}
        == {(capacity, method, endpoint) for capacity in CAPACITIES for method in METHODS for endpoint in endpoints_seen},
        "contrast summaries": len(contrasts) == 48
        and len({(row["capacity"], row["contrast"], row["endpoint"]) for row in contrasts}) == 48
        and {(row["capacity"], row["contrast"], row["endpoint"]) for row in contrasts}
        == {(capacity, contrast, endpoint) for capacity in CAPACITIES for contrast in {"F-D", "F-E"} for endpoint in endpoints_seen}
        and all(row["confirmatory_test"] == "False" for row in contrasts),
    }
    for label, passed in checks.items():
        if not passed:
            fail(label)

    forbidden = re.compile(r"/Users/|192\.168\.|(?:pi5|pi4b|pi3bplus)\.local")
    for path in RC1.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".json", ".csv", ".md", ".txt"}:
            if forbidden.search(path.read_text(encoding="utf-8", errors="ignore")):
                fail(f"private host/path token in {path.relative_to(ROOT)}")

    print("PASS: manifest, 12 sessions, 216 validators, 12 packages, and privacy scan")


if __name__ == "__main__":
    try:
        main()
    except (KeyError, ValueError, OSError, json.JSONDecodeError) as error:
        fail(str(error))
