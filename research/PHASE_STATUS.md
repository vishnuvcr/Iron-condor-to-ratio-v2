# Phase Status

| Phase | Status | Gate |
|---|---|---|
| 0 Foundation | COMPLETE | 0 |
| 1 Strategy specification | COMPLETE | 1 |
| 2 Data engineering | COMPLETE WITH RESTRICTIONS; strict Gate 2 CLOSED | 2 |
| 3 Strategy-fidelity/performance validation | COMPLETE WITH RESTRICTIONS | 3 |
| 4 Engine implementation | COMPLETE | 4 |
| 5 Independent tester gate | COMPLETE WITH RESTRICTIONS | 5 |
| 6 Historical research-use backtest | COMPLETE | 6 |
| 7 Robustness/statistics | COMPLETE AS DESCRIPTIVE/RESEARCH-USE ONLY; no parameter tuning authorized | 7 |
| 8 Manuscript | COMPLETE | 8 |

Every phase update must append a dated entry to this file and to the error log where applicable.

## 2026-10-04 update
Phase 2 remains IN PROGRESS. The current 19-expiry sample is explicitly classified as pipeline validation only. Multi-year source expansion and overlap validation are now required before historical performance can be accepted.

## 2026-10-04 update
Phase 2 remains IN PROGRESS. The 2022-2026 rissin expansion failed the continuity gate, and its 15-trade result remains validation-only. Developer remediation now uses the expiry-partitioned 2021-2026 thetrademarkk source, with historical lot-size boundaries corrected. No Gate 2 promotion is permitted until the new run and independent tester review pass.

## 2026-10-04 update
Phase 2 remains IN PROGRESS. The latest successful CI run is not a valid historical backtest: only one cycle traded, and that cycle used incomplete source data ending July 2 for a July 28 expiry. Developer code now rejects such incomplete expiry partitions. Gate 2 remains CLOSED pending a source with defensible 32-DTE-to-expiry coverage and an independent tester review.

## 2026-10-04 — free-source expansion
Phase 2 remains IN PROGRESS. The developer broadened the search to free/public sources. Cloud Trader Pro/Shoonya free NIFTY samples are the first empirical candidate; Zenodo 2017-2020 is an older-period candidate; thetrademarkk and artist-23 remain free Hugging Face candidates; MoneyTicks and public GitHub/API pipelines remain leads. No paid dataset has been purchased or assumed. Gate 2 remains CLOSED until actual files pass cycle-level coverage, quality, provenance, and independent tester checks.

## 2026-10-04 — composite fallback extension
Phase 2 remains IN PROGRESS. A provenance-aware composite dataset path has been added. The composite may replace invalid/missing whole contract-minute rows using exact timestamp+expiry+strike+option-type matches from lower-priority free sources; it may not interpolate, forward-fill, average, or synthesize option prices. The free-source staging workflow now targets monthly thetrademarkk files, Cloud Trader/Shoonya free samples, and optional Zenodo archival data. Gate 2 remains CLOSED until composite cycle coverage and overlap consistency are independently approved.

## 2026-10-04 — composite safeguard review
Developer implemented tester findings F1-F3 from Gate 2 Review 6: expiry provenance is explicit/inferred-tagged, inferred-only cycles are blocked from production expiry discovery, and composite source contribution plus focused loader/provenance tests are recorded. Gate 2 remains CLOSED until fresh CI and independent tester re-review pass.

## 2026-10-04 — disk-backed composite merge
Phase 2 remains IN PROGRESS. The first composite build was too memory-intensive because it concatenated all monthly files in Pandas. Developer replaced it with a sequential DuckDB merge and restored cancellation of superseded code-data CI runs. Gate 2 remains closed pending fresh CI and independent tester review.

## 2026-10-04 — consolidated CSV export
Phase 2 remains IN PROGRESS. Added a deterministic DuckDB export of the validated composite to `results/composite/consolidated_options_data.csv` for Google Drive transfer. CSV promotion remains gated on successful CI and independent tester reconciliation against the Parquet composite.

## 2026-10-04 — Gate 2 Review 9 remediation
Phase 2 remains IN PROGRESS. Independent tester Review 9 identified that coverage was non-blocking, interior date gaps were not checked, and CSV/Parquet reconciliation had not been enforced. Developer remediation now:
1. fails the coverage step when any cycle is incomplete or has missing expected exchange sessions;
2. uses an explicit exchange-calendar dependency for continuity checks;
3. runs a deterministic Parquet-to-CSV reconciliation that verifies schema, row counts, date bounds, and byte-level equivalence to a canonical Parquet-derived CSV;
4. keeps Gate 2 CLOSED until fresh CI succeeds and the tester independently reviews the generated artifacts.


