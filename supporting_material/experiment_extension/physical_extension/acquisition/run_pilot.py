"""Run the frozen paired pilot once. A failed preflight opens no physical arm."""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CODE = ROOT / "code"
sys.path.insert(0,str(CODE / "formal_tools"))
from pilot_mapping import PROTOCOL, backup_volume, copy_evidence, sha, disk_info, gates
from preflight import collect
from artifacts import write_json_new

def run(backup):
    for line in (ROOT/"SHA256SUMS.txt").read_text().splitlines():
        expected,name=line.split("  ",1)
        if sha(ROOT/name)!=expected:
            raise ValueError("Frozen file changed: "+name)
    volume = Path("/Volumes/RESEARCH_DATA")
    if backup and backup.resolve(strict=True) != volume:
        raise ValueError("Copy volume differs from storage amendment")
    os.environ["TON_EXT_BACKUP_VOLUME"] = str(volume)
    destination=Path(tempfile.mkdtemp(dir=ROOT/"checks",prefix="readiness_"))
    status=collect(destination/"preflight")
    print(json.dumps(status,indent=2),flush=True)
    if status["status"]!="PASS":
        return 2
    volume,uid=backup_volume()
    os.environ["TON_EXT_BACKUP_UUID"]=uid
    # Qualification includes a write/read test on the same research volume.
    with tempfile.TemporaryDirectory(dir=volume,prefix=".netshield-qualification-") as t:
        p=Path(t)/"write_probe"
        block=os.urandom(1024*1024)
        with p.open("xb") as f:
            f.write(block);f.flush();os.fsync(f.fileno())
        if p.read_bytes()!=block:
            raise IOError("Backup readback failed")
    write_json_new(destination/"backup.json",dict(copy_type="same physical research disk",uuid=uid,bytes_read_back=len(block),physical_preflight="PASS"))
    registry=ROOT/"raw"
    campaign=registry/PROTOCOL["campaign_id"]
    if campaign.exists():
        raise ValueError("Campaign already registered")
    py=json.loads((ROOT/"bundles/deployment.json").read_bytes())["core_python"]
    def launch(script,*args):
        subprocess.run([py,"-B",str(CODE/"hardware"/script),*map(str,args)],check=True,cwd=ROOT)
    try:
        launch("execute_hardware.py","--plan",ROOT/"plan","--deployment",ROOT/"bundles/deployment.json",
               "--qualification",ROOT/"QUALIFICATION.json","--freeze",ROOT/"INPUT_FREEZE.json","--registry",registry)
    finally:
        if campaign.is_dir():
            # Retain partial attempts as well as successful reconstructed arms.
            summary=campaign/"paired_pilot.json"
            try:
                launch("summarize_blocks.py",ROOT/"plan",campaign,summary)
            finally:
                copy_evidence(campaign,volume/"NetShield_Backup"/campaign.name/"final_registry")
    return 0

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--backup-volume",type=Path)
    sys.exit(run(p.parse_args().backup_volume))
