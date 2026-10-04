# Tester Gate 2 Review 14 — Monthly Expiry Candidate Integrity

Date: 2026-10-04
Role: Independent tester

## Verdict

**Gate 2: NOT PASSED / fallback monthly-expiry discrimination required.**

## Finding F8 — Max observed expiry can be a weekly expiry

The requested-window coverage code currently uses the latest observed expiry in a calendar month as the fallback candidate when the primary monthly file is absent.

For a sparse fallback source, the latest available contract could still be a weekly expiry that precedes the true monthly expiry. Treating it as the monthly cycle would satisfy the month gate without proving the intended monthly contract exists.

## Required remediation

For fallback-only months, require an independently defensible monthly-expiry signature in addition to explicit expiry provenance. A practical deterministic rule for this study is that the candidate expiry must fall within the final six calendar days of the month (the NIFTY monthly expiry schedules in the validated period place monthly expiries there, while earlier weekly expiries are farther away).

The coverage report should record whether the candidate came from the primary manifest or the fallback monthly-expiry inference, and a fallback candidate that fails the monthly-date test must be marked incomplete.

## Developer instruction

Implement F8 without copying tester implementation code, add a regression test for a month containing only an earlier weekly fallback expiry, rerun CI, and resubmit.

## Tester instruction

Verify that a fallback weekly expiry cannot satisfy a requested monthly cycle, while a genuine monthly fallback near month-end can.
