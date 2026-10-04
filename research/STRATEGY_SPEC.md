# Strategy Specification — Gate 1 Revision

## Source-derived rules

The supplied transcript states that the initial position is a monthly-expiry Iron Condor with short call/put around 0.30 delta and long call/put around 0.10 delta.

Transition: when either IC short leg reaches/about 0.10 delta, exit the entire Iron Condor and transition to a directional ratio spread.

Direction:
- Market moving down -> call-side ratio.
- Market moving up -> put-side ratio.

Initial ratio:
- Down/call side: long 1 call at about 0.50 delta; short 2 calls at about 0.40 delta; long 1 call at about 0.10 delta.
- Up/put side: long 1 put at about 0.50 delta; short 2 puts at about 0.40 delta; long 1 put at about 0.10 delta.

Continuation:
- Track the combined absolute delta of the two short ratio legs.
- When it falls to about 0.20, exit the whole ratio and rebuild in the same direction:
  - long 1 at about 0.40 delta;
  - short 2 at about 0.30 delta;
  - long 1 hedge at about 0.08 delta.

Reversal:
- When the combined absolute delta of the two short ratio legs rises to about 1.20–1.30, exit the whole ratio and reverse direction.
- The source uses the initial 0.50/0.40/0.10 construction on the new direction.

The source also discusses discretionary profit-taking and delayed adjustments. Those are excluded from the rules-only baseline and tested as separate variants.

## Deterministic rules-only baseline

### Date and entry
1. Use NIFTY monthly expiries defined as the latest NIFTY option expiry date in each calendar month present in the validated dataset.
2. Select each monthly expiry E.
3. The baseline entry date is the first available trading date on or after E minus 32 calendar days.
4. Initial IC decision time is 09:20 IST on that entry date. If 09:20 is absent, use the first available minute at or after 09:20.
5. The baseline has no discretionary entry-date shifting. 30-DTE and 31-DTE versions are sensitivity runs, not baseline.

### Delta model
Delta is a historical-model estimate, never a future/current-data lookup.

Primary baseline model:
- Black-76 with continuously compounded risk-free rate r = 0 for delta selection.
- Forward price F at each timestamp is estimated from call-put parity:
  F_i = K + C_i - P_i
  for strikes with simultaneously positive call and put prices.
- At each timestamp, take all strikes with both call and put volume > 0 and positive premium; use the cross-sectional median active strike K_med, retain paired strikes with 0.90*K_med <= K_i <= 1.10*K_med, and take the median F_i from those pairs.
- Implied volatility is solved numerically from the observed option close and the estimated forward.
- For a general rate r, DF = exp(-rT), call delta = DF*N(d1), and put delta = -DF*N(-d1). For the baseline r=0, these reduce to N(d1) and -N(-d1).
- If the observed premium is at/below intrinsic value within a small numerical tolerance, use the limiting delta rather than an unstable IV.
- If IV cannot be solved, that contract is ineligible for delta targeting on that timestamp.

Sensitivity models:
- r = 5% and r = 6%, using DF=exp(-rT) and forward parity F_i = K_i + (C_i-P_i)/DF.
- Where a validated source supplies IV/Greeks directly, it may be used as a cross-check, not as a silent replacement.

### Delta target selection
At a decision timestamp, select among valid monthly-expiry contracts:
- positive premium;
- positive volume on the signal bar;
- valid model delta;
- strike within 15% of estimated forward (0.85*F <= K <= 1.15*F);
- closest absolute delta to the target.

The engine records target delta, achieved delta, strike, and selection timestamp.

### Signal detection and execution
To prevent look-ahead:
- Signals are evaluated from the fully formed 1-minute bar at time t.
- Entry/replacement/closing orders caused by that signal execute at the next available 1-minute bar OPEN.
- Contract selection for the replacement is based on information available at time t, not time t+1.
- Planned end-of-trade exits do not depend on the bar price and may execute at the scheduled bar CLOSE.

