# Tester Gate 2 Review 8 — CSV Export and Timestamp Integrity

Date: 2026-10-04
Role: Independent tester

## Verdict

**Gate 2: PENDING.**

### Checks

1. Naive Date+Time source timestamps are now localized directly to Asia/Kolkata rather than interpreted as UTC. This prevents a 5:30-hour timestamp displacement.
2. A deterministic DuckDB CSV exporter now writes `results/composite/consolidated_options_data.csv` from the validated composite Parquet.
3. The CSV export is generated from the canonical composite, preserving timestamp, expiry, expiry provenance, strike, option type, OHLCV, OI, source and row-hash provenance.
4. The CSV is intended as a Google Drive-friendly transfer artifact; Parquet remains the research-native source because it is substantially more efficient for multi-year 1-minute options data.

### Remaining gate conditions

- Fresh CI must pass staging, composite build, coverage, timestamp/hash tests, and the backtest.
- The tester must inspect the generated CSV row count, schema, SHA256, and consistency against the Parquet row count.
- The tester must independently verify that every promoted expiry has explicit or independently resolved expiry provenance and complete 32-DTE-to-pre-expiry coverage.

No strategy performance metric is promoted to final status until these conditions pass.

## Developer instruction

Developer: complete the fresh CI run, publish the CSV artifact, and submit its manifest/hash and Parquet-vs-CSV reconciliation for independent review.

## Tester instruction

Tester: independently compare the CSV and Parquet counts/schema, inspect source provenance, and reject any discrepancy before Gate 2 approval.
