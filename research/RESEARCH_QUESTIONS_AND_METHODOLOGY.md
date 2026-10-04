# Research Questions and Scientific Methodology

Date: 2026-10-05

## Primary question
Does the user-defined monthly NIFTY 0.30/0.10-delta iron-condor strategy, converted causally into the specified 1:-2:+1 directional ratio structure and managed by the specified continuation/reversal rules, produce robust risk-adjusted returns after realistic Indian option-trading costs and slippage?

## Primary estimand
The primary estimand is the distribution of net cycle-level P&L under the deterministic strategy specification and fixed execution-cost model.

Secondary estimands: profit factor, win rate, maximum drawdown, return on reference capital, turnover/cost drag, tail-loss quantiles, annual/regime performance, transition frequency, state durations, continuation and reversal counts.

## Experimental unit
Expiry-cycle trade, with intraday orders nested inside each cycle.

## Causal information set
Signals use only completed-bar information. Orders execute at the next available executable observation. No future bar, future expiry information, or future strike selection.

## Strategy states
1. Initial monthly iron condor.
2. Call-ratio transition after falling-market trigger.
3. Put-ratio transition after rising-market trigger.
4. Same-direction continuation/reset.
5. Opposite-direction reversal.
6. Mandatory pre-expiry exit.

## Fixed controls
- Initial short legs: approximately 0.30 delta.
- Initial long hedges: approximately 0.10 delta.
- Ratio transition: +1 0.50 delta, -2 0.40 delta, +1 0.10 delta.
- Continuation threshold: combined short-leg absolute delta 0.20.
- Reversal trigger: fixed 1.30 short-leg delta.
- Current brokerage model: ₹20/order.
- Current slippage model: one adverse option tick/order.
- No synthetic missing prices.

## Data tiers
**Strict Gate 2:** complete lifecycle evidence required; currently closed.

**Research-use partial tier:** allowed because the user instructed that the most usable real data should be used even when imperfect. Every incomplete cycle and entry-timing deviation must remain explicit. The two tiers must never be conflated.

## Statistical analysis plan
1. Cycle-level descriptive statistics.
2. Bootstrap confidence intervals for mean/median net P&L and selected risk metrics, using cycles as the resampling unit.
3. Annual and regime-stratified results.
4. Static 0.30/0.10 IC benchmark using compatible data/execution assumptions.
5. Cost-drag decomposition.
6. State-transition frequency and fixed-1.30 reversal-event incidence.
7. Tail quantiles and expected shortfall where sample size permits.
8. Multiple-testing correction for this strategy is not applicable to reversal thresholds because no reversal-threshold grid was authorized or run.
9. Where the sample is too small for reliable inference, report effect sizes and uncertainty without overstating significance.

## Regime analysis
Where data support it, define regimes ex ante from observable variables:
- India VIX percentile;
- realized NIFTY volatility;
- trend state;
- option IV/skew;
- FII/DII positioning;
- major global-market shock indicator.

Regime cutoffs must be defined before inspecting regime-specific strategy returns.

## Benchmarks
At minimum:
- static monthly 0.30/0.10 iron condor;
- cash/reference-capital benchmark.

If sufficient data permit:
- static directional ratio structure;
- simple short-volatility benchmark.

All benchmarks require compatible costs and windows.

## Cost model
Every order includes the current ₹20 brokerage assumption and one adverse option tick. Exchange/statutory/other implementation charges should be added when date-specific Paytm Money schedules can be reconstructed. If an exact historical charge cannot be reconstructed, the omission must be quantified as a limitation.

## Missing-data analysis
Report requested months, usable expiries, complete/incomplete cycles, traded cycles, missing strikes, source contribution, entry-session deviations, and exclusion reasons.

No interpolation, forward-fill, synthetic price, or theoretical reconstruction is allowed.

## Promotion criteria
Promotion requires tester approval, acceptable provenance, economically meaningful net performance, non-dominated risk metrics, temporal/regime stability, cost robustness, and no unresolved implementation defect. The best P&L alone is never sufficient.

If these conditions fail, report an unsupported/negative finding rather than endlessly tuning parameters.

## Reproducibility
Preserve source manifests, hashes, parameters, execution assumptions, dependencies, workflow IDs, metrics, errors/remediation and tester reviews.