### State machine
States: IC_ACTIVE and RATIO_ACTIVE.

IC_ACTIVE:
- Track the held short call and short put absolute deltas.
- If neither <= 0.10, hold.
- If exactly one crosses <= 0.10, exit all four IC legs at t+1 open and build:
  - call ratio if short call is the trigger;
  - put ratio if short put is the trigger.
- If both cross <= 0.10 on the same signal bar, choose the leg with the smaller absolute delta; if tied within tolerance, record a tie and choose the direction indicated by the larger absolute change from the previous signal bar.

RATIO_ACTIVE:
- Let S be the sum of absolute deltas of the two short ratio legs.
- If S <= 0.20, exit all ratio legs at t+1 open and rebuild in the same direction using 0.40/0.30/0.08.
- Else if S >= 1.20, exit all ratio legs at t+1 open and reverse using 0.50/0.40/0.10.
- Otherwise hold.
- Only one replacement can be generated from a signal bar.

### End-of-cycle exit
Rules-only baseline:
- Exit any remaining position at 15:20 IST on the last non-expiry trading session for the monthly cycle.
- This is an explicit modelling assumption because the source demonstrates both pre-expiry profit-taking and occasional expiry-day continuation.
- Expiry-day carry is a separate sensitivity variant.

### Costs
Every executed order incurs:
- brokerage;
- NSE transaction charge;
- SEBI turnover fee;
- GST on brokerage/exchange/SEBI charges where applicable;
- stamp duty on the buyer;
- STT on option sales at the historical rate applicable on the trade date;
- slippage.

Modern Paytm Money baseline brokerage is Rs 20 per executed F&O order; Rs 10 and Rs 15 are sensitivity cases because public Paytm Money pages contain legacy account cohorts with lower brokerage.

### Slippage
Baseline: adverse 1 NIFTY option tick on every fill, with tick = Rs 0.05 and no fill below zero.
Stress: adverse 2 ticks.
Reference: zero slippage.

For a buy, fill = max(0, reference price + slippage_ticks*0.05).
For a sell, fill = max(0, reference price - slippage_ticks*0.05).

### Lot sizes
Lot size is mapped by the actual contract/expiry regime, not by a simple trade-date constant.
For the main production window beginning 2025-01-01:
- monthly expiries through 2025-12-30 use 75;
- monthly expiries from 2026-01-27 use 65.
A separate pre-2025 segment is reported only with an explicit NSE contract-file lot-size mapping.

### Benchmarks
At minimum:
1. Static monthly 0.30/0.10 Iron Condor using the same entry and exit convention, with no ratio conversion.
2. Rules-only strategy with zero slippage.
3. Rules-only strategy with 1-tick baseline and 2-tick stress slippage.
4. Brokerage sensitivity Rs 10/Rs 15/Rs 20.
5. Delta-model sensitivity r = 0%/5%/6%.

## Discretionary variants
The following are never mixed into the baseline:
- early profit-taking thresholds;
- delayed adjustment after a trigger;
- expiry-day carry;
- discretionary hedge shifting beyond the numeric target.

Each variant must be a separate run manifest and separately labeled.

## Data-quality and no-look-ahead requirements
- A trade cannot use a bar before it is available.
- A replacement contract cannot be selected using t+1 prices.
- A missing signal-bar delta invalidates that signal rather than being forward-filled.
- Contract prices cannot be forward-filled across trading gaps for execution.
- Every skipped, unfilled, or anomalous order must be logged.

## Gate 1 acceptance criteria
1. Every source-derived numeric rule is mapped to an explicit deterministic rule.
2. Entry timing, signal timing, execution timing, exit timing, delta model, slippage, and cost model are deterministic.
3. Discretionary statements are separated from the baseline.
4. Mathematical direction and lot counts are unit-testable.
5. No future information enters contract selection or trigger detection.
