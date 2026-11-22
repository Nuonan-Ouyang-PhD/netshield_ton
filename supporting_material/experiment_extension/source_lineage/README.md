# From traced CSV rows to a declared parent-capture split

## Completed source-row trace

The retained `SOURCE_ROW_TRACE.json` at `72cc05d` reports 31 source files:

| Archived split | Sources | Matched rows |
|---|---:|---:|
| Train | 18 | 2,998,132 |
| Validation | 6 | 996,486 |
| Test | 7 | 1,147,055 |
| Total | 31 | 5,141,673 |

The original and labelled CSV digest sets each contain 31 different values.
These denominators agree with the earlier exact and rounded overlap reports.
The trace reads unlabelled CSV rows and compares all 39 ordered binary64 feature
values with the frozen records selected by source group and physical CSV line
number (header is line 1). The labelled-file digest is copied from the frozen
manifest; its earlier file check is a separate retained provenance step.

This review leaves `trace_feature_rows.py` and `SOURCE_ROW_TRACE.json` unchanged.
It does not reopen the private five-million-row corpus. Repeating that trace is
unnecessary solely to update status or run this public arithmetic check:

```bash
python3 supporting_material/experiment_extension/source_lineage/prepare_capture_split.py verify-public
```

## The missing input is acquisition identity

The official [UNB description](https://www.unb.ca/cic/datasets/iotdataset-2023.html)
documents merging and splitting PCAP files during preparation. The
[original dataset paper, Sections 3.3 and 4](https://www.mdpi.com/1424-8220/23/13/5941)
describes merging the two monitoring streams for an experiment. A numbered
PCAP segment or a different CSV hash therefore does not by itself identify an
independent acquisition. These general descriptions do not map the 31 retained
source digests to specific parent recordings.

Read the retained acquisition logs, provider manifests, merge/split command
records and source-PCAP metadata. Establish which source segments came from
the same acquisition, including related probes or simultaneous monitor streams.
Bind that conclusion to the source CSV digests and retained evidence files.
Timestamps alone can establish ordering or overlap, but do not automatically
establish independent runs. Keep all files from a declared parent capture in
the same split. Within-capture episode labels do not create extra independent
groups in this conservative preparation route.

If the real parent inventory is too small, or cannot provide the required
binary-class support across a defensible train/validation/test design, retain
that result. Do not invent new capture IDs, split numbered segments across
partitions, or delete test matches until the design appears to pass. The formal
study then needs additional independently acquired data or a separately
justified design; the existing diagnostic remains usable within its scope.

## Prepare once actual mapping evidence is available

The tool below checks supplied mapping completeness, acquisition-evidence
file hashes and parent-level split assignments. It produces the `groups.csv`
schema already used by `evidence_value/score_evidence_value.py` and a source-to-
group join table. It does not infer capture parents, inspect the meaning of an
evidence document, prove independence, audit feature overlap, train models or
write predictions. Its status is `DECLARED_PARENT_SPLIT_CONSISTENT`, not a
formal-study qualification.

### Input 1: `capture_mapping.json`

Use exactly these keys. This is a schema illustration; placeholders must be
replaced by real identities. `sources` must cover every original CSV digest
in the supplied source trace exactly once. `evidence` files must already exist;
relative paths are resolved against this JSON. Multiple source files may
reference the same evidence artifact and parent.

```json
{
  "schema_version": "netshield.source_capture_mapping.v1",
  "data_origin": "actual_provenance",
  "group_definition": "REPLACE_WITH_THE_DOCUMENTED_PARENT_ACQUISITION_DEFINITION",
  "evidence": [
    {"id": "REPLACE_EVIDENCE_ID", "path": "acquisition_manifest.json", "sha256": "REPLACE_WITH_ACTUAL_SHA256"}
  ],
  "sources": [
    {
      "original_csv_sha256": "REPLACE_WITH_TRACED_SOURCE_SHA256",
      "parent_capture_id": "REPLACE_WITH_DOCUMENTED_PARENT_ID",
      "evidence_ids": ["REPLACE_EVIDENCE_ID"]
    }
  ]
}
```

### Input 2: `capture_splits.csv`

```csv
parent_capture_id,split
```

Provide one row per real parent capture, exactly one assignment to `train`,
`validation` or `test`, and all three partitions. Freeze the assignment and
selection rule before examining new model outcomes. Do not add artificial
parents to satisfy the three-partition condition.

### Command and outputs

```bash
python3 supporting_material/experiment_extension/source_lineage/prepare_capture_split.py prepare \
  --mapping /actual/private/capture_mapping.json \
  --splits /actual/private/capture_splits.csv \
  --output /new/private/capture_split
```

The new output directory contains:

- `groups.csv`: `group_id,split`, where each group ID is the supplied parent ID.
- `source_groups.csv`: `original_csv_sha256,parent_capture_id,split` for joining
  actual traced rows to their parent group.
- `CAPTURE_MAPPING_REPORT.json`: input/output and evidence digests, declared
  parent counts, reassigned traced-row totals and explicit scope limitations.

The default trace is the retained 31-source export. `--trace` may identify a
separately retained actual source trace for newly acquired inputs; it cannot be
used to relabel synthetic input as an experiment. Temporary tests require
`data_origin=SYNTHETIC_FIXTURE` and explicit `--allow-synthetic-fixture`.

## Continue into the existing content experiment

Once the evidence meaning and intended independent groups have been reviewed:

1. Join the frozen dataset manifest's `inputs[].sha256` to the trace's
   `labelled_csv_sha256`; this supplies each original `group_id` with its
   `original_csv_sha256`. Join that digest to `source_groups.csv`, preserving
   each frozen row's source identity and `row_number`. Create the existing
   scorer's complete `corpus.csv`,
   retaining ground truth separately from label-free canonical feature hashes.
   Create `occurrences.csv` from the planned generated held-out workload, before
   running predictions. Hash and freeze those inventories.
2. Run the predeclared exact and near-duplicate qualification on the new split.
   Rounding buckets are a declared sensitivity analysis and may miss neighbours
   across boundaries. Keep related/duplicate groups together or record a
   defensible prespecified exclusion rule. A mapping check does not complete
   this step, and the existing scorer rejects cross-split exact feature hashes.
3. Check actual class support and the number of independent test groups for
   the frozen estimand. Multiple source files or repeated events from one
   parent still provide one resampling unit. The existing scorer cannot infer
   independence from the IDs it receives.
4. Refit every learned component affected by the new split using its training
   data only, and select thresholds using its validation data only. This
   includes the light encoder model, consumer and any standardization. An
   archived model trained on sources reassigned to test is not a new held-out
   model. Preserve historical models; freeze new artifacts separately.
5. Execute all three real encoders and the frozen consumer on exactly the same
   held-out occurrence inventory. Export all returned/missing/rejected rows,
   payloads and identities according to the existing
   [evidence-value contract](../evidence_value/README.md), then use that scorer.
   Measured timely-correct output is a separate phase with real originating-
   probe timestamps; the information-only result supplies no Wi-Fi delay.

If parent provenance remains unavailable after examining the actual records,
the content branch stops at this explicit dependency. Preserve its current
diagnostic and continue other authorized branches without another review loop.

## Software verification

```bash
python3 -m unittest discover -s supporting_material/experiment_extension/source_lineage -p 'test_*.py' -v
```

Fixtures check shared-parent grouping, missing/duplicate/extra mappings,
conflicting or incomplete split assignments, absent/altered evidence, invalid
source counts and fresh-output/synthetic-data boundaries. They create no real
acquisition records or scientific observations.
