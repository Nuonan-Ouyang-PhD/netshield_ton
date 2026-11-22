# Public review of the retained private rerun and diagnostic reconciliation

Reviewed baseline: `9cc64edf8520c7d15e8fb95724be754d35597171` in PR #3.
This review checks the exported records, public source and supplied PDFs. It
does not reopen the private corpus or hardware logs, execute the private
models, or acquire new physical observations. The subsequent changes repair
the public summary verifier and update the continuation instructions; the
four exported JSON receipts and the two PDFs remain byte-identical.

## Completed work that no longer belongs on the pending list

| Item | Evidence checked | Conclusion within scope |
|---|---|---|
| Repaired private-record checker rerun | Checker and legacy SHA-256 values, default accepted-index identity, fresh private-output digest and qualification counters | The reported fresh execution is `PASS_RECORDED_FIELDS_ONLY`; the old result has not been relabelled as a new run. |
| Retained diagnostic reconciliation | Preserved-output identities, reconciliation source, seven group summaries and selected-subset counts | Preservation, event pairing and the subset-overlap audit have actual recorded outputs. Independent capture qualification remains separate. |
| Allocator comparison receipts | Two runtime tree identities and ordered allocation-result digests | Public rules reproduce both case digests across the declared 22,638 comparisons. This is a deterministic software check. |
| Manuscript integration | Current source/PDF/input hashes, new paragraphs and all 47 rendered pages | The submitted 14-page main paper and 33-page supplement agree with the new counts and have no observed layout defect. |

The earlier `FOLLOWUP_REVIEW.md` describes the state before these receipts
were supplied. Its requests to rerun the repaired checker and retain the
diagnostic outputs have now been satisfied. The current continuation is
[`CODEX_HANDOFF_CN.md`](../CODEX_HANDOFF_CN.md).

## Recorded-field qualification

[`qualification_summary.json`](qualification_summary.json) identifies the
active checker and the retained legacy version correctly. Its private index
digest equals the default public accepted-index digest; it declares the
default index was used. Expected, input and completed cohorts all contain
216 arms. The counts reconcile with the earlier public arm export:

- 864 runtime manifests and 63,720 checked/verified service rounds;
- 58,320 measured generated events;
- 24,012 required Core returns, all present;
- 14,416 timely and 9,596 late returns.

The public receipt records no qualification errors. Optional identity fields
that were absent are counted as absent. `PASS_RECORDED_FIELDS_ONLY` does not
prove per-chunk delivery, remote per-file deployment, clock boot epochs, or
physical NIC accounting. The historical `PASS_WITH_ISSUES` and its unresolved
archive issues remain separate. The current public review validates the
export's identity and consistency; the actual raw-record scan was performed
in the private local environment reported at the reviewed baseline.

## Meaning and arithmetic of the 896-row diagnostic

The reconciliation source checks 896 unique event identifiers against the
seven actual test-file prefixes and requires one prediction per event and
representation: 2,688 predictions. It compares both per-group and pooled
confusion counts with the preserved diagnostic output. It validates finite
input and quantized features and binds training-file/model identities.

The public seven-group table yields the following independent sums:

| Rule | Train only | Validation only | Both | Union matches | Fraction of 896 |
|---|---:|---:|---:|---:|---:|
| Exact feature vector | 308 | 3 | 55 | 366 | 40.8482% |
| Three significant digits | 465 | 3 | 76 | 544 | 60.7143% |

The 544 rounded matches include the 366 exact matches. Rounding can miss close
vectors across bucket boundaries. The exported global counts of 895 exact
vectors and 863 rounded vectors describe distinct vectors within the selected
rows; they do not count independent captures. Their consistency bounds can be
checked publicly, but their precise cross-group intersections require the
private feature rows. Neither the 530 exact-unmatched rows nor the 352
rounded-unmatched rows are thereby qualified as independent acquisitions.
The comparison uses the complete archived train/validation partitions; it
does not identify which matching rows entered the diagnostic consumer's
smaller fitting subset or quantify accuracy inflation caused by overlap.

