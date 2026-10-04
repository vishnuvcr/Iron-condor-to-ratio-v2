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