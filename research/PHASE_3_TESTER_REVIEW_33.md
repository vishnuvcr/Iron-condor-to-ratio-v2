# Phase 3 Tester Review 33 — User-Clarified Two-Lot Reversal and Early Entry

Date: 2026-10-05
Role: Independent tester
Developer branch reviewed: `phase-3-robustness-developer`
Reviewed implementation commits:
- `2f4b01dcacf8bdbe05229bb8c622a50bdfdafbbe` — backtest corrections
- `4e95c7d3e912bb18ce26bea261a17cfcbd9e31aa` — initial test correction
- `de74e53c106115d14f109149ad4c5b8d0616a61e` — test restoration
- `e79254434dd9c87dc066d10cd18aff390b77f43b` — calendar helper
- `c6323d31cd980f6f027f9593086ee1887db62a80` — main-loop previous-expiry correction
- `a5cb95ebf4b2e2a3bae689fa2e935c8e92b20410` — calendar tests

## Verdict

**PASS WITH RESTRICTIONS — strategy semantics correction accepted; performance rerun may proceed after CI validation.**

## Independent checks

### 1. Reversal arithmetic

The user clarification is implemented as:

`2 × individual short-option absolute delta >= 1.30`

Therefore the individual short-option trigger is 0.65.

The production helper now evaluates `2.0 * d >= 1.30`. The unit test checks:
- 0.649 -> no reversal
- 0.650 -> reversal
- 0.700 -> reversal

This resolves the prior impossible single-option 1.30 implementation without changing the user-specified threshold.

### 2. Continuation arithmetic

The ratio contains 2 short contracts. The previous implementation used only the option object's delta in the combined-delta test even though the strategy specifies the combined delta of the two short legs.

The corrected implementation calculates:

`sum(abs(short_lots) × individual_abs_delta)`

Thus two short contracts at individual delta 0.10 produce combined absolute delta 0.20. This is faithful to the stated rule and is not a new strategy parameter.

### 3. Entry timing

The user clarified that the initial Iron Condor should be entered as early as possible after the previous monthly expiry.

The developer now:
- derives the actual previous NIFTY monthly expiry from the calendar, rather than using the previous observed dataset expiry;
- requires the earliest normal NSE F&O session after that expiry for strict mode;
- uses the earliest observed post-expiry session only in explicitly labelled research-use partial mode;
- starts delta selection from the first available market minute after the 09:15 open and uses the next common executable bar, avoiding look-ahead.

This is materially closer to the user's stated timing than the previous first-session-of-target-month convention.

NSE's June 25, 2025 circular revised NIFTY monthly expiry from the last Thursday to the last Tuesday for expiries from September 2025 onward; the developer calendar helper reflects that transition. Official NSE contract specifications likewise identify Tuesday as the current NIFTY expiry day.

### 4. Calendar implementation

The new helper uses:
- last Thursday through the August 2025 expiry;
- last Tuesday from September 2025 onward;
- previous trading session when expiry falls on an NSE F&O holiday.

Tests cover July 2026 / June 2026 and September 2025 / August 2025 boundary examples.

### 5. Scope fidelity

- Fixed 1.30 remains unchanged.
- No threshold sensitivity was reintroduced.
- No optimization was introduced.
- No combined-delta interpretation was added beyond the user's explicit clarification that the 1.30 is for two short lots.
- The earlier negative performance result remains superseded.

## Restrictions before performance acceptance

1. CI/unit tests must pass on the corrected developer branch.
2. A fresh fixed-strategy backtest must be run from the corrected code; all prior 28-cycle metrics are superseded.
3. The new run manifest must record the actual previous monthly expiry and entry-date convention.
4. Manual-vs-automated reconciliation should use the user's manual trade examples where available. The tester will not assume the new result is correct merely because CI passes.
5. Strict Gate 2 remains CLOSED; research-use partial data must remain explicitly labelled.

## Tester → Developer

Run the corrected CI and a fresh fixed-strategy research-use backtest only after CI passes. Do not reuse the prior result files as current performance evidence. Preserve the fixed 1.30 two-lot rule and the earliest-post-previous-expiry entry convention.

## Developer → Tester

After the fresh run, independently verify the new order log, lifecycle transitions, reversal/continuation trigger calculations, entry dates, and headline P&L before any performance conclusion is promoted.
