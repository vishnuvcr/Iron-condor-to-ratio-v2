# Phase 3 — Strategy-Fidelity Validation

## Purpose
Validate and backtest **only the strategy specified by the user from the YouTube video**. This phase must not introduce parameter optimization, threshold grids, alternative entry/exit rules, or strategy modifications.

## Fixed strategy rules
- Monthly iron condor: short 0.30-delta call/put; long 0.10-delta call/put.
- Transition when either short IC leg reaches approximately 0.10 delta.
- Falling market: call ratio, +1 0.50Δ / -2 0.40Δ / +1 0.10Δ.
- Rising market: put ratio, +1 0.50Δ / -2 0.40Δ / +1 0.10Δ.
- Continuation when combined absolute delta of the two short ratio legs reaches approximately 0.20; rebuild the same-direction ratio at 0.40/0.30/0.08.
- Reversal when the relevant short-leg delta reaches 1.30; exit and reverse into the opposite initial ratio.
- No return to the iron condor after transition.
- No 32-DTE rule.

## Backtest controls
These are execution/data mechanics, not strategy parameters:
- Use completed-bar information and the next executable observation.
- Apply the repository's explicit brokerage and slippage model to every order.
- Use the validated delta model.
- Do not interpolate, forward-fill, average, or synthesize missing option prices.
- Research-use partial-data results remain clearly labelled as such.

## Validation outputs
- Exact strategy-state transition logs.
- Per-cycle order logs.
- Candidate/coverage status.
- Net/gross P&L and cost decomposition.
- Reproducibility manifest.
- Independent tester review.

## Gate
The strategy cannot be promoted until the tester confirms that the implementation matches the YouTube-defined rules and that no unauthorized strategy rule was introduced.

The previously created reversal-threshold sensitivity workflow/results are **out of scope and non-authoritative**. They must not be used as evidence for strategy performance.

## Phase status
- Unauthorized threshold-sensitivity work: CLOSED / DISCARDED FROM RESEARCH.
- Strategy-fidelity validation: IN PROGRESS.
- Tester approval required before performance conclusions.
