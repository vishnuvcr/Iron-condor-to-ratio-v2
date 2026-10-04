# Iron Condor -> Ratio Spread v2

Research status: **Phase 8 — final manuscript completed; strategy not promoted.**

**Scope reset (2026-10-05):** the initial transcript is non-authoritative and the 32-DTE constraint is removed. No prior 32-DTE result is a result for the current strategy.

## Navigation
- research/RESEARCH_PLAN.md
- research/STRATEGY_SPEC.md
- research/PHASE_STATUS.md
- research/LITERATURE_REVIEW_2026-10-05.md
- research/RESEARCH_QUESTIONS_AND_METHODOLOGY.md
- research/FREE_DATA_SOURCE_REVIEW.md
- research/COMPOSITE_DATA_PROTOCOL.md
- research/COST_MODEL.md
- research/ERROR_LOG.md
- research/CHAT_LOG.md
- research/ROLES_AND_GATES.md

## Roles and branches
- developer: `phase-3-robustness-developer`
- tester: `phase-3-robustness-tester`
- Phase 2 branches remain frozen historical implementation/review environments.

Developer and tester are isolated. Tester approval is required before strategy promotion.

## Current gate status

**Strict Gate 2: CLOSED. Research-use partial-data analysis: ENABLED.**

The current composite does not establish complete deterministic lifecycle coverage for all 69 requested months. This is disclosed rather than hidden.

## Final verified result

The exact user-defined strategy was tested with a **fixed 1.30 short-leg delta reversal trigger**. No reversal-threshold sensitivity testing or parameter optimization was performed.

Verified research-use result (workflow 37237347768):
- 28 traded cycles
- gross P&L: **−₹3,821.50**
- transaction costs: **₹16,633.96**
- net P&L: **−₹20,455.46**
- win rate: **46.43%**
- profit factor: **0.6468**
- max drawdown: **−₹41,981.20**
- annualized monthly Sharpe proxy: **−0.5414**
- 38 continuation resets
- **0 observed 1.30 reversal events**

The independent tester reproduced the reported metrics exactly from the compact trade/order outputs. The strategy is **not promoted**.

Strict lifecycle coverage remains **0/69 requested months**; the result is therefore a research-use partial-data conclusion, not a fully covered historical validation.

See [manuscript/FINAL_RESEARCH_MANUSCRIPT.md](manuscript/FINAL_RESEARCH_MANUSCRIPT.md) and [research/VERIFIED_RESULTS_2026-10-05.md](research/VERIFIED_RESULTS_2026-10-05.md).

## Scientific research expansion

The research now includes:
- literature review on iron condors, ratio spreads and skew;
- Indian option-market volatility/efficiency research;
- volatility-risk-premium evidence;
- FII/implied-volatility relationships;
- Indian derivatives-market structural changes;
- predefined volatility/skew/regime hypotheses;
- bootstrap and distributional analysis plans;
- static-IC benchmark comparison;
- cost-drag decomposition.

See [research/LITERATURE_REVIEW_2026-10-05.md](research/LITERATURE_REVIEW_2026-10-05.md) and [research/RESEARCH_QUESTIONS_AND_METHODOLOGY.md](research/RESEARCH_QUESTIONS_AND_METHODOLOGY.md).

NSE's current option-chain infrastructure exposes OI, volume, IV, bid/ask and LTP fields, while NSE contract specifications document expiry conventions and tick sizes. NSE also publishes participant-wise/FII derivatives statistics and daily F&O reports. These are important external reference streams for later regime and market-structure analysis. urlNSE Option Chainhttps://www.nseindia.com/option-chain?symbol=NIFTY urlNSE Contract Specificationshttps://www.nseindia.com/static/products-services/equity-derivatives-contract-specifications urlNSE F&O Reportshttps://www.nseindia.com/all-reports-derivatives

The project will explicitly account for the 2024–2025 Indian derivatives-market changes when interpreting time stability. NSE changed NIFTY expiry conventions effective April 2025, and SEBI introduced several index-derivatives measures from November 2024 onward. These structural breaks make pooled pre/post-reform performance comparisons important. 

## Data and CSV

The canonical research dataset is Parquet. The consolidated CSV is the transfer artifact for Google Drive/future reuse:

`results/composite/consolidated_options_data.csv`

The pipeline never interpolates, forward-fills, averages or theoretically reconstructs missing option prices.

## Baseline research-use result

The first research-use baseline (from the earlier pre-correction run) produced:
- 28 traded cycles
- net P&L: **−₹20,455.46**
- profit factor: **0.647**
- win rate: **46.43%**
- max drawdown: **−₹41,981.20**
- monthly-Sharpe proxy: **−0.541**

This result is exploratory and **not authoritative for the corrected fixed-1.30 implementation**. Strict lifecycle coverage remains 0/69.

## Final research objective

The research will stop at the predefined phases. The final deliverable will be a structured manuscript containing:
1. research questions and hypotheses;
2. literature review;
3. data/provenance methodology;
4. strategy specification;
5. statistical methodology;
6. benchmark and robustness results;
7. regime/skew/cost analysis where data permit;
8. discussion;
9. strengths and limitations;
10. conclusion;
11. future research;
12. tables, figures, appendices and reproducibility supplements.

No endless parameter search is permitted.


**Fixed reversal trigger:** 1.30 short-leg delta. No reversal-threshold sensitivity testing is authorized.
