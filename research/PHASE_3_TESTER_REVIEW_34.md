# Phase 3 Tester Review 34 — Corrected Performance Artifact / Coverage-Gate Blocker

Date: 2026-10-05
Role: Independent tester
Developer run: workflow 37252229020
Corrected compact artifact: 11321114236
Developer commit used by run: a5cb95ebf4b2e2a3bae689fa2e935c8e92b20410

## Verdict

**BLOCKED — performance artifact is internally reproducible, but coverage validation is not accepted.**

## Independent numerical verification

The compact artifact independently reproduces:

- 29 traded cycles.
- 628 orders.
- 314 BUY / 314 SELL orders.
- Gross P&L: **+₹8,294.00**.
- Transaction costs: **₹17,085.92**.
- Net P&L: **−₹8,791.92**.
- Win rate: 13/29 = **44.83%**.
- Profit factor: **0.833656**.
- Maximum drawdown: **−₹30,811.11**.
- P05: **−₹5,669.63**.
- P95: **₹4,289.12**.
- Annualized monthly Sharpe proxy: **−0.23854**.
- 66 recorded state transitions.
- 13 continuation rebuilds.
- 24 reversal rebuilds, inferred from 53 total initial_* ratio builds minus 29 original initial ratio builds.
- Slippage audit: removing the one adverse 0.05 tick from every fill gives **+₹10,320 gross before slippage**, so slippage drag is **₹2,026**.

This result is materially different from the superseded 28-cycle run and must replace it only after the remaining audit blocker is fixed.

## Critical blocker — coverage script/API mismatch

The workflow's Check composite coverage diagnostic failed with:

`TypeError: entry_and_exit_dates() missing 1 required positional argument: 'available_dates'`

The strategy entry function was correctly changed to require the previous monthly expiry, but scripts/check_composite_coverage.py still calls the old two-argument form.

The workflow marks this step continue-on-error, so the backtest proceeded. That is acceptable for research-use execution, but the coverage diagnostic itself is not valid evidence.

## Secondary documentation blocker

The generated research_use_data_status.json still describes the old first-session-of-target-expiry-month convention rather than the newly user-defined earliest-post-previous-expiry convention.

The final accepted run must correct this metadata.

## Strategy-fidelity checks

The following remain correct in the corrected implementation:
- fixed reversal threshold remains **1.30 for two short contracts**;
- reversal is evaluated as 2 × individual absolute short-option delta;
- continuation combined delta counts both short contracts;
- initial entry is based on the earliest session after the actual previous monthly expiry;
- no sensitivity grid or optimization was introduced.

## Decision

The corrected performance artifact is **not rejected mathematically**. It is rejected for final research acceptance solely because the coverage audit/metadata still reflect the previous API/convention.

## Tester → Developer

1. Update scripts/check_composite_coverage.py to use the actual previous NIFTY monthly expiry and the new entry_and_exit_dates signature.
2. Update research-use status text to describe earliest-post-previous-expiry entry.
3. Record actual previous-expiry and entry-rule metadata in the run manifest/candidate status.
4. Re-run CI and backtest from the corrected commit.
5. Do not alter the 1.30 two-lot reversal rule or 0.20 two-lot continuation rule.

## Developer → Tester

After remediation, independently verify the new coverage diagnostic, run manifest, candidate dates, 29-cycle arithmetic, reversal/continuation counts, and P&L before accepting the performance gate.