# Tester Gate 2 Review 5 — Free-source expansion

Date: 2026-10-04
Role: Independent tester

## Verdict

**Gate 2: NOT PASSED.** The free-source search materially improves the data-acquisition path, but no candidate has yet been independently demonstrated to satisfy the complete strategy-cycle data requirement. This report therefore authorizes continued source validation, not a production backtest or Phase 3 promotion.

## Independent findings

### 1. Cloud Trader Pro / Shoonya
The provider publicly states that NIFTY expired options are available as free sample CSVs at 1-minute OHLCV+OI resolution and that the samples include real expiry datasets. This makes it a legitimate empirical candidate. However, the public page distinguishes free samples from the requested full multi-year archive. The downloadable Google Drive sample could not be retrieved through the web access used for this review because the link returned HTTP 401. Therefore completeness across the required 32-DTE-to-pre-expiry window is **not yet proven**.

### 2. Zenodo 2017-2020
The public Zenodo record provides a 320.9 MB NIFTY options ZIP and describes monthly expiry folders with strike-specific one-minute OHLC data. An example contract begins well before its monthly expiry. This is useful evidence for an older-period extension. OI is not reported in the dataset description, so it cannot be treated as an OI-bearing replacement for the primary source without an explicit modeling decision.

### 3. thetrademarkk
The public dataset contains 1-minute option fields including OI and expiry/strike identity and has NIFTY expiry files beginning in 2021. However, its own dataset card warns that illiquid/far strikes can be sparse or absent. The previous developer run already demonstrated that at least one expiry partition ended before the required strategy entry date. This source therefore remains unapproved until expiry-by-expiry cycle coverage is demonstrated.

### 4. artist-23
The public dataset reports OHLC, IV, OI, strike and spot from 2020-12-29 through 2025-12-26. It remains a useful independent cross-check. Its published structure is not sufficient, by itself, to prove availability of every contract selected by the delta algorithm, especially the approximately 0.10-delta hedge.

### 5. MoneyTicks / OptionVault / broker collectors
MoneyTicks advertises a complete 1-minute archive but says the archive is not yet for sale; raw-data access is therefore not independently established. OptionVault exposes public samples but states that its full archive is licensed. Public Zerodha/Breeze collectors are reconstruction tools requiring eligible credentials, not independent free historical archives. These are leads, not approved primary data sources.

## Required next submission

The developer must submit actual free-source sample files or machine-readable manifests demonstrating:

1. expiry-by-expiry first date on/after expiry minus 32 calendar days;
2. final pre-expiry trading session present;
3. CE/PE strike coverage for all contracts selected by the deterministic delta algorithm;
4. one-minute timestamp integrity and IST normalization;
5. duplicate/missing-bar/OHLC/OI checks;
6. historical lot-size mapping;
7. immutable source revision/retrieval timestamp/file hashes;
8. overlap comparison against an independent source for representative contracts/dates;
9. explicit reasons for every skipped candidate expiry;
10. no performance metrics promoted from incomplete cycles.

## Tester gate instruction

Do not advance to Phase 3 or declare Gate 2 passed until the above evidence is available and independently reproducible.

## Developer instruction

**Developer:** validate the free Cloud Trader/Shoonya sample first, then the Zenodo archive, while continuing thetrademarkk/artist-23 overlap checks. Record every failed source test in ERROR_LOG.md and resubmit a complete Gate 2 evidence bundle.
