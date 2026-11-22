#!/usr/bin/env python3
"""Check frozen science, corrected public selector, and independent ledgers."""
from __future__ import annotations

import hashlib
import json
import re
import tempfile
from pathlib import Path

from audit_service_ledgers import audit_crfa, audit_software
from run_public_selector_audit import run as run_selector

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "supporting_material/methodology_validation"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(ok: bool, label: str) -> None:
    if not ok:
        raise AssertionError(label)


def main() -> None:
    frozen = json.loads((AUDIT / "FROZEN_INPUTS.json").read_text())
    for item in frozen["files"]:
        require(digest(ROOT / item["path"]) == item["sha256"], f"frozen input changed: {item['path']}")
    source = (ROOT / "submission/netshield_manuscript.tex").read_text()
    for item in frozen["original_formal_blocks"]:
        env = item["environment"]
        blocks = re.findall(r"\\begin\{" + env + r"\}.*?\\end\{" + env + r"\}", source, re.S)
        require(hashlib.sha256(blocks[item["index"]].encode()).hexdigest() == item["sha256"], f"formal block changed: {env}/{item['index']}")
    equations = {}
    for block in re.findall(r"\\begin\{equation\}.*?\\end\{equation\}", source, re.S):
        for label in re.findall(r"\\label\{([^}]+)\}", block):
            equations[label] = hashlib.sha256(block.encode()).hexdigest()
    for label, sha in frozen["original_labeled_equations"].items():
        require(equations.get(label) == sha, f"original equation changed: {label}")
    abstract = re.search(r"\\begin\{abstract\}.*?\\end\{abstract\}", source, re.S).group()
    require(hashlib.sha256(abstract.encode()).hexdigest() == frozen["abstract_sha256"], "abstract changed")

    public_names = ("PUBLIC_SELECTOR_AUDIT.json", "PUBLIC_SELECTOR_COMPARISON.csv", "TASK_A_REPLICATION_AUDIT.csv")
    with tempfile.TemporaryDirectory(prefix="netshield-selector-check-") as temp:
        output = Path(temp)
        selector = run_selector(output)
        for name in public_names:
            require((output / name).read_bytes() == (AUDIT / name).read_bytes(), f"stale public selector artifact: {name}")
    require(selector["legacy_reconstruction_matches_selected_frozen_fields_cases"] == 36, "public historical reproduction mismatch")
    require(selector["corrected_cases_with_changed_action_counts"] == 5, "unexpected corrected action sensitivity")
    require(selector["corrected_cases_with_changed_trajectory"] == 24, "unexpected corrected trajectory sensitivity")
    require(selector["all_configs_have_one_archived_simulation_outcome"], "unexpected historical stochastic variation")

    experiment = ROOT / "supporting_material/contention_validation"
    results = experiment / "results"
    for line in (results / "SHA256SUMS.txt").read_text().splitlines():
        expected, relative = line.split("  ", 1)
        require(digest(results / relative) == expected, f"contention result hash: {relative}")
    config = json.loads((results / "CONFIG.json").read_text())
    for relative, expected in config["source_sha256"].items():
        require(digest(experiment / relative) == expected, f"contention source changed after execution: {relative}")
    software = audit_software(results)
    crfa = audit_crfa(ROOT / "supporting_material/crfa_hardware")
    require(software == json.loads((AUDIT / "SOFTWARE_LEDGER_RECONSTRUCTION.json").read_text())["software"], "stale software reconstruction")
    require(crfa == json.loads((AUDIT / "CRFA_LEDGER_RECONSTRUCTION.json").read_text())["crfa"], "stale CRFA reconstruction")
    require(software["runs"] == 120 and software["events"] == 1668, "software cohort incomplete")
    require(crfa["service_rounds_reconstructed"] == 10620 and crfa["occurrences_reconstructed"] == 9720, "CRFA cohort incomplete")
    require([crfa["capacity_counts"][c]["post_release_timely_full"] for c in ("low", "mid", "high")] == [990, 2050, 3130], "CRFA timestamp reconstruction differs")

    build = json.loads((ROOT / "submission/audit/PDF_BUILD_METADATA.json").read_text())
    for name, record in build["documents"].items():
        require(digest(ROOT / "submission" / f"{name}.tex") == record["source_sha256"], f"PDF source changed after build: {name}")
        require(digest(ROOT / "submission" / f"{name}.pdf") == record["pdf_sha256"], f"PDF differs from build: {name}")
        for relative, expected in record["repository_input_sha256"].items():
            require(digest(ROOT / "submission" / relative) == expected, f"PDF input changed after build: {relative}")
        require(record["overfull_boxes"] == record["unresolved_references_or_citations"] == 0, f"PDF quality gate: {name}")

    print(f"PASS: {len(frozen['files'])} frozen file hashes, {len(frozen['original_formal_blocks'])} formal blocks, "
          f"{len(equations)} labeled equations, unchanged abstract, 36 reproducible public selector cases, "
          "120 software runs independently reconstructed, 10,620 CRFA service rounds / 9,720 occurrences, "
          "and source-matched manuscript/supplement PDFs")


if __name__ == "__main__":
    main()
