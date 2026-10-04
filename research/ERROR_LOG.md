# Error Log

| Date | Phase | Severity | Error / issue | Resolution |
|---|---|---|---|---|
| 2026-10-04 | 0 | INFO | Repository was empty when initialized; no pre-existing research files were available to inherit. | Created baseline research structure from the project protocol. |
| 2026-10-04 | 0 | INFO | Video rules include discretionary language (early exit and delayed adjustment) in addition to numeric delta triggers. | Preserve ambiguity explicitly; create deterministic baseline plus sensitivity variants before production backtest. |

| 2026-10-04 | 2 | ERROR | First GitHub Actions run 37211955857 failed at unit tests; production backtest was blocked. | Fix test environment before rerun. |
| 2026-10-04 | 2 | ERROR | 2025 monthly entry coverage was incomplete without December 2024 intraday data. | Add 2024 partition and reject uncovered cycles. |
| 2026-10-04 | 2 | ERROR | Exit-fill logic mixed timestamps with prices from earlier bars. | Redesign common fill timestamp logic. |
