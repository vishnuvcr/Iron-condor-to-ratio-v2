# Tester Gate 2 Review 13 — Requested Window Coverage

Date: 2026-10-04
Role: Independent tester

## Verdict

**Gate 2: NOT PASSED / requested-window coverage must be enforced.**

## Finding F7 — Primary staging does not span the full requested month range

The successful staging output for the 2021-01-01 to 2026-09-30 window reported **64** selected thetrademarkk monthly files. The inclusive calendar window contains **69** calendar months, so five months are absent from the primary source selection.

A gate that derives the expected expiry set only from staged primary files can therefore hide missing historical months.

## Required remediation

The coverage gate must derive the expected calendar months independently from the requested `start` and `end` recorded in the staging manifest. For every requested month:

1. identify the production monthly-expiry candidate in the composite;
2. accept the month only if the composite contains an explicit/resolved expiry with full 32-DTE-to-pre-expiry coverage and session continuity;
3. allow a lower-priority source to satisfy a month when it provides explicit expiry provenance;
4. fail Gate 2 for any requested month with no defensible monthly expiry candidate.

The report should separately show whether the primary source supplied the month versus a fallback source.

## Developer instruction

Implement F7 without importing tester-side implementation code, rerun CI, and submit the resulting month-coverage artifact.

## Tester instruction

Independently verify that a deliberately absent primary month is still a gate failure when no valid fallback exists, and that a valid fallback can legitimately satisfy a primary-source gap.
