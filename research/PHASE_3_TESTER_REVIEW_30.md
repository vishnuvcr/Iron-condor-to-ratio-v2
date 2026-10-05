# Phase 3 Tester Review 30 — Independent Doubt Audit

Date: 2026-10-05
Role: Independent tester
Reviewed developer branch: `phase-3-robustness-developer`
Reviewed result bundle: `results/trade_summary.csv`, `results/order_log.csv`, `results/metrics.json`, `results/run_manifest.json`

## Verdict

**NUMERICAL RECONCILIATION: PASS.**
**RESEARCH VALIDITY: RESTRICTED / DO NOT PROMOTE.**

The headline numerical result is reproducible from the stored compact outputs. However, the user's doubt is justified because the result is not a complete historical validation and the repository's documented cost methodology is not fully implemented in the published run.

## Independent recomputation

From the stored files:

- 28 traded cycles.
- 620 orders.
- 310 BUY / 310 SELL orders.
- Gross P&L: -₹3,821.50.
- Transaction costs: ₹16,633.95845258.
- Net P&L: -₹20,455.45845258.
- Win rate: 13/28 = 46.4286%.
- Profit factor: 0.6467776.
- Maximum drawdown: -₹41,981.1983.
- P05: -₹10,542.6790.
- P95: ₹4,464.9456.
- Annualized monthly Sharpe proxy: -0.5413648.

Independent aggregation of `order_log.csv` gives gross cashflow -₹3,821.50 and costs ₹16,633.95845258, matching the trade file and metrics file to rounding/float precision.

The order count also reconciles mechanically:
28 initial IC x 4 orders = 112
28 IC exits x 4 orders = 112
28 initial ratio builds x 3 orders = 84
38 continuation rebuilds x 6 orders = 228
28 scheduled exits x 3 orders = 84
Total = 620.

## Critical robustness observation

The published gross result already includes one adverse tick of slippage. Removing exactly that one-tick slippage from every recorded fill gives:

- Gross P&L before slippage: **-₹1,871.50**.
- Slippage drag: **₹1,950.00**.
- Therefore the strategy remains negative before transaction costs even with zero slippage.

So the negative direction is **not caused by brokerage or the one-tick slippage assumption**.

## Strategy-lifecycle check

The stored order reasons reconcile to:

- 28 IC-to-ratio transitions.
- 38 continuation resets.
- 0 reversal events in the order log.
- 66 state transitions total (28 + 38).

The fixed 1.30 threshold is present in the developer backtest code and is checked against the absolute delta of the active short ratio legs. No alternate reversal threshold was used in the final run.

## Major restriction: data completeness

The run manifest reports:

- Requested window: 2021-01-01 through 2026-09-30.
- 69 requested calendar months.
- 54 observed expiry candidates.
- 28 traded cycles.
- 24 skipped incomplete execution paths.
- 2 skipped empty.
- Strict complete lifecycle coverage: **0/69 months**.
- Research-use mode: `entry_mode=available`.

This means the 28 cycles are **not a representative or complete 69-month historical sample**. They are the subset for which an executable path happened to exist in the partial composite. This prevents treating the observed negative result as a definitive historical-performance estimate.

In addition, research-use entry can occur at the first observed session in the expiry month when the intended month-start session is unavailable. That is an explicitly documented research-use relaxation and is another reason the result should not be labelled an exact full-history replication.

## Cost-model implementation finding

`research/COST_MODEL.md` states that the implementation must use historical exchange/statutory rates by trade date. The current code instead contains a single exchange transaction rate of ₹3,553/crore for all dates.

NSE's February 27, 2026 circular makes ₹3,553/crore effective from March 1, 2026; earlier periods used different structures/rates. Therefore the published run is not fully compliant with its own stated historical-rate methodology.

This does **not** invalidate the arithmetic of the published result, but it requires either:
1. a documented decision to use the current retail pass-through cost schedule across historical dates, or
2. a corrected historical cost schedule and rerun.

Official sources:
- NSE transaction-charge circular, effective 2026-03-01: https://nsearchives.nseindia.com/content/circulars/FA73061.pdf
- NSE STT schedule, updated 2026-04-01: https://www.nseindia.com/static/products-services/equity-derivatives-securities-transaction-tax

## Brokerage verification note

Paytm Money's published material is internally inconsistent across pages. Its newer pricing material says brokerage was aligned to ₹20 across segments from January 15, 2025, while a current F&O FAQ page states ₹10 per unique executed order. The run uses ₹20/order.

Therefore the brokerage assumption must remain explicitly account-tariff-dependent and should not be presented as universally correct for every Paytm Money account.

## Slippage reporting gap

The repository's cost model requires zero-slippage, baseline, and stress slippage references. The final promoted artifact currently exposes only the one-tick baseline.

Because zero-slippage gross P&L can already be reconstructed as -₹1,871.50 from the stored fills, this is an auditable finding, but the final manuscript should distinguish the baseline run from any broader execution-cost conclusion.

## Tester decision

The final negative result is **arithmetically trustworthy for the exact stored 28-cycle research-use sample**.

It is **not sufficient to claim that the strategy is definitively unprofitable across the intended 69-month historical period**, because strict lifecycle coverage is 0/69.

Strategy promotion remains prohibited.

No parameter optimization, threshold sensitivity, or new trading rule is authorized.

## Required developer action

1. Keep the fixed 1.30 strategy unchanged.
2. Correct or explicitly reframe the historical cost methodology.
3. Ensure the manuscript clearly separates:
   - arithmetic verification of the 28-cycle sample,
   - zero-slippage audit result,
   - partial-data limitation,
   - non-promotion decision.
4. Update README, phase status, error log, and conversation log to reflect this audit.
5. Do not reopen Gate 2 or promote the strategy.

## Tester → Developer

Remediate only the cost-methodology/documentation discrepancy and research-validity labeling. Do not alter any strategy rule.

## Developer → Tester

After remediation, independently re-check the cost schedule, manuscript wording, and gate status without changing the strategy.
