# RC1 local structural and aggregate-consistency audit

**Verdict:** `PASS_WITH_OPEN_REVIEW_ITEMS`

The local audit reconstructed the accepted set from `ATTEMPT_INDEX.json` and
confirmed 12 complete sessions, 18 accepted arms per session, and 216 unique run
IDs. It read the original accepted-arm validator at each indexed location: all
216 report `overall = PASS`, and none records a failed check. Restore copies were
not counted.

The audit also confirmed that the aggregate arm set equals the accepted index,
recomputed all 144 descriptive rows from the 216 aggregate arm records, and
recomputed the paired values and mean differences in all 48 contrast rows. It
verified all 12 session package hashes against their receipts and confirmed that
each receipt records ZIP CRC and restored-hash `PASS`.

The final 1,340,825,224-byte archive and its independent backup both hash to:

```text
846643a85ace5d840d9c0d7a41245c760989d1886ce0d8c62ca4873368564acf
```

The external completion record reports independent ZIP restoration, CRC
`PASS`, and restored hashes `PASS`.

This audit is intentionally limited. The following gates remain open:

1. An independent reviewer has not issued a campaign verdict.
2. The raw event ledgers have not been independently reconstructed into metrics
   as part of this GitHub update.
3. The manuscript has not been rewritten or numerically audited against RC1.
4. Public artifact licensing and disclosure review remain incomplete.

Therefore the collection is complete, while paper use and submission remain
`HOLD`.
