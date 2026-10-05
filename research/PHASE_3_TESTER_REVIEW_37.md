# Phase 3 Tester Review 37 — Falsification Audit

Date: 2026-10-05
Role: Independent tester
Audit target: clean workflow 37253416839 / compact artifact 11321234763

## Verdict

**BLOCKED — the clean result cannot yet be accepted as a faithful strategy backtest.**

This audit was performed from the compact order/trade artifacts and independently derived invariants, rather than trusting `metrics.json`.

## Finding 1 — malformed ratio construction

The strategy requires a directional ratio with:
- 1 × 0.50-delta long option;
- 2 × 0.40-delta short option;
- 1 × 0.10-delta hedge.

The automated selector independently produced **2 malformed initial ratio builds out of 53** where the 0.50-delta long and 0.40-delta short used the **same strike and option type**:

1. 2021-07-29 expiry: CE 15700 used for both initial_long and initial_short.
2. 2025-11-25 expiry: CE 26100 used for both initial_long and initial_short.

The corresponding order log shows simultaneous long and short positions in the same contract. That means the simulated structure is not the intended distinct-strike 1:-2:+1 ratio for those builds.

The developer implementation currently selects each target independently in `select_contract()` and does not enforce distinct contract identities across ratio legs.

## Finding 2 — material acceptance consequence

The two affected cycles have net P&L:
- 2021-07-29: +₹2,052.26
- 2025-11-25: +₹2,690.73

They contribute approximately **+₹4,742.99** to the reported −₹8,791.92 net result.

Simply excluding these malformed cycles would change the sample result to approximately **−₹13,534.92**, before any corrected replacement selection. Therefore this finding does not explain the user's suspicion by itself, but it proves that the published result is not yet a valid implementation of the exact ratio structure.

## Other independent checks

- 628 orders reconcile exactly to the stored 29-cycle trade summary.
- 314 BUY / 314 SELL.
- 760 absolute lots.
- One-tick slippage arithmetic: ₹1,900.
- Every traded cycle has four IC-to-ratio closing orders and three scheduled-exit orders.
- The compact order/trade arithmetic is internally reproducible.
- Strict lifecycle coverage remains 0/69.

## Required developer remediation

1. Do **not** change the strategy parameters.
2. Enforce contract-identity validity for every ratio build.
3. Do not silently substitute a different strike merely to improve the result.
4. If the requested delta targets cannot be represented by distinct available contracts at the signal timestamp, record the lifecycle as unavailable/invalid rather than inventing a new selection rule.
5. Add an independent regression test proving that a ratio build cannot contain the same option contract as both long and short legs.
6. Re-run the complete clean workflow.
7. Re-run the independent tester falsification audit on the new artifact.
8. Reconcile the changed cycle count, order count, P&L, costs, transitions and coverage before any conclusion.

## Gate decision

**Performance acceptance: BLOCKED.**  
**Strict Gate 2: CLOSED.**  
**Current −₹8,791.92 result: PROVISIONAL / NOT ACCEPTED.**

## Tester → Developer

Fix the ratio-contract identity validation without changing any user-specified strategy rule, rerun the clean workflow, and submit the new compact artifact for independent falsification. Do not promote the current result or manuscript conclusion until Review 38 passes.
