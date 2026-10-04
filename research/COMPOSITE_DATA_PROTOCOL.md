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