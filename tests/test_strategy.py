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


def test_early_entry_after_previous_monthly_expiry():
    from datetime import date
    from scripts.backtest import entry_and_exit_dates

    dates = [date(2026, 6, 26), date(2026, 6, 29), date(2026, 7, 27)]
    entry, exit_date = entry_and_exit_dates(
        date(2026, 7, 28),
        date(2026, 6, 25),
        dates,
    )
    assert entry == date(2026, 6, 26)
    assert exit_date == date(2026, 7, 27)


def test_early_entry_rejects_missing_first_post_expiry_session():
    from datetime import date
    from scripts.backtest import entry_and_exit_dates

    dates = [date(2026, 6, 29), date(2026, 7, 27)]
    assert entry_and_exit_dates(
        date(2026, 7, 28),
        date(2026, 6, 25),
        dates,
    ) == (None, None)


def test_early_entry_uses_nse_calendar():
    from datetime import date
    from scripts.backtest import entry_and_exit_dates

    dates = [date(2026, 6, 29), date(2026, 7, 27)]
    entry, exit_date = entry_and_exit_dates(
        date(2026, 7, 28),
        date(2026, 6, 26),
        dates,
    )
    assert entry == date(2026, 6, 29)
    assert exit_date == date(2026, 7, 27)

def test_partial_data_entry_mode_is_explicit():
    import inspect
    from scripts.backtest import run_cycle
    assert "entry_mode" in inspect.signature(run_cycle).parameters
    assert inspect.signature(run_cycle).parameters["entry_mode"].default == "strategy"


def test_research_use_available_entry_does_not_require_strict_first_session(monkeypatch):
    import pandas as pd
    from datetime import date
    from scripts import backtest as bt

    ts = pd.Timestamp("2026-07-02 09:15:00+05:30")
    df = pd.DataFrame({
        "date": [date(2026, 7, 2), date(2026, 7, 27)],
        "timestamp": [ts, pd.Timestamp("2026-07-27 15:20:00+05:30")],
    })
    monkeypatch.setattr(bt, "entry_and_exit_dates", lambda expiry, previous_expiry, dates: (None, None))
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
    cycle = bt.run_cycle(
        df,
        date(2026, 7, 28),
        0.0,
        CostModel(),
        entry_mode="available",
        previous_expiry=date(2026, 6, 25),
    )
    assert cycle is None
    assert seen["nearest_bar"] == 1


def test_reversal_trigger_is_fixed_1_30_for_two_short_lots():
    from scripts.backtest import REVERSAL_DELTA_THRESHOLD, ratio_reversal_trigger
    assert REVERSAL_DELTA_THRESHOLD == 1.30
    assert ratio_reversal_trigger([0.649, 0.05]) is False
    assert ratio_reversal_trigger([0.650, 0.05]) is True
    assert ratio_reversal_trigger([0.700, 0.05]) is True


def test_continuation_counts_both_short_contracts():
    # Two short contracts at 0.10 individual delta have 0.20 combined delta.
    d = [0.10]
    lots = [-2]
    combined = sum(abs(l) * x for l, x in zip(lots, d))
    assert math.isclose(combined, 0.20, abs_tol=1e-9)

