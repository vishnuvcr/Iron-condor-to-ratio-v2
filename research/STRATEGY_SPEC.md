# Strategy Specification — Gate 1 Draft

## Source-derived rules

The source transcript states that the initial position is a monthly-expiry Iron Condor with short call/put around 0.30 delta and long call/put around 0.10 delta.

The transition rule is: when either Iron Condor short leg reaches approximately 0.10 delta, exit the entire Iron Condor and transition to a directional ratio spread.

Direction mapping:
- Market moving down -> call-side ratio spread.
- Market moving up -> put-side ratio spread.

Initial ratio construction:
- Down / call-side: long 1 call at about 0.50 delta; short 2 calls at about 0.40 delta; long 1 call at about 0.10 delta.
- Up / put-side: long 1 put at about 0.50 delta; short 2 puts at about 0.40 delta; long 1 put at about 0.10 delta.

Trend-continuation reset:
- Track the combined absolute delta of the two short ratio legs.
- The source describes the initial combined short-leg delta as about 0.80.
- If it falls to about 0.20, exit the whole ratio spread and rebuild in the same direction with:
  - long 1 option at about 0.40 delta;
  - short 2 options at about 0.30 delta;
  - long 1 hedge at about 0.08 delta.

Reversal reset:
- If the combined absolute delta of the two short ratio legs rises from about 0.80 to roughly 1.20–1.30, exit the entire ratio spread and switch to the opposite directional side.
- The source then uses the initial ratio construction on the opposite side.

The source also discusses taking profits early and sometimes delaying a delta-triggered adjustment, but does not define a single numeric rule. Those are therefore not allowed in the deterministic baseline.

## Deterministic baseline

### Contract cycle
1. Use NIFTY monthly expiries.
2. For each monthly expiry, enter the Iron Condor on the first available trading session approximately 30–32 calendar days before expiry, using the first executable timestamp after the chosen entry time.
3. Never use future information to select the expiry or strikes.
4. Close all remaining positions before expiry in the baseline. A separate expiry-day variant may be tested only after the baseline is validated.

### Delta convention
Use absolute option delta for strike selection:
- call delta is positive;
- put delta is negative;
- selection targets are absolute delta values.

Delta must be computed from historical option data using a documented pricing model or a validated supplied IV/Greeks field. No current/future chain data may be used.

### Strike selection
At a decision timestamp, select the listed contract for the relevant monthly expiry whose absolute delta is closest to the target, subject to:
- positive/valid premium;
- valid timestamp;
- sufficient liquidity/volume if a liquidity filter is enabled;
- no look-ahead.

The implementation must record both target and achieved delta.

### Entry and adjustment prices
Use the nearest available 1-minute bar at or immediately after the decision timestamp. Baseline fill is the close/mid proxy available in the dataset, plus the configured slippage model. Stress variants add adverse slippage by trade direction.

### State machine
States:
- IC_ACTIVE
- RATIO_ACTIVE

IC_ACTIVE:
- If neither short leg crosses the transition threshold, maintain positions.
- If a short leg crosses 0.10 absolute delta, close all IC legs and enter the ratio on the corresponding directional side.

RATIO_ACTIVE:
- If the combined absolute delta of the two short legs <= 0.20, close all ratio legs and rebuild the same direction with 0.40/0.30/0.08 targets.
- Else if combined absolute short-leg delta >= 1.20, close all ratio legs and reverse using 0.50/0.40/0.10 targets.
- Else hold.
- Evaluate continuation before reversal only if a timestamp could satisfy both; this tie case must be recorded as a deterministic engine event and tested. The baseline uses the first condition met in timestamp order, not a hindsight choice.

### Exit
Baseline exit:
- close all open positions at the end of the last non-expiry trading session if a position remains open;
- no automatic profit target;
- no discretionary early exit;
- no expiry-day trading.

This isolates the strategy's numeric mechanics from the video's discretionary profit-taking language.

## Important ambiguities to test separately
1. Entry timing: 30 DTE vs 32 DTE.
2. Entry session time.
3. Transition trigger: 0.10 exact crossing vs <= 0.10.
4. Continuation trigger: 0.20 vs 0.18/0.22.
5. Reversal trigger: 1.20 vs 1.25 vs 1.30.
6. Initial ratio targets around 0.50/0.40/0.10.
7. Continuation ratio targets around 0.40/0.30/0.08.
8. Profit-taking at fixed portfolio returns (e.g. 8%, 10%, 12%, 15% of a declared capital base).
9. Delayed adjustment policy.
10. Carrying to expiry vs last non-expiry day.

## Non-negotiable accounting rules
- One option lot per long leg.
- Two option lots on each short ratio leg.
- Lot size is date-dependent and must be sourced from NSE. NIFTY moved to 75 for new index-derivative contracts from 2024-11-20, and to 65 for revised contracts from 2025-10-03; the exact effective contract series must be mapped by expiry/introduction date.
- Every opening and closing order incurs brokerage and applicable charges.
- STT is charged according to the historical rules on the relevant side.
- No physical settlement is assumed for this baseline because positions are closed before expiry.

## Benchmarks
At minimum:
1. Static monthly Iron Condor with the same 0.30/0.10 construction and no ratio conversion.
2. The strategy with zero slippage.
3. The strategy with baseline and stress slippage.
4. Where data supports it, a simple market benchmark reported separately rather than mixed with option P&L.

## Acceptance criteria for Gate 1
- Every source-derived numeric rule is mapped to code.
- Every discretionary sentence is explicitly classified as deterministic, excluded, or sensitivity-tested.
- No hidden assumption about entry timing, expiry-day behaviour, or profit-taking.
- Unit tests cover delta sign convention, direction mapping, ratio net delta, trigger ordering, lot counts, and position closing.
