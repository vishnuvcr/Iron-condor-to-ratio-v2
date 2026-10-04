# Phase 3 Tester Review 28 — Fixed 1.30 Strategy-Fidelity Gate

Date: 2026-10-05
Role: Independent tester
Developer code reviewed: commit 316d3d3bf83600294f98604507941f434bd72ecd
Developer documentation head reviewed: phase-3-robustness-developer

## Verdict

**PASS WITH RESTRICTIONS — strategy implementation is faithful to the fixed 1.30 reversal rule; performance gate remains HOLD.**

The developer implementation now matches the user's corrected strategy scope. No reversal-threshold sensitivity grid is present in the active workflow directory, and the backtest code uses a fixed 1.30 short-leg-delta trigger.

## Independent checks

### 1. Reversal trigger
The developer code evaluates the two active ratio short legs and sets:
`reversal_trigger = any(float(d) >= 1.30 for d in short_deltas)`

This is the required fixed **1.30 short-leg delta** trigger. No 0.80–1.30 range and no combined-delta reversal threshold is used in the active implementation.

### 2. Direction reversal
On reversal, the current direction is switched:
- CALL_RATIO -> PUT_RATIO
- PUT_RATIO -> CALL_RATIO

The replacement uses the initial directional ratio construction.

### 3. Initial directional ratio
The initial ratio selector uses:
- +1 0.50-delta option
- -2 0.40-delta options
- +1 0.10-delta hedge

This matches the supplied strategy.

### 4. Continuation
The continuation selector uses:
- combined absolute delta of the two short legs <= 0.20
- same-direction rebuild at 0.40 / 0.30 / 0.08

This matches the supplied approximately-0.20 continuation rule.

### 5. Iron-condor transition
The trigger monitors only short IC positions. The short call/put delta reaching the approximately 0.10 trigger determines the breakout side and corresponding directional ratio.

### 6. Execution and look-ahead
New positions and transition exits use the next common executable bar open for all required legs. Signal evaluation is based on completed observations before that fill.

The pre-expiry scheduled exit is implemented at the documented 15:20 timestamp using the available bar close. This is an execution convention that must remain explicitly disclosed; it is not a new strategy signal.

### 7. Costs and slippage
The implementation applies:
- Paytm Money brokerage assumption;
- adverse one-tick slippage;
- exchange charges;
- SEBI turnover fee;
- GST;
- option STT by trade date;
- stamp duty on buys.

The current research run therefore includes explicit transaction-cost drag.

### 8. Research-use data policy
The strict strategy entry mode remains the default. The CI run explicitly selects research-use `entry_mode=available`, which permits the first observed expiry-month session when the strict first session is absent while retaining a mandatory pre-expiry exit. The manifest records the deviation.

### 9. CI execution
Workflow run 37235922082 has passed:
- unit tests;
- all six data partitions;
- composite assembly;
- coverage diagnostic execution;
- consolidated CSV export;
- CSV/Parquet reconciliation;
- the fixed-1.30 backtest step.

The large backtest-results artifact uploaded successfully.

## Tester restrictions

1. No strategy promotion is permitted yet because the independent tester has not verified the numerical performance output.
2. The 4.7 GB result artifact exceeds the connector's 512 MB download limit, so the exact `metrics.json`, trade summary, and compact run manifest have not yet been independently inspected.
3. The developer test suite currently has no explicit unit test whose assertion is specifically tied to the fixed 1.30 reversal threshold. This is a test-coverage gap, not evidence that the production logic is wrong.
4. Strict lifecycle coverage remains CLOSED; the current research-use result must remain labelled partial-data/exploratory.

## Required developer remediation

- Publish a compact, independently readable metrics output from the completed run (for example `results/metrics.json` plus `trade_summary.csv` and `run_manifest.json`) without requiring transfer of the 4.7 GB artifact.
- Add a regression test that verifies the reversal branch is fixed at 1.30 and that no alternate reversal parameter is exposed.
- Do not change the strategy, tune thresholds, run sensitivity grids, or introduce new trading rules.
- Resubmit the compact numerical outputs for independent tester verification.

## Gate decision

**Strategy-fidelity gate: PASS WITH RESTRICTIONS.**

**Performance gate: HOLD.**

No performance conclusion or strategy promotion is authorized until the tester independently verifies the numerical outputs and cost/transition accounting.

## Developer instruction

Implement only the compact-output/test-coverage remediation above. Do not alter strategy rules.

## Tester instruction

After remediation, independently recompute/check the reported metrics, trade-count reconciliation, cost totals, drawdown and P&L arithmetic, and confirm that the fixed 1.30 rule is unchanged.
