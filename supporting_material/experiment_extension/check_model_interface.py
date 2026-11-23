"""Real-model interface diagnostic on archived pilot inputs, without scoring labels."""
import hashlib
import json
import sys
from pathlib import Path

runtime = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(runtime))
from netshield.portable_models import load_portable_model
from netshield.identity_manifest import validate_runtime_identity_manifest

models = runtime / "artifacts/portable_models"
identity = validate_runtime_identity_manifest(models)
model = load_portable_model(models / "heavy.npz")


def encode(features):
    probability = model.predict_attack_probability(features)
    return [json.dumps(value, separators=(",", ":")).encode()
            for value in ({"prediction": int(probability >= 0.5)},
                          {"score": probability}, {"features": features})]


def consume(payload):
    record = json.loads(payload)
    if "features" in record:
        return int(model.predict_attack_probability(record["features"]) >= 0.5)
    if "score" in record:
        return int(record["score"] >= 0.5)
    return record["prediction"]


for file in sorted((runtime / "data/frozen/window_plans/PILOT01").glob("*.jsonl")):
    for line_number, line in enumerate(file.read_bytes().splitlines(), 1):
        for level, payload in zip(("alert", "summary", "full"), encode(json.loads(line)["features"])):
            print(json.dumps(dict(device=file.stem, line=line_number, level=level,
                                  source_sha256=hashlib.sha256(line).hexdigest(),
                                  model_sha256=identity["models"]["heavy"]["sha256"],
                                  encoded_bytes=len(payload),
                                  encoded_sha256=hashlib.sha256(payload).hexdigest(),
                                  prediction=consume(payload))))
