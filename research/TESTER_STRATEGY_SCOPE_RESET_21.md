# Tester Review — Latest Strategy Scope Reset

Date: 2026-10-05
Role: Independent tester
Developer branch reviewed: phase-2-data-developer

## Verdict
**PASS WITH MODELLING-CONVENTION CONDITIONS.**

The developer's revised STRATEGY_SPEC.md correctly removes the 32-DTE constraint and makes the latest user-defined rules authoritative. The initial transcript is explicitly non-authoritative.

## Verified rules
- Initial monthly IC: short 0.30Δ call/put; long 0.10Δ call/put.
- Transition monitors short IC legs only.
- Falling market maps to call ratio.
- Rising market maps to put ratio.
- Initial ratio: +1 0.50Δ, -2 0.40Δ, +1 0.10Δ hedge.
- No return to IC after transition.
- Continuation trigger: combined absolute delta of two short ratio legs ≈ 0.20, followed by same-direction 0.40/0.30/0.08 ratio.
- Reversal: exit and reverse to the opposite initial ratio when the stated 0.80–1.30 short-leg delta condition is reached.
- No 32-DTE rule.
- No look-ahead.

## Conditions before implementation acceptance
1. Initial entry timing is unspecified by the user and must be a documented modelling convention, not claimed as a strategy rule.
2. Exact treatment of the 0.80–1.30 reversal condition must be fixed before production testing. The implementation must not silently reinterpret it as a combined delta unless justified and sensitivity-tested.
3. If both IC short legs reach the trigger on the same completed bar, the direction-selection convention must be deterministic and recorded.
4. Order timing must remain causal: signal from completed bar, execution from the next available executable price.
5. Cost/slippage assumptions must be applied to every order.
6. The production engine must be tested against the revised specification; previous 32-DTE results are invalid for this scope.

## Gate recommendation
**Gate 1 strategy-scope review: PASS.**
**Gate 2 data gate: remains CLOSED.**
The tester does not approve any historical performance result until the data source supports the contracts and timestamps actually required by this strategy.

## Tester instruction to developer
Implement only the revised strategy. Resolve the listed modelling conventions explicitly, add regression tests, then resubmit the implementation for independent tester review before production backtesting.
