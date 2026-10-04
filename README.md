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

The current 2024–2026 pipeline detected 19 monthly expiries. This is **not** the final historical sample. It is being treated as a pipeline-validation sample only.

### Historical expansion
A multi-year expansion assessment is recorded in [research/HISTORICAL_DATA_EXPANSION.md](research/HISTORICAL_DATA_EXPANSION.md). Candidate sources include NSE official data, a public Hugging Face 1-minute index/options dataset covering approximately 2021–2026, and a Zenodo NIFTY 1-minute dataset covering 2017–2020. Sources will not be stitched into a production result until overlap, timestamp, contract, strike, and data-quality checks pass.

**No final performance conclusion will be accepted until the independent tester approves historical coverage and provenance.**
