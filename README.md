# Iron Condor -> Ratio Spread v2

Research status: **Gate 2 / Phase 2 data engineering in progress; final historical sample not yet accepted.**

This repository is the reproducible research record for backtesting the YouTube strategy supplied by the user:
https://youtu.be/T4gvTshMEyA

## Navigation
- research/RESEARCH_PLAN.md
- research/STRATEGY_SPEC.md
- research/PHASE_STATUS.md
- research/DATA_SOURCES.md
- research/HISTORICAL_DATA_EXPANSION.md
- research/FREE_DATA_SOURCE_REVIEW.md
- research/COMPOSITE_DATA_PROTOCOL.md
- research/COST_MODEL.md
- research/ERROR_LOG.md
- research/CHAT_LOG.md
- research/ROLES_AND_GATES.md
- research/TESTER_GATE_2_REVIEW_8.md
- research/TESTER_GATE_2_REVIEW_9.md
- research/TESTER_GATE_2_REVIEW_10.md
- research/TESTER_GATE_2_REVIEW_11.md

## Roles and branches
- developer: implementation branch; may write research code and workflow changes.
- tester: independent review branch; must not copy developer implementation code into tester code. Tester reviews developer commits read-only and records findings independently.
- phase-2-data-developer: isolated Phase 2 implementation branch.
- phase-2-data-tester: isolated Phase 2 independent-test branch.

## Research principle
The published video is the primary specification. Ambiguities are preserved and flagged rather than silently converted into assumptions. Any required assumption is documented, tested, and sensitivity-analysed.

## Current Gate 2 status

**CLOSED / PENDING TESTER APPROVAL.**

The previously observed one-trade result remains rejected because its source partition ended on July 2, 2026 for a July 28, 2026 expiry, so it did not span the deterministic 32-DTE entry to final pre-expiry monitoring.

### Composite data path
The current Phase 2 pipeline:
1. stages free/public sources and caches them;
2. builds an exact-key, provenance-aware composite in DuckDB/Parquet;
3. rejects invalid option OHLC rows without interpolation/averaging;
4. checks cycle coverage and expected exchange-session continuity;
5. exports `results/composite/consolidated_options_data.csv`;
6. reconciles the CSV against the canonical Parquet before any backtest is eligible.

Parquet remains the research-native dataset. The CSV is the transfer artifact for Google Drive and future repository reuse.

### Current acceptance conditions
Gate 2 cannot pass until:
- every promoted expiry spans the 32-DTE entry window and the final pre-expiry session;
- no expected exchange session is missing inside a promoted cycle;
- expiry provenance is explicit or resolved from another explicit source;
- fallback rows retain source-level provenance;
- the CSV schema and row count match the Parquet;
- the canonical Parquet-derived CSV has the same SHA-256 as the published CSV;
- fresh CI and the independent tester review pass.

No performance result is promoted while any of these conditions remain open.

## Current research status — 2026-10-04

**Phase 2 / Gate 2: NOT PASSED.** The latest successful historical-data run produced only a one-trade validation artifact and was rejected. The enforcing pipeline has now been updated after independent tester Reviews 9, 10, 11, 12, 13, 14, and 15; unit tests now run before data staging; a fresh CI run is required before Gate 2 can be reconsidered.

### Historical expansion
The multi-year source assessment is recorded in [research/HISTORICAL_DATA_EXPANSION.md](research/HISTORICAL_DATA_EXPANSION.md). The current primary candidate remains the expiry-partitioned TradeMarkk 1-minute NIFTY options dataset covering approximately 2021–2026; rissin is retained for overlap validation, with other free/public candidates retained as documented fallbacks.

### Free source and composite research
See [research/FREE_DATA_SOURCE_REVIEW.md](research/FREE_DATA_SOURCE_REVIEW.md) and [research/COMPOSITE_DATA_PROTOCOL.md](research/COMPOSITE_DATA_PROTOCOL.md). No paid dataset has been assumed.

### CSV transfer artifact
The pipeline writes [results/composite/consolidated_options_data.csv](results/composite/consolidated_options_data.csv) only after a canonical composite has been built. Gate 2 promotion still requires independent tester reconciliation.

### Gate 2 review trail
- [Tester Review 8](research/TESTER_GATE_2_REVIEW_8.md)
- [Tester Review 9](research/TESTER_GATE_2_REVIEW_9.md)
- [Tester Review 10](research/TESTER_GATE_2_REVIEW_10.md)
- [Tester Review 11](research/TESTER_GATE_2_REVIEW_11.md)
- [Tester Review 12](research/TESTER_GATE_2_REVIEW_12.md)
- [Tester Review 13](research/TESTER_GATE_2_REVIEW_13.md)
- [Tester Review 14](research/TESTER_GATE_2_REVIEW_14.md)
- [Tester Review 15](research/TESTER_GATE_2_REVIEW_15.md)

No strategy performance conclusion is accepted until Gate 2 is independently approved.
