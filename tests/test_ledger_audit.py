"""Mutate public saved ledgers to test the auditor, not the simulator.

Fixtures are whole, genuine exported runs. All mutations occur in temporary
directories; frozen research files are never edited. No allocator or event
simulator is imported to decide what constitutes a valid ledger.
"""

from __future__ import annotations

import copy
import csv
import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("independent_ledger_auditor", ROOT / "scripts/audit_service_ledgers.py")
audit = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(audit)


def read(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


class LedgerMutationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        software = ROOT / "supporting_material/contention_validation/results"
        # This actual zero-delay run uses exactly the middle capacity and has
        # both admitted and rejected requests, including an inclusive1000ms
        # endpoint. A second run exercises actual nonzero pipeline durations.
        wanted = {
            "n03_mid_empty_zero__new_bytes_only",
            "n03_mid_empty_assumed_homogeneous__new_bytes_only",
        }
        cls.software = {
            name: [row for row in read(software / name) if row["run_id"] in wanted]
            for name in ("RUN_SUMMARY.csv", "EVENT_LEDGER.csv", "SERVICE_LEDGER.csv")
        }
        crfa = ROOT / "supporting_material/crfa_hardware"
        service = read(crfa / "CRFA_SERVICE_AUDIT.csv")
        run = service[0]["run_id"]
        cls.crfa = {
            "CRFA_SERVICE_AUDIT.csv": [row for row in service if row["run_id"] == run],
            "CRFA_OCCURRENCE_LEDGER.csv": [
                row for row in read(crfa / "CRFA_OCCURRENCE_LEDGER.csv")
                if row["event_key"].split("|")[1] == run
            ],
        }

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="netshield_ledger_audit_")
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)

    def materialize(self, fixture):
        for name, rows in fixture.items():
            write(self.directory / name, rows)
        return self.directory

    def test_genuine_saved_software_and_crfa_runs_pass(self):
        software = audit.audit_software(self.materialize(self.software))
        self.assertEqual(software["status"], "PASS")
        self.assertEqual(software["runs"], 2)
        self.assertEqual(software["events"], 6)
        crfa = audit.audit_crfa(self.materialize(self.crfa))
        self.assertEqual(crfa["status"], "PASS")
        self.assertEqual(crfa["service_runs"], 1)
        self.assertEqual(crfa["occurrences_reconstructed"], 270)
        self.assertEqual(crfa["capacity_counts"]["low"]["selected_full"], 90)

    def test_forged_zero_violation_flags_do_not_hide_extra_service(self):
        with self.subTest(kind="software"):
            fixture = copy.deepcopy(self.software)
            for row in fixture["RUN_SUMMARY.csv"]:
                row["cap_violation_counter"] = "0"
            target = next(row for row in fixture["SERVICE_LEDGER.csv"] if "_empty_zero__" in row["run_id"])
            target["served_bytes"] = str(int(target["served_bytes"]) + 1)
            with self.assertRaisesRegex(audit.AuditError, "cap violation"):
                audit.audit_software(self.materialize(fixture))
        with self.subTest(kind="CRFA"):
            fixture = copy.deepcopy(self.crfa)
            row = fixture["CRFA_SERVICE_AUDIT.csv"][0]
            row["actual_shared_cap_violation"] = "False"
            empty_device = next(d for d in ("P1", "P2", "P3") if row[f"{d}_grant_bytes"] == "0")
            row[f"{empty_device}_grant_bytes"] = "1"
            row[f"{empty_device}_demand_bytes"] = "1"
            row["sum_grant_bytes"] = str(int(row["sum_grant_bytes"]) + 1)
            row["aggregate_service_demand_bytes"] = str(int(row["aggregate_service_demand_bytes"]) + 1)
            with self.assertRaisesRegex(audit.AuditError, "cap violation"):
                audit.audit_crfa(self.materialize(fixture))

    def test_missing_and_duplicate_software_service_are_rejected(self):
        for mutation in ("missing", "duplicate"):
            with self.subTest(mutation=mutation):
                fixture = copy.deepcopy(self.software)
                services = fixture["SERVICE_LEDGER.csv"]
                if mutation == "missing":
                    services.pop(0)
                else:
                    services.append(copy.deepcopy(services[0]))
                with self.assertRaises(audit.AuditError):
                    audit.audit_software(self.materialize(fixture))

    def test_software_upload_result_and_deadline_flags_are_reconstructed(self):
        for field in ("upload_done_tick", "result_return_tick", "upload_on_time", "result_on_time"):
            with self.subTest(field=field):
                fixture = copy.deepcopy(self.software)
                event = next(row for row in fixture["EVENT_LEDGER.csv"]
                             if row["selected"] == "1" and "_empty_zero__" in row["run_id"])
                if field.endswith("_tick"):
                    event[field] = str(int(event[field]) + 1)
                else:
                    event[field] = "0" if event[field] == "1" else "1"
                with self.assertRaises(audit.AuditError):
                    audit.audit_software(self.materialize(fixture))

    def test_crfa_requires_every_measured_service_occurrence_once(self):
        for mutation in ("missing", "renamed_duplicate"):
            with self.subTest(mutation=mutation):
                fixture = copy.deepcopy(self.crfa)
                events = fixture["CRFA_OCCURRENCE_LEDGER.csv"]
                if mutation == "missing":
                    # Missing H_NONE is still a missing generated event;
                    # auditing only selected full events must not hide it.
                    index = next(i for i, event in enumerate(events) if event["admitted_action_id"] == "H_NONE")
                    events.pop(index)
                else:
                    copied = copy.deepcopy(events[0])
                    # Keep the key structurally well formed while assigning
                    # a new external identity to the same serviced request.
                    copied["campaign_id"] = "SYNTHETIC_MUTATION"
                    parts = copied["event_key"].split("|")
                    parts[0] = copied["campaign_id"]
                    copied["event_key"] = "|".join(parts)
                    events.append(copied)
                with self.assertRaises(audit.AuditError):
                    audit.audit_crfa(self.materialize(fixture))

    def test_crfa_result_deadline_flags_are_reconstructed(self):
        for field in ("post_release_on_time_full", "nominal_on_time_full", "full_core_result_returned"):
            with self.subTest(field=field):
                fixture = copy.deepcopy(self.crfa)
                event = next(row for row in fixture["CRFA_OCCURRENCE_LEDGER.csv"] if row["admitted_action_id"] == "H_FULL")
                event[field] = "False" if event[field] == "True" else "True"
                with self.assertRaises(audit.AuditError):
                    audit.audit_crfa(self.materialize(fixture))


if __name__ == "__main__":
    unittest.main()
