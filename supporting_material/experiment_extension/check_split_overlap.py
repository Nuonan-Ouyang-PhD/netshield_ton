"""Count cross-split feature matches, independent of labels and source IDs."""
import hashlib
import json
import struct
import sys
from pathlib import Path

root = Path(sys.argv[1])
membership = {}
counts = {}
for bit, split in enumerate(("train", "validation", "test")):
    rows = overlap = 0
    content = hashlib.sha256()
    with (root / (split + ".jsonl")).open("rb") as stream:
        for line in stream:
            content.update(line)
            values = json.loads(line)["features"]
            key = hashlib.sha256(struct.pack(">39d", *(x or 0.0 for x in values))).digest()
            previous = membership.get(key, 0)
            overlap += bool(previous & ((1 << bit) - 1))
            membership[key] = previous | (1 << bit)
            rows += 1
    counts[split] = dict(rows=rows, rows_matching_earlier_split=overlap,
                         file_sha256=content.hexdigest())
print(json.dumps(counts, indent=2))
