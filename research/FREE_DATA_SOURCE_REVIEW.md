# Free Data Source Review

Date: 2026-10-04

## Decision

Phase 2 will continue with free/public sources before considering any paid archive. No paid dataset is authorized or required at this stage.

## Ranked candidates

| Candidate | Free access evidence | Resolution | OHLCV | OI | Contract coverage | Current role |
|---|---|---:|---|---|---|---|
| Cloud Trader Pro / Shoonya free samples | Provider states sample expiry datasets are downloadable free | 1 min | Yes | Yes | Claims NIFTY expired contracts and all strikes, but only a few sample expiries are exposed publicly | **First empirical validation target** |
| Zenodo: Nifty spot, futures and options 2017-2020 | Public research download | 1 min | Yes | No | Monthly expiry/strike files; example contract history begins well before expiry | **Older-period validation/extension** |
| Hugging Face thetrademarkk | Public dataset, CC-BY-NC-4.0 | 1 min | Yes | Dataset schema includes OI | Expiry files exist 2021 onward, but author warns far/illiquid strikes can be sparse | **Free primary candidate, not yet accepted** |
| Hugging Face artist-23 | Public dataset | 1 min | Yes | Yes | Published structure is strike-relative/ATM±10; 0.10-delta hedge coverage not established | Secondary validation |
| MoneyTicks | Public catalogue; archive described as complete, but downloads/API not yet for sale | 1 min | Yes | Yes | Claims every NIFTY contract back to 2023 | **Free catalogue lead; raw-data access unconfirmed** |
| OptionVault | Public GitHub repository with sample files | 1 min | Yes | Yes | Claims 2018-present, but full dataset is licensed; public samples only | Sample/schema validation |
| Public GitHub collectors (Zerodha/Breeze) | Code is public | 1 min | Yes | Yes | Requires broker/API credentials; not a pre-existing historical archive | Reconstruction route, if legally/accessibly available |

## Evidence reviewed

- Cloud Trader Pro explicitly states that a few NIFTY expired-option datasets can be downloaded free and documents 1-minute OHLCV+OI columns. The full multi-year archive is separately requested, so the free sample must be tested before treating it as continuous. Source: https://cloudtraderpro.in/free-historical-options-data/
- Shoonya's page independently points to the Cloud Trader free NIFTY CSV and states 1-minute OHLCV+OI and free download. Source: https://shoonyatrader.in/free-historical-expired-options-contract-data/
- Zenodo provides a 320.9 MB public NIFTY options ZIP for 2017-2020, with monthly expiry folders and strike-specific one-minute OHLC files. It does not report OI, so it cannot silently replace the OI-bearing primary dataset. Source: https://zenodo.org/records/10899828
- thetrademarkk currently reports 376.5M rows and NIFTY expiry files beginning in 2021; its schema includes OI, but the dataset card explicitly warns that illiquid/far strikes may be sparse or absent. Source: https://huggingface.co/datasets/thetrademarkk/india-index-options-1m
- artist-23 currently reports 34.0M rows from 2020-12-29 to 2025-12-26 with OHLC, IV, OI, strike and spot fields. Its published structure still requires a direct check of the required 0.10-delta hedge contracts. Source: https://huggingface.co/datasets/artist-23/nifty-options-data
- MoneyTicks says its archive is complete and browseable but also says the archive is not yet for sale; therefore raw-data accessibility is not established. Source: https://moneyticks.com/
- OptionVault's public repository provides samples and schema but says the complete 300+ GB archive is licensed. It is therefore not a confirmed free full-history source. Source: https://github.com/QuantDev-stack/OptionVault
- Public GitHub collectors can retrieve 1-minute OHLCV+OI through Zerodha/Breeze APIs, but they require eligible credentials and are not themselves a free historical archive. Example: https://github.com/i9-tradebot/NIFTY_Options_Historical_Data_Collector and https://github.com/mukhilj/breeze_options_pipeline

## Acceptance test

A source is not accepted merely from its description. It must provide actual files/data sufficient to demonstrate, expiry by expiry:

1. First available trading session on/after expiry minus 32 calendar days.
2. Continuous/defensible one-minute data through the final pre-expiry trading session.
3. CE and PE contracts needed by the delta selector, including the approximately 0.10-delta hedge where selected.
4. Strike, expiry, option type and timestamp identity without ambiguity.
5. Valid OHLCV and, for the primary source, OI.
6. No impossible OHLC relationships, duplicate contract-minute rows, or timezone ambiguity.
7. Immutable retrieval/source revision information and file hashes.
8. Independent overlap comparison with another source for a representative set of dates/contracts.

## Immediate next step

Download/inspect the free Cloud Trader sample first. If its sample expiries contain complete 32-DTE-to-expiry histories and adequate strike coverage, use them for a schema/coverage harness and overlap checks. In parallel, download the Zenodo archive metadata/sample and inspect the 2017-2020 contract-history structure. Continue thetrademarkk validation only where its actual expiry files satisfy the cycle-span gate.

## Integrity rule

No performance metrics from incomplete or sample-only cycles may be promoted to research results. No paid source will be purchased without explicit user authorization.


## 2026-10-04 composite implementation update
The project now attempts a composite dataset when a free source has invalid or missing contract-minute rows. Thetrademarkk rows with explicit expiry remain the primary candidate. Cloud Trader/Shoonya rows may supply exact-key fallback observations, but expiry inferred only from the last observed timestamp is marked provisional and cannot make an expiry eligible for production by itself. Prices are never averaged or interpolated across sources.

## 2026-10-04 additional open-source leads
- OptionVault documents a very large Indian derivatives archive with NIFTY options at 1-minute resolution and OHLCV+OI, but its complete archive is licensed; public samples are for evaluation only. It remains useful for schema/overlap validation, not as a confirmed free full-history source.
- pythonwallahpro/data-lake provides a validated one-minute NIFTY/SENSEX option data-lake architecture with expiry/strike/CE-PE identity and missing-segment tracking, but requires Angel Broking SmartAPI credentials to generate the data. It is a reconstruction route rather than a free pre-existing archive.
- Open-source Zerodha and Breeze collectors similarly provide 1-minute OHLCV+OI retrieval but require eligible broker/API credentials. They are retained as possible reconstruction fallbacks.


## 2026-10-04 builder optimization
The composite merge was changed from whole-history Pandas concatenation to a disk-backed DuckDB sequential merge. Source rows are validated one file at a time; higher-priority rows remain authoritative, lower-priority exact-key rows fill missing observations, and overlap diagnostics are aggregated by source/file.


## 2026-10-04 — rissin composite fallback
The public rissin dataset is now promoted to the first exact-key fallback for 2024–2026. Its Upstox NIFTY partitions provide explicit expiry, strike, CE/PE, IST timestamp and 1-minute OHLC/volume. Intraday OI is documented as unavailable, which is acceptable for the baseline delta engine because OI is not a strategy signal. The composite will use rissin for missing/invalid price rows and overlap validation, never by interpolating prices. [Dataset evidence](https://huggingface.co/datasets/rissin/nse-options-intraday).


## Additional free-source lead — 2026-10-04
Public research also identified the open-source `fnopy` project, which exposes an NSE historical-data retrieval interface for NIFTY options and examples for specifying expiry, option type, strike and date windows. It is a data-access lead rather than an already-materialized dataset, so it is not promoted as a production source until a cached extract is independently validated for completeness, licensing/availability, and reproducibility.
