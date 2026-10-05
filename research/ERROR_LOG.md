# Error Log

| Date | Phase | Severity | Error / issue | Resolution |
|---|---|---|---|---|
| 2026-10-04 | 0 | INFO | Repository was empty when initialized; no pre-existing research files were available to inherit. | Created baseline research structure from the project protocol. |
| 2026-10-04 | 0 | INFO | Video rules include discretionary language (early exit and delayed adjustment) in addition to numeric delta triggers. | Preserve ambiguity explicitly; create deterministic baseline plus sensitivity variants before production backtest. |

| 2026-10-04 | 2 | ERROR | First GitHub Actions run 37211955857 failed at unit tests; production backtest was blocked. | Fix test environment before rerun. |
| 2026-10-04 | 2 | ERROR | 2025 monthly entry coverage was incomplete without December 2024 intraday data. | Add 2024 partition and reject uncovered cycles. |
| 2026-10-04 | 2 | ERROR | Exit-fill logic mixed timestamps with prices from earlier bars. | Redesign common fill timestamp logic. |
| 2026-10-04 | 2 | ERROR | IC trigger logic keyed deltas only by option type, so the 0.10-delta hedge could overwrite the 0.30-delta short leg. | Changed trigger monitoring to use short positions only; removed dead selection loop. |
| 2026-10-04 | 2 | ERROR | Black-76 function named implied_vol_black76 returned delta instead of implied volatility, causing the regression test to interpret 0.5114 as IV. | Split IV solver from price-to-delta conversion and added regression tests. |
| 2026-10-04 | 2 | ERROR | Full backtest failed after unit tests passed; the initial workflow did not capture backtest stdout/stderr. | Hardened workflow to tee backtest output into a committed diagnostic file on failure. |
| 2026-10-04 | 2 | INFO | A second semantic issue was found in IC trigger monitoring: both short and long legs share option_type keys. | Added a deterministic choose_ic_trigger helper and short-leg-only state tracking. |
| 2026-10-04 | 2 | ERROR | Canonical full backtest failed because dataset timestamps were timezone-aware while expiry/decision timestamps were naive. | Normalize data timestamps to IST and construct all expiry/entry/exit decision timestamps as Asia/Kolkata-aware. |
| 2026-10-04 | 2 | ERROR | First timezone patch missed a duplicate naive expiry expression later in add_forward_and_delta; run 37212653706 failed in the same arithmetic. | Removed the duplicate expression and added a timezone regression test. |
| 2026-10-04 | 2 | ERROR | The speed optimization globally removed strikes outside 85%-115% of forward before the cycle simulation, which can delete held legs from delta tracking as the market moves. | Reverted global filtering; apply the 15% window only when selecting a new target strike, while computing deltas for held legs across the available chain. |
| 2026-10-04 | 2 | PERF | Full-chain IV/delta calculation was unnecessarily slow and coupled to strike filtering. | Refactored to compute forward per timestamp and IV/delta only for candidate/held contracts, retaining full chain rows for held-leg triggers. |
| 2026-10-04 | 2 | ERROR | Successful data pipeline run produced no trades because build_ratio referenced undefined local rate; all 19 cycles recorded NameError. | Pass rate explicitly through build_ratio and both ratio-building call sites; added signature regression test. |
| 2026-10-04 | 2 | ERROR | Historical sample was only 19 monthly expiries because the current pipeline was limited to 2024–2026 source partitions; this is inadequate as a final research sample. | Added multi-source historical expansion assessment; final backtest will use the longest independently validated continuous window. |
| 2026-10-04 | 2 | ERROR | Provenance helper references hashlib while the current script snapshot lacks the import; CI must validate this before Gate 2. | Flagged for automated verification and correction before tester approval. |
| 2026-10-04 | 2 | ERROR | Expanded rissin source declared 2022-2026 partitions but the actual run produced only one 2022 expiry with 15 rows and no 2023 expiries; continuity was not demonstrated. | Replaced the primary Phase-2 source with the expiry-partitioned thetrademarkk NIFTY 1-minute dataset covering 2021-2026; retain rissin for independent overlap validation. |
| 2026-10-04 | 2 | ERROR | Historical NIFTY lot-size function incorrectly treated all expiries through Nov-2024 as 25, which is inconsistent with NSE's 50-lot regime before the May-2024 revision. | Added 2021-2026 expiry-boundary regimes and regression tests. |
| 2026-10-04 | 2 | ERROR | Thetrademarkk expiry partitions can end weeks before expiry; the prior engine treated the last available date as the cycle exit, producing an invalid shortened July-2026 trade. | Changed entry/exit validation to require the 32-DTE entry window and data through the final pre-expiry session; incomplete partitions are now rejected. |
| 2026-10-04 | 2 | TEST ERROR | New expiry-coverage regression test expected 2026-06-29 even though 2026-06-26 is the first date on/after the 32-DTE target for a 2026-07-28 expiry. | Corrected the fixture; no production-code change was required. |
| 2026-10-04 | 2 | RESEARCH TOOL LIMITATION | Zenodo exposes the 311.9 MB NIFTY options ZIP publicly, but the web/file tooling could not download the large binary directly; this is an access limitation, not evidence that the dataset is unavailable. | Record the public DOI/MD5 metadata and validate the archive through a GitHub Actions download/cache step when implementing the free-source harness. |
| 2026-10-04 | 2 | TESTER FINDING | Composite fallback initially allowed expiry to be inferred from the last observed timestamp without explicit provenance. | Added expiry_source tracking and blocked inferred-only composite cycles from production expiry discovery. Added source-contribution coverage and composite loader tests. |
| 2026-10-04 | 2 | RESEARCH TOOL LIMITATION | Container could not resolve github.com for a local clone, so local pytest could not be executed outside GitHub Actions. | Use the repository's automated GitHub Actions environment as the executable test runner; keep the limitation documented. |
| 2026-10-04 | 2 | CI ERROR | Workflow run 37221737875 failed during Install because requirements.txt temporarily contained literal escape characters instead of real newlines. | Corrected requirements.txt and added subsequent CI validation; no production result was accepted from the failed run. |
| 2026-10-04 | 2 | TEST ERROR | Composite unit tests failed in source_row_hash generation because Pandas row-wise join still encountered numeric objects despite an astype(str) conversion. | Replaced hashing with explicit per-cell map(str) conversion and added a mixed-type regression test. |
| 2026-10-04 | 2 | DATA INTEGRITY | Composite normalization initially parsed naive Date+Time fields with utc=True, which would shift local IST source times by 5:30 hours when converted back to IST. | Changed timestamp parsing to localize naive timestamps directly to Asia/Kolkata and added an exact-time regression test. |
| 2026-10-04 | 2 | CI ERROR | Composite coverage checker failed after building the dataset because expiry was a datetime.date and code called .date() on it. | Removed the redundant date() call and added rissin as a free exact-key fallback source after Cloud Trader sample download failed in CI. |
| 2026-10-04 | 2 | DATA INTEGRITY | Composite timestamp normalization required explicit handling of naïve Date+Time fields as IST. | Production code now localizes naïve timestamps to Asia/Kolkata and converts only already timezone-aware timestamps. |
| 2026-10-04 | 2 | TESTER FINDING | Gate 2 Review 9 found that cycle coverage did not fail CI, interior session gaps were not checked, and CSV/Parquet reconciliation had not yet been enforced. | Developer added an enforcing coverage step, exchange-calendar session continuity checks, a deterministic CSV/Parquet reconciliation script, and workflow reporting. |
| 2026-10-04 | 2 | RESEARCH TOOL LIMITATION | GitHub connector returned HTTP 404 when retrieving live workflow-job logs while run 37224425114 was in progress. | No research result was inferred from the failed log request; rely on the workflow status/artifacts after completion. |

