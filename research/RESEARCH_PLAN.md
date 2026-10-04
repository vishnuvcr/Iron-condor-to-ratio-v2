# Research Plan

## Research question
Does the latest user-defined NIFTY strategy — monthly 0.30/0.10 Iron Condor, 0.10-delta breakout transition, directional ratio spread, 0.20 continuation reset, and fixed 1.30 short-leg-delta reversal trigger — produce robust risk-adjusted returns after realistic Indian option-trading costs and slippage?

## Secondary questions
1. How often does the initial Iron Condor reach the transition trigger?
2. How many ratio-spread resets occur per trade, and what is the distribution of outcomes across strategy states and transitions?
3. How do results change across low-, medium-, and high-volatility regimes?
4. What is the distribution of drawdowns, tail losses, turnover, and cost drag?
5. Does the strategy add value versus a static Iron Condor benchmark and a simple cash benchmark where appropriate?
6. How dependent are results on discretionary choices described in the video, especially early profit-taking and delayed adjustments?

## Proposed phases
### Phase 0 — Foundation
Create repository structure, role separation, logs, and research protocol. Status: COMPLETE.
### Phase 1 — Strategy specification
Translate every rule in the source into deterministic rules, identify ambiguities, and define an executable state machine. Status: COMPLETE; Gate 1 passed.
### Phase 2 — Data engineering
Acquire historical NIFTY monthly option intraday data, validate timestamps/strikes/expiries, cache data, and document provenance. Attempt a provenance-aware composite dataset when any source has gaps, but never interpolate or blend option prices. Status: IN PROGRESS.
### Phase 3 — Strategy-fidelity validation
Validate the exact YouTube strategy with the fixed 1.30 reversal trigger, realistic costs/slippage, and research-use data disclosure. Status: IN PROGRESS.
### Phase 4 — Engine implementation
Implement and validate the deterministic event-driven backtester in Python, including delta selection, transitions, position accounting, costs, expiry handling, and no-look-ahead constraints. Status: COMPLETE for the current strategy implementation; final acceptance remains gated.
### Phase 5 — Independent tester gate
Tester independently checks formulas, signs, delta logic, timestamps, contract mapping, P&L accounting, cost model, and edge cases before strategy promotion. Status: PENDING current fixed-1.30 run.
### Phase 6 — Historical backtest
Run the longest defensible common-data window; retain cached-data manifests, trade logs, daily equity, costs, and diagnostics. Status: CURRENT EXECUTION (research-use partial tier).
### Phase 7 — Robustness and statistical analysis
Compare to benchmarks, bootstrap trade sequences where appropriate, analyze regime/skew/cost dimensions, and report uncertainty without introducing unapproved strategy parameters. Status: PENDING tester acceptance.
### Phase 8 — Manuscript
Produce tables, charts, appendices, limitations, conclusions, and future research directions. Status: PLANNED.

### Phase-2 extension: composite-source fallback
When a free source contains a missing contract-minute observation, attempt exact-key recovery from another validated source. Prefer complete OHLCV rows from the highest-priority validated source; use lower-priority sources only for exact-key fallback. Keep source provenance on every row and require independent overlap checks before promotion. This extension does not change the stop rule.\n\n## Stop rule
The research stops after Phase 8 or earlier if the data are demonstrably insufficient for a defensible backtest. No unbounded data collection is permitted.


## 2026-10-05 scope correction
The reversal rule is fixed at a **1.30 short-leg delta trigger**. The previously drafted 0.80/1.00/1.20/1.30 sensitivity grid was unauthorized and is excluded from the research. No alternative reversal threshold, combined-delta reversal rule, optimization, or tuning is permitted unless the user/video explicitly changes the strategy.
