"""Verify public arithmetic and source identities in the retained review."""
import hashlib
import json
from pathlib import Path

base = Path(__file__).resolve().parent


def load(name):
    return json.loads((base/name).read_bytes())


def check(ok, msg):
    if not ok:
        raise ValueError(msg)


q = load("qualification_summary.json")
check(q["expected_index_is_repository_default"] and q["status"]=="PASS_RECORDED_FIELDS_ONLY"
      and q["errors"]==[], "qualification result")
for key,file in (("checker_sha256",base.parent/"qualify_private_records.py"),
                 ("legacy_checker_sha256",base.parent/"private_record_qualification/legacy/qualify_private_records_dc5269c.py"),
                 ("expected_index_sha256",base.parents[1]/"formal_campaign_audit/results/ATTEMPT_INDEX.json")):
    check(hashlib.sha256(file.read_bytes()).hexdigest()==q[key],key)
c=q["counts"]
check(c["generated"]==216*3*90 and c["verified_rounds"]==216*295 and
      c["runtime_manifest_matches"]==216*4 and c["returned_core"]-c["timely_core"]==9596,"counts")
d=load("diagnostic_review.json")
check(len({f["group"] for f in d["files"]})==7,"groups")
for name in ("CONTENT_PROTOCOL.md","content_diagnostic.py"):
    check(hashlib.sha256((base.parent/name).read_bytes()).hexdigest()==d["sha256"][name],name)
for group in d["files"]:
    check(group["generated"]==128,"file size")
    for level in ("alert","summary","full"):
        check(sum(group[level].values())==128,"outcome census")
    for rule in ("exact","rounded"):
        check(sum(group[rule][k] for k in ("train_only","validation_only","both","neither"))==128,"bucket census")
for rule,n in (("exact",366),("rounded",544)):
    check(sum(128-f[rule]["neither"] for f in d["files"])==n,rule)
print("PASS: published source identities, cohort arithmetic and seven group summaries")
