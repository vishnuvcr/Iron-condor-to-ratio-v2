# Tester Gate 2 Review 16 — Composite Build Resource Stability

Date: 2026-10-04
Role: Independent tester

## Verdict

**Gate 2: NOT PASSED / composite-build resource failure.**

## Finding F10 — bulk primary scan is not resource-stable

CI run 37226055771 passed all unit tests and source staging, then was terminated by the GitHub-hosted runner during the composite build with exit 143.

The developer composite implementation currently bulk-scans all staged thetrademarkk monthly Parquet files into one DuckDB CREATE TABLE statement. For the multi-year option-chain sample this creates unnecessary peak memory pressure and is inconsistent with the repository's stated disk-backed/sequential composite protocol.

## Required remediation

Process the primary monthly partitions incrementally:
- read/filter one partition at a time;
- append to the disk-backed composite table;
- avoid materializing all primary partitions simultaneously;
- preserve exact-key deduplication within each partition and all row-level provenance;
- retain the same validation/OHLC/source-priority rules.

Do not weaken the Gate 2 coverage or provenance rules to make the build pass.

## Developer instruction

Implement bounded-memory/sequential ingestion, rerun CI, and submit the build logs and composite manifest for independent review.

## Tester instruction

Verify that the new build path does not bulk-materialize all primary partitions and that the resulting Parquet remains reproducible and row/provenance equivalent.
