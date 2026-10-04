# Tester Report — Gate 2 Data/Implementation Review

Reviewer role: Independent tester
Reviewed branch: phase-2-data-developer
Gate result: **FAIL — implementation fixes required**

## Automated-run finding
The first GitHub Actions run (Run 37211955857) failed at the unit-test step, so no production backtest result is accepted.

## Independent implementation findings

### Critical 1 — exit fills are timestamp-inconsistent
The close-position logic finds a next-open timestamp separately for each leg, then uses the maximum timestamp but keeps each leg's earlier price. This reports fills at a timestamp different from the price actually used.
Required fix: determine a common execution timestamp first, then retrieve each contract's executable price at that exact timestamp. If a contract is unavailable, the adjustment must be marked unfilled/rejected rather than mixing timestamps.

### Critical 2 — first monthly cycle can violate the 32-DTE rule
The pipeline only downloads 2025 and 2026 files, but the first 2025 monthly expiry needs December 2024 data to satisfy the 32-calendar-day entry rule. Without 2024 data, the first cycle can silently choose an artificially late entry date.
Required fix: include the 2024 NIFTY intraday partition and explicitly exclude any cycle whose true 32-DTE entry window is not covered.

### Critical 3 — unit-test failure blocks the gate
The test workflow failed before backtest execution. Fix the import/test environment and reproduce the same test suite locally/CI before rerunning.

### High 4 — execution availability is not fully logged
A missing next-open bar can cause a cycle to be returned as None without a structured reason. Log skipped cycles, missing legs, incomplete adjustment fills, and anomaly reasons.

### High 5 — forward/IV numerical validation is missing
The Black-76 Newton solver is not independently cross-checked. Require a sample-level comparison against a bracketed/root-solver implementation and report convergence/error statistics.

### High 6 — data-quality checks are incomplete
The pipeline checks duplicates but does not yet enforce expected 1-minute cadence by session, timezone normalization, non-negative volume, monotonic timestamps by contract, expiry consistency, selected four-leg IC coverage, or replacement-contract coverage.

### Medium 7 — dataset provenance
The HF dataset is a public assembly of NSE daily data and Upstox intraday candles. The run manifest must retain dataset revision/commit identifier, retrieval date, file names, and schema hash so the run is reproducible.

## Gate decision
**Do not proceed to production backtest or Gate 3.**

## Tester instruction to developer
Fix all Critical and High findings, make the workflow green through unit tests, then resubmit Phase 2 for independent review. Do not alter the tester branch implementation.