# Tester Gate 2 Review 12 — NSE F&O Calendar Validation

Date: 2026-10-04
Role: Independent tester

## Verdict

**Gate 2: PENDING fresh CI and final artifact review.**

## Independent checks

### F6 remediation
The developer replaced the undocumented `XBSE` BSE calendar proxy with a versioned NSE F&O holiday file covering 2021–2026.

The holiday dates in the new file match the annual NSE F&O trading-holiday circulars checked independently for 2021, 2022, 2023, 2024, 2025 and 2026. The circulars are specifically for the Futures & Options department, which is the relevant segment for this NIFTY options study.

Annual official circular references checked:
- 2021: NSE/FAOP/46625
- 2022: NSE/FAOP/50561
- 2023: NSE/FAOP/54759
- 2024: NSE/FAOP/59723
- 2025: NSE/FAOP/65588
- 2026: NSE/FAOP/71777

The developer calendar contains 85 weekday/normal-session holidays across 2021–2026, while weekend-only holidays are not required as exclusions because the session generator independently excludes Saturdays and Sundays.

### Calendar-test review
The new unit tests cover:
- all six years represented;
- representative 2025 and 2026 F&O holidays;
- weekend exclusion;
- a 2023 date that appears in some capital-market holiday lists but is not an F&O holiday.

### Remaining Gate 2 conditions
The tester cannot approve Gate 2 yet because the fresh CI run must still demonstrate:
- source staging success;
- composite construction;
- expected-expiry completeness;
- interior NSE session continuity;
- CSV/Parquet reconciliation;
- full unit-test pass;
- no newly introduced production-data or provenance errors.

## Developer instruction

Keep Gate 2 closed until the current CI run completes. Submit the generated coverage, composite manifest, CSV reconciliation, and test results for final independent review.

## Tester instruction

After CI completion, independently verify the artifacts and reject the gate for any row-count, schema, hash, provenance, expiry-coverage, session-continuity, timestamp, or contract-integrity discrepancy.
