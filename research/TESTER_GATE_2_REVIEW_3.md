# Tester Gate 2 Review — Historical Expansion

Date: 2026-10-04

**Decision: GATE 2 NOT PASSED / PENDING**

The current 19-expiry result is correctly classified as pipeline validation, not a final historical backtest.

## Independent checks

- A public Hugging Face dataset advertises 1-minute OHLCV(+OI) index and option-chain data for approximately 2021–2026.
- A Zenodo dataset advertises NIFTY spot, futures and options 1-minute data for 2017–2020.
- NSE publishes official historical derivatives reports and separately offers historical order/trade data products.
- These sources have different provenance and field structures; they cannot be stitched without overlap validation.

## Required developer actions

1. Finish and inspect the current CI run.
2. Resolve all runtime/provenance errors, including any missing imports or manifest fields.
3. Validate the expanded historical source(s) independently.
4. Demonstrate expiry-by-expiry coverage with explicit statuses.
5. Verify timestamps, strike/expiry mapping, OHLCV/OI quality and lot-size regimes.
6. Produce immutable source revisions/file hashes and retrieval timestamps.
7. Only then rerun the strategy over the longest defensible continuous window.
8. Submit the complete artifacts for independent review.

## Gate restriction

No final P&L, Sharpe, drawdown, win-rate, or profitability claim may be promoted from the 19-expiry validation sample.

**Tester instruction to developer:** remain in Phase 2 until the historical coverage and provenance checks above pass.