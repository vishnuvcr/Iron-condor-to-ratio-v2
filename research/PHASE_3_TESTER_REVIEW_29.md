# Phase 3 Tester Review 29 — Numerical Verification and Performance Gate

Date: 2026-10-05
Role: Independent tester
Developer run: workflow 37237347768
Code commit: 9adf6381039f2e627c58c2762116018086e2d006
Compact artifact: 11316213198

## Verdict

**PASS WITH RESTRICTIONS — numerical performance output independently verified; strategy promotion is NOT approved.**

The fixed **1.30 short-leg-delta** strategy has been independently checked from the compact trade/order outputs. The negative result is reproducible and is sufficient to close the strategy-promotion question for the present research-use dataset.

## Independently verified performance

From `trade_summary.csv`:
- 28 traded cycles
- total gross P&L: -₹3,821.50
- total transaction costs: ₹16,633.96
- total net P&L: -₹20,455.46
- average net P&L: -₹730.55
- median net P&L: -₹433.80
- win rate: 13/28 = 46.43%
- profit factor: 0.64678
- maximum drawdown: -₹41,981.20
- 5th percentile cycle P&L: -₹10,542.68
- 95th percentile cycle P&L: ₹4,464.95
- ROI on ₹1,00,000 reference capital: -20.455%
- annualized monthly Sharpe proxy: -0.54136

The tester independently recomputed all of these from the trade-level cycle file and obtained exact agreement with `metrics.json`.

## Cost and order reconciliation

From `order_log.csv`:
- 620 order rows
- trade-summary order count: 620
- total order-level costs: ₹16,633.96
- trade-summary costs: ₹16,633.96
- cost reconciliation difference: ₹0
- 310 BUY orders and 310 SELL orders
- 66 total lifecycle transitions

Gross cash-flow sum from the order log is -₹3,821.50, matching total gross P&L.

## Strategy-state reconciliation

Across the 28 traded cycles:
- 28 IC-to-ratio transitions
- 38 ratio resets/continuations
- 38 continuation rebuilds
- no additional initial-ratio builds beyond the first build in any traded cycle
- therefore **zero 1.30 reversal-trigger events were observed** in the research-use sample.

This is a result of the supplied strategy and observed data, not an added rule.

## Data-quality restrictions

The run manifest records:
- requested window: 2021-01-01 to 2026-09-30
- 54 observed composite expiry candidates
- 28 traded cycles
- 24 skipped because a complete executable path was unavailable
- 2 skipped because data were empty
- strict lifecycle coverage: 0/69 requested calendar months
- entry mode: research-use `available`
- brokerage: ₹20/order
- slippage: one adverse option tick
- continuation trigger: 0.20
- reversal trigger: fixed 1.30

The strict Gate 2 remains CLOSED. The result is therefore an exploratory/research-use finding, not a fully covered historical validation.

## Promotion decision

The current strategy is **not promoted**.

The evidence is directionally strong enough to conclude that, under the exact video-defined rules, this dataset/cost/execution configuration did not demonstrate a positive trading edge. Further parameter tuning or reversal-threshold optimization is not justified because it would change the strategy under test.

## Tester instruction to developer

Proceed to the manuscript/conclusion phase without changing the strategy. Clearly label the result as research-use partial-data, retain strict Gate 2 CLOSED, include the cost drag and zero-reversal observation, and document the limitations and future research path. Do not introduce new trading rules or parameter searches.

## Developer instruction

Prepare the final research manuscript and reproducibility supplements from the verified compact outputs. Strategy promotion remains prohibited.
