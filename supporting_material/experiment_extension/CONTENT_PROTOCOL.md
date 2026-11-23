# Offline representation diagnostic

Population: the archived binary CICIoT feature split (39 ordered values).
The unit is one source row. Treat source files as strata; related captures
may share a parent session. Keep all three original splits. Before outcomes,
select the first 128 rows in archived order from each group, identically for
all representations. This bounds model and encoding costs and defines a
file-prefix diagnostic. Report pooled confusion counts and per-file results.
The primary contrast is full minus alert correctness on all generated rows.
Do not use capture bootstrap intervals without parent-session identities.

Use the deployed light logistic model for the alert bit (threshold 0.5).
Alert sends this bit; summary appends the first four frozen features; full
appends all 39. Encode the bit as one byte and each feature as a network-order
binary64. All levels use the same training-only diagonal Gaussian naive Bayes
consumer with a Laplace-smoothed Bernoulli alert likelihood, empirical class
prior and variance floor 1e-8. It marginalizes unobserved dimensions by
omitting their likelihood terms. Use threshold 0.5 for all levels. No tuning.
Report arithmetic mean correctness across files separately. These payloads
refer to this diagnostic encoder. Radio and queue delays are outside scope.

For the overlap audit of the full archived splits, normalize signed zero,
round each feature to three significant decimal digits, and hash the ordered
binary64 vector without IDs or labels. Equal signatures identify candidate
near duplicates across splits, including exact duplicates. The relative
resolution is fixed before scanning. This exhaustive bucket lookup misses
pairs across rounding boundaries. Retain all rows regardless of overlap.
