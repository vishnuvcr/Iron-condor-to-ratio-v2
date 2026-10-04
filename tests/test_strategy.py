import math
from datetime import date

from src.strategy_engine import (
    CostModel,
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
