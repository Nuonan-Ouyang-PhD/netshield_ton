# Formal metric schema — NSF12_20260906_RC1

Authoritative cohort: 270 measured-origin occurrences per arm, aggregated over
P1/P2/P3 before taking rates. The 15 warmup occurrences remain in raw evidence
and lifecycle/byte checks but not the primary measured denominator.

- `common_core_return_coverage`: core-required results received / generated.
- `common_on_time_correct_core_coverage`: correct core result received on the
  originating probe within its deadline / generated. Unmatured missing results
  yield null plus explicit lower/upper bounds, not definitive misses.
- `core`: required, received, correct, on_time, on_time_correct, censored counts;
  conditional rates retain pending/failed/cancelled in the required denominator.
- `local`: the corresponding local-ready endpoint, separately from evidence
  receipt and from the core-required endpoint. No local fallback in core counts.
- `evidence`: required/generated fraction and transfer-complete/required rate,
  with action/evidence-kind mix. Summary receipt is not local-ready time.
- `classification`: only the final admitted execution's valid prediction;
  TP/TN/FP/FN and N_total/N_scored/N_unscored. F1=2TP/(2TP+FP+FN); a zero
  denominator is null; nonzero FP/FN with TP=0 gives 0.
- `states`: mutually exclusive pending / terminal_failed / terminal_cancelled /
  terminal_success_timely / terminal_success_late; sum equals generated.
- `latency_by_action`: p50/p95 (linear interpolation), completed/required
  coverage and late/pending counts. Core inference duration uses the core clock;
  result end-to-end, local-ready and receipt use only each originating probe's
  clock. Cross-host monotonic subtraction is prohibited.
- Event bytes: generated payload, sent payload, unique received, duplicate wire,
  framing, remaining queued and in-flight. Payload = unique received + queued +
  in-flight + cancelled/discarded. Application wire is not total TCP/IP/Wi-Fi
  traffic; link-layer total remains `not_measured`.
- Window diagnostics separate warmup/measured/drain **service periods** from
  event-origin cohorts. Queue maxima are sampled, not continuous peaks. Queue
  pressure, age and lateness are reported, not used to erase poor performance.
- `legacy_f1_alias` is empty. The old timely F1 field is prohibited.
- Non-inferiority: status `not_evaluated`, margin and decision null.

Across sessions: per-capacity F−E and F−D paired session-block differences,
10,000 bootstrap draws using NumPy default_rng(12020609), linear 2.5/97.5%
quantiles. All 12 session slots are displayed. Any null pair withholds the full
paired interval and explicitly reports valid-pair count; no silent complete-case
exclusion or confirmatory claim. This is descriptive, not a power calculation.

The frozen configuration retains its legacy default seed field; actual CLI
session seed is validated separately in manifests/core rows and is passed to
frozen window-plan selection. Configuration bytes are not rewritten.

All offline fixture results, including those using actual models/plans and
hardware-mode config with memory transport, remain offline fixtures.
