# Iron Condor -> Ratio Spread v2

Research status: **Phase 2 — Data engineering in progress; strategy scope reset to the latest user-defined rules only.**

**Scope reset (2026-10-05):** the initial transcript is non-authoritative and the 32-DTE constraint is removed. No prior 32-DTE result is a result for the current strategy.

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

**CLOSED / NOT PASSED.**

No strategy performance result is accepted. Earlier data-gate work used a 32-DTE protocol, but that protocol has been removed from the current strategy scope; those artifacts are retained only as infrastructure/history.

### Composite data path
The current Phase 2 pipeline:
1. stages free/public sources and caches them;
2. builds an exact-key, provenance-aware composite in DuckDB/Parquet;
3. rejects invalid option OHLC rows without interpolation/averaging;
4. checks cycle coverage and expected exchange-session continuity;
5. exports `results/composite/consolidated_options_data.csv`;
6. reconciles the CSV against the canonical Parquet before any backtest is eligible.

Parquet remains the research-native dataset. The CSV is the transfer artifact for Google Drive and future repository reuse.

### Gate 1 implementation convention
The 0.80–1.30 reversal rule is not given as an exact computational threshold. The baseline research convention is combined absolute delta of the two short ratio legs reaching 1.20, explicitly treated as a modelling convention rather than a user rule. Before any performance conclusion, reversal sensitivity runs must cover 0.80, 1.00, 1.20 and 1.30.

### Current acceptance conditions
Gate 2 cannot pass until:
- every promoted expiry spans the current strategy's deterministic first-expiry-month-session entry and final pre-expiry session;
- no expected exchange session is missing inside a promoted cycle;
- expiry provenance is explicit or resolved from another explicit source;
- fallback rows retain source-level provenance;
- the CSV schema and row count match the Parquet;
- the canonical Parquet-derived CSV has the same SHA-256 as the published CSV;
- fresh CI and the independent tester review pass.

No performance result is promoted while any of these conditions remain open.

## Current research status — 2026-10-05

**Phase 2 / Gate 2: NOT PASSED.** The latest composite remains data-incomplete for the current strategy lifecycle, so no performance result has been promoted. The enforcing pipeline has now been updated after independent tester Reviews 9, 10, 11, 12, 13, 14, 15, and 16; unit tests now run before data staging; CI diagnostics are uploaded as artifacts rather than pushed to the developer branch; the composite build is file-backed and partitioned by year with a deterministic assembly step, and the assembly preserves the requested coverage window; CI run 37231413691 passed unit tests, all six partitions and composite assembly, but the lifecycle gate remained 0/69 complete months; independent tester Review 24 confirmed Gate 2 remains closed.

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
- [Tester Review 16](research/TESTER_GATE_2_REVIEW_16.md)
- [Tester Review 17](research/TESTER_GATE_2_REVIEW_17.md)
- [Tester Review 18](research/TESTER_GATE_2_REVIEW_18.md)
- [Gate 2 Review 19 — Data Coverage](research/TESTER_GATE_2_REVIEW_19.md)
- [Gate 2 Review 20 — Lead-In Hypothesis](research/TESTER_GATE_2_REVIEW_20.md)
- [Tester Review 19](research/TESTER_GATE_2_REVIEW_19.md)
- [Tester Review 24 — Post-scope-reset data gate](research/TESTER_GATE_2_REVIEW_20.md)

No strategy performance conclusion is accepted until Gate 2 is independently approved.
