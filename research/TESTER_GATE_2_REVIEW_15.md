# Tester Gate 2 Review 15 — Cross-Source Expiry Dtype

Date: 2026-10-04
Role: Independent tester

## Verdict

**Gate 2: NOT PASSED; code regression requires remediation, then fresh CI.**

## Finding F9 — mixed expiry types in composite merge

CI run 37225753011 installed current Pandas 3.0.6 and failed 1 of 33 unit tests:
`tests/test_composite.py::test_symbol_month_resolves_against_explicit_source`.

The failure occurred because cross-source expiry resolution produced mixed Python `date` and Pandas `Timestamp` objects. Pandas 3.x refused to order those mixed types during the composite sort.

This is a reproducibility/code-integrity issue because the same source combination that should be accepted by the research protocol could fail depending on dependency version.

## Required remediation

Normalize the canonical composite expiry dtype immediately before source frames are concatenated, and add a regression test that combines an explicit-expiry frame with a symbol-derived/resolved-expiry frame.

Do not alter source-priority, expiry provenance, or pricing logic as part of the fix.

## Developer instruction

The isolated developer branch must record the fix, rerun CI, and submit the full test result for independent review.

## Tester instruction

After the rerun, independently verify that:
- all unit tests pass;
- mixed date/Timestamp expiry values no longer occur in the canonical composite;
- provenance remains unchanged;
- no Gate 2 data-quality condition has been weakened.
