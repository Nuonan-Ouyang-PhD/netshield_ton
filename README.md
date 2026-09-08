# NetShield

Private research repository for the NetShield IEEE Transactions on Networking
manuscript and its formal three-device Raspberry Pi campaign.

> **Current state (8 September 2026):** protocol
> `NSF12_20260906_RC1` completed 12 sessions and 216 accepted arms. All 216
> accepted-arm validators report `PASS`; three interrupted attempts remain
> preserved and excluded. The campaign is **pending independent review** and the
> submission state is **HOLD**.

The earlier V4.4 submission candidate is preserved under
[`legacy/v4_4/`](legacy/v4_4/). Its pre-RC1 empirical numbers are historical and
must not be presented as results from the RC1 campaign.

## Repository map

| Path | Purpose |
|---|---|
| [`formal_rc1/`](formal_rc1/) | Path-free RC1 status, accepted-attempt index, 216-arm matrix, validator summary, aggregate descriptive tables, configuration snapshot, and integrity manifest |
| [`ToN_V1_3_Methodology_Repair_20260909/`](ToN_V1_3_Methodology_Repair_20260909/) | Isolated path-free sensitivity, desynchronisation, nominal-deadline reconstruction, and scaling-validation review package |
| [`legacy/v4_4/`](legacy/v4_4/) | Payload-preserved V4.4 manuscript package and its original supporting material |
| [`scripts/verify_repository.py`](scripts/verify_repository.py) | Standard-library verification of hashes, expected counts, package receipts, and private host/path exclusion |
| [`scripts/verify_methodology_repair.py`](scripts/verify_methodology_repair.py) | Standard-library verification of V1.3 row counts, hashes, scope guards, and path-free publication boundary |
| [`CHANGELOG.md`](CHANGELOG.md) | Repository-level history and status transitions |
| [`RIGHTS_AND_ACCESS.md`](RIGHTS_AND_ACCESS.md) | Access, redistribution, and licensing boundary |

## Verified campaign boundary

- Design: 12 sessions × 6 methods × 3 capacities = **216 accepted arms**.
- Accepted set: 12 complete session blocks, each containing 18 arms.
- Invalid attempts retained: `F12_S03/a01`, `F12_S04/a01`, and
  `F12_S07/a01`; none contributes to the accepted set.
- Validator result: **216/216 `PASS`**, with zero recorded failed checks.
- Session packages: **12/12** pass receipt SHA-256, ZIP CRC, and restored-hash
  checks.
- Final raw archive: `NetShield_Formal_Campaign_V1_2_20260908.zip`,
  1,340,825,224 bytes, SHA-256
  `846643a85ace5d840d9c0d7a41245c760989d1886ce0d8c62ca4873368564acf`.
- The primary archive and independent backup are byte-identical. The archive is
  deliberately not stored in Git because it contains private raw evidence and
  is 1.34 GB.

These checks establish collection structure and artifact integrity. They do not
constitute an independent scientific verdict or authorize manuscript claims.

The frozen matrix deliberately retains its pre-activation
`PLANNED_NOT_AUTHORIZED` provenance field. The later author approval, frozen
tool identities, fixture evidence hashes, and backup gate are recorded in
[`formal_rc1/results/activation_record.json`](formal_rc1/results/activation_record.json).

## Verify this checkout

```bash
python3 scripts/verify_repository.py
python3 scripts/verify_methodology_repair.py
```

To verify the archived V4.4 bundle separately:

```bash
cd legacy/v4_4
shasum -a 256 -c docs/MANIFEST_SHA256.txt
```

The GitHub Actions workflow runs the same repository checks on every push and
pull request.

## Evidence and disclosure policy

Only aggregate, role-labelled, path-free audit material is committed here. Raw
event ledgers, packet-level material, model artifacts, machine addresses, SSH
targets, user paths, and the full campaign archive remain outside Git. Public
release and licensing require a separate author decision and dataset/model
license review. Repository visibility must remain private during review.

The V1.3 methodology-repair directory is supplementary analysis, not a new
Raspberry Pi campaign and not a manuscript revision. Tasks A, B, and D are
offline replay/simulation; Task C alone reconstructs metrics from retained
formal timestamps.

## Open review gates

1. Record an independent review verdict for the RC1 protocol, accepted-set
   reconstruction, raw-log metric reconstruction, and retry/exclusion logic.
2. Rewrite and numerically audit the manuscript against RC1 if the verdict
   permits publication use.
3. Complete artifact licensing and disclosure review before any public release.
4. Keep submission status at `HOLD` until those decisions are recorded.