| 2026-10-04 | 2 | DOC ERROR | README CSV link initially used ../results from a root-level README. | Corrected to results/composite/consolidated_options_data.csv; no research-data effect. |

| 2026-10-04 | 2 | TESTER FINDING | Gate 2 Review 10 found that deriving expected expiries from observed composite rows allowed an entirely missing monthly expiry to escape the coverage gate. | Coverage checker now derives expected monthly expiries from the staged primary-source manifest and fails any missing expected cycle. |

| 2026-10-04 | 2 | TESTER FINDING | Gate 2 Review 11 found that the continuity checker used the XBSE BSE calendar for an NSE F&O study. | Replaced the BSE proxy with a versioned NSE F&O holiday calendar from annual NSE F&O trading-holiday circulars for 2021–2026; added calendar unit tests and removed the unused exchange-calendars dependency. |
| 2026-10-04 | 2 | TEST TOOLING | Local synthetic testing initially could not import duckdb in the analysis sandbox; no repository code or files were modified by that failed attempt. | Retried the independent expected-expiry logic without duckdb and verified that a deliberately missing monthly expiry is detected; full repository tests remain delegated to GitHub Actions. |

| 2026-10-04 | 2 | TESTER CONFIRMATION | Gate 2 Review 12 independently matched the versioned 2021–2026 NSE F&O holiday file to the annual NSE F&O circulars; no calendar-date mismatch found. | Keep Gate 2 pending until CI and final artifact checks pass. |
| 2026-10-04 | 2 | DATA INTEGRITY | The cycle boundary helper used a fixed three-calendar-day tolerance and could reject a valid Friday-to-Tuesday cycle when Monday was an NSE holiday; it also rejected a 32-DTE target that itself fell on a holiday. | Reworked cycle boundaries to use the versioned NSE F&O session calendar and added boundary regression tests. |
| 2026-10-04 | 2 | PROVENANCE | Primary DuckDB composite rows used MD5 while normalized fallback rows used SHA-256 for source_row_hash. | Standardized the primary DuckDB path to SHA-256; fallback rows already used SHA-256. |

