# Phase 3 Tester Review 35 — Clean Corrected Run

Date: 2026-10-05
Role: Independent tester
Developer run: workflow 37253416839
Developer commit: d7b1bc03da8fed525b26ee4c3a6d433c12ed3487
Compact artifact: backtest-results-compact (artifact 11321234763)

## Verdict

**PASS WITH RESTRICTIONS — performance arithmetic and the previously blocked coverage audit are now internally consistent. Strict Gate 2 remains CLOSED because the requested 69-month dataset is not fully covered.**

## Independent checks

- Workflow: all unit tests, six partition builds, composite assembly, coverage validation, CSV export, CSV/Parquet reconciliation, backtest, and result publication completed successfully.
- CSV/Parquet reconciliation: PASS; 18,064,638 rows in each representation and identical SHA-256.
- Strategy metadata records fixed 1.30 reversal across two short contracts and 0.20 continuation combined across both short contracts.
- Candidate status records the actual previous monthly expiry and post-expiry entry date.
- 29 traded cycles.
- 628 orders.
- 314 BUY / 314 SELL.
- Gross P&L: +₹8,294.00.
- Costs: ₹17,085.92.
- Net P&L: −₹8,791.92.
- Win rate: 44.83%.
- Profit factor: 0.833656.
- Maximum drawdown: −₹30,811.11.
- P05: −₹5,669.63.
- P95: ₹4,289.12.
- Annualized monthly Sharpe proxy: −0.23854.
- State transitions: 66.
- Ratio builds: 53. With 29 original ratio builds and 13 continuation rebuilds, the remaining 24 ratio rebuilds are reversals.
- Continuation rebuilds: 13, confirmed by 13 continuation_long + 13 continuation_short + 13 continuation_hedge order groups.
- Reversal rebuilds: 24, inferred from total ratio-build groups.
- BUY/SELL symmetry is exact at 314/314.

## Slippage arithmetic

The order log contains 760 absolute lots. At one adverse ₹0.05 tick per lot and lot size 50, the reconstructed slippage drag is ₹1,900. This is an independent arithmetic check of the execution-cost implementation. It must not be confused with total transaction costs of ₹17,085.92.

## Coverage finding

The research-use status explicitly reports:
- requested months: 69
- strict complete cycles: 0
- strict gate: FAILED
- research-use partial mode: TRUE

Therefore the result is **not** a complete 2021-01 through 2026-09 historical validation. The 29 traded cycles are an explicitly partial/research-use sample.

## Strategy-fidelity decision

No unauthorized optimization, reversal sensitivity grid, alternate threshold, or new trading rule is present in this run. The user's fixed 1.30 two-short-contract reversal rule and 0.20 two-short-contract continuation rule are preserved.

## Gate decision

Performance arithmetic and the corrected audit layer pass. Strict Gate 2 remains closed. The strategy must not be promoted to live trading from this partial-data result alone.

## Tester → Developer

Update the developer branch's phase status, error log, chat log, README, and manuscript status to record this PASS WITH RESTRICTIONS. Preserve the strict Gate 2 CLOSED designation and clearly label the −₹8,791.92 result as research-use partial-data evidence. Do not introduce any strategy changes or optimization.
