# Tester Gate 2 Review 9 — Coverage Gate and Reconciliation Preconditions

Date: 2026-10-04
Role: Independent tester

## Verdict

**Gate 2: NOT PASSED / pending remediation.**

## Independent findings

### F1 — CI coverage step is not an enforcing gate
The current `scripts/check_composite_coverage.py` writes cycle statuses but exits successfully even when cycles are incomplete. The workflow therefore proceeds to CSV export and later stages without failing on an incomplete historical sample.

**Required remediation:** fail the process when any production-eligible expiry is incomplete, has missing entry coverage, or lacks final pre-expiry coverage. The workflow must treat this as a blocking Gate 2 condition.

### F2 — Coverage validation uses only first/last observed dates
The current checker compares minimum and maximum timestamps/dates against the entry/exit dates. This does not detect missing interior trading sessions.

**Required remediation:** add an independently derived continuity check over expected market sessions, or a documented defensible equivalent. Any unresolved interior gap must mark the cycle incomplete.

### F3 — CSV reconciliation is still outstanding
The CSV export step exists, but Gate 2 requires a post-export independent reconciliation against the canonical Parquet dataset.

**Required remediation:** record Parquet row count, CSV row count, ordered schema, deterministic digest/hash information, and sampled row/hash equality. A mismatch blocks Gate 2.

### F4 — Provenance must be checked after materialization
The composite manifest records source contribution, but Gate 2 still requires independent verification that every promoted cycle has admissible expiry provenance and that fallback rows retain their source identity.

**Required remediation:** tester must inspect the generated composite manifest, cycle coverage report, and CSV/Parquet reconciliation before approval.

## Developer instruction

Do not declare Gate 2 passed. Remediate F1-F4, rerun fresh CI, and submit the generated artifacts for an independent review.

## Tester instruction

After remediation, independently inspect the new CI artifacts and reject the gate if any coverage, provenance, schema, row-count, hash, or reconciliation discrepancy remains.
