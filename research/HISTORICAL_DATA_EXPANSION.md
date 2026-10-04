# Historical Data Expansion Assessment

Date: 2026-10-04

## Decision

The 2024–2026 `rissin/nse-options-intraday` run was a pipeline-validation dataset, not the final research sample. The previously selected `rissin/nse-options-intraday` source did expose nominal 2022/2023 partitions, but the actual run showed unusable coverage: one 2022 expiry had only 15 rows and no 2023 expiries were detected. Therefore that source cannot establish a continuous 2022–2026 research sample. The primary source is now `thetrademarkk/india-index-options-1m`, whose NIFTY options directory exposes expiry-level files from 2021 through 2026. The production backtest must still pass expiry-by-expiry coverage and overlap validation.

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

## Current expanded source

The primary source now targets `upstox_intraday/NIFTY/NIFTY_2022.parquet` through `NIFTY_2026.parquet`. The dataset card states that the Upstox intraday track is 1-minute NIFTY data, while its repository history explicitly shows the 2022 and 2023 NIFTY partitions. The dataset notes that intraday OI is not supplied by Upstox, so OI is not used as a hidden input to the baseline delta model.

## Current gap

The current Phase-2 implementation has switched away from the incomplete `rissin` 2022–2026 expansion. The prior run detected only 23 candidate expiries, with 2022 and 2023 unusable; only 15 were traded. This is explicitly validation-only and is not a performance conclusion.

## Lot-size regimes

For the expanded window, the engine uses 75 through the June-2021 NIFTY monthly expiry, 50 from July-2021 through April-2024, 25 for the May-2024 through November-2024 transition, 75 from the November-2024 new-contract regime through December-2025, and 65 from the January-2026 monthly regime. These breakpoints are tied to NSE contract revisions and are covered by unit tests.

## Production target

Prefer a continuous multi-year NIFTY option sample. If the free sources can be validated and stitched, target approximately 2017–2026. If only the 2021–2026 chain source is sufficiently complete, use that as the primary sample and report the earlier period separately rather than manufacturing continuity.

## Research integrity rule

No performance conclusion may be labelled final until the tester has independently approved the source coverage, stitching logic, provenance, and candidate-expiry accounting.

## 2026-10-04 source revalidation
The thetrademarkk source is useful for pipeline/schema validation but is **not currently sufficient for the baseline strategy**. Its expiry partitions may contain only a short segment of the contract life; the July 28, 2026 partition in the CI run ended July 2. Because the strategy requires entry at expiry minus 32 calendar days and monitoring through the final pre-expiry session, such partitions cannot be used as complete cycles. The backtest engine now rejects incomplete cycles rather than substituting an early exit.

A defensible final dataset must demonstrate, expiry-by-expiry, coverage from the required entry date through the final pre-expiry trading session. Candidate paid full-chain archives and Kaggle/GitHub-derived datasets remain research candidates only until schema, provenance, coverage, and redistribution/access conditions are independently verified.
