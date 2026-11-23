"""Reaggregate the public trajectory export and report contrasts in the stated direction."""
import csv
import json
import sys
from collections import Counter, defaultdict
from hashlib import sha256
from itertools import combinations, product
from math import ceil
from pathlib import Path
from statistics import mean


sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "methodology_repair"))
from run_methodology_repair import detect_period


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def analyze(path):
    data = json.loads((path / "arms.json").read_bytes())
    trajectory = path / "trajectory.csv"
    require(sha256(trajectory.read_bytes()).hexdigest() == data["trajectory_sha256"], "trajectory identity")
    grouped = defaultdict(list)
    with trajectory.open() as stream:
        for row in csv.DictReader(stream):
            grouped[row["attempt"]].append(row)
    blocks = defaultdict(dict)
    periods = {}
    for arm in data["attempts"]:
        if not arm["completed"]:
            continue
        records = grouped.pop(arm["attempt"])
        rounds, queues = defaultdict(list), defaultdict(int)
        measured = Counter()
        for r in records:
            device, i = r["device"], int(r["round"])
            before, new, grant, served, after = [int(r[k]) for k in ("before", "new_payload", "grant", "unique_service", "after")]
            require(before == queues[device] and after == before + new - served, "queue continuity")
            queues[device] = after
            rounds[i].append((device, before + new, grant, served))
            if 5 <= i < 95:
                measured[r["action"]] += 1
        require(measured == arm["measured_action_mix"] and sum(measured.values()) == 270, "measured action mix")
        if data["study"] == "allocator":
            seq = defaultdict(list)
            for item in records:
                i = int(item["round"])
                if 5 <= i < 95:
                    seq[i].append((item["device"], item["action"], int(item["before"]), int(item["after"])))
            states = [tuple(sorted(seq[i])) for i in range(5, 95)]
            periods[arm["attempt"]] = dict(action=detect_period([tuple(v[1] for v in state) for state in states]),
                action_and_queue=detect_period(states))
        cap = 131072 if data["study"] == "allocator" else 262144
        for group in rounds.values():
            require(sorted(row[0] for row in group) == ["P1", "P2", "P3"], "incomplete service round")
        unused = sum(min(cap, sum(v[1] for v in g)) - sum(v[3] for v in g) for g in rounds.values())
        counts = arm["counts"]
        require(unused == counts["unused_serviceable_bytes"], "unused serviceable byte total")
        require(sum(sum(v[3] for v in g) for g in rounds.values()) == counts["aggregate_service_bytes"], "service total")
        require(sum(sum(v[2] for v in g) > cap for g in rounds.values()) == counts["cap_violation_rounds"], "grant cap count")
        require(sum(sum(v[3] for v in g) > cap for g in rounds.values()) == counts["actual_service_cap_violation_rounds"], "service cap count")
        endpoints = path / (arm["attempt"] + "_endpoints.csv")
        require(sha256(endpoints.read_bytes()).hexdigest() == arm["endpoint_sha256"], "endpoint identity")
        with endpoints.open() as f:
            endpoint_rows = list(csv.DictReader(f))
        require(len({(e["device"],e["round"]) for e in endpoint_rows}) == len(endpoint_rows) == 270, "paired endpoint units")
        for name, timing in arm["timing"].items():
            es = endpoint_rows if name == "all_measured_generation_batches" else [e for e in endpoint_rows if int(e["round"]) == 5]
            full = [e for e in es if e["action"] == "H_FULL"]
            require(len(es) == timing["generated"] and len(full) == timing["selected"], "stratum denominator")
            for anchor in ("post_release","nominal"):
                timely, censored = 0, 0
                for e in full:
                    offset = int(e["release_lateness_ns"]) if anchor == "nominal" else 0
                    if e["post_latency_ns"] != "":
                        timely += int(e["post_latency_ns"])+offset <= int(e["deadline_ns"])
                    else:
                        censored += int(e["post_followup_ns"])+offset < int(e["deadline_ns"])
                require(timely == timing[anchor]["timely"] and censored == timing[anchor]["censored"], "deadline endpoint")
                require([timely/len(es),(timely+censored)/len(es)] == timing[anchor]["coverage_bounds"], "coverage bounds")
        all_rounds = arm["timing"]["all_measured_generation_batches"]
        require(all_rounds["post_release"]["timely"] == counts["timely_full"] and all_rounds["generated"] == 270, "event endpoint")
        key = arm["condition"]
        require(key not in blocks[arm["block"]], "duplicate included attempt")
        blocks[arm["block"]][key] = arm
    require(not grouped, "unknown attempts in trajectory")
    contrasts = defaultdict(list)
    for b, methods in sorted(blocks.items()):
        for a, c in combinations(sorted(methods), 2):
            if data["study"] == "shared_stage" and a.split("_")[0] != c.split("_")[0]:
                continue
            # Corrected minus original for allocator. Name both sides on every record.
            left, right = (c, a) if data["study"] == "allocator" else (a, c)
            effect = {}
            for stratum, ta in methods[left]["timing"].items():
                tb = methods[right]["timing"][stratum]
                lo, hi = ta["post_release"]["coverage_bounds"]
                other_lo, other_hi = tb["post_release"]["coverage_bounds"]
                effect[stratum] = [lo - other_hi, hi - other_lo]
            contrasts[left+" minus "+right].append(dict(block=b, bounds=effect,
                unused_difference_bytes=methods[left]["counts"]["unused_serviceable_bytes"] - methods[right]["counts"]["unused_serviceable_bytes"]))
    intervals = {}
    if data["phase"] == "formal" and sum(len(x) for x in blocks.values()) == data["planned_arms"]:
        for name, rows in contrasts.items():
            if len(rows) != len(blocks) or not 2 <= len(rows) <= 6:
                continue
            n = len(rows)
            interval = {}
            for stratum in rows[0]["bounds"]:
                samples = [tuple(sum(rows[j]["bounds"][stratum][k] for j in indices)/n for k in (0,1))
                           for indices in product(range(n), repeat=n)]
                interval[stratum] = [sorted(v[k] for v in samples)[ceil(p * len(samples))-1]
                                     for k,p in ((0,.025),(1,.975))]
            intervals[name] = interval
    return dict(campaign=data["campaign"], action_periods=periods, paired_percentile_intervals=intervals, planned=data["planned_arms"], attempts=len(data["attempts"]),
                complete_arms=sum(len(x) for x in blocks.values()), by_contrast=dict(contrasts),
                mean_within_block_bounds={k:{s:[mean(row["bounds"][s][i] for row in rows) for i in range(2)]
                for s in rows[0]["bounds"]} for k,rows in contrasts.items()})


if __name__ == "__main__":
    print(json.dumps(analyze(Path(sys.argv[1])), indent=2, allow_nan=False))
