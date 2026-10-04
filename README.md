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
