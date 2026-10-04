# Tester Report — Gate 1 Specification Review

Reviewer role: Independent tester
Reviewed branch: developer
Reviewed artifact: research/STRATEGY_SPEC.md
Gate result: **FAIL — changes required before implementation**

## Checks performed

### 1. Source-rule fidelity
PASS for the core numeric mechanics:
- IC short legs near 0.30 delta and long hedges near 0.10.
- Transition when an IC short leg reaches about 0.10.
- Down move -> call ratio; up move -> put ratio.
- Initial ratio uses 0.50 / 0.40 x2 / 0.10.
- Same-direction reset uses 0.40 / 0.30 x2 / 0.08.
- Reversal uses combined short-leg delta around 1.20–1.30.

These match the supplied transcript's explicit rules.

### 2. Mathematical delta sanity checks
PASS.
For the initial call ratio, signed net delta at target deltas is:
+0.50 - 2(0.40) + 0.10 = -0.20.
For the initial put ratio:
-0.50 + 2(0.40) - 0.10 = +0.20.
For the continuation call ratio:
+0.40 - 2(0.30) + 0.08 = -0.12.
For the continuation put ratio:
-0.40 + 2(0.30) - 0.08 = +0.12.
Directionality is internally consistent.

### 3. Trigger ordering
FAIL / AMBIGUOUS.
The specification currently says a trigger detected from a minute bar can be executed on the same bar. If the trigger is computed from the bar close, same-bar execution is look-ahead unless the data contains a tradeable closing price after the signal is known. The deterministic implementation should detect at bar close and execute at the next available bar open (or explicitly justify a different convention).

### 4. Entry timing
FAIL / AMBIGUOUS.
"Approximately 30–32 calendar days before expiry" is not deterministic. The production baseline must choose exactly one rule (for example, first session on/after 32 DTE at a fixed time), with 30/31/32 DTE as sensitivity variants.

### 5. Exit rule
CONDITIONAL FAIL.
Exiting on the last non-expiry session is a modelling assumption, not a direct hard rule in the source. It is acceptable as a baseline only if explicitly labeled as an implementation assumption and compared with expiry-carry variants.

### 6. Delta calculation
FAIL / INCOMPLETE.
The data-model requirement says delta must be calculated or sourced, but the specification does not yet define:
- pricing model;
- risk-free rate convention;
- forward/dividend treatment;
- implied-volatility fallback when price is zero/missing;
- how to handle deep OTM options with zero volume;
- how delta is computed for puts;
- tolerance when no contract is near the requested delta.

These must be specified before the data gate.

### 7. Fill timing and slippage
FAIL / AMBIGUOUS.
The specification says "nearest available 1-minute bar at or immediately after the decision timestamp." For a bar-close signal, execution needs to be on the next bar, not the signal bar. Slippage also needs an exact formula, not only a qualitative stress description.

### 8. Lot-size mapping
PASS with required precision.
NSE states NIFTY's revised 65 lot applies to the first monthly expiry on 2026-01-27; existing 75-lot weekly/monthly contracts retain 75 through the 2025-12-30 expiry. This must be implemented by contract/expiry, not by a generic calendar date.

### 9. Cost model
FAIL / NEEDS HISTORICAL VERSIONING.
The developer baseline should not assume one current rate. Charges must be date-versioned. Paytm Money public pages currently contain inconsistent legacy FAQ text (Rs 10) versus later pricing communication indicating Rs 20 flat brokerage for new users from Jan 15, 2025. Use Rs 20 as the modern-account baseline, but run Rs 10/Rs 15/Rs 20 sensitivities and clearly state that the actual user's tariff may differ.

### 10. Acceptance criteria
FAIL.
The Gate 1 acceptance statement says "no hidden assumption" but still leaves several modelling assumptions unresolved. Gate 1 should remain failed until the above points are closed.

## Independent recommendations to developer
1. Make entry timing exact.
2. Make signal-detection and execution timestamps explicit.
3. Define Black-Scholes/IV/delta methodology and missing-data fallbacks.
4. Define exact slippage in ticks/points.
5. Version lot size by actual expiry/contract introduction.
6. Version all costs by effective date and expose brokerage sensitivity.
7. Mark expiry-day treatment as an assumption and test it separately.

## Tester instruction to developer
Do not progress to the data/engine gate until this report's FAIL items are resolved and resubmitted for independent review.
