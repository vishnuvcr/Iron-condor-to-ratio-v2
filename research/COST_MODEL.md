# Cost Model

## Brokerage
Default baseline for a modern Paytm Money account: Rs 20 per executed F&O order, subject to the user's actual account tariff. Older account cohorts can have different legacy brokerage.

## Exchange / statutory charges
The implementation must apply the historical rate by trade date rather than a single timeless constant.

Verified current references:
- NSE equity-options transaction charge: Rs 3,553 per crore of premium traded per side from 2026-03-01.
- NSE levy page: STT on sale of an option is 0.15% from 2026-04-01 and 0.10% through 2026-03-31.
- GST: 18% on broker services/eligible charges.
- SEBI turnover fee: Rs 10 per crore of securities turnover.
- Equity-option stamp duty: 0.003% on buyer.

These values will be versioned by effective date in code and checked against official sources before production runs.

## Slippage
Because historical bid/ask is not guaranteed in public datasets, results must report at least:
- zero-slippage reference;
- baseline conservative slippage, documented in option premium points or percentage;
- stress slippage.

No result may be presented as execution-realistic without showing the slippage assumption.
