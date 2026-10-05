# Final Research Manuscript

## Iron Condor → Directional Ratio Spread v2: Research-Use Evaluation of the User-Defined NIFTY Strategy

**Research date:** 5 October 2026  
**Developer branch:** `phase-3-robustness-developer`  
**Tester branch:** `phase-3-robustness-tester`  
**Verified workflow:** 37253416839  
**Developer commit:** `d7b1bc03da8fed525b26ee4c3a6d433c12ed3487`  
**Independent tester review:** `research/PHASE_3_TESTER_REVIEW_35.md`

---

## Abstract

This study evaluates only the latest user-defined NIFTY monthly options strategy. The strategy begins with a 0.30-delta short call/put iron condor hedged by 0.10-delta long call/put options. When either original short reaches 0.10 absolute delta, the iron condor is closed and converted to a directional 1:-2:+1 ratio spread. Same-direction continuation occurs when the combined absolute delta of the two short ratio contracts reaches 0.20. Reversal occurs at a fixed combined threshold of 1.30 across the two short contracts, equivalent to 2 × the individual absolute short-option delta. The initial iron condor is entered as early as possible after the previous monthly NIFTY monthly expiry.

A provenance-aware composite of free/public option data was used. Strict lifecycle coverage for the requested January 2021–September 2026 window was not achieved, so the study explicitly separates a failed strict data gate from a research-use partial-data tier. No missing option prices were interpolated, forward-filled, averaged, or theoretically synthesized.

The clean research-use run produced 29 traded cycles, 628 orders, gross P&L of +₹8,294.00, modeled transaction costs of ₹17,085.92, and net P&L of **−₹8,791.92**. Win rate was 44.83%, profit factor 0.833656, maximum drawdown −₹30,811.11, and the annualized monthly Sharpe proxy −0.23854. There were 13 continuation rebuilds and 24 reversal rebuilds. Independent Tester Review 35 reproduced the principal arithmetic and accepted the result with restrictions.

The result is **not a fully covered historical validation and does not justify live-trading promotion**.

---

## 1. Research questions

### Primary question

Does the exact user-defined iron-condor-to-directional-ratio strategy produce positive and sufficiently robust risk-adjusted returns after realistic option-trading costs and slippage?

### Secondary questions

1. How frequently does the iron condor transition to a directional ratio?
2. How frequently does same-direction continuation occur?
3. How frequently is the fixed 1.30 two-short-contract reversal condition reached?
4. What is the effect of brokerage, statutory charges and slippage?
5. What are the cycle-level loss, drawdown and tail characteristics?
6. How much confidence can be assigned to the findings given incomplete historical lifecycle coverage?

---

## 2. Aims and objectives

### Aim

To scientifically evaluate the supplied strategy without introducing new trading rules or optimizing its parameters.

### Objectives

- Implement the exact stated delta rules.
- Use causal, executable fills without look-ahead.
- Preserve option-contract provenance.
- Include brokerage, statutory costs and slippage.
- Independently reconcile the final outputs.
- Quantify performance and risk descriptively.
- Explicitly separate data limitations from strategy performance.
- Stop at the predefined research phases rather than optimize indefinitely.

---

## 3. Exact strategy specification

### 3.1 Initial iron condor

- Sell 1 × 0.30-delta call.
- Sell 1 × 0.30-delta put.
- Buy 1 × 0.10-delta call.
- Buy 1 × 0.10-delta put.

### 3.2 Iron-condor trigger

When either original short option reaches 0.10 absolute delta:

- close the iron condor;
- convert to the directional ratio corresponding to the market direction;
- do not return to the iron condor within that cycle.

### 3.3 Falling-market / call ratio

- Buy 1 × 0.50-delta call.
- Sell 2 × 0.40-delta calls.
- Buy 1 × 0.10-delta call hedge.

### 3.4 Rising-market / put ratio

- Buy 1 × 0.50-delta put.
- Sell 2 × 0.40-delta puts.
- Buy 1 × 0.10-delta put hedge.

### 3.5 Continuation reset

When the **combined absolute delta of both short contracts** reaches 0.20:

- close the current ratio;
- rebuild in the same direction:
  - buy 1 × 0.40 delta;
  - sell 2 × 0.30 delta;
  - buy 1 × 0.08 delta hedge.

Both short contracts are counted in the combined delta.

### 3.6 Reversal

When the **combined absolute delta of the two short contracts** reaches 1.30:

- close the current ratio;
- reverse direction;
- build the opposite 0.50/0.40/0.10 ratio.

For equal two-lot short positions this is equivalent to an individual short-option absolute-delta trigger of 0.65.

No alternate reversal threshold or sensitivity grid is authorized or tested.

### 3.7 Entry timing

The initial iron condor is entered at the earliest normal NSE F&O session after the actual previous NIFTY monthly expiry. In research-use mode, if that exact first session is unavailable in the dataset, the earliest observed post-expiry session is used and explicitly labelled as partial-data execution.

