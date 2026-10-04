# Research Plan

## Research question
Does the video strategy — starting with a monthly NIFTY Iron Condor and switching to a directional ratio spread when the condor's short leg reaches about 0.10 delta — produce robust risk-adjusted returns after realistic Indian option-trading costs and slippage?

## Secondary questions
1. How often does the initial Iron Condor reach the transition trigger?
2. How many ratio-spread resets occur per trade, and how sensitive are results to the stated delta thresholds?
3. How do results change across low-, medium-, and high-volatility regimes?
4. What is the distribution of drawdowns, tail losses, turnover, and cost drag?
5. Does the strategy add value versus a static Iron Condor benchmark and a simple cash benchmark where appropriate?
6. How dependent are results on discretionary choices described in the video, especially early profit-taking and delayed adjustments?

## Proposed phases
### Phase 0 — Foundation
Create repository structure, role separation, logs, and research protocol. Status: COMPLETE.
### Phase 1 — Strategy specification
Translate every rule in the source into deterministic rules, identify ambiguities, and define an executable state machine. Status: IN PROGRESS.
### Phase 2 — Data engineering
Acquire historical NIFTY monthly option intraday data, validate timestamps/strikes/expiries, cache data, and document provenance. Status: PLANNED.
### Phase 3 — Cost/slippage model
Implement Paytm Money brokerage and applicable exchange/statutory charges by date, plus explicit slippage scenarios. Status: PLANNED.
### Phase 4 — Engine implementation
Implement a deterministic event-driven backtester in Python. Unit-test delta selection, transitions, position accounting, costs, expiry handling, and no-look-ahead constraints. Status: PLANNED.
### Phase 5 — Independent tester gate
Tester independently checks formulas, signs, delta logic, timestamps, contract mapping, P&L accounting, cost model, and edge cases before any production backtest is accepted. Status: PLANNED.
### Phase 6 — Historical backtest
Run the longest defensible common-data window; retain cached-data manifests, trade logs, daily equity, costs, and diagnostics. Status: PLANNED.
### Phase 7 — Robustness and statistical analysis
Compare to benchmarks, bootstrap trade sequences where appropriate, run parameter sensitivity, regime splits, and uncertainty estimates. Status: PLANNED.
### Phase 8 — Manuscript
Produce tables, charts, appendices, limitations, conclusions, and future research directions. Status: PLANNED.

## Stop rule
The research stops after Phase 8 or earlier if the data are demonstrably insufficient for a defensible backtest. No unbounded data collection is permitted.
