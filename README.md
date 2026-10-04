# Iron Condor -> Ratio Spread v2

Research status: **Gate 1 passed; Phase 2 data engineering in progress.**

This repository is the reproducible research record for backtesting the YouTube strategy supplied by the user:
https://youtu.be/T4gvTshMEyA

## Navigation
- research/RESEARCH_PLAN.md
- research/STRATEGY_SPEC.md
- research/PHASE_STATUS.md
- research/DATA_SOURCES.md
- research/HISTORICAL_DATA_EXPANSION.md
- research/COST_MODEL.md
- research/ERROR_LOG.md
- research/CHAT_LOG.md
- research/ROLES_AND_GATES.md

## Roles and branches
- developer: implementation branch; may write research code and workflow changes.
- tester: independent review branch; must not copy developer implementation code into tester code. Tester reviews developer commits read-only and records findings independently.

## Research principle
The published video is the primary specification. Ambiguities are preserved and flagged rather than silently converted into assumptions. Any required assumption is documented, tested, and sensitivity-analysed.

## Current gate
**Gate 2 / Phase 2 — data engineering: IN PROGRESS.**

The prior expanded pipeline detected 23 candidate monthly expiries but only 15 complete trades; 2022/2023 continuity was not established. That result is **validation-only**, not a final historical sample. Phase 2 now uses the expiry-partitioned 2021–2026 NIFTY source and must pass independent coverage/provenance checks.

### Historical expansion
A multi-year expansion assessment is recorded in [research/HISTORICAL_DATA_EXPANSION.md](research/HISTORICAL_DATA_EXPANSION.md). The current primary candidate is the expiry-partitioned TradeMarkk 1-minute NIFTY options dataset covering approximately 2021–2026; the rissin source is retained for overlap validation, with NSE and Zenodo sources as independent references/candidates. Sources will not be stitched into a production result until overlap, timestamp, contract, strike, and data-quality checks pass.

**No final performance conclusion will be accepted until the independent tester approves historical coverage and provenance.**


## Current research status — 2026-10-04

**Phase 2 / Gate 2: NOT PASSED.** The latest CI run completed technically, but the resulting one-trade output is invalid for the baseline because the selected expiry partition did not contain the required 32-DTE-to-expiry history. The July 28, 2026 partition ended on July 2. The engine has now been hardened to reject incomplete expiry partitions instead of treating their last observation as an early exit.

- Strategy specification: [research/STRATEGY_SPEC.md](research/STRATEGY_SPEC.md)
- Research plan: [research/RESEARCH_PLAN.md](research/RESEARCH_PLAN.md)
- Phase status: [research/PHASE_STATUS.md](research/PHASE_STATUS.md)
- Data-source expansion: [research/HISTORICAL_DATA_EXPANSION.md](research/HISTORICAL_DATA_EXPANSION.md)
- Error log: [research/ERROR_LOG.md](research/ERROR_LOG.md)
- Tester Gate 2 reports: [research/TESTER_GATE_2_REVIEW_3.md](research/TESTER_GATE_2_REVIEW_3.md)

No performance result from the current one-trade run is treated as evidence of strategy profitability. The next Gate 2 submission requires a defensible continuous historical source with complete cycle coverage and independent tester approval.


## Free data-source investigation — 2026-10-04
The project is actively prioritizing free/public data before any paid source. See [research/FREE_DATA_SOURCE_REVIEW.md](research/FREE_DATA_SOURCE_REVIEW.md). The first empirical target is the free NIFTY 1-minute OHLCV+OI sample exposed by Cloud Trader Pro/Shoonya; Zenodo 2017-2020 is an older-period candidate. No incomplete sample is allowed to generate final performance claims.
