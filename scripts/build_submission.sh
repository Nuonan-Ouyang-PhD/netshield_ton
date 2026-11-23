#!/usr/bin/env bash
# Build current source with genuine IEEEtran; preserve frozen evidence.
set -euo pipefail

repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
source_dir="$repo_root/submission"
for command_name in pdflatex kpsewhich python3; do
    if ! command -v "$command_name" >/dev/null 2>&1; then
        printf 'Missing dependency: %s. See submission/BUILD_INSTRUCTIONS.md.\n' "$command_name" >&2
        exit 1
    fi
done
for tex_file in IEEEtran.cls pdflatex.fmt pdftex.map amsmath.sty amssymb.sty \
    mathtools.sty amsthm.sty booktabs.sty array.sty multirow.sty graphicx.sty \
    cite.sty url.sty enumitem.sty microtype.sty hyperref.sty \
    longtable.sty pdflscape.sty float.sty ptmr7t.tfm utmr8a.pfb; do
    if ! kpsewhich "$tex_file" >/dev/null 2>&1; then
        printf 'TeX cannot locate %s. Install/repair the actual distribution; no substitute class is used.\n' "$tex_file" >&2
        exit 1
    fi
done

build_parent="${TON_PDF_BUILD_ROOT:-${TMPDIR:-/tmp}}"
mkdir -p -- "$build_parent"
build_dir="$(mktemp -d "$build_parent/netshield-pdf.XXXXXXXX")"
printf 'Building current sources in %s\n' "$build_dir"
cd -- "$source_dir"
for document in netshield_manuscript netshield_supplementary; do
    for pass_number in 1 2 3; do
        if ! pdflatex -no-shell-escape -interaction=nonstopmode -halt-on-error \
            -file-line-error -recorder -output-directory="$build_dir" \
            "$document.tex" > "$build_dir/$document.pass$pass_number.stdout" 2>&1; then
            tail -n 50 "$build_dir/$document.pass$pass_number.stdout" >&2
            printf 'Build failed; existing PDFs were not replaced. Logs: %s\n' "$build_dir" >&2
            exit 1
        fi
    done
done

python3 - "$build_dir" "$source_dir" <<'PY'
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

build_dir, source_dir = map(Path, sys.argv[1:])
documents = ("netshield_manuscript", "netshield_supplementary")
fatal_patterns = (
    r"Overfull \\[hv]box", r"(?:Citation|Reference).*?undefined",
    r"There were undefined references", r"Rerun to get cross-references right",
    r"Label\(s\) may have changed", r"Missing character:",
    r"Fatal error", r"Emergency stop", r"^!",
)
results = {}
for name in documents:
    log = (build_dir / f"{name}.log").read_text(errors="replace")
    problems = [pattern for pattern in fatal_patterns if re.search(pattern, log, re.MULTILINE)]
    if problems:
        raise SystemExit(f"Build quality gate failed for {name}: {problems}. Inspect {build_dir}; existing PDFs were not replaced.")
    pdf = build_dir / f"{name}.pdf"
    if not pdf.is_file() or not pdf.stat().st_size:
        raise SystemExit(f"Missing output: {pdf}")
    output_line = re.search(r"Output written on .*?\((\d+) pages?", log, re.DOTALL)
    input_hashes = {}
    for line in (build_dir / f"{name}.fls").read_text(errors="replace").splitlines():
        if not line.startswith("INPUT "):
            continue
        item = Path(line[6:])
        item = (source_dir / item).resolve() if not item.is_absolute() else item.resolve()
        if item.is_relative_to(source_dir) and item.is_file() and item.suffix in {".tex", ".pdf", ".bib", ".bst", ".sty", ".cls"}:
            input_hashes[item.relative_to(source_dir).as_posix()] = hashlib.sha256(item.read_bytes()).hexdigest()
    results[name] = {
        "source_sha256": hashlib.sha256((source_dir / f"{name}.tex").read_bytes()).hexdigest(),
        "pdf_sha256": hashlib.sha256(pdf.read_bytes()).hexdigest(),
        "pages": int(output_line.group(1)) if output_line else None,
        "warning_lines": [line for line in log.splitlines() if "Warning:" in line],
        "repository_input_sha256": dict(sorted(input_hashes.items())),
        "overfull_boxes": 0, "unresolved_references_or_citations": 0,
    }
ieee_class = Path(subprocess.check_output(["kpsewhich", "IEEEtran.cls"], text=True).strip())
metadata = {
    "engine": subprocess.check_output(["pdflatex", "--version"], text=True).splitlines()[0],
    "ieeetran_sha256": hashlib.sha256(ieee_class.read_bytes()).hexdigest(),
    "passes_per_document": 3, "shell_escape_enabled": False,
    "documents": results,
    "scope": "PDF build and log checks only; no simulation, hardware rerun, or raw-evidence audit",
    "font_scope": "Imported figure fonts are retained; inspect pdffonts before archival-format claims",
}
(build_dir / "build_metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
for name in documents:
    shutil.copy2(build_dir / f"{name}.pdf", source_dir / f"{name}.pdf")
print(json.dumps(metadata, indent=2))
print(f"Built and copied both PDFs. Logs and metadata: {build_dir}")
PY
