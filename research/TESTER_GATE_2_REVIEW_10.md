# Tester Gate 2 Review 10 — Expected Expiry Coverage

Date: 2026-10-04
Role: Independent tester

## Verdict

**Gate 2: NOT PASSED / additional remediation required.**

## Finding F5 — Missing-expiry escape path

The revised coverage checker still derives its `monthly_expiries` list from expiries already present in the composite summary. Therefore, if an entire monthly expiry partition is absent from the composite, that expiry is absent from the expected set and cannot be marked incomplete.

This is a structural coverage blind spot: the checker can prove that observed cycles are complete while failing to prove that the requested historical sample contains every expected monthly cycle.

### Required remediation

Derive the expected monthly expiry set independently of the composite observations. The preferred source for this gate is the staged primary-source manifest because the staging step explicitly selects one monthly expiry file per calendar month. The checker must:

1. read the staging manifest's selected primary expiry files;
2. extract the expected expiry dates from those filenames;
3. compare the expected set with the composite set;
4. mark any missing expected expiry as INCOMPLETE and fail CI;
5. retain any composite-only expiry as an anomaly for review.

This remains required even after the exchange-session continuity check and CSV/Parquet reconciliation are implemented.

## Developer instruction

Implement F5 without copying tester-side implementation code, rerun CI, and submit the resulting coverage artifact for independent verification.

## Tester instruction

Verify that the expected-expiry set is independently sourced from staging metadata and that a deliberately missing expiry causes a deterministic Gate 2 failure.
