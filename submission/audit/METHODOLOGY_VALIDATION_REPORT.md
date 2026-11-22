# Methodology validation report

## Executed scope

This revision starts from Git commit
`fe09ee0eca28dc666dd9c729ac266b8426c055b9`. It corrects the public offline
analysis source, executes public deterministic model checks, independently
reconstructs public exported ledgers, and revises the manuscript's evidence
labels. It does not execute a Raspberry Pi campaign, reopen the primary
private raw archive, measure new Wi-Fi latency, train a detector, or rerun
the existing hardware bootstrap contrasts.

## Checks completed

| Check | Result and exact scope |
|---|---|
| Frozen scientific artifacts | 120 file hashes unchanged; list in `supporting_material/methodology_validation/FROZEN_INPUTS.json` |
| Existing mathematics and abstract | 14 theorem/proposition/corollary/proof blocks, 21 labeled equations and abstract unchanged |
| Public Task A reconstruction | 36/36 old-source configurations reproduce five selected archived output fields using published rounded utilities/payloads |
| Task A replication audit | 432 rows = 36 configurations × 12 labels; each configuration has one trajectory and one simulation outcome |
| Corrected allocator sensitivity | 24/36 trajectories and 5/36 action mixes differ; separate corrected outputs retained |
| Allocator/admission/endpoint tests | 12 tests pass; includes 13,750 independent integer conservation/fairness cases |
| Ledger mutation tests | 6 test groups pass; forged zero-cap flags, missing/duplicate records and wrong timestamps/flags are rejected |
| Shared-service model tests | 9 tests pass, including a 1-ms unmodeled-delay counterexample to physical deadline inference |
| New deterministic experiment | 30 configurations × 4 policies = 120 runs; 1,668 events and 1,637 event/round service records |
| Independent software accounting | 167 nonempty service rounds reconstructed, no cap excess; bytes, endpoint milestones and summary counts agree |
| Public CRFA export reconstruction | 36 runs, 10,620 service rounds and 9,720 events; post-release timely full-core counts 990/2050/3130 and nominal counts 360/720/1079 |
| Existing repository checks | `verify_methodology.py`, `verify_campaign_audit.py`, `verify_submission.py`, and `submission/validate_submission.py` pass |

The new revision verifier reruns the 36-case public selector audit in a
temporary directory and requires byte-identical derived artifacts. It also
recalculates both ledger audits, checks experiment source/result hashes,
and verifies the frozen artifact/mathematics hashes. A simulator's own
`cap_violation_counter` is never accepted as the independent cap check.

## Important interpretation

- Old A/B fields containing `core_result` actually terminate at payload
  upload completion. Current source and paper state that endpoint.
- The new contention model uses declared latency assumptions and the same
  model for reservation and execution; it is a counterexample/conformance
  study, not an independent physical-safety or effectiveness comparison.
- Existing hardware C-QPG/CRFA results and nonconcurrent paired intervals
  remain frozen. The original primary raw audit's `PASS_WITH_ISSUES` state
  remains applicable.
- CRFA record reconstruction uses its public per-probe export, not the
  private primitive archive or a new physical-link measurement.
- Evidence-content detection utility remains **NOT_EXECUTED**. See the
  protocol in `supporting_material/contention_validation/DETECTION_VALUE_PROTOCOL.md`.

## Source versioning and manifests

The original methodology driver is preserved in `legacy/` with the exact
hash named in its old public manifest. `scripts/verify_methodology.py`
explicitly maps only that old source entry to the preserved file; the
historical CSVs/JSONs and their original manifest are unchanged. Current
source hashes are captured by the new public-model audit/configuration.
The current `submission/SHA256SUMS.txt` describes the revised deliverables;
older audit documents are labeled historical and do not certify this build.

## PDF build

The genuine IEEEtran source build, final page counts, input/output hashes
and visual checks are recorded in `PDF_BUILD_REPORT.md` and
`PDF_BUILD_METADATA.json` in this directory. The build command is
`bash scripts/build_submission.sh`. Those build checks are separate from
simulation execution and hardware evidence auditing.
