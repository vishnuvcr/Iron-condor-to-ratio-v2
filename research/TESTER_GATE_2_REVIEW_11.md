# Tester Gate 2 Review 11 — Exchange Calendar Identity

Date: 2026-10-04
Role: Independent tester

## Verdict

**Gate 2: NOT PASSED / calendar identity requires explicit validation.**

## Finding F6 — NSE strategy, BSE session calendar

The revised continuity check uses `exchange_calendars` calendar `XBSE` to define expected sessions. The research instrument is NIFTY options on NSE, so the production gate should use the NSE trading calendar or an explicitly validated NSE-equivalent calendar.

The developer must not silently assume that BSE and NSE holiday/session schedules are identical for all dates in the 2021–2026 research window.

### Required remediation

Either:
1. use a maintained NSE trading calendar; or
2. create a versioned NSE holiday/session calendar from official NSE holiday notices and validate the exchange-calendar proxy against it for the full research window.

The calendar source/version must be recorded in the run manifest and in the research data protocol.

Official NSE holiday evidence currently confirms that NSE publishes annual equity/F&O trading holidays, including the 2026 holiday schedule. The final gate should rely on NSE rather than an undocumented proxy.

## Developer instruction

Resolve F6 or explicitly document and independently validate the proxy before Gate 2 submission.

## Tester instruction

After remediation, independently compare the session-calendar implementation against the stored/official NSE holiday schedule and reject the gate for any unexplained mismatch.
