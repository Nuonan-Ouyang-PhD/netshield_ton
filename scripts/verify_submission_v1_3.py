#!/usr/bin/env python3
"""Verify the path-free NetShield ToN V1.3 submission snapshot."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "submission_v1_3"
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


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    manifest = PACKAGE / "SHA256SUMS.txt"
    listed: set[Path] = set()
    for line in manifest.read_text(encoding="utf-8").splitlines():
        expected, relative = line.split("  ./", 1)
        path = PACKAGE / relative
        listed.add(path)
        if not path.is_file() or sha256(path) != expected:
            fail(f"SHA-256 mismatch: {relative}")
    actual = {path for path in PACKAGE.rglob("*") if path.is_file()} - {manifest}
    if listed != actual:
        fail("manifest file list does not match submission_v1_3 contents")

    required = {
        "netshield_ton_manuscript_v1_3.tex",
        "netshield_ton_manuscript_v1_3.pdf",
        "netshield_ton_supplementary_v1_3.tex",
        "netshield_ton_supplementary_v1_3.pdf",
        "BUILD_REPORT.md",
        "VALIDATION_REPORT_V1_3.md",
        "audit/CLAIM_AUDIT_V1_3.md",
        "audit/MANUSCRIPT_NUMBER_PROVENANCE_V1_3.csv",
        "audit/REFERENCE_AUDIT_V1_3.md",
    }
    required |= {f"figures/{path.name}" for path in (PACKAGE / "figures").glob("fig*.pdf")}
    if len([name for name in required if name.startswith("figures/")]) != 7:
        fail("expected seven figures")
    for relative in required:
        if not (PACKAGE / relative).is_file():
            fail(f"missing artifact: {relative}")

    for name, expected in EXPECTED_ROWS.items():
        data = rows(PACKAGE / "evidence" / name)
        expected_status = "SOURCE_AND_LOG_SUPPORTED" if name == "RELEASE_LATENESS_DIAGNOSTIC.csv" else "PASS"
        if len(data) != expected or any(row.get("status") != expected_status for row in data):
            fail(f"row count/status: {name}")
    scaling = rows(PACKAGE / "evidence/SCALING_RESULTS.csv")
    if any(row["theory_simulation_match"].lower() != "true" or row["shared_cap_violation"].lower() != "false" for row in scaling):
        fail("scaling conformance")

    raw = json.loads((PACKAGE / "evidence/RAW_AUDIT_SUMMARY.json").read_text(encoding="utf-8"))
    expected_raw = {
        "accepted_arms_rebuilt": 216,
        "measured_events_rebuilt": 58320,
        "raw_to_delivered_mismatches": 0,
        "shared_rounds_checked": 63720,
        "shared_round_violations": 0,
    }
    if any(raw.get(key) != value for key, value in expected_raw.items()):
        fail("raw-audit headline values")

    shield = rows(PACKAGE / "evidence/SHIELD_INTERVENTION_SUMMARY.csv")
    by_key = {(row["capacity"], row["arm"]): row for row in shield}
    if (by_key[("low", "F")]["shield_safety_interventions"] != "3240"
            or by_key[("mid", "E")]["capacity_admission_interventions"] != "2160"
            or by_key[("mid", "F")]["capacity_admission_interventions"] != "2160"):
        fail("shield-intervention summary")

    main_source = (PACKAGE / "netshield_ton_manuscript_v1_3.tex").read_text(encoding="utf-8")
    supp_source = (PACKAGE / "netshield_ton_supplementary_v1_3.tex").read_text(encoding="utf-8")
    citations = {item.strip() for group in re.findall(r"\\cite\{([^}]+)\}", main_source) for item in group.split(",")}
    bibitems = set(re.findall(r"\\bibitem\{([^}]+)\}", main_source))
    if citations != bibitems or len(citations) != 17:
        fail("citation/bibliography identity")
    if "IEEE/ACM Transactions on Networking" not in main_source:
        fail("journal title")

    for source in (main_source, supp_source):
        for target in re.findall(r"\\(?:includegraphics|input)(?:\[[^]]*\])?\{([^}]+)\}", source):
            candidates = [PACKAGE / target, PACKAGE / "figures" / target, PACKAGE / "tables" / target]
            if not any(path.is_file() for path in candidates):
                fail(f"missing LaTeX target: {target}")

    provenance = rows(PACKAGE / "audit/MANUSCRIPT_NUMBER_PROVENANCE_V1_3.csv")
    if not provenance or any(row["verified"] != "PASS" for row in provenance):
        fail("number provenance status")
    for row in provenance:
        source = row["source_file"]
        candidates = [PACKAGE / source, PACKAGE / "evidence" / source]
        if not any(path.is_file() for path in candidates):
            fail(f"missing provenance source: {source}")

    forbidden_claims = ["timely_f1", "0.9332", "0.2845", "0.9336", "0.2823", "1/2/3 Mbps"]
    if any(token.lower() in main_source.lower() for token in forbidden_claims):
        fail("forbidden superseded claim")
    if "Verdict: **PASS**" not in (PACKAGE / "audit/CLAIM_AUDIT_V1_3.md").read_text(encoding="utf-8"):
        fail("claim audit verdict")

    forbidden_private = re.compile(r"/Users/|/Volumes/|192\.168\.|(?:pi5|pi4b|pi3bplus)\.local|nuonanouyang|\.ssh/")
    for path in PACKAGE.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".json", ".csv", ".md", ".txt", ".tex", ".py"}:
            if forbidden_private.search(path.read_text(encoding="utf-8", errors="ignore")):
                fail(f"private host/path token in {path.relative_to(ROOT)}")

    print("PASS: V1.3 submission hashes, evidence, provenance, citations, claims, and privacy scan")


if __name__ == "__main__":
    try:
        main()
    except (KeyError, ValueError, OSError, json.JSONDecodeError) as error:
        fail(str(error))
