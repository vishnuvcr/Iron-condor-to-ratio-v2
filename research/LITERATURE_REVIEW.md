# Literature Review — Initial Pass

## Scope
The literature search is being used to frame hypotheses and robustness checks; it is not treated as evidence that this exact IC-to-ratio rule works.

## Findings
1. Condor performance is regime-sensitive. Niblock's empirical study of monthly condor spreads reports that some short-volatility condor structures generated attractive nominal/risk-adjusted returns while others did not, and links performance to volatility preferences and return-distribution shape.
2. Iron condors have limited-risk, capped-profit exposure and are commonly framed as range/low-volatility strategies; the source literature emphasizes delta/gamma/vega/theta and underlying-price sensitivity as important risk dimensions.
3. A 2023 SSRN analysis of SPX iron condors over 32 years reports that market and volatility conditions materially affect outcomes, supporting regime-stratified analysis rather than a single aggregate average.
4. Recent work on iron condor portfolio optimization frames early stopping/adjustment as an optimal-control problem, reinforcing that discretionary exits can materially change performance.
5. Ratio spreads create directional exposure but introduce meaningful adverse-move risk, especially because a ratio spread can contain naked short options. Practitioner literature emphasizes strike spacing and adverse gap risk.
6. A recent one-minute SPX 0DTE study found profitable iron-condor variants in its sample, but also reported implied-volatility overstatement relative to realized volatility. This supports testing whether premium/volatility conditions influence the strategy's edge rather than assuming theta alone explains returns.

## Research implication
The current strategy should therefore be tested by volatility regime, direction/regime transition frequency, gap/reversal frequency, cost drag, and drawdown/tail loss — not only total ROI.

## Direct gap in literature
No peer-reviewed or public research located in this initial search evaluates the exact rule set from the supplied YouTube video: monthly NIFTY 0.30/0.10 Iron Condor -> 0.10-delta transition -> 0.50/0.40/0.10 ratio -> 0.20 continuation reset -> 1.20–1.30 reversal reset. This motivates an explicit out-of-sample backtest rather than relying on generic options-strategy claims.

## Key references
- Niblock, S.J. — Flight of the Condors: Evidence on the Performance of Condor Option Spreads in Australia. Applied Finance Letters. https://doi.org/10.24135/afl.v6i01.69
- de Saint-Cyr, A. — A Simple Historical Analysis of the Performance of Iron Condors on the SPX. SSRN 2023. https://doi.org/10.2139/ssrn.4643378
- Dziawgo, E. — The Iron Condor Strategy in Financial Risk Management. 2020.
- Huang, H., Sun, Q., Yang, X. — Stochastic Optimal Control of Iron Condor Portfolios for Profitability and Risk Management. arXiv:2501.12397.
- Perz, P. — Profitability of Selected 0DTE Index Options Strategies. 2024/2026 SSRN versions.
