# Historical Data Expansion Assessment

Date: 2026-10-04

## Decision

The 2024–2026 `rissin/nse-options-intraday` run is a pipeline-validation dataset, not the final research sample. The production backtest must use the longest defensible common-data window after independent validation.

## Candidate sources

| Source | Coverage advertised | Resolution | Options fields | Role |
|---|---|---|---|---|
| NSE official historical/F&O reports | Official daily derivatives reports; historical order/trade data is available by subscription | Daily / order-trade level depending on product | Authoritative source; intraday historical trade data may require subscription | Validation / authoritative reference |
| Hugging Face `thetrademarkk/india-index-options-1m` | Approximately 2021–2026 | 1 minute | OHLCV, OI; option contract structure | Primary free/open research candidate |
| Zenodo NIFTY spot/futures/options dataset | 2017–2020 | 1 minute | OHLCV; option contract files | Older-period candidate |
| `optionsdata.shop` | 2021–2026 or 2023–2026 depending catalog page | 1 minute | OHLCV + OI, full chain advertised | Paid fallback, not silently substituted |

## Required validation before combining sources

1. Verify exact NIFTY option contract coverage by expiry and strike.
2. Verify timestamps are IST and minute bars are consistently formed.
3. Verify option expiry dates and historical contract conventions.
4. Verify lot sizes from historical NSE contract files rather than assuming current lot size.
5. Check for duplicate bars, missing bars, zero/negative prices, and impossible OHLC relationships.
6. Compare overlapping dates across sources before stitching them.
7. Keep source provenance, dataset revision/version, retrieval time, file hashes, and coverage ranges in every run manifest.
8. Do not mix sources in a single production result unless overlap validation demonstrates acceptable comparability.

## Current gap

The current Phase-2 implementation uses 2024–2026 files from `rissin/nse-options-intraday`. That explains why only 19 monthly expiries were detected in the initial production-window test. It does not justify treating 19 expiries as the final sample.

## Production target

Prefer a continuous multi-year NIFTY option sample. If the free sources can be validated and stitched, target approximately 2017–2026. If only the 2021–2026 chain source is sufficiently complete, use that as the primary sample and report the earlier period separately rather than manufacturing continuity.

## Research integrity rule

No performance conclusion may be labelled final until the tester has independently approved the source coverage, stitching logic, provenance, and candidate-expiry accounting.
