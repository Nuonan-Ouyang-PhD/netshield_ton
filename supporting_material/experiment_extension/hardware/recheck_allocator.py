"""Run once per private runtime in a fresh interpreter and retain case digest."""
import hashlib
import itertools
import json
import sys
from pathlib import Path

runtime, mode = Path(sys.argv[1]), sys.argv[2]
if mode not in ("original","corrected"):
    raise ValueError(mode)
sys.path.insert(0, str(runtime.resolve()))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]/"methodology_repair"))
from netshield.core import Coordinator
from netshield.common import package_tree_sha256
from simulation_primitives import waterfill

h = hashlib.sha256()
total = matches = 0
for v in itertools.product(range(7),repeat=3):
    demands = dict(zip(("P1","P2","P3"),v))
    for cap, offset in itertools.product(range(22),range(3)):
        args = (demands,cap,offset) if mode=="corrected" else (demands,cap)
        actual = Coordinator._allocate_shared_cap(*args)
        matches += actual == waterfill(demands,cap,tie_offset=offset)
        total += 1
        h.update(json.dumps([v,cap,offset,actual],sort_keys=True).encode()+b"\n")
print(json.dumps(dict(mode=mode, cases=total, matches=matches, tree=package_tree_sha256(),
                      case_digest=h.hexdigest())))
if mode=="corrected" and matches!=total:
    raise SystemExit(1)
