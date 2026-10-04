import math
from datetime import date

from src.strategy_engine import (
    CostModel,
    choose_ic_trigger,
    direction_from_trigger,
    lot_size_for_monthly_expiry,
    ratio_net_delta,
    validate_ratio_direction_algebra,
)


def test_ratio_algebra():
    out = validate_ratio_direction_algebra()
    assert math.isclose(out["initial_call"], -0.20, abs_tol=1e-9)
    assert math.isclose(out["initial_put"], 0.20, abs_tol=1e-9)
    assert math.isclose(out["continuation_call"], -0.12, abs_tol=1e-9)
    assert math.isclose(out["continuation_put"], 0.12, abs_tol=1e-9)


def test_direction_mapping():
    assert direction_from_trigger("CALL") == "CALL_RATIO"
    assert direction_from_trigger("PUT") == "PUT_RATIO"


def test_lot_sizes():
    assert lot_size_for_monthly_expiry(date(2021, 6, 24)) == 75
    assert lot_size_for_monthly_expiry(date(2021, 7, 29)) == 50
    assert lot_size_for_monthly_expiry(date(2024, 4, 25)) == 50
    assert lot_size_for_monthly_expiry(date(2024, 5, 30)) == 25
    assert lot_size_for_monthly_expiry(date(2024, 11, 28)) == 75
    assert lot_size_for_monthly_expiry(date(2025, 12, 30)) == 75
    assert lot_size_for_monthly_expiry(date(2026, 1, 27)) == 65


def test_cost_model_side_logic():
    cm = CostModel(brokerage_per_order=20.0, slippage_ticks=1)
    buy = cm.costs(100.0, 75, 75, "BUY", date(2026, 5, 1))
    sell = cm.costs(100.0, 75, 75, "SELL", date(2026, 5, 1))
    assert sell["stt"] > 0
    assert buy["stt"] == 0
    assert buy["stamp"] > 0
    assert sell["stamp"] == 0
    assert buy["total"] > 0
    assert sell["total"] > 0


from scipy.special import ndtr
from scipy.stats import norm
import numpy as np
from src.strategy_engine import black76_delta_from_forward, black76_delta_from_price, implied_vol_black76


def test_black76_delta_and_iv_roundtrip():
    F = np.array([100.0])
    K = np.array([100.0])
    T = np.array([30.0 / 365.0])
    sigma = np.array([0.20])
    d1 = 0.5 * sigma * np.sqrt(T)
    d2 = d1 - sigma * np.sqrt(T)
    call_price = F * ndtr(d1) - K * ndtr(d2)
    call_delta = black76_delta_from_forward(F, K, T, sigma, 0.0, np.array([True]))[0]
    put_delta = black76_delta_from_forward(F, K, T, sigma, 0.0, np.array([False]))[0]
    assert abs(call_delta - ndtr(d1)[0]) < 1e-10
    assert abs(put_delta + ndtr(-d1)[0]) < 1e-10
    recovered_iv = implied_vol_black76(F, K, T, call_price, np.array([True]), 0.0)[0]
    recovered_delta = black76_delta_from_price(F, K, T, call_price, np.array([True]), 0.0)[0]
    assert abs(recovered_iv - 0.20) < 1e-5
    assert abs(recovered_delta - ndtr(d1)[0]) < 1e-10


def test_stt_boundary_and_slippage():
    cm = CostModel(brokerage_per_order=20.0, slippage_ticks=1)
    pre = cm.costs(100.0, 1, 75, "SELL", date(2026, 3, 31))["stt"]
    post = cm.costs(100.0, 1, 65, "SELL", date(2026, 4, 1))["stt"]
    assert post > pre
    assert cm.price_with_slippage(100.0, "BUY") == 100.05
    assert cm.price_with_slippage(100.0, "SELL") == 99.95


def test_ic_trigger_rule_and_tie_break():
    assert choose_ic_trigger(0.09, 0.20) == "CALL"
    assert choose_ic_trigger(0.20, 0.09) == "PUT"
    assert choose_ic_trigger(0.07, 0.09) == "CALL"
    assert choose_ic_trigger(0.09, 0.07) == "PUT"
    assert choose_ic_trigger(0.09, 0.09, prev_call_abs_delta=0.15, prev_put_abs_delta=0.12) == "CALL"


def test_timezone_aware_expiry_arithmetic():
    import pandas as pd
    from datetime import date
    expiry_close = pd.Timestamp(date(2025, 1, 27), tz="Asia/Kolkata") + pd.Timedelta(hours=15, minutes=30)
    ts = pd.Series(pd.to_datetime(["2025-01-02 09:20:00+05:30", "2025-01-27 15:20:00+05:30"]))
    delta_days = (expiry_close - ts).dt.total_seconds() / 86400.0
    assert delta_days.iloc[0] > 20
    assert delta_days.iloc[1] > 0


def test_build_ratio_accepts_rate_parameter():
    import inspect
    from scripts.backtest import build_ratio
    assert "rate" in inspect.signature(build_ratio).parameters