| 2026-10-04 | 2 | CI INFRASTRUCTURE | Hardened CI run 37225146663 staged all 64 primary monthly files and began the composite build, then the GitHub-hosted runner received a shutdown signal and exited 143. | No research output from that run was promoted. Failed jobs were automatically re-run as attempt 2. |

| 2026-10-04 | 2 | TESTER FINDING | Gate 2 Review 13 found the requested 2021-01 to 2026-09 window contains 69 calendar months while primary staging selected only 64 monthly files. | Coverage gate now derives requested months independently from the staging start/end range; a month may pass only if a defensible composite monthly-expiry candidate is present. |

| 2026-10-04 | 2 | TESTER FINDING | Gate 2 Review 14 found that a fallback-only calendar month could be satisfied by a weekly expiry because the coverage code selected the latest observed expiry without testing its month-end status. | Coverage now filters observed fallback candidates to defensible month-end monthly expiries and reports/rejects primary files whose filename expiry is itself not monthly unless a valid fallback monthly expiry exists. Added primary and fallback monthly-candidate regression tests. |

| 2026-10-04 | 2 | TESTER FINDING | Gate 2 Review 15 identified a Pandas 3.x incompatibility: cross-source expiry resolution mixed Python date and pandas Timestamp objects and caused one unit-test failure. | Developer normalized canonical expiry dtype to Python dates before composite concatenation and added a regression test combining explicit and symbol-derived expiries. No strategy or source-priority logic changed. |

| 2026-10-04 | 2 | TEST ERROR | CI run 37225959932 failed 1/34 tests because the expiry-resolution regression fixture expected a lower-priority cloud row to win over a valid primary row. | Corrected the fixture so the primary row is invalid on price while still supplying explicit expiry provenance; added a separate dtype regression test. |
| 2026-10-04 | 2 | CI INFRASTRUCTURE | CI failure handlers attempted to commit/push diagnostics while the developer branch had advanced, producing non-fast-forward push failures. | Removed failure-time git pushes; diagnostics are now uploaded as workflow artifacts, while research/ERROR_LOG.md remains the canonical error log. |

| 2026-10-04 | 2 | TESTER FINDING | Gate 2 Review 16 found the composite build was terminated during bulk primary ingestion after unit tests and source staging passed. | Replaced the in-memory/bulk primary scan with a file-backed DuckDB database and one-partition-at-a-time ingestion; lowered the working memory cap to 4GB while preserving validation and provenance. |
| 2026-10-04 | 2 | DATA INTEGRITY | Primary staging contains weekly-dated files in June/August 2026 (2026-06-09, 2026-08-04); the symbol-expiry resolver could have used those as the month calendar. | The staged primary calendar resolver now ignores filenames outside the final six calendar days of their month; added regression coverage for the 2026 weekly/monthly distinction. |

