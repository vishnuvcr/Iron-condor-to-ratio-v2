# Developer / Tester Protocol

## Developer branch
The developer implements the research plan, strategy engine, data pipeline, workflows, and documentation.

## Tester branch
The tester is independent. The tester may inspect the developer branch but must not reuse/copy its implementation code into tester-side test code. Tester work consists of independently derived checks, expected-value tests, invariant checks, and review reports.

## Gates
1. Foundation gate: repo structure and role separation.
2. Specification gate: deterministic state machine with no material ambiguity hidden.
3. Data gate: provenance, coverage, quality checks, caching, and leakage checks.
4. Cost gate: brokerage, STT, exchange charges, SEBI fee, GST, stamp duty, slippage.
5. Engine gate: unit tests and accounting invariants.
6. Backtest gate: approved run manifest and successful independent verification.
7. Statistical gate: robust reporting and sensitivity analysis.
8. Manuscript gate: complete research record.

The developer must not declare a phase passed until a tester report exists for that gate.
