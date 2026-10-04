from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, date, time, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import math
import numpy as np
import pandas as pd
from scipy.special import ndtr
from scipy.stats import norm


TICK = 0.05


@dataclass
class CostModel:
    brokerage_per_order: float = 20.0
    slippage_ticks: int = 1
    exchange_rate: float = 3553 / 10_000_000
    sebi_rate: float = 10 / 10_000_000
    gst_rate: float = 0.18
    stamp_rate: float = 0.00003
    stt_rate_pre_2026_04_01: float = 0.001
    stt_rate_from_2026_04_01: float = 0.0015

    def stt_rate(self, trade_date: date) -> float:
        return self.stt_rate_from_2026_04_01 if trade_date >= date(2026, 4, 1) else self.stt_rate_pre_2026_04_01

    def price_with_slippage(self, price: float, side: str) -> float:
        slip = self.slippage_ticks * TICK
        if side == "BUY":
            return max(0.0, price + slip)
        return max(0.0, price - slip)

    def costs(self, price: float, quantity: int, lot_size: int, side: str, trade_date: date) -> Dict[str, float]:
        turnover = abs(price * quantity * lot_size)
        brokerage = self.brokerage_per_order
        exchange = turnover * self.exchange_rate
        sebi = turnover * self.sebi_rate
        stt = turnover * self.stt_rate(trade_date) if side == "SELL" else 0.0
        stamp = turnover * self.stamp_rate if side == "BUY" else 0.0
        gst = self.gst_rate * (brokerage + exchange + sebi)
        total = brokerage + exchange + sebi + stt + stamp + gst
        return {
            "brokerage": brokerage,
            "exchange": exchange,
            "sebi": sebi,
            "stt": stt,
            "stamp": stamp,
            "gst": gst,
            "total": total,
        }


def monthly_expiries(expiries: List[date]) -> List[date]:
    vals = sorted(set(expiries))
    out: Dict[Tuple[int, int], date] = {}
    for e in vals:
        out[(e.year, e.month)] = max(out.get((e.year, e.month), e), e)
    return sorted(out.values())


def lot_size_for_monthly_expiry(expiry: date) -> int:
    # Production research window begins 2025.
    # NSE circular: 75 through 2025-12-30 monthly expiry; 65 from 2026-01-27.
    if expiry <= date(2025, 12, 30):
        return 75
    return 65


def black76_delta_from_forward(
    forward: np.ndarray,
    strike: np.ndarray,
    t: np.ndarray,
    sigma: np.ndarray,
    rate: float,
    is_call: np.ndarray,
) -> np.ndarray:
    df = np.exp(-rate * t)
    sqrt_t = np.sqrt(np.maximum(t, 1e-12))
    d1 = (np.log(np.maximum(forward, 1e-12) / np.maximum(strike, 1e-12)) + 0.5 * sigma**2 * t) / (np.maximum(sigma, 1e-8) * sqrt_t)
    call_d = df * ndtr(d1)
    put_d = -df * ndtr(-d1)
    return np.where(is_call, call_d, put_d)


def implied_vol_black76(
    forward: np.ndarray,
    strike: np.ndarray,
    t: np.ndarray,
    price: np.ndarray,
    is_call: np.ndarray,
    rate: float,
    max_iter: int = 12,
) -> np.ndarray:
    forward = np.asarray(forward, dtype=float)
    strike = np.asarray(strike, dtype=float)
    t = np.asarray(t, dtype=float)
    price = np.asarray(price, dtype=float)
    is_call = np.asarray(is_call, dtype=bool)
    df = np.exp(-rate * t)
    sqrt_t = np.sqrt(np.maximum(t, 1e-12))

    intrinsic_call = df * np.maximum(forward - strike, 0.0)
    intrinsic_put = df * np.maximum(strike - forward, 0.0)
    intrinsic = np.where(is_call, intrinsic_call, intrinsic_put)
    upper = np.where(is_call, df * forward, df * strike)

    valid = (
        np.isfinite(forward) & np.isfinite(strike) & np.isfinite(t) & np.isfinite(price)
        & (forward > 0) & (strike > 0) & (t > 0)
        & (price > intrinsic + 1e-7) & (price < upper - 1e-7)
    )

    sigma = np.full_like(price, 0.30)
    sigma = np.clip(sigma, 0.01, 5.0)

    for _ in range(max_iter):
        d1 = (np.log(np.maximum(forward, 1e-12) / np.maximum(strike, 1e-12)) + 0.5 * sigma**2 * t) / (np.maximum(sigma, 1e-8) * sqrt_t)
        d2 = d1 - sigma * sqrt_t
        call_model = df * (forward * ndtr(d1) - strike * ndtr(d2))
        put_model = df * (strike * ndtr(-d2) - forward * ndtr(-d1))
        model = np.where(is_call, call_model, put_model)
        vega = df * forward * norm.pdf(d1) * sqrt_t
        step = np.where(vega > 1e-10, (model - price) / vega, 0.0)
        next_sigma = np.clip(sigma - step, 1e-4, 5.0)
        sigma = np.where(valid, next_sigma, sigma)

    d1 = (np.log(np.maximum(forward, 1e-12) / np.maximum(strike, 1e-12)) + 0.5 * sigma**2 * t) / (np.maximum(sigma, 1e-8) * sqrt_t)
    d2 = d1 - sigma * sqrt_t
    call_model = df * (forward * ndtr(d1) - strike * ndtr(d2))
    put_model = df * (strike * ndtr(-d2) - forward * ndtr(-d1))
    model = np.where(is_call, call_model, put_model)
    residual = np.abs(model - price)
    valid = valid & (residual <= 0.02)

    # Return the solved implied volatility; delta from an observed premium is computed separately.
    sigma = np.where(valid, sigma, np.nan)
    return sigma