## 2026-10-04 — Gate 2 Review 10 remediation
Phase 2 remains IN PROGRESS. Tester Review 10 found that an entirely missing monthly expiry could escape coverage because the expected set came from observed composite rows. The coverage gate now reads the staged primary-source manifest to derive the expected monthly expiry set and fails any missing cycle. Fresh CI and independent tester re-review are required before Gate 2 promotion.


## 2026-10-04 — Gate 2 Review 11 remediation
Phase 2 remains IN PROGRESS. Tester Review 11 required an NSE-specific session calendar rather than the BSE proxy. Developer added `research/NSE_FNO_HOLIDAYS_2021_2026.csv`, switched continuity validation to that calendar, added tests, and removed the unused exchange-calendars dependency. Fresh CI and independent tester re-review are required before Gate 2 promotion.


## 2026-10-04 — Gate 2 Review 12 confirmation and boundary hardening
Phase 2 remains IN PROGRESS. Tester Review 12 found no mismatch between the stored NSE F&O holiday calendar and the annual NSE circulars checked for 2021–2026. Developer also hardened cycle boundary logic to use the same NSE session calendar and standardized composite row hashes to SHA-256. Gate 2 remains closed pending fresh CI and final tester review.


## 2026-10-04 — CI infrastructure retry
Phase 2 remains IN PROGRESS. Hardened CI run 37225146663 was interrupted by a GitHub-hosted runner shutdown during composite construction after source staging succeeded. No research result was promoted; failed jobs were re-run automatically as attempt 2.


## 2026-10-04 — Gate 2 Review 13 remediation
Phase 2 remains IN PROGRESS. The requested 2021-01 to 2026-09 window contains 69 calendar months, but primary staging selected 64 monthly files. The coverage gate now derives expected months from the requested start/end independently of primary-file presence and records whether a complete month is supplied by the primary source or a fallback composite source. Gate 2 remains closed pending fresh CI and tester review.


## 2026-10-04 — CI ordering improvement
Phase 2 remains IN PROGRESS. Unit tests were moved to immediately after dependency installation so code regressions are rejected before multi-year source staging and composite construction. Gate criteria remain unchanged.


## 2026-10-04 — Gate 2 Review 14 remediation
Phase 2 remains IN PROGRESS. Tester Review 14 found that the latest observed expiry in a fallback-only month could be a weekly expiry. Developer now requires every production candidate expiry—primary or fallback—to be a defensible month-end monthly expiry; an invalid primary file can only be rescued by a valid explicit fallback monthly expiry. Regression tests were added. Fresh CI and independent tester review are required.


## 2026-10-04 — Gate 2 Review 15 remediation
Phase 2 remains IN PROGRESS. Review 15 found a dependency-sensitive expiry dtype failure under Pandas 3.x. The developer branch now normalizes composite expiry values to Python dates before source concatenation and includes a regression test. Fresh CI and independent tester review are required.


## 2026-10-04 — CI test-fixture and diagnostics remediation
Phase 2 remains IN PROGRESS. The 33/34 unit-test result from run 37225959932 was traced to a test fixture, not production strategy code. The fixture and dtype regression coverage were corrected. CI diagnostic recording was also changed from git pushes to artifact uploads to eliminate branch-race failures.


## 2026-10-04 — Gate 2 Review 16 remediation
Phase 2 remains IN PROGRESS. Composite construction was resource-unstable under the previous bulk/in-memory implementation. The primary path is now file-backed DuckDB with sequential monthly-partition ingestion. A separate resolver safeguard excludes weekly-dated primary files from symbol-based expiry inference. Fresh CI and tester review remain required.


## 2026-10-04 — CI timeout remediation
Phase 2 remains IN PROGRESS. The sequential composite build is resource-stable but the hosted runner terminated it at about 4m19s. An explicit 30-minute job timeout has been added; Gate 2 remains closed pending a complete composite build.


## 2026-10-04 — Gate 2 Review 17 remediation
Phase 2 remains IN PROGRESS. Composite construction is now partitioned into six bounded year jobs with independent artifacts, followed by a single assembly job. This preserves the data gate while avoiding a monolithic multi-year build. Fresh CI and tester review are required.


## 2026-10-04 — Gate 2 Review 18 remediation
Phase 2 remains IN PROGRESS. All six partitions built successfully, but coverage could not derive the requested 69-month window because the assembly manifest omitted start/end. The assembly now persists the requested window and partition list. Fresh CI and tester review are required.


