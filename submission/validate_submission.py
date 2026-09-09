#!/usr/bin/env python3
"""Run self-contained checks for the NetShield ToN submission package."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MANUSCRIPT = ROOT / "manuscript.tex"
SUPPLEMENTARY = ROOT / "supplementary.tex"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


manuscript = MANUSCRIPT.read_text()
supplementary = SUPPLEMENTARY.read_text()

bibliography_keys = set(re.findall(r"\\bibitem\{([^}]+)\}", manuscript))
citation_keys: set[str] = set()
for group in re.findall(r"\\cite\{([^}]+)\}", manuscript):
    citation_keys.update(key.strip() for key in group.split(","))

require(len(bibliography_keys) == 28, "expected 28 bibliography entries")
require(citation_keys == bibliography_keys, "citation/bibliography mismatch")
require((ROOT / "manuscript.pdf").is_file(), "missing manuscript.pdf")
require((ROOT / "supplementary.pdf").is_file(), "missing supplementary.pdf")
require(len(list((ROOT / "figures").glob("*.pdf"))) == 7, "expected seven figures")
require(len([p for p in (ROOT / "tables").iterdir() if p.is_file()]) == 10,
        "expected ten table/data files")

require(r"\title{Supplementary Material: NetShield}" in supplementary,
        "supplementary title is not submission-clean")

for token in ["0.9332", "0.2845", "timely_f1", "NetShield is the first"]:
    require(token.lower() not in manuscript.lower(),
            f"forbidden legacy/priority token present: {token}")

for path in ROOT.rglob("*"):
    if path.is_file():
        name = path.name.lower()
        require("version" not in name and not re.search(r"20\d{6}", name),
                f"non-clean filename: {path.relative_to(ROOT)}")

print("PASS: clean naming, 28 cited references, expected files, and claim scan")