| 2026-10-04 | 2 | CI INFRASTRUCTURE | Sequential composite run 37226364257 passed 35 unit tests and source staging but the hosted runner shut down at ~4m19s during composite construction; no later commit or concurrency cancellation caused the shutdown. | Added an explicit 30-minute job timeout and retained the bounded-memory sequential build. The run produced no accepted data output. |

| 2026-10-04 | 2 | TESTER FINDING | Gate 2 Review 17 found the monolithic sequential composite build remained in-progress beyond eight minutes and was not compatible with the project's bounded execution requirement. | Replaced the single composite job with six bounded year partitions plus a deterministic assembly job; Gate 2 checks now run only after assembly. |

| 2026-10-04 | 2 | TESTER FINDING | Gate 2 Review 18 found the partitioned assembly produced the Parquet but omitted the requested start/end contract required by the coverage gate. | Assembly now accepts start/end and writes both `composite_manifest.json` and `source_staging_manifest.json`; the workflow passes the requested window explicitly. |

| 2026-10-04 | 2 | TESTER FINDING | Gate 2 Review 19 found that year partitions beginning on January 1 omitted the preceding 32-DTE lead-in, causing 0/69 deterministic cycles to pass coverage. | Partition windows now overlap the preceding year from 20 November; final assembly deduplicates overlapping canonical keys deterministically by source priority. |

| 2026-10-05 | 2 | DATA COVERAGE | Gate 2 Review 19: assembled composite contains monthly expiry files but 0/69 deterministic 32-DTE cycles pass. TradeMarkk coverage is explicitly partial; 2021 Jan-Apr are absent from the staged primary set and later expiry files do not span the required pre-expiry window. | Do not weaken the 32-DTE gate. Investigate alternative reproducible historical acquisition paths and admit data only after independent tester validation. |

| 2026-10-05 | 2 | TESTER REMEDIATION | Tester Review 19 required partition lead-in before first expiry and deterministic deduplication of overlap rows. | Developer added 46-day partition lead-ins (2020-11-15/2021-11-15/.../2025-11-15) and canonical-key deduplication with source-priority ordering in assembly. |

| 2026-10-05 | 2 | GATE CLOSED | Tester Review 20: partition lead-in and cross-partition deduplication were implemented and all six partitions passed, but substantive coverage remained 0/69. This confirms the principal blocker is source lifecycle coverage, not partition boundaries. | Keep Gate 2 closed. Do not relax 32-DTE. Next admissible step is a complete historical 1-minute option source with acceptable access/licensing or a user-provided dataset. |

| 2026-10-05 | 2 | DOCUMENTATION ERROR | Developer previously described the strategy as a generic iron-condor-to-ratio transformation and incorrectly presented 32-DTE entry as part of the video rules. | Corrected: the video strategy starts with monthly-expiry 0.30/0.30 short and 0.10/0.10 hedge deltas, transitions when a short-leg delta reaches 0.10, then deploys the specified directional ratio spread; 32-DTE is a separate research protocol constraint only if explicitly retained, not a video rule. |

| 2026-10-05 | 1/2 | SCOPE RESET | User explicitly instructed that the initial transcript and 32-DTE constraint must be ignored and only the latest strategy be tested. | Rewrote STRATEGY_SPEC.md and research plan to use only the latest user-defined strategy. Existing data pipeline artifacts remain infrastructure validation, not strategy results. |
| 2026-10-05 | 1 | ERROR | CI test used an incorrect January 2026 month-start assumption; the repository calendar did not classify the asserted session as expected. | Verified against NSE F&O holiday file and corrected the test to use the calendar-defined month-start session. No strategy logic changed. |


| 2026-10-05 | 1 | TEST FIX | CI run 37231086646 still failed the month-start regression: the test used expiry 2026-01-27, whose final pre-expiry session is 2026-01-23, not 2026-01-27. The test therefore could not satisfy the production boundary contract. | Replaced the fixture with March 2026: 2026-03-03 is explicitly listed as an NSE F&O holiday, so the expected first session is 2026-03-02 and the pre-expiry session for 2026-03-30 is 2026-03-27. No strategy logic changed. |

