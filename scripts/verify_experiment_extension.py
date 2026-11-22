#!/usr/bin/env python3
"""Verify offline preparation and preservation of prior scientific artifacts.

No network, device access, model training, experiment launch or result
fabrication is performed. All new test data are temporary synthetic fixtures.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXTENSION = ROOT / "supporting_material/experiment_extension"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_identities() -> dict:
    paths = sorted(EXTENSION.rglob("*.py")) + [Path(__file__)]
    for directory in (EXTENSION / "hardware", EXTENSION / "evidence_value"):
        paths.extend(sorted(directory.rglob("*.json")))
    return {path.relative_to(ROOT).as_posix(): digest(path) for path in paths}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Fresh JSON report path; existing reports are never overwritten")
    args = parser.parse_args()
    if args.output and args.output.exists():
        parser.error("Output exists; use a fresh report path")
    before = source_identities()
    commands = [
        ("asset_discovery", [sys.executable, "-m", "unittest", "discover", "-s", str(EXTENSION), "-p", "test_discover_assets.py", "-v"]),
        ("input_freezing", [sys.executable, "-m", "unittest", "discover", "-s", str(EXTENSION), "-p", "test_freeze_inputs.py", "-v"]),
        ("evidence_value_scoring", [sys.executable, "-m", "unittest", "discover", "-s", str(EXTENSION / "evidence_value/tests"), "-p", "test_*.py", "-v"]),
        ("hardware_plan_generation", [sys.executable, "-m", "unittest", "discover", "-s", str(EXTENSION / "hardware"), "-p", "test_*.py", "-v"]),
        ("frozen_science_and_prior_reconstruction", [sys.executable, "scripts/verify_methodology_revision.py"]),
    ]
    checks = []
    for name, command in commands:
        start = time.monotonic()
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
        matches = re.findall(r"Ran (\d+) tests?", result.stderr)
        tests = sum(int(value) for value in matches)
        passed = result.returncode == 0 and (tests > 0 or name == "frozen_science_and_prior_reconstruction")
        checks.append({
            "name": name,
            "status": "PASS" if passed else "FAIL",
            "command": ["python3" if item == sys.executable else item.replace(str(ROOT) + "/", "") for item in command],
            "return_code": result.returncode,
            "tests_run": tests,
            "tool_elapsed_seconds": round(time.monotonic() - start, 3),
            "stdout": result.stdout,
            "stderr": result.stderr,
        })
        print(f"{name}: {'PASS' if passed else 'FAIL'} ({tests} fixture tests)")
    after = source_identities()
    stable = before == after
    passed = stable and all(check["status"] == "PASS" for check in checks)
    report = {
        "schema_version": 1,
        "status": "OFFLINE_PREPARATION_VALIDATED" if passed else "OFFLINE_PREPARATION_FAILED",
        "new_scientific_experiments_executed": False,
        "physical_devices_used": False,
        "detector_models_executed": False,
        "new_fixture_tests": sum(check["tests_run"] for check in checks),
        "sources_unchanged_during_verification": stable,
        "source_sha256": before,
        "checks": checks,
        "interpretation": "This verifies preparation tools on synthetic fixtures and preserves prior public evidence. It does not qualify private inputs or demonstrate detection gain, physical latency, or deployment safety.",
    }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8") as handle:
            json.dump(report, handle, indent=2, sort_keys=True)
            handle.write("\n")
    print(json.dumps({key: value for key, value in report.items() if key not in {"checks", "source_sha256"}}, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
