# Literature Review — Iron Condor to Directional Ratio Strategy

Date: 2026-10-05

## Scope
Iron condors, delta-selected ratio spreads, volatility skew, variance/volatility risk premia, Indian index-option efficiency, FII positioning, volatility regimes, transaction costs, and Indian derivatives regime changes.

## Research questions generated
1. Does converting the initial iron condor into a directional ratio spread improve risk-adjusted returns versus a static IC?
2. Is any observed edge due to volatility/variance risk premium rather than the transition rule?
3. Does option-skew state predict transition profitability or tail risk?
4. Does performance differ across volatility regimes?
5. Does FII derivatives positioning provide explanatory regime information?
6. How much gross edge survives brokerage, statutory costs and slippage?
7. Are results stable across major Indian derivatives-market changes?
8. Does sparse availability of far-OTM/low-delta strikes create availability bias?

## Findings
### Iron condor
An iron condor combines a bear-call and bull-put spread and is generally associated with range/low-volatility expectations. Strike distance, volatility and tail risk are therefore central to interpretation. Fidelity's 2026 strategy reference describes the structure as a four-leg limited-risk strategy suited to relatively low volatility.

### Ratio spreads
Ratio spreads contain more short than long options and can create substantial or unlimited adverse-side risk. Wiley's ratio-spread material and CME educational material both emphasize asymmetric payoff and delta-based strike selection.

**Implication:** evaluate tail loss, drawdown and regime dependence, not just average P&L.

### Volatility skew
Ratio-spread literature explicitly connects ratio structures with implied-volatility skew. Skew can improve premium received but can also represent compensation for genuine tail risk.

**Implication:** record IV/skew diagnostics at entry and transition whenever the data permit.

### Indian option pricing and IV
Jain (2019) finds that a smile-adjusted Black model fits Indian equity options well and that implied volatility contains incremental predictive information about future volatility.

**Implication:** IV/skew should be explanatory variables in the analysis rather than assuming delta alone describes the market state.

### Volatility risk premium
Indian research reports volatility-risk-premium/commonality effects. A 2025 NIFTY study reports implied variance regularly exceeding realized variance, while a 2026 preprint specifically highlights the importance of realistic implementation costs and post-2024 structural changes.

**Implication:** option-selling profitability cannot automatically be interpreted as evidence that this transition rule adds alpha.

### FII positioning
A 2023 Indian study using 2012–2021 weekly data reports a relationship between FII derivatives-market behaviour and option implied volatility.

**Implication:** FII/DII positioning should initially be treated as an explanatory regime covariate, not an optimized trading signal.

### Structural changes
Research on weekly index options shows that market evolution can affect information absorption and volatility. Recent regulatory/contract changes further motivate temporal sub-samples.

**Implication:** final analysis should report time/regime splits rather than relying solely on pooled results.

## Methodological consequences
Without changing the user-defined trading rules:
1. Add volatility-regime stratification.
2. Add IV/skew diagnostics where possible.
3. Add FII/DII positioning as explanatory/regime information.
4. Explicitly quantify implementation-cost drag.

These are analysis layers, not new optimized parameters.

## Hypotheses
**H1:** Dynamic IC-to-ratio transition improves risk-adjusted returns versus static IC after costs.

**H2:** Transition performance differs materially by volatility regime.

**H3:** Transition profitability/tail risk depends on option-skew state.

**H4:** Costs consume a meaningful fraction of gross returns.

**H5:** A credible strategy conclusion requires reasonable temporal/regime stability.

## Important caution
Literature provides economic motivation, not proof of profitability for this specific strategy. Strategy-specific evidence must come from the predefined backtests and independent tester gates.

## Selected references
- Jain, S. (2019). *Indian equity options: Smile, risk premiums, and efficiency*. Journal of Futures Markets, 39(2), 150–163. DOI 10.1002/fut.21971.
- Chakrabarti, P. (2021). *Co-movement of volatility risk premium: evidence from single stock options market in India*. Applied Economics Letters, 28(14), 1181–1186. DOI 10.1080/13504851.2020.1803485.
- Jain, P. & Kotha, K.K. (2022). *Does options improve the information absorption? Evidence from the introduction of weekly index options*. International Review of Finance, 22(4), 770–776. DOI 10.1111/irfi.12372.
- *Investment Behavior of Foreign Institutional Investors and Implied Volatility Dynamics: An Empirical Study on the Indian Equity Derivatives Market* (2023). Journal of Risk and Financial Management, 16(11), 470.
- Lowell, L. (2012). *A Bonus Strategy: Ratio Option Spreads*. Wiley.
- Rhoads, R. (2012). *Ratio Spreads*. Wiley.
- Passarelli, D. (2012). *Ratio Spreads and Complex Spreads*. Wiley.
- CME Group. *Option Ratio Spreads*.
- Fidelity. *The iron condor options strategy* (2026).
