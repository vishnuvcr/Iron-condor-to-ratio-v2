# Iron Condor -> Ratio Spread v2

Research status: **Phase 8 — manuscript complete; corrected research-use backtest **PROVISIONAL / BLOCKED pending falsification remediation**; strategy not promoted.**

**Scope reset (2026-10-05):** testing follows only the latest user-defined strategy. The earlier 32-DTE protocol and earlier 28-cycle result are superseded.

## Navigation
- [Research plan](research/RESEARCH_PLAN.md)
- [Strategy specification](research/STRATEGY_SPEC.md)
- [Phase status](research/PHASE_STATUS.md)
- [Literature review](research/LITERATURE_REVIEW_2026-10-05.md)
- [Research questions and methodology](research/RESEARCH_QUESTIONS_AND_METHODOLOGY.md)
- [Free data-source review](research/FREE_DATA_SOURCE_REVIEW.md)
- [Composite data protocol](research/COMPOSITE_DATA_PROTOCOL.md)
- [Cost model](research/COST_MODEL.md)
- [Error log](research/ERROR_LOG.md)
- [Chat log](research/CHAT_LOG.md)
- [Roles and gates](research/ROLES_AND_GATES.md)
- [Tester Review 35](https://github.com/vishnuvcr/Iron-condor-to-ratio-v2/blob/phase-3-robustness-tester/research/PHASE_3_TESTER_REVIEW_35.md)

## Roles and branches
- Developer: `phase-3-robustness-developer`
- Independent tester: `phase-3-robustness-tester`

The branches remain isolated. Developer progression requires tester review.

## Gate status

**Strict Gate 2: CLOSED.**

A separate **research-use partial-data** tier is enabled because the user requested the best usable real data with explicit limitations. No missing option prices are interpolated, forward-filled, averaged, or theoretically synthesized.

## Current verified research-use result

Clean GitHub Actions workflow: **37253416839**  
Developer commit: `d7b1bc03da8fed525b26ee4c3a6d433c12ed3487`

Independent Tester Review 37: **BLOCKED** — malformed ratio construction found. Tester Review 35 is superseded for performance acceptance.

| Metric | Result |
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
| P05 | −₹5,669.63 |
| P95 | ₹4,289.12 |
| Annualized monthly Sharpe proxy | −0.23854 |
| State transitions | 66 |
| Continuation rebuilds | 13 |
| Reversal rebuilds | 24 |

The order log contains 760 absolute lots. At one adverse ₹0.05 tick per lot and a 50-unit lot size, independently reconstructed slippage drag is **₹1,900**. This is separate from total transaction costs.

**Interpretation:** this is research-use partial-data evidence, not complete historical validation and not a live-trading recommendation.

## Coverage limitation

Requested window: **2021-01-01 through 2026-09-30 = 69 months**.

Clean run status:
- strict complete cycles: **0/69**
- strict Gate 2: **FAILED/CLOSED**
- research-use partial mode: **TRUE**

The composite and consolidated CSV reconcile exactly at **18,064,638 rows** with identical canonical SHA-256.

## Exact strategy fidelity

- Initial Iron Condor: sell 0.30-delta CE/PE; buy 0.10-delta CE/PE.
- IC trigger: either original short reaches 0.10 absolute delta.
- Directional ratio: buy 0.50 delta; sell 0.40 delta ×2; buy 0.10 delta hedge.
- Continuation: combined absolute delta of **both** short contracts reaches 0.20; rebuild 0.40 long / 0.30 short ×2 / 0.08 hedge.
- Reversal: **1.30 across the two short contracts = 2 × individual absolute short-option delta**. No sensitivity testing or alternate threshold.
- Entry: earliest normal NSE F&O session after the actual previous monthly expiry; research-use mode uses the earliest observed post-expiry session when the exact first session is unavailable.
- Execution economics include the stated brokerage/slippage/statutory-cost baseline.
- No strategy optimization has been introduced.

## Research framework

The project contains the predefined research questions, literature review, scientific methodology, statistical analysis plan, data provenance, cost model, strengths/limitations, discussion, conclusion, future research, appendices and reproducibility records.

The final manuscript is retained under `manuscript/`. The research stops at the predefined phases; no endless parameter search is permitted.

## Decision

The corrected strategy run is **PROVISIONAL and NOT ACCEPTED**. Tester Review 37 found two malformed ratio builds in which the 0.50-delta long and 0.40-delta short used the same contract. A corrected rerun and independent tester review are required.

**The strategy is NOT promoted to live trading.**


## 2026-10-05 falsification audit
Tester Review 37 found a material strategy-fidelity defect: 2/53 ratio builds used the same CE contract for both the 0.50-delta long and 0.40-delta short. The current −₹8,791.92 result is therefore provisional and not accepted. The strict Gate 2 remains CLOSED.