## 2026-10-04 — Gate 2 Review 19 remediation
Phase 2 remains IN PROGRESS. Partition boundaries now include the preceding 32-DTE lead-in with margin, and assembly deduplicates overlap deterministically. Gate 2 remains closed until the next coverage report confirms cycle completeness and explicitly reports unresolved 2026 source gaps.


## 2026-10-05 — Gate 2 Review 19
Phase 2 remains IN PROGRESS and Gate 2 CLOSED. Partitioning and assembly are operational. The data-quality gate correctly rejects the current composite because it cannot support the deterministic 32-DTE cycle across the requested 69-month window. Next work is alternative-source acquisition/validation, not strategy relaxation.


## 2026-10-05 — Review 19 remediation
Phase 2 remains IN PROGRESS; Gate 2 CLOSED. Partition lead-ins and deterministic cross-partition deduplication are now implemented. A fresh CI run and independent tester review are required before any further phase transition.


## 2026-10-05 — Gate 2 final blocker
Phase 2 remains IN PROGRESS and Gate 2 CLOSED. The current composite is not admissible for backtesting because no requested month has a complete 32-DTE-to-pre-expiry lifecycle. Do not proceed to strategy results until a complete source is independently validated.


## 2026-10-05 — strategy scope reset
Phase 1 specification is being reset to the latest user-defined strategy only. The initial transcript is non-authoritative, and the 32-DTE constraint is removed entirely. Phase 2 remains IN PROGRESS and Gate 2 remains CLOSED. The existing data work is retained only as infrastructure validation; production testing will be rerun against the corrected strategy specification once the data gate and independent tester approve the reset.

## 2026-10-05 developer update
Latest strategy reset implementation is active. CI run 37230721613 failed at unit tests because one month-start test used an incorrect calendar assumption; the engine itself was not implicated. The test was corrected and the error was logged. Gate 1 remains awaiting tester confirmation of the corrected implementation; Gate 2 remains CLOSED.


## 2026-10-05 — calendar test fixture correction
Phase 1 strategy-scope implementation remains under validation. CI run 37231086646 failed because the regression fixture expected the expiry date as the pre-expiry exit. Developer corrected the fixture to an actual NSE holiday boundary in March 2026. Gate 1 remains pending independent tester review; Gate 2 remains CLOSED and is not reopened by this test fix.


## 2026-10-05 — Gate 1 Review 22 remediation
Phase 1 remains under implementation validation. Independent tester Review 22 rejected implementation acceptance because the reversal condition had been silently fixed at combined short-leg delta 1.20. Developer parameterized and documented 1.20 as a modelling convention within the user-stated 0.80–1.30 range, added validation/tests, and defined the required sensitivity grid. Fresh CI and independent tester re-review are required. Gate 2 remains CLOSED.


## 2026-10-05 — threshold regression test correction
Phase 1 remains under implementation validation. CI run 37231284204 reached 35 passing tests and one fixture failure in the newly added threshold test. The production parameter validation was not implicated; the empty-data fixture was corrected. Fresh CI and tester re-review remain required. Gate 2 remains CLOSED.


## 2026-10-05 — Gate 1 PASS / Gate 2 recheck
Independent tester Review 23 passed the revised strategy implementation after reversal-threshold remediation. CI run 37231413691 passed unit tests and all six partitions, but the current strategy lifecycle coverage check failed at 0/69 requested months. Independent tester Review 24 confirms Gate 2 CLOSED. No performance result was produced. Alternative historical-source acquisition remains the next phase-2 task.


## 2026-10-05 — research-use data tier activated
Per user instruction, Phase 2 now has two clearly separated outcomes: (1) strict Gate 2, which remains CLOSED because full lifecycle coverage is not available; and (2) a research-use partial-data tier that may run the best available real dataset with explicit limitations. No missing prices will be synthesized. The research-use engine can use the first observed expiry-month session when the deterministic month-start session is unavailable, and it will retain the strict coverage failure in the run manifest. Tester approval is required before treating the resulting analysis as a research result.


## 2026-10-05 — Research-use execution remediation
- Phase: 2 — data engineering / exploratory execution.
- Strict Gate 2: CLOSED (full lifecycle coverage still not demonstrated).
- CI run 37232172004: in progress after a prior run was cancelled during composite assembly.
- Code correction: research-use `entry_mode=available` now genuinely permits the first observed expiry-month session when the deterministic first session is unavailable, while still requiring the final pre-expiry session.
- Regression test added for the partial-entry path.
- Additional cleanup: stale 32-DTE coverage output removed; continuation branch now uses the configured 0.20 threshold; diagnostics upload is unconditional.
- No performance conclusion is promoted yet.


