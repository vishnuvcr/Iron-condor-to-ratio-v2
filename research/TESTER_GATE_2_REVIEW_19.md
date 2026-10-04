# Tester Gate 2 Review 19 — Partition Lead-In and Cross-Partition Deduplication

Date: 2026-10-04
Role: Independent tester

## Verdict

**Gate 2 remains CLOSED pending rerun.**

## Finding F13 — partition boundaries were incompatible with 32-DTE coverage

The first partitioned run built all six partitions successfully, but the coverage gate reported 0/69 complete cycles. The logs show valid monthly expiries were present but lacked the preceding 32-DTE observation window because each yearly partition began on January 1.

## Required remediation

Each partition must include a deterministic lead-in before the nominal calendar year—at least 32 calendar days, with margin—so the first expiry in that partition can be evaluated.

Because this creates overlap between adjacent partitions, the final assembly must deduplicate identical canonical keys deterministically while preserving source priority and provenance.

The June/August/September 2026 monthly gaps remain unresolved data-coverage findings and must not be hidden by this boundary fix.

## Developer instruction

Rerun the partitioned workflow with lead-in windows and deterministic cross-partition deduplication. Then resubmit the complete coverage report.

## Tester instruction

Verify that:
- all valid first-of-partition cycles now have the required lead-in;
- cross-partition duplicate keys are removed deterministically;
- row hashes/provenance remain stable;
- 2026 missing-month findings remain visible if no valid fallback exists.