Each representation has 768 TP, 128 TN, zero FP/FN, so the observed paired
correctness difference is zero on this selected diagnostic. The result does
not estimate independent held-out efficacy or prove that full evidence has
no value. Hash binding is retrospective: the new receipts do not establish
the timing of the initial model execution or a complete pre-execution freeze.

## Public allocator reproduction

The public corrected `simulation_primitives.waterfill` and the retained
legacy `waterfill` were evaluated over the same ordered demands, capacities
and rotation offsets as `hardware/recheck_allocator.py`. Only the legacy
function was extracted; its private-input driver was not imported or run.

| Rule | Comparisons | Matches to corrected reference | Ordered result SHA-256 |
|---|---:|---:|---|
| Original | 22,638 | 18,228 | `ee7ea8c2f74138f699859c742471912564a13770857bdff49b70eab8019ef48d` |
| Corrected | 22,638 | 22,638 | `6d63e849caa655317eb51c938736461e56b36950ffc8fe89aaff43f5b5b77783` |

Both digests match the supplied private-runtime receipts. In this enumeration,
the 4,410 original-rule mismatches leave demand unserved despite remaining
capacity: 3,087 waste 1 B and 1,323 waste 2 B. Neither rule exceeds cap or any
individual demand. The original ignores rotation, so these comparisons cover
7,546 distinct original `(demands, cap)` inputs, of which 1,470 have this
remainder problem. These are exhaustive small-input software cases, not
independent experiments or an estimate of hardware failure frequency.

## Public-verifier repair

The supplied summaries themselves were consistent. A synthetic mutation
nevertheless showed that the old public verifier accepted an eighth entry
reusing an existing group name, making the denominator 1,024. It also accepted
zero global distinct counts because those fields were not checked.

The revised verifier rejects malformed group cardinality, non-integer or
negative counts, inconsistent denominators/outcomes, impossible distinct
counts and violations of necessary exact-to-rounded inclusion. Checks use
explicit failures and remain active under `python -O`. Regression fixtures
cover those demonstrated failure modes. The public verifier and its tests are
included in `scripts/verify_experiment_extension.py`; the four source JSON
receipts and the private producer are unchanged.

The [current verification receipt](../RETAINED_REVIEW_VERIFICATION.json)
records 63 passing preparation/reconciliation fixtures, including the ten
new public-summary tests, and passing public-export and frozen-evidence
checks. The four repository validators also pass. All 120 frozen scientific
file hashes, 14 formal blocks, 21 labelled equations and the abstract remain
unchanged. These fixture counts are software validation, not experiment sizes.

## PDF review

The source hashes, PDF hashes and all 12 main / 13 supplementary metadata
input hashes match. Both PDFs identify pdfTeX 1.40.29, consistent with the
supplied TeX Live 2026 build record. This review did not rerun TeX or obtain
the private build's fresh compiler logs; the three-pass and log-check claims
remain the supplied build record.

All 47 pages were freshly rendered and inspected in six contact sheets.
Main pages 12–14 and supplementary page 33 were also inspected at full
resolution. No clipping, overlap, missing glyphs or out-of-page content blocks
were observed; all 35 references are present. The added 366/544 and
896/895/863 paragraphs preserve the diagnostic and acquisition limitations.

| PDF | Pages | SHA-256 |
|---|---:|---|
| Main manuscript | 14 | `77f7ac03b8934a1c128e98f89504f32a318ff6eb55de9a29dda434161ad2309a` |
| Supplementary material | 33 | `04cc6a5d87f6faad0ca2222b891a48934ee98849be00a0be164fc91dc232204e` |

## Remaining execution dependencies

1. Recover and qualify the three-probe testbed for the old/corrected allocator
   comparison. P1's reported identity response does not qualify P2/P3; failed
   DNS and SSH attempts do not diagnose whether those devices are powered off.
2. Finish the deployable causal shared-stage controller, independent stage
   calibration and pilot before freezing its physical comparison. Public
   assumed-stage simulations remain software evidence.
3. Obtain parent capture/episode identities, boundaries and row mappings;
   qualify the new train/validation/test split and freeze the content study.
   Measured timely-correct output requires its own paired communication
   experiment on those qualified inputs.

No new physical arms or formal independent content-value measurements are
added by this public review. Existing records are preserved, and completed
private reruns should not be repeated solely to refresh status documents.
