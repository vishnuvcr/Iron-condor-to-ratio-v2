# Tester Gate 2 Review 20 — Lead-In Hypothesis Rejected

Date: 2026-10-05
Role: Independent tester

## Verdict

**Gate 2 CLOSED.**

The mandated partition lead-in and deterministic cross-partition deduplication were implemented and all six partition jobs passed. The substantive coverage gate nevertheless remains **0/69 requested calendar months complete**.

The remaining failures are overwhelmingly “does not span deterministic 32-DTE entry to pre-expiry exit”, plus missing calendar months. The lead-in did not materially change this result.

## Conclusion

Partition boundaries are not the principal cause. The current free TradeMarkk expiry files are insufficient for the required lifecycle; its published documentation explicitly describes option coverage as partial. citeturn15search4turn17search14

Upstox's expired-instrument API can provide 1-minute historical expired-contract candles, but the expired-contract API is restricted to Upstox Plus. citeturn18search2turn18search5

## Gate decision

Do not weaken the 32-DTE lifecycle requirement.

A new source must demonstrate full 32-DTE-to-pre-expiry coverage, valid 1-minute OHLCV/OI fields, explicit expiry/timestamp provenance, session continuity, acceptable licensing/access, and independent tester reproduction.

## Developer instruction

Do not backtest on the current composite. Prepare the next source-acquisition path or integrate a user-provided complete dataset while preserving existing provenance.

## Tester instruction

For the next submission, independently verify licensing/access, lifecycle coverage, session continuity, expiry mapping, duplicate resolution, and provenance before reopening Gate 2.

## Review 24 — Post-scope-reset data-gate recheck
Date: 2026-10-05
Developer run reviewed: 37231413691

### Verdict
**FAIL — Gate 2 remains CLOSED.**

### Evidence
- All six partition builds passed.
- Composite assembly passed.
- Current lifecycle coverage check reports 0/69 requested calendar months complete.
- Missing calendar months include 2021-01 through 2021-04, 2022-04 through 2022-10, and 2026-06, 2026-08 and 2026-09.
- Most observed monthly expiry candidates from 2022 onward still do not span the deterministic first-expiry-month-session entry through the final pre-expiry session.
- The failure is source coverage, not partition execution or strategy-code validation.
- No backtest was executed because the workflow correctly stopped at the data gate.

### Scope note
This review applies the latest strategy lifecycle, not the superseded 32-DTE protocol. The required lifecycle is first normal NSE F&O session of the expiry month through the final normal NSE F&O session before expiry.

### Required developer action
Continue source acquisition/validation. Do not relax lifecycle coverage, manufacture missing bars, or publish performance results. A complete admissible historical 1-minute option source or a user-provided equivalent dataset is required before Gate 2 can pass.

### Tester instruction to developer
Keep Gate 2 CLOSED and continue the documented alternative-source search. If no admissible free source can complete the window, escalate only the genuine data-access/licensing blocker; do not convert incomplete data into a strategy result.
## Review 25 — User-directed imperfect-data research tier
Date: 2026-10-05
Developer branch reviewed: phase-2-data-developer

### Verdict
**PASS WITH RESTRICTIONS — research-use partial-data analysis is admissible; strict Gate 2 remains CLOSED.**

### Independent checks
- The developer did not alter the strict coverage criterion.
- A separate research-use path preserves and reports strict coverage failures.
- No interpolation, forward filling, theoretical pricing, or cross-source price averaging was introduced.
- The partial-data entry mode is explicit and defaults to the strict strategy mode in the engine; CI explicitly selects the research-use mode.
- The research-use deviation is recorded in the run manifest and candidate status.
- Scheduled pre-expiry exit remains required.
- Repository documentation now requires disclosure of incomplete-cycle counts and changed entry timing.
- The public TradeMarkk dataset documentation independently confirms approximately 2021–2026 1-minute coverage but warns that option coverage is partial, particularly for illiquid/far strikes.

### Restrictions
1. Research-use output must never be labelled as a fully covered backtest.
2. The strict 0/69 coverage result must accompany research-use results.
3. Final results must quantify the number and percentage of cycles using the partial-data entry convention.
4. Results must include limitations for availability bias, sparse-strike bias, source/provenance bias, and changed entry timing.
5. Production strategy conclusions remain prohibited until strict Gate 2 or a separately justified data-quality gate is passed.

### Tester instruction to developer
Run the research-use CI path. When results are produced, independently inspect candidate-status, data-quality, run-manifest and coverage outputs before accepting any conclusion.

## Tester Review 26 — Research-use execution readiness (2026-10-05)

**Role:** Independent tester. Developer implementation branch was inspected read-only; no developer code was copied into the tester branch.

