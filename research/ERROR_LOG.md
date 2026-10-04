# Error Log

| Date | Phase | Severity | Error / issue | Resolution |
|---|---|---|---|---|
| 2026-10-04 | 0 | INFO | Repository was empty when initialized; no pre-existing research files were available to inherit. | Created baseline research structure from the project protocol. |
| 2026-10-04 | 0 | INFO | Video rules include discretionary language (early exit and delayed adjustment) in addition to numeric delta triggers. | Preserve ambiguity explicitly; create deterministic baseline plus sensitivity variants before production backtest. |

| 2026-10-04 | 2 | ERROR | First GitHub Actions run 37211955857 failed at unit tests; production backtest was blocked. | Fix test environment before rerun. |
| 2026-10-04 | 2 | ERROR | 2025 monthly entry coverage was incomplete without December 2024 intraday data. | Add 2024 partition and reject uncovered cycles. |
| 2026-10-04 | 2 | ERROR | Exit-fill logic mixed timestamps with prices from earlier bars. | Redesign common fill timestamp logic. |
| 2026-10-04 | 2 | ERROR | IC trigger logic keyed deltas only by option type, so the 0.10-delta hedge could overwrite the 0.30-delta short leg. | Changed trigger monitoring to use short positions only; removed dead selection loop. |
| 2026-10-04 | 2 | ERROR | Black-76 function named implied_vol_black76 returned delta instead of implied volatility, causing the regression test to interpret 0.5114 as IV. | Split IV solver from price-to-delta conversion and added regression tests. |
| 2026-10-04 | 2 | ERROR | Full backtest failed after unit tests passed; the initial workflow did not capture backtest stdout/stderr. | Hardened workflow to tee backtest output into a committed diagnostic file on failure. |
| 2026-10-04 | 2 | INFO | A second semantic issue was found in IC trigger monitoring: both short and long legs share option_type keys. | Added a deterministic choose_ic_trigger helper and short-leg-only state tracking. |
| 2026-10-04 | 2 | ERROR | Canonical full backtest failed because dataset timestamps were timezone-aware while expiry/decision timestamps were naive. | Normalize data timestamps to IST and construct all expiry/entry/exit decision timestamps as Asia/Kolkata-aware. |