## 2026-10-05 — Research-use baseline result
- CI run 37232849676: execution completed successfully through backtest; automatic repository push of the multi-GB result bundle failed with HTTP 500 after creating commit 7a047f5 locally on the runner.
- Backtest artifact 11315040792 preserves the complete result bundle.
- Baseline research-use result: 28 traded cycles; net P&L −₹20,455.46; profit factor 0.647; win rate 46.43%; max drawdown −₹41,981.20; Sharpe proxy −0.541.
- Strict Gate 2: CLOSED; 0/69 deterministic lifecycle months complete.
- Performance gate: NOT PASSED. Next predefined phase is reversal-threshold sensitivity at 0.80, 1.00, 1.20, 1.30.


## 2026-10-05 — Phase 3 robustness started
- New isolated developer branch: `phase-3-robustness-developer`.
- New isolated tester branch: `phase-3-robustness-tester`.
- Tester Review 27 did not pass strategy promotion; it required only the predefined reversal sensitivity grid.
- Phase 3 workflow `.github/workflows/sensitivity.yml` is running thresholds 0.80, 1.00, 1.20 and 1.30 with identical research-use data/cost/slippage assumptions.
- Phase 2 baseline remains frozen and unchanged.


## 2026-10-05 — scientific research expansion
Phase 3 remains IN PROGRESS. A literature review and formal research-methodology document were added. The review identifies volatility/skew, variance-risk-premium, FII positioning, transaction costs and Indian derivatives-market structural changes as explanatory dimensions that must be analysed around the fixed strategy rather than converted into unapproved trading parameters. Research questions and hypotheses are now explicitly recorded. Official NSE sources confirm that option-chain data expose OI, volume, IV, bid/ask and LTP fields and that F&O reports include participant/FII statistics. NSE also documents expiry conventions and tick-size rules, while SEBI reports major index-derivatives framework changes beginning November 2024. These will be treated as regime/structural-break context, not hidden strategy optimization.

## 2026-10-05 — Phase 3 execution status
The six composite partitions and assembly completed successfully in workflow 37234230420. The 1.30 reversal-threshold sensitivity job completed successfully; 0.80, 1.00 and 1.20 remained in progress at the latest status check. No result has been promoted. Independent tester review remains mandatory after the full sensitivity set is available.


## 2026-10-05 — explicit strategy-scope correction
The user ordered that strategy testing must contain **only the strategy given in the YouTube video**. The previously introduced 0.80/1.00/1.20/1.30 reversal-threshold sensitivity grid was unauthorized and is removed from the research plan. The sensitivity workflow was deleted and its results are non-authoritative. Phase 3 is reset to strategy-fidelity validation only. No strategy parameter may be added, optimized, tuned, or sensitivity-tested unless explicitly supplied by the user/video.


## 2026-10-05 — fixed-1.30 execution status
Phase 3 remains IN PROGRESS. The developer branch now treats the reversal as a fixed **1.30 short-leg delta trigger** only. Workflow run `37235922082` has passed unit tests, all six composite partitions, composite assembly, coverage diagnostic execution, consolidated CSV export, and CSV-to-Parquet reconciliation; the fixed-1.30 backtest step is currently executing. No performance conclusion has been promoted and independent tester review remains mandatory.

## 2026-10-05 — workflow-log access error
An attempt to retrieve live logs for workflow job `111535265912` returned GitHub `404 BlobNotFound` while the job was still running. This is an infrastructure/log-access issue, not a strategy or data result. The run remains monitored through workflow/job status APIs; no conclusion is based on unavailable live logs.

## 2026-10-05 — Phase 3 research-use performance conclusion
Tester Review 29 independently verified the fixed-1.30 research-use result from workflow 37237347768. Phase 3 strategy-fidelity and numerical verification are **COMPLETE WITH RESTRICTIONS**. The result is negative: 28 traded cycles, net P&L -₹20,455.46, profit factor 0.6468, max drawdown -₹41,981.20, Sharpe proxy -0.5414. Gross P&L is already negative before costs. Zero 1.30 reversal events occurred; 38 continuation resets occurred. Strategy promotion is rejected. Strict Gate 2 remains CLOSED at 0/69 months. Phase 8 manuscript has been produced and the research stop rule is satisfied.


## 2026-10-05 — Tester Review 30 / doubt audit

