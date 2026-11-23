#!/usr/bin/env python3
"""Freeze or verify named files without copying private contents or paths.

This records byte identity, not scientific adequacy or execution. Use a private
output directory for manifests of private experimental material.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def input_map(values: list[str]) -> dict[str, Path]:
    result = {}
    for item in values:
        name, separator, value = item.partition("=")
        if not separator or not value or not re.fullmatch(r"[A-Za-z0-9_.-]+", name):
            raise ValueError("Inputs must use unique logical NAME=PATH identifiers")
        if name in result:
            raise ValueError(f"Duplicate input name: {name}")
        path = Path(value).expanduser()
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"Input must be a regular non-symlink file: {name}")
        result[name] = path
    if not result:
        raise ValueError("At least one input file is required")
    return result


def records(inputs: dict[str, Path]) -> dict:
    output = {}
    for name, path in sorted(inputs.items()):
        before = path.stat()
        sha = digest(path)
        after = path.stat()
        if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) != (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns):
            raise ValueError(f"Input changed during hashing: {name}")
        output[name] = {"sha256": sha, "size_bytes": after.st_size}
    return output


def freeze(inputs: dict[str, Path], manifest: Path, label: str) -> dict:
    if not label.strip():
        raise ValueError("A nonempty manifest label is required")
    if manifest.exists():
        raise ValueError("Manifest already exists; create a new version, do not overwrite")
    result = {
        "schema_version": 1,
        "label": label,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "status": "INPUT_IDENTITIES_FROZEN_EXPERIMENT_NOT_EXECUTED",
        "interpretation": "Byte identity only. Scientific qualification, temporal separation and actual execution require separate evidence.",
        "tool_sha256": digest(Path(__file__)),
        "files": records(inputs),
    }
    manifest.parent.mkdir(parents=True, exist_ok=True)
    with manifest.open("x", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return result


def verify(inputs: dict[str, Path], manifest: Path) -> dict:
    result = json.loads(manifest.read_text(encoding="utf-8"))
    if result.get("schema_version") != 1 or result.get("status") != "INPUT_IDENTITIES_FROZEN_EXPERIMENT_NOT_EXECUTED":
        raise ValueError("Unsupported manifest schema or status")
    expected = result.get("files")
    if not isinstance(expected, dict) or set(expected) != set(inputs):
        raise ValueError("Input names must exactly match the manifest; missing/extra inputs are not ignored")
    actual = records(inputs)
    changed = [name for name in expected if expected[name] != actual[name]]
    if changed:
        raise ValueError("Input identity mismatch: " + ", ".join(sorted(changed)))
    return {"status": "IDENTITIES_MATCH", "manifest_sha256": digest(manifest), "files_verified": len(actual)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("freeze", "verify"))
    parser.add_argument("--input", action="append", required=True, metavar="NAME=PATH")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--label", default="")
    args = parser.parse_args()
    try:
        inputs = input_map(args.input)
        result = freeze(inputs, args.manifest, args.label) if args.action == "freeze" else verify(inputs, args.manifest)
    except (OSError, ValueError, TypeError) as error:
        parser.error(str(error))
    print(json.dumps({key: value for key, value in result.items() if key != "files"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