| 2026-10-05 | 1 | TESTER GATE 1 FINDING | Independent tester Review 22 found the implementation had silently chosen combined short-leg delta >= 1.20 for reversal although the user rule only specifies a 0.80–1.30 short-leg-delta range. | Parameterized the reversal threshold, constrained it to the stated range, documented 1.20 as a modelling convention, and defined mandatory sensitivity points 0.80/1.00/1.20/1.30. Added regression validation. |

| 2026-10-05 | 1 | TEST ERROR | CI run 37231284204 found the new threshold regression test called run_cycle with an empty DataFrame and expected a normal return for the valid 1.20 threshold, but the empty fixture lacked the required date column. | Kept the production validation unchanged and corrected the test to assert that a valid threshold with unavailable data returns None; invalid thresholds remain required to raise ValueError. |

| 2026-10-05 | 2 | DATA GATE | CI run 37231413691 successfully built all six partitions and assembled the composite, but lifecycle coverage failed at 0/69 requested months. No backtest was run. | Independent tester Review 24 confirms Gate 2 remains CLOSED. Continue alternative-source acquisition; do not relax lifecycle coverage or promote performance. |

| 2026-10-05 | 2 | DATA POLICY CHANGE | Strict Gate 2 coverage is 0/69, but the user explicitly requested use of the most usable real data rather than waiting for perfect coverage. | Added a separate research-use partial-data tier with explicit entry-timing deviation, strict-gate disclosure, provenance preservation, and mandatory limitations. Production/full-coverage status remains closed. |

| 2026-10-05 | 2 | CODE REVIEW | Developer follow-up found a stale `target_32dte` field still being emitted by the composite coverage CSV despite the strategy scope reset. | Removed the obsolete field; coverage now reports only the current first-entry-month contract. |
| 2026-10-05 | 2 | CODE REVIEW | Developer follow-up found the continuation branch compared against a hard-coded 0.20 instead of the configured continuation threshold. | Replaced the hard-coded comparison with `continuation_delta_threshold`; this preserves the specified 0.20 default while making sensitivity/configuration internally consistent. |
| 2026-10-05 | 2 | CI DIAGNOSTICS | The workflow uploaded diagnostics only on overall job failure; a deliberately tolerated Gate 2 coverage failure could therefore suppress the diagnostic artifact. | Changed diagnostic upload to `if: always()` so strict-gate evidence is retained even when research-use mode intentionally continues. |


| 2026-10-05 | 2 | RESEARCH-USE BUG | Initial partial-data implementation still called the strict cycle-boundary function before selecting `entry_mode=available`, so missing the deterministic first session could cause every partial cycle to be rejected before execution. | Refactored `run_cycle` so research-use mode independently requires the final pre-expiry session and selects the first observed session within the expiry month; strict mode is unchanged. Added a regression test that verifies execution reaches the partial-entry path. |


| 2026-10-05 | 2 | TEST FIX | CI run 37232180287 failed 1/38 tests because the new partial-entry regression fixture returned an empty DataFrame without the option columns required by `select_contract`. | Added the expected empty-schema columns; production code was unchanged. |


| 2026-10-05 | 2 | CI ERROR | CI run 37232241237 successfully assembled all six partitions and passed unit tests, but `export_composite_csv.py` failed because DuckDB interpreted the parameterized COPY paths incorrectly and attempted to read the destination CSV as an input. | Replaced the parameterized COPY path arguments with safely escaped SQL string literals. No data-selection logic changed. |


| 2026-10-05 | 2 | CI ERROR | CI run 37232519372 assembled data and exported the CSV successfully, but reconciliation failed because DuckDB's timestamp CSV reader required the missing `pytz` package. | Added `pytz` to requirements and hardened the reconciliation COPY path handling. Backtest was correctly blocked until reconciliation passes. |


