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
