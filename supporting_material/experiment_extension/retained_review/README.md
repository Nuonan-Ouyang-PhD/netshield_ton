# Recorded-field and diagnostic reconciliation

Base b8a978bd7606657e157c1eb3394ddf32d5ff912e, clean checkout. A fresh
output from the active checker used the default public index. The complete
private output digest is 42e7d0cd90cf95844237bbcec36513d7ccf7fdbcb39e77da0b753707dde1cb07.
The earlier private report retains digest d4010a4c45df2824d1f5731e871016efcc66bf2e4cd9321334c981dc40060142.
The exported qualification summary omits private paths and individual arms.
Optional identity fields absent in the producer records are counted in the
summary. All 9,596 late required returns remain in the cohort.

The private run directory contains byte-identical preserved copies of
consumer.json, occurrences.jsonl, predictions.jsonl, results.json and overlap.json.
The diagnostic reconciliation verified each selected row against its original
test-file prefix, joined truth by event identity, and required exactly one
prediction per level. Group names are pseudonyms. For 896 events, there were
895 unique exact vectors and 863 rounded vectors. Exact matches to training
or validation occurred for 366 rows; rounded matches occurred for 544 rows.
Rounded counts include exact matches and omit near neighbours across bucket
boundaries. Digests bind the retained outputs, partitions, model and source
files retrospectively. They do not certify the timing of the initial run.

The allocator receipts come from two separate interpreter invocations of
hardware/recheck_allocator.py with the original and corrected private runtime
respectively. The case digest binds the ordered demands, caps, rotations and
actual allocations. The comparison uses the public corrected waterfill rule.

P1 returned its hardware identity on the configured SSH connection. P2/P3
name lookup failed and the recorded interface addresses timed out. No new
physical arms were acquired. The locally retained feature CSVs establish
file-level identities; independent parent acquisition IDs, episode boundaries
and a verified mapping to the feature rows remain unavailable. Formal
content, measured timely-correct output and physical controller validation
remain pending.

## Public verification and continuation

The [public review](PUBLIC_REVIEW.md) records which earlier pending items are
now closed and distinguishes the exported private findings from the checks
reproduced with public inputs. Continue with the updated
[Codex handoff](../CODEX_HANDOFF_CN.md); the fresh private checker run and the
retained 896-row reconciliation do not need to be repeated for a documentation
update.

From the repository root:

```bash
python3 supporting_material/experiment_extension/retained_review/verify_export.py
python3 -m unittest discover -s supporting_material/experiment_extension/retained_review -p 'test_*.py' -v
```

The verifier checks the exact seven-group cohort, nonnegative integer counts,
denominators, pooled outcomes, signature-count bounds and the necessary
exact-to-rounded inclusion relations, as well as the published source/index
identities. The 895/863 global distinct counts are exported private scan
findings: their bounds can be checked here, but the cross-group feature-vector
intersections cannot be reconstructed from these anonymized summaries alone.
The regression inputs are synthetic mutations of the public summaries and
are not additional scientific observations.
