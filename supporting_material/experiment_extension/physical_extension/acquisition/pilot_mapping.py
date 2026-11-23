"""Frozen replacement pilot identity, transport and external storage checks."""
import hashlib
import json
import os
import plistlib
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROTOCOL_PATH = ROOT / "ALLOCATOR_PILOT_PROTOCOL.json"
PROTOCOL = json.loads(PROTOCOL_PATH.read_bytes())
ROLES = PROTOCOL["roles"]
HOST_KEYS = ROOT / "enrollment/known_hosts"


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def validate_identity(role, data):
    ref = ROLES[role]
    serial = re.search(r"^Serial\s*:\s*(\S+)", data["cpuinfo"], re.M)
    actual = dict(hostname=data["hostname"]["stdout"].strip(), model=data["model"],
                  architecture=data["architecture"]["stdout"].strip(), kernel=data["kernel"]["stdout"].strip(),
                  serial=serial.group(1) if serial else "", python=data["python"]["stdout"].strip())
    return all(ref[k] == v for k, v in actual.items()) and (
        'PRETTY_NAME="' + ref["os"] + '"' in data["os_release"].splitlines())


def disk_info(path):
    """Resolve APFS physical stores or the physical parent of a partition."""
    device = subprocess.check_output(["df", "-P", str(path)], text=True).splitlines()[-1].split()[0]
    def info(dev):
        return plistlib.loads(subprocess.check_output(["diskutil", "info", "-plist", dev]))
    volume = info(device)
    parts = [s["APFSPhysicalStore"] for s in volume.get("APFSPhysicalStores", [])]
    disks = {info(part)["ParentWholeDisk"] for part in parts} if parts else {volume["ParentWholeDisk"]}
    externals = plistlib.loads(subprocess.check_output(["diskutil","list","-plist","external","physical"]))["WholeDisks"]
    return dict(device=volume["DeviceIdentifier"], volume_uuid=volume["VolumeUUID"],
                internal=volume["Internal"], physical_stores=parts, physical_disks=sorted(disks),
                external_physical=bool(disks) and disks.issubset(externals),
                filesystem=volume["FilesystemType"], free_bytes=shutil.disk_usage(path).free)


def gates(primary, backup):
    return dict(backup_external=backup["external_physical"] and not backup["internal"],
                same_research_volume=primary["volume_uuid"] == backup["volume_uuid"] and
                primary["physical_disks"] == backup["physical_disks"],
                backup_uuid_matches=backup["volume_uuid"] == os.getenv("TON_EXT_BACKUP_UUID",backup["volume_uuid"]))


def backup_volume():
    raw = os.environ.get("TON_EXT_BACKUP_VOLUME")
    if not raw:
        raise ValueError("Research-disk copy volume required")
    mount = Path(raw)
    if mount.resolve() != mount or mount.parent != Path("/Volumes") or not mount.is_mount():
        raise ValueError("Backup must be a mounted external volume")
    a,b = disk_info(ROOT),disk_info(mount)
    if not all(gates(a,b).values()) or b["free_bytes"] < 20*1024**3:
        raise ValueError("Research-disk copy identity or reserve failed")
    return mount,b["volume_uuid"]


def copy_evidence(source, target):
    """Exclusive copy with a readback and a free-space reserve."""
    volume, _ = backup_volume()
    if not target.resolve().is_relative_to(volume) or target.exists():
        raise ValueError("Invalid or reused backup destination")
    names = [p for p in source.rglob("*") if p.is_file()]
    if shutil.disk_usage(volume).free < sum(p.stat().st_size for p in names)+20*1024**3:
        raise ValueError("Insufficient backup reserve")
    target.mkdir(parents=True,exist_ok=False)
    for p in names:
        out = target / p.relative_to(source)
        out.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(p,out)
        if sha(p)!=sha(out):
            raise ValueError("Backup readback mismatch")
    backup_volume()
