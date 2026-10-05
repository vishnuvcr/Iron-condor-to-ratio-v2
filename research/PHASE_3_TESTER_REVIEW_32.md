# Phase 3 Tester Review 32 — Reversal Semantics / Manual-vs-Automated Reconciliation Blocker

Date: 2026-10-05
Role: Independent tester
Reviewed developer branch: `phase-3-robustness-developer`
Reviewed published backtest code/result lineage: run code commit `279790ce4d65c66d550e34114fb84c059f8eccb0`

## Verdict

**FAIL — STRATEGY-FIDELITY GATE BLOCKED.**

The arithmetic of the stored result may still be internally reproducible, but the implementation does not currently provide a credible empirical test of the stated fixed 1.30 reversal rule.

## Finding 1 — 1.30 is applied to one option's delta

The backtest function `ratio_reversal_trigger(short_deltas)` returns true only when an individual active short delta satisfies `d >= 1.30`.

The delta engine computes ordinary Black-76 option deltas. With the published run rate of 0.0, call delta is `N(d1)` and put delta is `-N(-d1)`; therefore each individual absolute delta is bounded by 1.00.

**Consequence:** the reversal branch is unreachable for genuine model-generated deltas. The recorded zero reversal events cannot be interpreted as an observed market property.

## Finding 2 — Unit test does not test real reachability

The unit test asserts that `ratio_reversal_trigger([1.30, 0.05])` returns true. This tests the helper with an arbitrary synthetic input, not whether the production delta model can generate such a value. No regression test currently prevents an impossible single-leg 1.30 threshold from being used in production.

## Finding 3 — Strategy meaning remains unresolved

The user's latest instruction establishes the reversal number as **1.30**, but the repository does not independently establish whether 1.30 refers to one leg or an aggregate quantity. An aggregate interpretation must not be invented by the tester or developer. The authoritative video/source must settle the semantics before any code change.

## Finding 4 — Execution-convention reconciliation is also required

The current backtest uses deterministic modelling conventions not explicitly contained in the video, including first observed expiry-month entry in research-use mode, next available common open for multi-leg execution, one-tick adverse slippage, and a pre-expiry scheduled exit. These may be legitimate research conventions, but they must be reconciled against the user's profitable manual backtest before attributing the performance difference to the strategy itself.

## Decision

- Do **not** accept the current negative P&L as a faithful replication result.
- Do **not** change 1.30 to another threshold or silently convert it to a combined delta.
- Keep Strict Gate 2 CLOSED.
- Keep the developer/tester branch separation intact.
- Require a source-accurate reversal definition and a trade-by-trade manual-vs-automated reconciliation before re-running performance.
- The previously stored arithmetic result remains an auditable result of the stored implementation, but it is **not an accepted strategy conclusion**.

## Tester → Developer

Resolve the reversal-semantic ambiguity from the authoritative source, document the exact definition, add a reachability test for the production delta path, and then resubmit for independent tester review. Do not optimize or introduce any new threshold.

## Developer → Tester

On resubmission, independently verify the exact source wording/meaning, the production delta range, reversal trigger implementation, and a matched manual-vs-automated trade sample before reopening the performance gate.
