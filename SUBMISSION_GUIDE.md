# NetShield submission guide

Use the 14-page manuscript and 36-page supplement listed below. Both include
the completed hardware studies and the separate CICIoMT2024 content
experiment. File checksums are recorded in the package manifests.

## Files for submission

| Purpose | File in this package |
|---|---|
| Main paper | `submission/netshield_manuscript.pdf` |
| Supplementary material | `submission/netshield_supplementary.pdf` |
| Cover letter | `submission/cover_letter.md`; copy the text into the submission system if required |
| LaTeX sources | `submission/netshield_manuscript.tex`, `submission/netshield_supplementary.tex`, and the adjacent `figures/` and `tables/` directories |
| Overleaf package | `review_package/NetShield_ToN_Overleaf.zip`, also supplied as a separate download |
| Public results and verification | `supporting_material/experiment_extension/physical_extension/` and `supporting_material/experiment_extension/content_measurement/` |
| Build and verification notes | `submission/BUILD_INSTRUCTIONS.md` and `submission/audit/CONTENT_CLOSEOUT.md` |

The current PDFs are in `submission/`. Earlier versions in
`supporting_material/archive/` and the frozen snapshots are retained for
provenance.

## Experimental scope

- Allocator: a two-arm pilot and four formal pairs, giving eight formal
  physical arms.
- Shared-stage: a separate 16-condition physical calibration, a six-arm pilot
  and 36 formal physical arms.
- The two hardware studies contain 44 formal arms. Including qualification,
  calibration, pilots and the aborted attempt, 75 attempts were registered
  and 74 arms were reconstructed.
- The calibrated policy rejected every Full request under the tested
  conditions. This completed negative result remains in the paper.
- The content study uses ten CICIoMT2024 captures with verified provenance.
  Of the same 72 test windows, Alert, Summary and Full returned 63, 62 and 0
  correct results within one second, respectively. See the
  [data, execution and verification notes](supporting_material/experiment_extension/content_measurement/README.md).
- Correctness uses the capture-scenario labels. The training, validation and
  test sets contain 96, 72 and 72 windows; the duplicate audit covers all
  105,789 source rows. The three representations encode 1, 33 and 313 B of
  information and use fixed padded payloads of 256, 16,384 and 131,072 B.
  The supplement also reports recall and false-positive rates.

The original 216-arm primary campaign, 36-arm CRFA campaign and later
replacement-device cohort are reported separately. The complete package
contains public evidence, acquisition and analysis code, and verification
records. See `RIGHTS_AND_ACCESS.md` and `REPRODUCIBILITY.md` for access to
private raw records and third-party data.

## Build and verify

After importing the Overleaf package, select pdfLaTeX and set
`netshield_manuscript.tex` as the main document. Switch to
`netshield_supplementary.tex` to build the supplement. To build from the full
repository locally, run `bash scripts/build_submission.sh`.

The complete ZIP includes `SHA256SUMS_REVIEW.txt`; the Overleaf ZIP includes
`SHA256SUMS_OVERLEAF.txt`. If you edit or rebuild the files, generate new
checksums and retain the corresponding build record.

PR #3 was merged into `main` at `0ff77a1`. Journal submission is handled by
the authors; merging the repository does not submit the paper.