---

## 4. Scientific methodology

### 4.1 Experimental unit

The primary unit is the monthly expiry cycle. Orders and state transitions are nested within each cycle.

### 4.2 Information and execution model

Signals use completed observations. New orders use the next common executable observation for the required legs. Future bars, future option prices and future state information are not used.

### 4.3 Delta and volatility model

The engine uses a Black-76/parity framework to infer implied volatility and option delta from observed option prices, forward estimates and the recorded zero-rate modelling input.

### 4.4 Strike selection

New contracts are selected by the specified delta target from the available chain. Held positions remain tracked even when they move outside the new-strike candidate window.

### 4.5 Transaction-cost model

The published research baseline includes:

| Component | Baseline |
|---|---:|
| Paytm Money brokerage | ₹20/order |
| Option tick | ₹0.05 |
| Adverse slippage | 1 tick per executed lot |
| NSE transaction charge | current documented retail baseline |
| SEBI fee | ₹10/crore |
| STT | current-period documented rate schedule |
| Buyer stamp duty | 0.003% |
| GST | 18% on applicable brokerage/service charges |

The cost model is explicitly a consistent modern retail execution-cost baseline applied to the historical price path. It is not represented as a year-by-year reconstruction of historical broker invoices.

### 4.6 Data-integrity rules

The composite pipeline:

- preserves timestamp + expiry + strike + option-type identity;
- retains source provenance;
- uses exact-key fallback only;
- does not interpolate;
- does not forward-fill;
- does not average prices between sources;
- does not synthesize theoretical option prices;
- uses an NSE F&O session calendar for continuity checks;
- reconciles the consolidated CSV against the Parquet dataset.

---

## 5. Data and coverage

Requested study window: **2021-01-01 through 2026-09-30**, or 69 calendar months.

The clean composite contains 54 observed expiry candidates:

| Candidate outcome | Count |
|---|---:|
| Traded | 29 |
| Skipped: no complete executable path | 23 |
| Skipped: empty data | 2 |
| Observed candidates | 54 |
| Requested months | 69 |

The strict lifecycle gate reports **0/69 complete cycles**. Therefore the strict data gate remains closed.

The clean workflow reconciled **18,064,638 Parquet rows** with **18,064,638 CSV rows**, with matching canonical SHA-256.

The research-use tier is therefore a partial-data research sample, not a complete historical population.

---

## 6. Statistical analysis

The analysis is primarily descriptive because the strict data gate failed and the traded-cycle sample is small.

Reported statistics include:

- total and average net P&L;
- median cycle P&L;
- win rate;
- profit factor;
- maximum drawdown;
- empirical P05/P95 cycle outcomes;
- annualized monthly Sharpe proxy;
- order count and transition count;
- cost and slippage decomposition.

No parameter optimization, multiple-threshold search or post-hoc strategy selection is performed.

Inferential claims are restricted by the partial-data sample and must not be interpreted as population-level proof of profitability or unprofitability.

---

## 7. Results

### 7.1 Primary performance

| Metric | Clean verified result |
|---|---:|
| Traded cycles | 29 |
| Orders | 628 |
| BUY / SELL | 314 / 314 |
| Gross P&L | +₹8,294.00 |
| Transaction costs | ₹17,085.92 |
| Net P&L | **−₹8,791.92** |
| Win rate | 44.83% |
| Profit factor | 0.833656 |
| Maximum drawdown | −₹30,811.11 |
| P05 cycle P&L | −₹5,669.63 |
| P95 cycle P&L | ₹4,289.12 |
| Annualized monthly Sharpe proxy | −0.23854 |

### 7.2 Lifecycle behaviour

- 29 original ratio conversions.
- 13 continuation rebuilds.
- 24 reversal rebuilds.
- 66 total recorded state transitions.

The clean run therefore exercises the fixed reversal mechanism materially; the previous zero-reversal result from the superseded implementation must not be used.

### 7.3 Slippage audit

The order log contains 760 absolute lots. With a ₹0.05 adverse tick and 50-unit lot size:

**760 × ₹0.05 × 50 = ₹1,900**

Thus the independently reconstructed one-tick slippage drag is ₹1,900.

The gross result before that slippage component is approximately ₹10,194.00. After the modeled transaction costs, the final net result is −₹8,791.92.

Transaction costs are therefore the dominant modeled execution drag in this run.

---

## 8. Inferences

The clean run does **not** provide evidence of a positive net trading edge in this partial-data sample.

The gross result is positive, but the modeled transaction costs exceed the gross profit and convert the result to a net loss. The result therefore demonstrates substantial sensitivity to execution economics even without introducing any strategy change.

The 24 reversal rebuilds demonstrate that the corrected two-short-contract reversal interpretation materially changes strategy lifecycle behaviour compared with the superseded single-leg interpretation.