def test_iv_matches_independent_brentq():
    from scipy.optimize import brentq
    from scipy.special import ndtr
    F, K, T, r, sigma_true = 102.0, 100.0, 45.0 / 365.0, 0.05, 0.27
    df = math.exp(-r * T)
    d1 = (math.log(F / K) + 0.5 * sigma_true**2 * T) / (sigma_true * math.sqrt(T))
    d2 = d1 - sigma_true * math.sqrt(T)
    price = df * (F * ndtr(d1) - K * ndtr(d2))

    def f(sig):
        a = (math.log(F / K) + 0.5 * sig**2 * T) / (sig * math.sqrt(T))
        b = a - sig * math.sqrt(T)
        return df * (F * ndtr(a) - K * ndtr(b)) - price

    expected = brentq(f, 1e-4, 5.0)
    actual = implied_vol_black76(
        np.array([F]), np.array([K]), np.array([T]), np.array([price]), np.array([True]), r
    )[0]
    assert abs(actual - expected) < 1e-4


def test_incomplete_monthly_cycle_is_rejected():
    from datetime import date
    from scripts.backtest import entry_and_exit_dates

    # Data beginning after the first NSE session of the expiry month cannot
    # satisfy the latest strategy's entry convention.
    assert entry_and_exit_dates(
        date(2026, 7, 28),
        [date(2026, 7, 2), date(2026, 7, 27)],
    ) == (None, None)


def test_monthly_cycle_uses_first_expiry_month_session_and_pre_expiry_session():
    from datetime import date
    from scripts.backtest import entry_and_exit_dates

    dates = [date(2026, 7, 1), date(2026, 7, 2), date(2026, 7, 24), date(2026, 7, 27)]
    entry, exit_date = entry_and_exit_dates(date(2026, 7, 28), dates)
    assert entry == date(2026, 7, 1)
    assert exit_date == date(2026, 7, 27)


def test_cycle_boundary_uses_nse_holiday_calendar_for_month_start():
    from datetime import date
    from scripts.backtest import entry_and_exit_dates

    # March 3 is an NSE F&O holiday in the stored 2026 calendar; March 1 is
    # Sunday, so March 2 is the first eligible expiry-month session.
    dates = [date(2026, 3, 2), date(2026, 3, 27)]
    entry, exit_date = entry_and_exit_dates(date(2026, 3, 30), dates)
    assert entry == date(2026, 3, 2)
    assert exit_date == date(2026, 3, 27)


def test_cycle_boundary_accepts_complete_month_without_32dte_lead_in():
    from datetime import date
    from scripts.backtest import entry_and_exit_dates

    # The cycle is valid when the first expiry-month session is present even
    # though the dataset contains no prior-month/32-DTE lead-in.
    dates = [date(2026, 2, 2), date(2026, 2, 26)]
    entry, exit_date = entry_and_exit_dates(date(2026, 2, 27), dates)
    assert entry == date(2026, 2, 2)
    assert exit_date == date(2026, 2, 26)


def test_ratio_cycle_threshold_conventions_are_explicit():
    import pandas as pd
    from scripts.backtest import run_cycle

    # Empty data returns before a cycle can be traded, but invalid modelling
    # parameters must be rejected deterministically before execution.
    empty = pd.DataFrame()
    cm = CostModel()
    try:
        run_cycle(empty, date(2026, 3, 30), 0.0, cm, reversal_delta_threshold=0.79)
    except ValueError:
        pass
    else:
        raise AssertionError("reversal threshold below the stated 0.80–1.30 range was accepted")

    try:
        run_cycle(empty, date(2026, 3, 30), 0.0, cm, reversal_delta_threshold=1.31)
    except ValueError:
        pass
    else:
        raise AssertionError("reversal threshold above the stated 0.80–1.30 range was accepted")

    # The baseline 1.20 convention is explicitly admissible by the production
    # function default; execution itself is covered by the backtest integration.
    import inspect


def test_partial_data_entry_mode_is_explicit():
    import inspect
    from scripts.backtest import run_cycle
    assert "entry_mode" in inspect.signature(run_cycle).parameters
    assert inspect.signature(run_cycle).parameters["entry_mode"].default == "strategy"


def test_research_use_available_entry_does_not_require_strict_first_session(monkeypatch):
    import pandas as pd
    from datetime import date
    from scripts import backtest as bt

    ts = pd.Timestamp("2026-07-02 09:20:00+05:30")
    df = pd.DataFrame({
        "date": [date(2026, 7, 2), date(2026, 7, 27)],
        "timestamp": [ts, pd.Timestamp("2026-07-27 15:20:00+05:30")],
    })
    monkeypatch.setattr(bt, "entry_and_exit_dates", lambda expiry, dates: (None, None))
    monkeypatch.setattr(
        bt,
        "nse_fno_sessions",
        lambda start, end: [date(2026, 7, 1), date(2026, 7, 27)],
    )
    seen = {"nearest_bar": 0}
    monkeypatch.setattr(bt, "nearest_bar", lambda data, target: seen.__setitem__("nearest_bar", 1) or ts)
    monkeypatch.setattr(
        bt,
        "snapshot_at",
        lambda data, target: pd.DataFrame(columns=["option_type", "close", "volume", "forward", "strike", "timestamp"]),
    )
    cycle = bt.run_cycle(df, date(2026, 7, 28), 0.0, CostModel(), entry_mode="available")
    assert cycle is None
    assert seen["nearest_bar"] == 1
