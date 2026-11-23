"""Rebuild the 16 empirical envelopes from within-arm, same-clock timings."""
import hashlib
import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parent
sys.path.insert(0, str(root.parent / "stage_adapter"))
from build_profile import batch_components
from stage_admission import envelope_key, validate_profile


def verify(profile_path):
    profile = json.loads(profile_path.read_bytes())
    validate_profile(profile)
    if profile["calibration_complete_blocks"] != 1 or profile["margin_ns"] != 0:
        raise ValueError("Unexpected calibration design")
    expected = {envelope_key(e["backlog_by_probe_bytes"], e["selected_devices"]): e
                for e in profile["envelopes"]}
    seen = set()
    for line in (root / "calibration_relative.jsonl").read_text().splitlines():
        row = json.loads(line)
        key = envelope_key(row["backlog_by_probe_bytes"], row["selected_devices"])
        if key in seen or row["campaign_id"] != profile["campaign"]:
            raise ValueError("Calibration identity mismatch")
        target = expected[key]
        seen.add(key)
        values = batch_components(row, {"backlog_by_probe_bytes": target["backlog_by_probe_bytes"],
                                        "stage_capture_devices": target["selected_devices"]})
        if target["observed_batches"] != 1 or any(target[k] != v for k, v in values.items()):
            raise ValueError("Calibration envelope differs from observed timing")
    if seen != expected.keys() or len(seen) != 16:
        raise ValueError("Calibration conditions incomplete")
    print(f"Verified {len(seen)} envelopes. Profile SHA-256 {hashlib.sha256(profile_path.read_bytes()).hexdigest()}")


if __name__ == "__main__":
    verify(root / "physical_profile.json" if len(sys.argv) == 1 else Path(sys.argv[1]))