Phase 3 numerical output remains **COMPLETE WITH RESTRICTIONS**. Independent recomputation confirms the published 28-cycle result exactly. A zero-slippage reconstruction gives gross P&L of −₹1,871.50 before transaction costs, confirming that the negative direction is not created by the one-tick slippage assumption.

The study remains research-use only because strict lifecycle coverage is **0/69 requested months**. The cost methodology is now explicitly described as a consistent modern retail execution-cost baseline rather than a year-by-year historical broker invoice reconstruction.

No strategy rule changed. Fixed reversal trigger remains **1.30**. Strategy promotion remains prohibited.

## 2026-10-05 — Phase 3 re-opened for reversal-semantics audit

The user reported that manual backtesting was profitable, creating a substantive reconciliation requirement. Code audit found that the published reversal check applies a 1.30 threshold to a single option's absolute delta. With the published Black-76 implementation and rate=0.0, an individual option absolute delta is bounded by 1.00; therefore the reversal branch is unreachable in the actual backtest. The prior zero-reversal count is consequently not a valid empirical finding about market reversals.

Phase 3 performance acceptance is therefore **REOPENED / BLOCKED** for strategy-fidelity review. The existing negative 28-cycle result is treated as a provisional arithmetic result of the stored implementation, not as a trustworthy replication of the YouTube strategy. Gate 2 remains CLOSED. No strategy-code interpretation or new threshold will be introduced until the reversal semantics are resolved from the authoritative source and independently tester-reviewed.

## 2026-10-05 — reversal/entry clarification implementation

The user clarified that the reversal trigger of 1.30 applies to the **two-lot short leg**, so reversal occurs when 2 × the individual short-option absolute delta reaches 1.30. The user also instructed that the initial Iron Condor be entered as early as possible after the previous monthly expiry.

Developer corrected:
- reversal calculation to 2 × individual short delta;
- continuation combined-delta calculation to count both short contracts;
- entry timing to the earliest normal NSE F&O session after the previous monthly expiry.

All previous performance outputs based on the single-leg 1.30 interpretation and first-target-month entry convention are **superseded**. Phase 3 remains blocked pending tester review of these corrections. Strict Gate 2 remains CLOSED.

## 2026-10-05 — Review 34 remediation applied

Developer corrected the coverage validator to use the actual previous NIFTY monthly expiry and the earliest-post-previous-expiry entry convention. Research-use metadata wording was corrected, and fresh run manifests/candidate status will record previous monthly expiry plus entry/exit dates. No strategy rule, threshold, or execution economics were changed.


## 2026-10-05 — Tester Review 35 / clean corrected run accepted with restrictions

Workflow 37253416839 completed successfully across unit tests, six partition builds, composite assembly, coverage validation, consolidated CSV export, CSV/Parquet reconciliation, backtest, and result publication. Independent Tester Review 35 on the isolated tester branch passed the corrected arithmetic and audit layer WITH RESTRICTIONS.

Verified research-use metrics:
- 29 traded cycles; 628 orders; 314 BUY / 314 SELL.
- Gross P&L +₹8,294.00; costs ₹17,085.92; net P&L −₹8,791.92.
- Win rate 44.83%; profit factor 0.833656.
- Maximum drawdown −₹30,811.11; P05 −₹5,669.63; P95 ₹4,289.12; annualized monthly Sharpe proxy −0.23854.
- 66 state transitions; 13 continuation rebuilds; 24 reversal rebuilds.
- Order-log arithmetic independently reconstructs ₹1,900 of one-tick slippage drag (760 absolute lots × ₹0.05 × 50).

Strict Gate 2 remains CLOSED: requested months 69, strict complete cycles 0. The result is research-use partial-data evidence only and must not be promoted to live trading. No strategy parameter, optimization, sensitivity grid, or alternate threshold was introduced.

## 2026-10-05 — Tester Review 37 / falsification blocker

Independent Tester Review 37 blocked performance acceptance. The compact artifact is internally reproducible, but the tester found **2 malformed initial ratio builds out of 53** in which the 0.50-delta long and 0.40-delta short used the same option contract: CE 15700 for 2021-07-29 and CE 26100 for 2025-11-25. The current selector chooses each target independently and does not enforce distinct contract identities.

The affected cycles contribute approximately +₹4,742.99 net to the current result. This does not explain the user's doubt by itself, but it means the −₹8,791.92 result is not yet a faithful implementation result.

**Performance acceptance is BLOCKED. Strict Gate 2 remains CLOSED. The current result is PROVISIONAL.** Developer remediation must reject malformed ratio construction without changing strategy parameters, rerun the workflow, and obtain a new independent tester report.