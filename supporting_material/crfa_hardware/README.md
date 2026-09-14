# CRFA hardware extension

This directory contains the path-free result layer for the separately frozen
36-arm Cyclic Rotating Full Admission (CRFA) hardware extension.

- 36 accepted arms from 55 indexed attempts;
- 19 infrastructure exclusions retained in `CRFA_ATTEMPT_INDEX.json`;
- 9,720 measured occurrences and 10,620 reconstructed service rounds;
- zero shared-capacity violations;
- timing outcomes are reported as outcomes, not acceptance gates.

The occurrence ledger, service audit, summaries, timing reconstruction,
protocol, and number provenance are included for independent review. Absolute
machine paths and private host identifiers have been removed. The raw arm
archives and private hardware material remain controlled and are not included
in GitHub.

Verify the committed hashes from this directory with:

```bash
python3 - <<'PY'
import hashlib
from pathlib import Path

root = Path("supporting_material/crfa_hardware")
for line in (root / "SHA256SUMS.txt").read_text().splitlines():
    digest, name = line.split("  ", 1)
    actual = hashlib.sha256((root / name).read_bytes()).hexdigest()
    if actual != digest:
        raise SystemExit(f"SHA-256 mismatch: {name}")
print("PASS: CRFA hardware result-layer hashes")
PY
```
