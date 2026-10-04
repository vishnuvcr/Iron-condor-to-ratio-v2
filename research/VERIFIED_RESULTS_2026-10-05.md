# Verified Results Supplement — 2026-10-05

## Run identity
- Workflow: 37237347768
- Code commit: 9adf6381039f2e627c58c2762116018086e2d006
- Compact artifact: 11316213198
- Strategy reversal trigger: fixed 1.30 short-leg delta
- Entry mode: research-use available
- Brokerage: ₹20/order
- Slippage: one adverse tick
- Continuation trigger: 0.20 combined absolute delta

## Independently recomputed metrics
| Metric | Value |
|---|---:|
| Trades | 28 |
| Gross P&L | -₹3,821.50 |
| Costs | ₹16,633.96 |
| Net P&L | -₹20,455.46 |
| Average net P&L | -₹730.55 |
| Median net P&L | -₹433.80 |
| Win rate | 46.43% |
| Profit factor | 0.64678 |
| Max drawdown | -₹41,981.20 |
| P05 | -₹10,542.68 |
| P95 | ₹4,464.95 |
| ROI on ₹1L | -20.455% |
| Annualized monthly Sharpe proxy | -0.54136 |

## Independent reconciliation
- Trade rows: 28
- Order rows: 620
- Trade-summary orders: 620
- Order-level total costs: ₹16,633.96
- Trade-summary total costs: ₹16,633.96
- Cost difference: ₹0
- Order gross cashflow: -₹3,821.50
- Trade-summary gross P&L: -₹3,821.50
- BUY orders: 310
- SELL orders: 310
- IC transitions: 28
- Continuation resets: 38
- Reversal events: 0

## Coverage
- Requested calendar months: 69
- Composite observed expiry candidates: 54
- Traded cycles: 28
- Skipped incomplete execution: 24
- Skipped empty: 2
- Strict complete cycles: 0
- Strict Gate 2: CLOSED

## Interpretation
The exact tested strategy did not demonstrate a positive net-return edge in the available research-use sample. The result is exploratory because the strict lifecycle gate remains closed. The strategy is not promoted.