### Checks performed
1. **Strategy scope:** latest user-defined rules remain the active specification; the obsolete 32-DTE condition is not used as a strategy entry rule.
2. **Strict Gate 2:** remains CLOSED. The latest completed data coverage run reported 0/69 complete deterministic lifecycle months.
3. **Research-use tier:** the developer now has a distinct `entry_mode=available` path that can use the first observed expiry-month session while still requiring the final pre-expiry session. This is an explicit research-use deviation, not a relaxation of strict validation.
4. **No synthetic data:** no interpolation, theoretical option pricing, averaging, or forward-filling was introduced to manufacture missing prices.
5. **Execution causality:** signals are evaluated from observed completed bars and orders use the next executable open convention already documented in the strategy implementation.
6. **Costs:** brokerage and adverse slippage remain part of every order.
7. **Implementation regression:** the new partial-entry regression fixture was corrected after CI identified a test-schema defect; the subsequent CI run passed 38/38 unit tests.
8. **Composite/transfer integrity:** latest run 37232849676 successfully completed composite assembly, coverage check, CSV export, and Parquet↔CSV reconciliation. The strict coverage result remains a failure by design, but research-use continuation is explicitly labelled.
9. **Performance gate:** the backtest is still running in CI. No performance metric, trade count, or profitability conclusion is accepted until the run completes and the resulting `candidate_status.csv`, `trade_summary.csv`, `metrics.json`, and `run_manifest.json` are independently inspected.

### Tester decision
**PASS WITH RESTRICTIONS — implementation and data-transfer prerequisites for research-use execution are acceptable; Gate 2 strict validation remains CLOSED; performance conclusions are NOT YET APPROVED.**

### Required before performance acceptance
- Inspect actual traded-cycle count and partial-entry fraction.
- Verify every reported trade has a complete executable order path and scheduled exit.
- Verify `entry_mode`, brokerage, slippage, reversal threshold, and data provenance in `run_manifest.json`.
- Confirm no result is described as fully covered historical validation.
- Quantify availability bias, sparse-strike/liquidity bias, source bias, and changed entry timing in limitations.
- Require separate reversal sensitivity at 0.80/1.00/1.20/1.30 before robustness conclusions.

**Instructions to developer:** Do not promote performance results or advance to the next research phase until the current backtest artifacts are independently inspected and the tester either passes the performance gate or records a specific remediation. If the run times out, remediate performance without weakening the strategy or data-integrity rules.


## Tester Review 27 — First research-use performance result (2026-10-05)

### Independent result check
CI run **37232849676** completed the backtest successfully after all structural checks passed.

The backtest command explicitly used research-use `--entry-mode available`, brokerage **₹20/order**, and **1 option tick** of adverse slippage.

Observed performance printed by the workflow:
- traded cycles: **28**
- total net P&L: **−₹20,455.46**
- average net P&L: **−₹730.55**
- median net P&L: **−₹433.80**
- win rate: **46.43%**
- profit factor: **0.647**
- maximum drawdown: **−₹41,981.20**
- 5th percentile monthly P&L: **−₹10,542.68**
- 95th percentile monthly P&L: **₹4,464.95**
- return on ₹1 lakh reference capital: **−20.46%**
- annualized monthly Sharpe proxy: **−0.541**

The run considered 65 observed monthly-expiry candidates in the available dataset window, versus 69 requested calendar months. Thus the traded sample is approximately **43.1% of observed expiry candidates** and **40.6% of requested months**.

### Tester interpretation
The baseline research-use implementation **does not demonstrate a profitable edge**. The negative net P&L, profit factor below 1, negative Sharpe proxy, and substantial drawdown all point against promoting the strategy in its current baseline form.

However, this is **not yet a final scientific conclusion**, because the sample is availability-biased and incomplete, the strict Gate 2 remains closed, and reversal-threshold robustness has not yet been run.

### Decision
**PERFORMANCE GATE: HOLD / NOT PASSED FOR STRATEGY PROMOTION.**

Required next step:
1. Run the pre-specified reversal sensitivity grid **0.80 / 1.00 / 1.20 / 1.30** under the same data, costs, and research-use rules.
2. Compare net P&L, profit factor, drawdown, win rate, and traded-cycle count across thresholds.
3. If no threshold produces a robust improvement, document the baseline strategy as unsupported by the available imperfect sample and move to the planned discussion/future-research stage rather than tuning indefinitely.

**Instructions to developer:** Run only the predefined reversal sensitivity grid next. Do not optimize the threshold beyond those four points unless the research plan is formally amended and independently tested. Preserve the negative baseline result and all data-coverage limitations.