However, because strict coverage is 0/69 months, these observations cannot be generalized to the complete requested historical period.

---

## 9. Discussion

The main methodological lesson is that strategy fidelity and data completeness are separate requirements. Earlier runs were invalidated because the reversal quantity and entry convention did not match the user's clarified strategy. The current implementation explicitly counts both short contracts and starts the initial cycle after the actual previous monthly expiry.

The current result is also materially different from the superseded 28-cycle result. That difference is expected because the corrected reversal semantics create actual reversal events and the entry convention changes the lifecycle.

The negative net result is driven primarily by modeled transaction costs rather than by an intrinsically negative gross result. This makes cost realism particularly important for a strategy with frequent state transitions and multi-leg rebuilds.

No claim is made that the strategy is universally unprofitable. The correct conclusion is narrower: **the available research-use sample does not demonstrate a positive net edge after the specified execution-cost model.**

---

## 10. Strengths

1. Exact user-defined strategy rules are preserved.
2. The two-lot delta semantics are explicitly represented.
3. No unauthorized optimization remains.
4. Causal execution logic reduces look-ahead risk.
5. Source provenance is retained.
6. Missing option prices are not synthetically filled.
7. Brokerage and statutory costs are included.
8. Slippage is explicitly modeled and independently audited.
9. CSV and Parquet outputs reconcile exactly.
10. Developer and tester branches are isolated.
11. The clean run passed the automated workflow stages.
12. Independent tester review accepted the numerical artifact with restrictions.

---

## 11. Limitations

1. Strict historical lifecycle coverage is 0/69 requested months.
2. The traded sample contains only 29 cycles.
3. The data are a composite of free/public sources with heterogeneous availability.
4. Research-use mode can start at the earliest observed post-expiry session when the exact first session is missing.
5. The cost model is a consistent modern baseline, not historical invoice reconstruction.
6. Delta estimation depends on the Black-76 modelling assumptions and available option prices.
7. The Sharpe figure is a proxy based on monthly cycle observations, not a conventional high-frequency portfolio Sharpe estimate.
8. No defensible full-period regime-stratified inference can be made from the current coverage.
9. No live execution slippage, queue position or market-impact model is available.
10. The result should not be treated as a trading recommendation.

---

## 12. Conclusion

Under the exact clarified strategy rules and the current research-use dataset, the clean run produced:

**Gross P&L: +₹8,294.00**  
**Costs: ₹17,085.92**  
**Net P&L: −₹8,791.92**

The strategy therefore **does not pass a net-profitability acceptance criterion in the available research-use sample**.

The result is not sufficient to claim universal failure because strict historical coverage is incomplete. The scientifically defensible conclusion is that the available evidence does not demonstrate a positive net trading edge after modeled execution costs.

**Live-trading promotion is rejected.**

---

## 13. Future research

Only predefined research directions should be considered:

1. Obtain a complete, independently validated historical NIFTY option dataset covering all requested cycles.
2. Re-run the exact strategy without changing any strategy parameter.
3. Compare the strategy with a predefined static iron-condor benchmark.
4. Stratify results by independently defined volatility/skew regimes only as explanatory analysis.
5. Incorporate NSE/BSE market-structure information, FII/DII positioning, volatility indices, corporate actions and relevant global-market conditions where the data are available and causally appropriate.
6. Validate execution assumptions against real broker fills if user-provided transaction records become available.
7. Reassess statistical uncertainty once a complete historical sample exists.

No future work should turn these explanatory variables into unapproved strategy optimization parameters.

---

## 14. Reproducibility and governance

The authoritative records are maintained in the repository:

- `research/RESEARCH_PLAN.md`
- `research/STRATEGY_SPEC.md`
- `research/PHASE_STATUS.md`
- `research/ERROR_LOG.md`
- `research/CHAT_LOG.md`
- `research/PHASE_3_TESTER_REVIEW_35.md` on the isolated tester branch
- `research/COST_MODEL.md`
- `research/COMPOSITE_DATA_PROTOCOL.md`

The clean workflow artifact is **backtest-results-compact**, generated by workflow 37253416839.

The strict Gate 2 remains closed. The strategy is not promoted.

---

## Appendix A — Decision record

**Accepted:** corrected strategy implementation and clean numerical artifact, with restrictions.  
**Rejected:** full historical validation claim.  
**Rejected:** live-trading promotion.  
**Rejected:** any parameter optimization or unauthorized sensitivity analysis.

## Appendix B — Superseded results

The earlier 28-cycle result is retained only as an audit-history record. It is not a result for the current strategy because it used the wrong reversal quantity and earlier entry convention.

## Appendix C — Tester decision

Tester Review 35: **PASS WITH RESTRICTIONS**.

The tester independently verified the clean run's arithmetic, execution counts, transition structure, coverage status and cost/slippage methodology. The tester specifically required that the strict Gate 2 CLOSED status remain visible.

