# Composite Dataset Protocol

Date: 2026-10-04

## Purpose
A free source may be incomplete even when its rows are otherwise valid. The project will therefore attempt a composite NIFTY option dataset before rejecting a historical cycle, while preserving source provenance and avoiding synthetic price construction.

## Core rule
The composite is assembled at the contract-minute row level.
Canonical key: timestamp + expiry + strike + option_type.
A retained row must come entirely from one source for the required trading fields: open, high, low, close, volume.
We do not average or interpolate option prices across sources.

## Source priority
Priority is determined by validation evidence, not convenience.
Initial candidates:
- thetrademarkk: 2021–2026 option partitions; exact expiry/strike/type fields; OI available.
- Cloud Trader/Shoonya samples: 1-minute OHLCV+OI; exact symbol strings; free sample expiries.
- artist-23: 2020–2025; strike/option type/OI/spot present, but exact expiry is not directly exposed and requires validation.
- Zenodo: 2017–2020; one-minute OHLCV and monthly/strike files; no OI documented.

## Missing-value policy
Required trading fields: if a row is missing/invalid in any required trading field, it may be replaced by an exact-key row from a lower-priority source.
Replacement requires identical timestamp after IST normalization, identical expiry, identical strike, and identical option type.
The replacement row is retained as a whole. No individual price field is borrowed from another source.
Open interest: higher-priority OI is retained; exact-key lower-priority OI may fill a missing OI field and must record oi_source. OI is not a baseline strategy signal.

## Conflict policy
When sources overlap on a valid contract-minute row, retain the higher-priority complete OHLCV row and record the competing source in the overlap audit. Do not average prices.
Large systematic OHLC differences are a source-validation failure, not a reason to blend.

## Quality gates
- IST timestamps.
- One row per canonical key.
- Positive OHLC and non-negative volume.
- High >= max(open, close); low <= min(open, close).
- OI >= 0 when present.
- No impossible expiry before timestamp.
- Explicit cycle coverage from expiry-32 calendar days through the final pre-expiry session.
- Required strategy-selected strikes must be recoverable.

## Provenance
Every composite row records price_source, oi_source, source_file, source_revision, and source_row_hash.
The run manifest records retrieval time, source revision, file SHA256, source counts, fallback counts, overlap statistics, and skipped-expiry reasons.

## Restriction
A composite may repair missing observations. It may not manufacture continuity by forward filling, interpolation, theoretical pricing, or ambiguous contract mapping.

## Promotion rule
The composite becomes the Phase-2 production dataset only after cycle coverage, contract mapping, overlap consistency, immutable provenance, and independent tester approval all pass.
No performance result is final before that gate.

## 2026-10-04 implementation update
The production composite builder is now disk-backed using DuckDB and merges source files sequentially. This avoids holding the complete multi-year chain in a single in-memory Pandas object. The overlap audit is stored as a compact CSV summary to keep the CI artifact bounded while retaining conflict statistics.


## 2026-10-04 exchange-calendar update
Continuity validation now uses a versioned NSE Futures & Options holiday calendar stored at `research/NSE_FNO_HOLIDAYS_2021_2026.csv`, sourced from the annual NSE F&O trading-holiday circulars for 2021–2026. The prior BSE calendar proxy has been removed from the production coverage gate.


## 2026-10-04 provenance/calendar hardening
- Exchange-session continuity uses `research/NSE_FNO_HOLIDAYS_2021_2026.csv` for normal NSE F&O weekdays; weekend-only holiday entries are unnecessary because Saturdays/Sundays are excluded by the session generator, while special Muhurat dates are not treated as normal 09:20 sessions.
- Composite `source_row_hash` uses SHA-256 for both primary and normalized sources.
- Cycle entry/exit boundary validation uses the same NSE F&O normal-session calendar rather than a fixed calendar-day tolerance.


## 2026-10-04 monthly-expiry integrity
A requested calendar month is production-eligible only when its candidate expiry is a defensible monthly expiry near month-end. Primary staging filenames are checked rather than blindly treated as monthly; a non-monthly primary file may be superseded only by an explicit valid fallback monthly expiry. Weekly expiries cannot satisfy the monthly cycle gate.


## 2026-10-04 resource and resolver hardening
- Composite construction uses a file-backed DuckDB working database and sequential primary-partition ingestion to bound peak memory.
- Staged primary filenames used for symbol-only expiry resolution must themselves satisfy the month-end monthly-expiry candidate rule; weekly-dated files are ignored for that calendar mapping.


## 2026-10-04 partitioned build protocol
For CI stability, primary and lower-priority source construction is executed in bounded year partitions: 2021, 2022, 2023, 2024, 2025, and 2026 through September. Each partition emits a validated Parquet artifact and manifest. A deterministic assembly job creates the canonical composite; only then may coverage, CSV reconciliation, or backtesting run.


## 2026-10-04 partition boundary rule
Year partitions overlap the preceding year from 20 November so the first monthly expiry in a nominal year retains its full deterministic 32-DTE lead-in. The final assembly removes overlap duplicates by canonical key using the established source-priority order.
