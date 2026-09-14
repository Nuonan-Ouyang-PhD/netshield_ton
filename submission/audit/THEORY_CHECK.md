# NetShield Theory/Data Cross-Check

Status: **PASS**

## Full-evidence byte frontier

For `n=3`, `B=131072 B`, `S=16384 B`:

- Low: unrestricted `K=1`, universal-coverage `K=0`, price = 1 full slot.
- Mid: unrestricted `K=2`, universal-coverage `K=1`, price = 1 full slot.
- High: unrestricted `K=3`, universal-coverage `K=3`, price = 0.

The unrestricted quantity is a byte frontier. Physical deadline attainment is measured separately.

## CRFA hardware attainment of the frontier

- Low: timely-full/generated = 0.305556; frontier = 1/3; attainment = 0.916667.
- Mid: timely-full/generated = 0.632716; frontier = 2/3; attainment = 0.949074.
- High: timely-full/generated = 0.966049; frontier = 1; attainment = 0.966049.
- Selected-full eventual result-return fraction = 1.0 at all three capacities.
- Shared-cap violations = 0 across 10,620 reconstructed extension service rounds.

At mid capacity, session-matched primary C-QPG gives 0.293827 timely full-core results per generated occurrence; CRFA gives 0.632716. The paired mean difference is +0.338889 with descriptive 95% session-bootstrap [0.330556, 0.347840]. At high capacity the paired difference is -0.003704 with interval [-0.013272, 0.004630].

Interpretation: the low/mid gap between summary-preserving C-QPG and CRFA is a measured coverage/richness trade-off. This is not a universal CRFA-dominance claim because CRFA assigns H-NONE to non-selected probes.

## Desynchronization common denominator

Software sensitivity at mid capacity:

- C-QPG: timely-full/generated = 0.333333; payload = 14.745600 MB.
- Phase-randomized I-QPG: timely-full/generated = 0.335185; payload = 23.592960 MB; conditional timely = 0.502778.
- C-QPG application-byte reduction at near-equal software timely-full output: 37.5%.

The phase-randomized 2/3 request fraction and CRFA 2/3 admitted fraction are analytically related operating fractions but not a direct hardware-versus-hardware method comparison.

## Desynchronization independent-slot benchmark

- Bernoulli `p=2/3` approximation: conditional timely = 5/9 = 0.555556; common timely-full/generated = 10/27 = 0.370370.
- Simulated phase-randomized mean: conditional = 0.502778; common = 0.335185.
- The Bernoulli calculation is an independence approximation, not a proved upper bound.

## Admission fairness versus timing fairness

Across 12 CRFA sessions each probe receives exactly:

- 360 low-capacity full opportunities; max inter-selection interval 3 rounds.
- 720 mid-capacity full opportunities; max interval 2 rounds.
- 1,080 high-capacity full opportunities; max interval 1 round.

Mid selected-full post-release timely fractions are P1 0.915278, P2 0.931944, P3 1.000000. Equal admission opportunity therefore does not imply equal physical timing.

## Timing anchors

Primary aggregate release-lateness p50:

- P1 1972.34 ms;
- P2 763.90 ms;
- P3 83.56 ms.

CRFA aggregate nominal timely-full/generated is 0.111111/0.222222/0.333025 at low/mid/high, versus post-release 0.305556/0.632716/0.966049. P1 and P2 have zero selected-full nominal on-time fraction in CRFA; P3 is 1.0/1.0/0.999074.

These values support the manuscript's separation of the post-release 1-s service SLO from the schedule-inclusive nominal-anchor sensitivity. The exact recurring low-level OS/network proposal-order cause remains UNKNOWN.

## Selective integration: analytical planning additions

The baseline empirical and CRFA checks above are unchanged. The corrected mid residual
is 131072/3 B = 128/3 KiB, approximately 43691 B or 42.7 KiB. Supplementary IV
adds independent-request quantile planning, the equal-value heterogeneous count rule,
and continuous-versus-integer qualifications. The written derivations include their
feasibility domains and counterexamples to stronger claims. Arithmetic and exact
small-case checks pass in 13 groups (6555 cases); these are not hardware findings or
a replacement for a general proof. See ANALYTICAL_PROVENANCE.md.
