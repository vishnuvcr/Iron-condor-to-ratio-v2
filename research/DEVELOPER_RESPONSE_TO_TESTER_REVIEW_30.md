# Developer Response to Tester Review 30

Date: 2026-10-05

## Accepted findings

The developer accepts the tester's independent arithmetic verification and the research-validity restriction.

1. The published 28-cycle numerical result is reproducible from the compact trade/order outputs.
2. The order lifecycle reconciles to 620 orders and 66 transitions.
3. The fixed 1.30 reversal rule is present; zero reversal events were observed.
4. Strict lifecycle coverage is 0/69 requested months and remains CLOSED.
5. Reversing the one-tick fill adjustment produces gross P&L of -₹1,871.50 before slippage and transaction costs.

## Remediation

The cost methodology has been clarified rather than silently leaving a false historical-rate claim in the manuscript.

The published run is now explicitly described as using a consistent modern retail execution-cost baseline:
- Paytm Money brokerage assumption: ₹20/order;
- current NSE equity-options transaction baseline: ₹3,553/crore;
- applicable statutory rates as documented in research/COST_MODEL.md;
- one adverse ₹0.05 tick per executed order.

This is a research execution-cost assumption applied consistently to the historical price path. It is not represented as an exact year-by-year historical Paytm Money invoice reconstruction.

No strategy rule was changed. The reversal trigger remains fixed at 1.30.

## Research conclusion after audit

The negative result is arithmetically trustworthy for the observed 28-cycle research-use sample and remains not suitable for live promotion.

The strongest additional finding is:

**Even with the one-tick slippage removed, gross P&L remains negative at -₹1,871.50 before transaction costs.**

Therefore the negative direction is not an artifact of brokerage or the one-tick slippage assumption.

The primary unresolved limitation is data completeness, not arithmetic.

## Gate status

- Strict Gate 2: CLOSED.
- Phase 3: COMPLETE WITH RESTRICTIONS.
- Strategy promotion: REJECTED.
- Fixed reversal threshold: 1.30.
- Parameter optimization/sensitivity: NOT performed and remains unauthorized.

## Developer → Tester

Re-check only the updated cost-model wording, manuscript statements, README status, and gate status. Confirm that no strategy rule or threshold was changed.
