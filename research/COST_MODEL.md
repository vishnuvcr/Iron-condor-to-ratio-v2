# Cost Model

## Brokerage

Baseline research assumption: **₹20 per executed F&O order**, representing the modern Paytm Money tariff used for this study. Paytm Money states that historical/account-specific tariffs can differ, so ₹20/order is a declared research baseline, not a universal claim for every account cohort.

## Exchange / statutory charges

For the published fixed-1.30 research-use run, the exchange transaction-cost baseline is a **current-rate retail execution assumption applied consistently across the historical price series**, not a reconstruction of the broker/exchange member tariff that would have applied in each historical year.

Baseline values:

- NSE equity-options transaction charge: **₹3,553 per crore of traded option premium per side**, effective from 2026-03-01.
- STT on sale of an option: **0.15% from 2026-04-01 and 0.10% through 2026-03-31**.
- SEBI turnover fee: **₹10 per crore**.
- Equity-option stamp duty: **0.003% on the buyer**.
- GST: **18% on applicable brokerage/service charges**.

The final run uses these baseline assumptions to answer a clean research question: what would the historical strategy outcome look like under a consistent modern retail execution-cost environment?

This choice is now explicitly labelled so the study does not imply that the exact historical Paytm Money/NSE invoice would have matched every year.

Official references:
- NSE transaction-charge circular: https://nsearchives.nseindia.com/content/circulars/FA73061.pdf
- NSE STT schedule: https://www.nseindia.com/static/products-services/equity-derivatives-securities-transaction-tax
- NSE statutory/levy schedule: https://www.nseindia.com/static/invest/first-time-investor-sebi-turnover-fees-stt-other-levies
- Paytm Money pricing material: https://www.paytmmoney.com/blog/all-new-paytm-money-updates-revisions-and-more/

## Slippage

The published baseline uses **one adverse option tick per executed order**, with tick size ₹0.05.

Independent audit of the stored order log also reconstructs a **zero-slippage reference** without rerunning the strategy:

- baseline gross P&L with one-tick slippage: **−₹3,821.50**;
- slippage drag: **₹1,950.00**;
- gross P&L before slippage: **−₹1,871.50**.

Therefore the negative gross result is not created by the one-tick slippage assumption.

A stress-slippage run was not promoted because the study is explicitly restricted to the fixed user-defined strategy and the final research-use result is already negative before transaction costs and before the one-tick slippage drag.