| 2026-10-05 | 2 | CI INFRASTRUCTURE | Run 37232849676 completed all research execution steps successfully, but the automatic `git push` of the 4.7GB result bundle failed with HTTP 500 / remote disconnect. | The complete result remains preserved as GitHub Actions artifact 11315040792. Repository promotion of multi-GB raw result files is not reliable; lightweight summaries should be committed while large raw datasets remain artifacts/cache. |
| 2026-10-05 | 2 | RESULT | Research-use baseline run completed with 28 traded cycles and negative performance: net P&L −₹20,455.46, profit factor 0.647, win rate 46.43%, max drawdown −₹41,981.20, Sharpe proxy −0.541. | Treat as exploratory only; strict Gate 2 remains CLOSED. Tester Review 27 requires predefined reversal sensitivity 0.80/1.00/1.20/1.30 before strategy promotion. |

| 2026-10-05 | 3 | SCOPE ERROR | Developer introduced a 0.80/1.00/1.20/1.30 reversal-threshold sensitivity grid and a 1.20 combined-delta convention that were not authorized by the user and did not faithfully test the YouTube strategy. | Removed the sensitivity workflow and threshold parameterization; restored the reversal rule to the literal stated 0.80–1.30 short-leg-delta range. Results from the unauthorized runs are non-authoritative and excluded from research conclusions. |

| 2026-10-05 | 4 | USER CORRECTION | Developer incorrectly converted the user's fixed 1.30 reversal trigger into a 0.80–1.30 range. | Corrected implementation and research plan to use a fixed 1.30 short-leg delta reversal trigger; no reversal sensitivity testing is permitted. |

| 2026-10-05 | 3 | CI LOG ACCESS | Attempted to fetch live logs for workflow job `111535265912` while the fixed-1.30 backtest was still running; GitHub returned `404 BlobNotFound`. | Treat as an infrastructure/log-stream access issue only. Continue monitoring via workflow/job status endpoints and do not infer a backtest outcome from missing live logs. |

| 2026-10-05 | 3 | TOOLING | One internal sleep-monitor command was malformed and returned `sleep: missing operand`; no research computation or repository state was affected. | Corrected the command and continued monitoring. |
| 2026-10-05 | 3 | TOOLING | A direct GitHub Actions job-URL fetch was rejected by the connector allowlist (HTTP 400); the supported workflow-job wrapper was used instead. | No research state was affected; use the supported GitHub workflow job APIs for subsequent monitoring. |

| 2026-10-05 | 3 | CI LOG ACCESS | Live log retrieval for workflow job `111539404198` returned GitHub `404 BlobNotFound` while the backtest step was still running. | Continue monitoring by workflow/job status; do not infer an outcome from missing live logs. |

| 2026-10-05 | 3 | TOOLING | First local compact-artifact inspection assumed a nested results/compact directory, but the downloaded artifact contains the compact files at its root. | Corrected the path; no research data were altered. |
| 2026-10-05 | 3 | CI RACE | Previous workflow run 37235922082 created a local result commit but push was rejected because newer documentation commits had advanced the remote branch. | Workflow was changed to fetch/rebase before publishing compact result files. |


## 2026-10-05 — TESTER REVIEW 30 / independent doubt audit

- **NUMERICAL RECONCILIATION:** PASS. The compact trade/order outputs independently reproduce 28 cycles, 620 orders, −₹3,821.50 gross P&L, ₹16,633.96 costs, −₹20,455.46 net P&L, 46.43% win rate, 0.6468 profit factor, −₹41,981.20 maximum drawdown, and −0.5414 Sharpe proxy.
- **ZERO-SLIPPAGE AUDIT:** Removing the recorded one-tick adverse slippage from the stored order fills gives gross P&L of −₹1,871.50 before slippage and before transaction costs. The negative direction is therefore not created by the one-tick slippage assumption or brokerage.
- **DATA VALIDITY:** Strict lifecycle coverage remains 0/69 requested months; the result is valid only as a research-use partial-data finding.
- **COST-METHODOLOGY FINDING:** The repository requirement for year-by-year historical charges was not matched by the final code's single ₹3,553/crore exchange-rate constant. The study methodology is therefore explicitly reframed to a consistent modern retail execution-cost baseline across the historical price path; no strategy rule changed.
- **SLIPPAGE REPORTING:** Zero-slippage was independently reconstructed from the order log; the final manuscript now records this audit.
- **DOCUMENTATION:** README, cost model, manuscript, phase status and conversation log updated. Strategy remains fixed at reversal trigger 1.30; no threshold optimization or alternate rule introduced.

