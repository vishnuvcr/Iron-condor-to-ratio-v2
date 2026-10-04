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
The public Hugging Face dataset rissin/nse-options-intraday advertises 1-minute NIFTY options from October 2024 onward through 2026, with expiry, strike, option type, OHLC, volume, timestamp, and spot fields. It will be schema-validated before use.

## Important limitation
A dataset that only presents rolling moneyness buckets without persistent contract identity is not sufficient for contract-level P&L.
