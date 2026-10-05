# Strategy Specification — Latest User-Defined Strategy Only

## Authority
The only authoritative strategy specification for the backtest is the user's latest explicit rule set in chat. The initial transcript and any earlier 32-DTE protocol are ignored.

## Strategy rules

### Initial position — monthly Iron Condor
For the selected NIFTY monthly expiry:
- Sell 1 × 0.30-delta Call.
- Buy 1 × 0.10-delta Call hedge.
- Sell 1 × 0.30-delta Put.
- Buy 1 × 0.10-delta Put hedge.

The initial position is neutral/range-oriented.

### Transition trigger
Continuously monitor the deltas of the two **short Iron Condor legs only**.

When either short leg reaches approximately 0.10 delta:
1. Exit the entire Iron Condor.
2. Determine direction from the breakout side.
3. Enter the corresponding directional Ratio Spread.
4. Do not return to the Iron Condor during that strategy cycle.

### Directional Ratio Spread

#### Falling market
Deploy a Call Ratio Spread:
- Buy 1 × 0.50-delta Call.
- Sell 2 × 0.40-delta Calls.
- Buy 1 × 0.10-delta Call hedge.

#### Rising market
Deploy a Put Ratio Spread:
- Buy 1 × 0.50-delta Put.
- Sell 2 × 0.40-delta Puts.
- Buy 1 × 0.10-delta Put hedge.

### Ratio continuation / profit-taking
If the trend continues and the **combined absolute delta of the two short ratio legs** reaches approximately 0.20:
1. Exit the current Ratio Spread.
2. Rebuild a new Ratio Spread in the same direction:
   - Buy 1 × 0.40-delta option.
   - Sell 2 × 0.30-delta options.
   - Buy 1 × 0.08-delta hedge.

### Ratio reversal / stop-loss
If the market reverses and the **two short contracts together reach 1.30 absolute delta** — equivalently, 2 × the individual absolute delta of the short option reaches 1.30 (individual delta = 0.65) —:
1. Exit the current Ratio Spread.
2. Reverse direction.
3. Build the opposite-direction initial Ratio Spread:
   - Buy 1 × 0.50 delta.
   - Sell 2 × 0.40 delta.
   - Buy 1 × 0.10 delta hedge.

## Explicit exclusions
- No 32-DTE rule.
- No rule from the initial transcript is authoritative.
- No discretionary rule is silently converted into a new rule.
- No look-ahead information may be used.

## Deterministic implementation conventions requiring validation
The supplied strategy does not specify the exact treatment when both IC short legs trigger simultaneously. The user has clarified that the initial Iron Condor is entered **as early as possible after the previous monthly expiry**, using the earliest normal NSE F&O session available for the new monthly cycle. The backtest uses the first available 1-minute bar after market open to select contracts and then executes on the next common executable bar to avoid look-ahead. These are modelling conventions only and must not alter the strategy rules.

For the reversal rule, the user has clarified that **1.30 applies to the two short contracts**, so the trigger is 2 × the individual absolute delta. No alternative threshold, range, combined-delta interpretation, optimization, or sensitivity grid is substituted.

Where the data cannot distinguish an exact discretionary action described by the video, the implementation must record the ambiguity and use the least-assumptive deterministic interpretation without creating a new trading rule.

Continuation remains the specified approximately-0.20 combined absolute delta of the two short ratio legs. No alternative continuation threshold is tested.

## Delta model
Use the existing validated Black-76/parity framework for historical delta estimation, with the model and rate assumptions explicitly reported. Delta selection records target, achieved delta, strike, timestamp, and model parameters.

## Execution
Signals use completed information at timestamp t and execute at the next available minute-bar open unless a separate modelling convention is explicitly documented.

## Costs
All executed orders include brokerage, exchange/statutory charges, taxes where applicable, and explicit slippage scenarios using the repository's validated cost model.

## Benchmarks
At minimum:
1. Static monthly 0.30/0.10 Iron Condor under the same entry convention.
2. Latest strategy with zero slippage.
3. Latest strategy with baseline and stress slippage.
4. Cost/brokerage sensitivities.
5. Delta-model sensitivities.

## Research acceptance
A result is not accepted as a strategy result unless the underlying data provide complete observations for the contracts actually required by each simulated lifecycle and the independent tester approves the implementation.
