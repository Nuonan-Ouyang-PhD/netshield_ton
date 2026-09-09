# CLAIM_AUDIT_V1_3

Verdict: **PASS**

## Required semantic checks

- PASS: Tasks A, B, and D are identified as offline replay/software sensitivity/discrete-event conformance, not hardware measurement.
- PASS: Task C alone is reconstructed from accepted formal hardware timestamps.
- PASS: No universal centralized-over-decentralized superiority claim is made.
- PASS: No safety-filter superiority over C-QPG is claimed.
- PASS: The n=32 result is identified as simulation conformance, not physical scale validation.
- PASS: The 1-s metric is identified as a post-release service SLO, not a complete end-to-end deadline.
- PASS: The formal classifier ceiling is disclosed as a controlled diagnostic, not IDS superiority.
- PASS: The superseded timely-F1 causal story is absent.
- PASS: Desynchronization is disclosed as changing the RQ2 interpretation.
- PASS: The n=3 physical granularity limitation is disclosed.

## Forbidden-claim scan

- PASS: `timely_f1` count=0; expectation=absent.
- PASS: `0.9332` count=0; expectation=absent.
- PASS: `0.2845` count=0; expectation=absent.
- PASS: `0.9336` count=0; expectation=absent.
- PASS: `0.2823` count=0; expectation=absent.
- PASS: `non-inferiority` count=1; expectation=allowed only as superseded/not carried forward.
- PASS: `universally outperforms` count=1; expectation=allowed only in explicit denial.
- PASS: `zero intervention` count=0; expectation=absent.
- PASS: `1/2/3 Mbps` count=0; expectation=absent.

The audit distinguishes negative/disclaiming occurrences from affirmative claims.