Tester review: `research/PHASE_3_TESTER_REVIEW_30.md` on the isolated tester branch.

## 2026-10-05 — REVERSAL SEMANTICS AUDIT BLOCKER

The developer's fixed-1.30 implementation applies the reversal threshold to the absolute delta of one individual short option. Under the published Black-76 implementation with non-negative discounting (the run uses rate=0.0), an individual option absolute delta is bounded by 1.00, so a single-leg threshold of 1.30 is mathematically unreachable. The final run consequently recorded zero reversal events by construction, not as evidence that no reversal occurred in the market.

This creates a material strategy-fidelity question because the user's statement was only that reversal is 1.30; the repository's wording that this means one individual short-leg delta was not independently established from the video. A possible alternative interpretation is a combined quantity across the two short ratio legs, but that must NOT be invented or substituted without source confirmation.

Action: withdraw confidence in the current performance conclusion as a faithful YouTube-strategy replication; keep Gate 2 CLOSED; do not alter the strategy code or introduce a new interpretation until the reversal semantics are independently resolved and tester-reviewed. Also audit the entry/exit timing convention against the manual backtest because the automated run uses a first-observed-session / pre-expiry-session modelling convention that the video did not explicitly specify.

## 2026-10-05 — USER CLARIFICATION / REVERSAL AND ENTRY TIMING

User clarified that the fixed **1.30 reversal trigger applies to the two short contracts**, so the relevant quantity is 2 × the individual absolute delta of the short option. Therefore the individual short-option trigger is 0.65, while the user-facing strategy threshold remains 1.30.

User also clarified that the initial Iron Condor should be entered **as early as possible after the previous monthly expiry**. The prior first-session-of-target-expiry-month convention is superseded.

Implementation audit additionally found that the previous continuation check did not multiply the short option delta by its 2-contract quantity, despite the strategy specifying the combined delta of the two short legs. This has been corrected to count both short contracts. No new strategy rule was introduced.

## 2026-10-05 — REVIEW 34 REMEDIATION

Tester Review 34 found that the corrected backtest succeeded, but the coverage validator still called the superseded entry-date API and research-use metadata described the old target-month entry convention. Developer corrected both audit-layer defects. Strategy logic remains unchanged.


## 2026-10-05 — TESTER REVIEW 35 / clean corrected run

The clean corrected workflow 37253416839 passed all execution stages, including the previously blocked coverage validation and CSV/Parquet reconciliation. Independent Tester Review 35 accepted the numerical result and audit layer with restrictions.

Independent checks reproduced 29 cycles, 628 orders, 314 BUY/314 SELL, gross +₹8,294.00, costs ₹17,085.92, net −₹8,791.92, 44.83% win rate, profit factor 0.833656, maximum drawdown −₹30,811.11, P05 −₹5,669.63, P95 ₹4,289.12, and Sharpe proxy −0.23854. The order log contains 760 absolute lots, implying ₹1,900 of one-tick slippage drag at ₹0.05 and 50-unit lot size.

Coverage remains 0/69 strict complete cycles, so this is not a complete historical validation. No strategy change was introduced.

## 2026-10-05 — TESTER REVIEW 37 / MALFORMED RATIO BLOCKER

Independent falsification audit found that 2 of 53 ratio builds used the same CE contract as both the 0.50-delta long and 0.40-delta two-lot short. This occurs because ratio target selection is performed independently without a distinct-contract validity check.

Affected cycles:
- 2021-07-29: CE 15700 long and short.
- 2025-11-25: CE 26100 long and short.

Their combined net contribution is approximately +₹4,742.99. The current −₹8,791.92 result is therefore provisional and cannot be accepted as an exact ratio-strategy replication.

Required remediation: enforce distinct contract identities or, if the target structure cannot be represented by available data, reject that build/cycle rather than inventing a replacement strike. Add regression tests and rerun the complete workflow. No strategy rule may be changed.