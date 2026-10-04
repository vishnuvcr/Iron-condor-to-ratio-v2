# Tester Gate 2 Review 18 — Assembly Manifest Contract

Date: 2026-10-04
Role: Independent tester

## Verdict

**Gate 2 remains CLOSED pending rerun.**

## Finding F12 — assembled coverage manifest omitted the requested window

The partitioned build successfully produced all six year artifacts and the assembly Parquet. The coverage gate then failed because `results/composite/source_staging_manifest.json` was absent in the assembly job, so the requested 2021-01 to 2026-09 window could not be reconstructed independently of source availability.

This is a gate-contract defect, not evidence that the data are complete.

## Required remediation

The assembly step must persist:
- requested `start`;
- requested `end`;
- assembled partition list.

The coverage job must consume that contract and derive the expected 69 calendar months independently of primary-source availability.

## Developer instruction

Rerun the complete partitioned workflow after the manifest fix. Submit coverage, CSV reconciliation, and provenance artifacts for final Gate 2 review.

## Tester instruction

Verify the requested month set is exactly 69 months, verify every month has a defensible monthly candidate or is explicitly reported missing, and independently reconcile the final CSV to the assembled Parquet.
