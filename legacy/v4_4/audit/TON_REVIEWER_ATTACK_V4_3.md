# Simulated ToN Editor + Reviewer Attack — V4.3

Date: 5 Sep 2026

## Executive decision

**Current status: submit-capable after one small reproducibility field is filled.** No result rerun is required for the present claim set. The largest remaining scientific limitation is the absence of a paper-eligible shield-intervention episode; the manuscript now treats shielding as non-interference under the evaluated feasible envelope rather than as demonstrated intervention superiority.

## Editor / desk-screen attack

### Risk: networking novelty could be mistaken for IDS-classifier benchmarking — MEDIUM, mitigated
The revised paper now states that detector design is not the contribution. The novelty claim is endogenous evidence generation over a common service, queue state, deterministic pre-admission, and mechanism-isolating real-hardware evaluation.

### Risk: prior ACISP 2026 SoK overlap — LOW, mitigated
The SoK is cited and explicitly distinguished in Related Work and the cover letter. NetShield has no prior conference/journal/preprint version.

## Reviewer 1 — stochastic network control / theory

### Attack 1: “This is not a full Lyapunov DPP implementation.” — HIGH before V4.3; mitigated
The earlier V4.2 wording could be read as claiming a formal DPP optimizer. V4.3 now retains the frozen method labels only for provenance and describes the deployed selector as the implemented finite-action queue-penalized DPP-style score. No O(1/V), queue-stability, or stochastic-optimality theorem is claimed.

### Attack 2: “Equation for central-DPP claims a global joint argmax that the implementation does not solve.” — HIGH before V4.3; resolved
The global argmax formulation has been removed. Central coordination is now described as deterministic monotone pre-admission/degradation until aggregate payload fits the shared cap. Proposition 1 is limited to nonempty finite termination.

### Attack 3: “Where is the exact selector coefficient?” — MEDIUM / OPEN
The paper gives the implemented score form but the final numeric frozen `dpp_v` coefficient is not present in the delivered public result package. Before submission, insert the exact value from the formal low/mid/high configuration and preferably include the frozen config files in the reproducibility artifact.

## Reviewer 2 — systems / experimentation

### Attack 1: “Only three probes.” — MEDIUM, disclosed
The paper explicitly limits the claim to a small heterogeneous edge domain and does not extrapolate throughput/scalability to tens of probes.

### Attack 2: “Capacity is controlled rather than naturally varying Wi-Fi.” — MEDIUM, disclosed
The paper says the low/mid/high values are application-service budgets imposed on real Wi-Fi, not PHY-rate claims. This is defensible for mechanism isolation.

### Attack 3: “Feature-vector replay is not live packet capture.” — MEDIUM, disclosed
The paper explicitly calls the workload CICIoT2023-derived feature-vector replay and avoids open-world IDS claims.

### Attack 4: “The shield never intervenes.” — HIGH but bounded
E and F choose identical actions in all 9,720 measured windows. The manuscript does not claim intervention efficacy. This is the strongest likely major-revision request. A prospective paper-eligible stress campaign would strengthen the paper, but it is not logically required for the current narrow non-interference claim.

## Reviewer 3 — statistics / measurement

### Attack 1: pseudo-replication — RESOLVED
The analysis uses sessions (n=12) as the inferential unit; capacities/devices are pooled within session. The 36 session-capacity cells are descriptive only.

### Attack 2: multiple testing — RESOLVED
Exact sign-flip tests and within-family Holm correction are reported.

### Attack 3: “14.1% fewer bytes” lacks a prespecified paired hypothesis test — MEDIUM before V4.3; mitigated
V4.3 explicitly labels this as descriptive aggregate mechanism accounting. It is no longer presented as an inferentially established population effect.

### Attack 4: non-inferiority p=1 confusion — RESOLVED
The paper correctly states that non-inferiority follows from the prespecified -0.02 margin and observed CI/difference, not from rejecting equality.

## Reviewer 4 — security / IDS

### Attack: perfect F1 for five methods looks unrealistic — MEDIUM, mitigated
The revised text states that the detector pool is frozen and the ceiling result is a property of the controlled replay. The paper does not claim classifier state of the art. Fixed-full degradation is interpreted as evidence freshness/timing behavior rather than intrinsic heavy-detector inaccuracy.

## Recommended submission position

Do not enlarge the claim set. Submit the paper as a networking systems/control paper about evidence generation, queue freshness, and shared pre-admission. Keep the shield claim strictly at non-interference unless a new formal stress campaign is run.

## One item needed from the corresponding author

Provide the exact frozen `dpp_v` value (or the three formal low/mid/high configuration JSON files) used in S01-S12 so the selector equation can be fully numerically reproducible.
