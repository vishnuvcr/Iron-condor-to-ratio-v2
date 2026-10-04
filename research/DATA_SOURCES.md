# Data Sources

## Primary strategy source
YouTube video supplied by the user:
https://youtu.be/T4gvTshMEyA

Uploaded transcript: 2,251 lines; key rules include initial Iron Condor, delta trigger, ratio-spread construction, directional resets, and examples.

## Candidate market-data sources reviewed
1. NSE option-chain / official exchange resources.
2. Hugging Face public NIFTY intraday options datasets.
3. GitHub open-source NIFTY option-data and backtesting projects.

Candidate sources must be accepted only after validating exact contract-level fields, timestamp granularity, expiry mapping, and licensing/provenance. No source is validated merely because it advertises intraday data.

## Current preferred research-data candidate
The public Hugging Face dataset `thetrademarkk/india-index-options-1m` is now the primary continuous intraday candidate. Its NIFTY options directory contains expiry-partitioned 1-minute Parquet files beginning in 2021 and continuing through 2026, with timestamp, OHLCV, strike, option type and expiry fields. The dataset explicitly warns that option coverage is partial for illiquid/far strikes, so contract-level completeness remains a gate. The `rissin/nse-options-intraday` Upstox/NSE-derived dataset remains an independent overlap-validation source for 2024 onward.

## Important limitation
A dataset that only presents rolling moneyness buckets without persistent contract identity is not sufficient for contract-level P&L.


## 2026-10-04 candidate-source review
- Hugging Face artist-23/nifty-options-data: 2020-12-29 to 2025-12-26, about 34M rows, monthly NIFTY data with ATM±10 strike-relative files. It is promising for auxiliary validation but is not yet accepted as the primary baseline because the published structure does not establish coverage of the 0.10-delta hedge across all regimes. [Hugging Face dataset](https://huggingface.co/datasets/artist-23/nifty-options-data)
- optionsdata.shop advertises a full-chain 1-minute NIFTY archive covering 2021/2023 onward through 2026 with OI, but it is a paid source. It remains a candidate fallback; no purchase or access assumption is made. [NIFTY 1-minute full-chain archive](https://optionsdata.shop/data/nifty-options-historical-data)
- Thetrademarkk remains useful for free schema/pipeline validation, but its expiry-partition coverage must be proven cycle-by-cycle before use for the baseline.