def black76_delta_from_price(
    forward: np.ndarray,
    strike: np.ndarray,
    t: np.ndarray,
    price: np.ndarray,
    is_call: np.ndarray,
    rate: float,
) -> np.ndarray:
    sigma = implied_vol_black76(forward, strike, t, price, is_call, rate)
    df = np.exp(-rate * t)
    sqrt_t = np.sqrt(np.maximum(t, 1e-12))
    safe_sigma = np.maximum(np.nan_to_num(sigma, nan=0.0), 1e-8)
    d1 = (
        np.log(np.maximum(forward, 1e-12) / np.maximum(strike, 1e-12))
        + 0.5 * safe_sigma**2 * t
    ) / (safe_sigma * sqrt_t)
    call_delta = df * ndtr(d1)
    put_delta = -df * ndtr(-d1)
    delta = np.where(is_call, call_delta, put_delta)

    df = np.exp(-rate * t)
    intrinsic_call = df * np.maximum(forward - strike, 0.0)
    intrinsic_put = df * np.maximum(strike - forward, 0.0)
    intrinsic = np.where(is_call, intrinsic_call, intrinsic_put)
    near_intrinsic = np.isfinite(price) & (price <= intrinsic + 1e-7)
    limiting_call = np.where(forward > strike, df, np.where(forward < strike, 0.0, 0.5 * df))
    limiting_put = np.where(forward > strike, 0.0, np.where(forward < strike, -df, -0.5 * df))
    limit_delta = np.where(is_call, limiting_call, limiting_put)
    return np.where(near_intrinsic, limit_delta, np.where(np.isfinite(sigma), delta, np.nan))


@dataclass
class Position:
    key: str
    expiry: date
    strike: float
    option_type: str
    lots: int
    entry_ts: pd.Timestamp
    entry_price: float


@dataclass
class Order:
    cycle_expiry: date
    timestamp: pd.Timestamp
    action: str
    option_type: str
    strike: float
    lots: int
    price: float
    gross_cashflow: float
    costs: Dict[str, float]
    reason: str


@dataclass
class CycleResult:
    expiry: date
    entry_date: date
    orders: List[Order] = field(default_factory=list)
    state_transitions: List[dict] = field(default_factory=list)

    @property
    def pnl_gross(self) -> float:
        return sum(o.gross_cashflow for o in self.orders)

    @property
    def total_costs(self) -> float:
        return sum(o.costs["total"] for o in self.orders)

    @property
    def pnl_net(self) -> float:
        return self.pnl_gross - self.total_costs

    @property
    def order_count(self) -> int:
        return len(self.orders)


def direction_from_trigger(trigger_type: str) -> str:
    if trigger_type == "CALL":
        return "CALL_RATIO"
    if trigger_type == "PUT":
        return "PUT_RATIO"
    raise ValueError(trigger_type)


def choose_ic_trigger(
    call_abs_delta: float,
    put_abs_delta: float,
    threshold: float = 0.10,
    prev_call_abs_delta: Optional[float] = None,
    prev_put_abs_delta: Optional[float] = None,
) -> Optional[str]:
    call_hit = np.isfinite(call_abs_delta) and call_abs_delta <= threshold
    put_hit = np.isfinite(put_abs_delta) and put_abs_delta <= threshold
    if not call_hit and not put_hit:
        return None
    if call_hit and not put_hit:
        return "CALL"
    if put_hit and not call_hit:
        return "PUT"
    if call_abs_delta < put_abs_delta:
        return "CALL"
    if put_abs_delta < call_abs_delta:
        return "PUT"
    call_move = (
        abs(call_abs_delta - prev_call_abs_delta)
        if prev_call_abs_delta is not None and np.isfinite(prev_call_abs_delta)
        else -1.0
    )
    put_move = (
        abs(put_abs_delta - prev_put_abs_delta)
        if prev_put_abs_delta is not None and np.isfinite(prev_put_abs_delta)
        else -1.0
    )
    return "CALL" if call_move > put_move else "PUT"

def ratio_net_delta(direction: str, target: str) -> float:
    if target == "initial":
        if direction == "CALL_RATIO":
            return 0.50 - 2 * 0.40 + 0.10
        return -0.50 + 2 * 0.40 - 0.10
    if target == "continuation":
        if direction == "CALL_RATIO":
            return 0.40 - 2 * 0.30 + 0.08
        return -0.40 + 2 * 0.30 - 0.08
    raise ValueError(target)


def validate_ratio_direction_algebra() -> Dict[str, float]:
    return {
        "initial_call": ratio_net_delta("CALL_RATIO", "initial"),
        "initial_put": ratio_net_delta("PUT_RATIO", "initial"),
        "continuation_call": ratio_net_delta("CALL_RATIO", "continuation"),
        "continuation_put": ratio_net_delta("PUT_RATIO", "continuation"),
    }
