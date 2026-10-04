# Phase 3 — Reversal Threshold Robustness

## Purpose
Test only the pre-specified reversal-threshold sensitivity grid required by Tester Review 27: **0.80, 1.00, 1.20, 1.30**.

## Fixed controls
- Same composite data and provenance as the Phase 2 research-use baseline.
- Same research-use entry mode: first observed expiry-month session when strict first-session coverage is unavailable.
- Same pre-expiry scheduled exit.
- Same brokerage: ₹20/order.
- Same adverse slippage: 1 option tick.
- Same continuation threshold: 0.20.
- No threshold optimization outside the four predefined points.
- No interpolation, theoretical pricing, forward filling, or synthetic option prices.
- No look-ahead.

## Outputs
For each threshold:
- trade summary
- order log
- candidate status
- metrics
- run manifest

Aggregate:
- threshold comparison CSV/JSON
- traded-cycle counts
- net P&L
- profit factor
- win rate
- max drawdown
- P05/P95 monthly P&L
- Sharpe proxy

## Decision gate
A threshold is not promoted because it has the highest backtest P&L alone. The tester must assess whether the result is robust across the four pre-specified values and whether conclusions survive incomplete/availability-biased data.

If all four remain weak, the strategy is documented as unsupported by the available research-use sample and the project moves to discussion/limitations/future research rather than indefinite tuning.

## Phase status
- Phase 2 baseline: completed, performance gate not passed.
- Phase 3: in progress.
- Tester review required before any strategy promotion or further parameter search.
