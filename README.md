# Iron Condor -> Ratio Spread v2

Research status: **Phase 0 — Foundation initialized; Phase 1 specification in progress.**

This repository is the reproducible research record for backtesting the YouTube strategy supplied by the user:
https://youtu.be/T4gvTshMEyA

## Navigation
- research/RESEARCH_PLAN.md
- research/STRATEGY_SPEC.md (to be added at Gate 1)
- research/PHASE_STATUS.md
- research/DATA_SOURCES.md
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
Gate 0 — repository foundation / role separation.
Next: formalize the strategy specification, cost model, data contract, and testable acceptance criteria before running the backtest.
