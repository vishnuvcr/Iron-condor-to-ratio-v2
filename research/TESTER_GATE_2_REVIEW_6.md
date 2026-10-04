# Tester Gate 2 Review 6 — Composite Dataset Path

Date: 2026-10-04
Role: Independent tester

## Verdict

Gate 2: NOT PASSED. The composite design is directionally correct and materially improves the research path, but the current implementation still requires one provenance safeguard and one executable coverage safeguard before composite results can be accepted.

## Independent checks

### 1. Whole-row fallback is correct
The composite builder rejects invalid OHLCV rows and selects a complete lower-priority row on the exact canonical key. It does not average prices or splice OHLC fields from multiple sources. This is consistent with the research protocol.

### 2. OI supplementation is appropriately isolated
OI may be supplemented from a lower-priority exact-key source while retaining the higher-priority source price row. This is acceptable because OI is not a baseline trading signal, provided the source field is preserved.

### 3. Canonical-key handling is appropriate
Timestamp + expiry + strike + option type is the correct minimum contract-minute identity for this strategy. Timestamp normalization to IST is required and is present.

## Findings requiring remediation

### F1 — Inferred expiry needs explicit provenance and a promotion guard
The Cloud Trader/Shoonya free sample schema is documented as Symbol + Date + Time + OHLCV + OI rather than an explicit expiry field. The current composite code infers expiry from the maximum observed timestamp for a symbol.
That inference is acceptable only as a provisional mapping. It can be wrong if a sample ends before the actual contract expiry. The resulting row could otherwise appear internally consistent while carrying the wrong expiry date.
Required remediation: add an explicit expiry_source or expiry_confidence field, mark such rows as INFERRED_LAST_OBSERVED, and prevent an inferred-only expiry from becoming a production cycle unless an independent source confirms the expiry date.

### F2 — Composite cycle coverage must report source contribution
The current coverage check reports expiry span but does not yet show whether a cycle required observations from the primary source, fallback source, or a mixture.
Required remediation: add per-expiry source contribution counts and a flag showing whether any selected cycle relies on fallback rows.

### F3 — Composite-specific backtest test
The engine has been wired to consume the composite file, but there is not yet a focused unit test proving that composite expiry discovery works, an exact-key fallback row reaches the backtest loader, and a non-complete inferred expiry is rejected.
Required remediation: add deterministic tests for those three cases.

## Positive observations
- No interpolation or forward-filling is used.
- Overlapping rows are audited rather than averaged.
- File hashes and source revisions are retained.
- Free-source research remains separated from paid-source assumptions.

## Gate restriction
Do not promote composite P&L or any historical performance metric until F1–F3 are corrected and a fresh automated run is independently reviewed.

## Developer instruction
Developer: implement F1–F3, rerun the complete automated workflow, and submit the resulting composite manifest, cycle coverage, source contribution report, and CI outputs for Gate 2 re-review.

## Tester instruction
Remain on the isolated tester branch and recheck the composite provenance, cycle coverage, and backtest integration independently after the developer resubmits.