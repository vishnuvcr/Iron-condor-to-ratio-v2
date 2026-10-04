# Tester Gate 2 Review 17 — Composite Runtime Architecture

Date: 2026-10-04
Role: Independent tester

## Verdict

**Gate 2 remains CLOSED pending partitioned-build CI.**

## Finding F11 — monolithic composite build exceeded practical CI runtime

Run 37226884355 passed 35 unit tests and source staging, then remained in the composite build for more than eight minutes without producing a completed artifact. The earlier equivalent run was terminated at approximately 4m19s. Raising the job timeout did not make the monolithic build acceptable within the project's bounded execution requirement.

## Required remediation

The composite build should be partitioned into bounded year jobs, followed by a deterministic assembly job:
- 2021–2025 full-year partitions;
- 2026 through 2026-09-30;
- each partition must produce a canonical Parquet plus manifest;
- assembly must combine only the validated partition artifacts;
- Gate 2 coverage and CSV/Parquet reconciliation must run after assembly;
- no backtest may run if any partition or assembly step fails.

The partitioned design must preserve source priority, expiry provenance, row hashes, and the same validation rules.

## Developer instruction

Implement and run the partitioned workflow, then submit the complete partition manifests, assembled manifest, coverage report, CSV reconciliation, and CI test result.

## Tester instruction

Independently verify every partition, row/schema consistency, no cross-partition overlap, complete requested-month coverage, CSV/Parquet equality, provenance, and hashes before approving Gate 2.
