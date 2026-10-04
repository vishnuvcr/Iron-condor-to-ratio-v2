from __future__ import annotations

import argparse
import json
import os
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import duckdb
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from huggingface_hub import HfApi, hf_hub_download

from src.strategy_engine import (
    CostModel,
    CycleResult,
    Order,
    Position,
    TICK,
    choose_ic_trigger,
    black76_delta_from_forward,
    black76_delta_from_price,
    implied_vol_black76,
    lot_size_for_monthly_expiry,
    monthly_expiries,
)


REPO_ID = "rissin/nse-options-intraday"
REMOTE_FILES = [
    "upstox_intraday/NIFTY/NIFTY_2024.parquet",
    "upstox_intraday/NIFTY/NIFTY_2025.parquet",
    "upstox_intraday/NIFTY/NIFTY_2026.parquet",
]
DATASET_CARD_URL = "https://huggingface.co/datasets/rissin/nse-options-intraday"



def download_data(cache_root: Path) -> List[Path]:
    token = os.getenv("HF_TOKEN")
    paths = []
    for filename in REMOTE_FILES:
        p = hf_hub_download(
            repo_id=REPO_ID,
            filename=filename,
            repo_type="dataset",
            token=token or None,
            cache_dir=str(cache_root),
        )
        paths.append(Path(p))
    return paths


def dataset_revision() -> str:
    token = os.getenv("HF_TOKEN")
    try:
        info = HfApi(token=token or None).dataset_info(REPO_ID, revision="main")
        return str(info.sha)
    except Exception:
        return "unknown"

def qpaths(paths: List[Path]) -> str:
    vals = ",".join("'" + str(p).replace("'", "''") + "'" for p in paths)
    return "[" + vals + "]"


def load_expiry_list(paths: List[Path], start: date, end: date) -> List[date]:
    con = duckdb.connect()
    sql = f"""
    SELECT DISTINCT CAST(expiry AS DATE) AS expiry
    FROM read_parquet({qpaths(paths)})
    WHERE underlying='NIFTY' AND granularity='1min'
      AND CAST(date AS DATE) BETWEEN DATE '{start}' AND DATE '{end}'
      AND CAST(expiry AS DATE) BETWEEN DATE '{start}' AND DATE '{end}'
    ORDER BY 1
    """
    df = con.execute(sql).df()
    con.close()
    raw = [x.date() if hasattr(x, "date") else x for x in pd.to_datetime(df["expiry"])]
    return monthly_expiries(raw)


def load_cycle_data(paths: List[Path], expiry: date, start_date: date, end_date: date) -> pd.DataFrame:
    con = duckdb.connect()
    sql = f"""
    SELECT date, timestamp, expiry, strike, option_type, open, high, low, close, volume
    FROM read_parquet({qpaths(paths)})
    WHERE underlying='NIFTY' AND granularity='1min'
      AND CAST(expiry AS DATE)=DATE '{expiry}'
      AND CAST(date AS DATE) BETWEEN DATE '{start_date}' AND DATE '{end_date}'
      AND timestamp IS NOT NULL
    """
    df = con.execute(sql).df()
    con.close()
    if df.empty:
        return df
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["date"] = pd.to_datetime(df["date"]).dt.date
    df["expiry"] = pd.to_datetime(df["expiry"]).dt.date
    for c in ["strike", "open", "high", "low", "close", "volume"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=["timestamp", "strike", "close", "open"])
    df = df[(df["close"] > 0) & (df["open"] > 0) & (df["volume"] > 0)]
    df = df.sort_values(["timestamp", "strike", "option_type"]).drop_duplicates(
        ["timestamp", "strike", "option_type"], keep="last"
    )
    return df


def add_forward_and_delta(df: pd.DataFrame, expiry: date, rate: float) -> pd.DataFrame:
    if df.empty:
        return df
    calls = df[df["option_type"] == "CE"][["timestamp", "strike", "close", "volume"]].rename(
        columns={"close": "call_close", "volume": "call_volume"}
    )
    puts = df[df["option_type"] == "PE"][["timestamp", "strike", "close", "volume"]].rename(
        columns={"close": "put_close", "volume": "put_volume"}
    )
    pairs = calls.merge(puts, on=["timestamp", "strike"], how="inner")
    pairs = pairs[(pairs["call_close"] > 0) & (pairs["put_close"] > 0) & (pairs["call_volume"] > 0) & (pairs["put_volume"] > 0)]
    if pairs.empty:
        return df.assign(forward=np.nan, delta=np.nan)

    t_pairs = (pd.Timestamp(expiry) + pd.Timedelta(hours=15, minutes=30) - pairs["timestamp"]).dt.total_seconds() / (365.0 * 86400.0)
    t_pairs = np.maximum(t_pairs.values, 1e-6)
    df_disc = np.exp(-rate * t_pairs)
    kmed = pairs.groupby("timestamp")["strike"].median().rename("kmed")
    pairs = pairs.join(kmed, on="timestamp")
    pairs = pairs[(pairs["strike"] >= 0.90 * pairs["kmed"]) & (pairs["strike"] <= 1.10 * pairs["kmed"])]
    t = (pd.Timestamp(expiry) + pd.Timedelta(hours=15, minutes=30) - pairs["timestamp"]).dt.total_seconds() / (365.0 * 86400.0)
    df_disc = np.exp(-rate * np.maximum(t.values, 1e-6))
    pairs["forward_i"] = pairs["strike"].values + (pairs["call_close"].values - pairs["put_close"].values) / df_disc
    pairs.loc[pairs["forward_i"] <= 0, "forward_i"] = np.nan
    forward = pairs.groupby("timestamp")["forward_i"].median().rename("forward")
    df = df.join(forward, on="timestamp")
    t = (pd.Timestamp(expiry) + pd.Timedelta(hours=15, minutes=30) - df["timestamp"]).dt.total_seconds() / (365.0 * 86400.0)
    t = np.maximum(t.values, 1e-6)
    is_call = df["option_type"].values == "CE"
    delta = black76_delta_from_price(
        df["forward"].values,
        df["strike"].values,
        t,
        df["close"].values,
        is_call,
        rate,
    )
    df["delta"] = delta
    return df


def trading_dates(df: pd.DataFrame) -> List[date]:
    return sorted(df["date"].unique())


def entry_and_exit_dates(expiry: date, available_dates: List[date]) -> Tuple[Optional[date], Optional[date]]:
    target = expiry - timedelta(days=32)
    if not available_dates or min(available_dates) > target:
        return None, None
    entries = [d for d in available_dates if d >= target and d < expiry]
    if not entries:
        return None, None
    entry_date = entries[0]
    exit_date = entries[-1]
    return entry_date, exit_date


def nearest_bar(df: pd.DataFrame, target_dt: pd.Timestamp) -> Optional[pd.Timestamp]:
    idx = df.index[df["timestamp"] >= target_dt]
    if len(idx) == 0:
        return None
    return df.loc[idx[0], "timestamp"]


def snapshot_at(df: pd.DataFrame, ts: pd.Timestamp) -> pd.DataFrame:
    return df[df["timestamp"] == ts].copy()


def select_contract(snapshot: pd.DataFrame, option_type: str, target_abs_delta: float) -> Optional[pd.Series]:
    x = snapshot[(snapshot["option_type"] == option_type) & snapshot["delta"].notna() & (snapshot["close"] > 0) & (snapshot["volume"] > 0)]
    if x.empty:
        return None
    x = x[(x["delta"].abs() >= 0.01) & (x["delta"].abs() <= 0.99)]
    if x.empty:
        return None
    x = x.copy()
    x["dist"] = (x["delta"].abs() - target_abs_delta).abs()
    return x.sort_values(["dist", "volume"], ascending=[True, False]).iloc[0]


def add_order(
    cycle: CycleResult,
    expiry: date,
    position: Position,
    action: str,
    timestamp: pd.Timestamp,
    ref_price: float,
    cost_model: CostModel,
    lot_size: int,
    reason: str,
    lots_override: Optional[int] = None,
) -> Position:
    lots = abs(lots_override if lots_override is not None else position.lots)
    side = "BUY" if action == "BUY" else "SELL"
    fill = cost_model.price_with_slippage(ref_price, side)
    signed_lots = lots if action == "BUY" else -lots
    gross_cashflow = -signed_lots * fill * lot_size
    costs = cost_model.costs(fill, lots, lot_size, side, timestamp.date())
    cycle.orders.append(
        Order(
            cycle_expiry=expiry,
            timestamp=timestamp,
            action=action,
            option_type=position.option_type,
            strike=position.strike,
            lots=lots,
            price=fill,
            gross_cashflow=gross_cashflow,
            costs=costs,
            reason=reason,
        )
    )
    return position


def common_next_open(
    df: pd.DataFrame,
    signal_ts: pd.Timestamp,
    legs: List[Tuple[float, str]],
    max_minutes: int = 5,
) -> Optional[Tuple[pd.Timestamp, Dict[Tuple[float, str], float]]]:
    cutoff = signal_ts + pd.Timedelta(minutes=max_minutes)
    candidates = sorted(
        pd.to_datetime(df.loc[(df["timestamp"] > signal_ts) & (df["timestamp"] <= cutoff), "timestamp"].unique())
    )
    for ts in candidates:
        refs: Dict[Tuple[float, str], float] = {}
        ok = True
        for strike, option_type in legs:
            row = df[
                (df["timestamp"] == ts)
                & (df["strike"] == float(strike))
                & (df["option_type"] == option_type)
                & (df["open"] > 0)
                & (df["volume"] > 0)
            ]
            if row.empty:
                ok = False
                break
            refs[(float(strike), option_type)] = float(row.iloc[0]["open"])
        if ok:
            return pd.Timestamp(ts), refs
    return None


def build_ratio(
    snapshot: pd.DataFrame,
    direction: str,
    target_set: str,
    signal_ts: pd.Timestamp,
    expiry: date,
    df: pd.DataFrame,
    cycle: CycleResult,
    cost_model: CostModel,
    lot_size: int,
) -> Optional[Tuple[List[Position], pd.Timestamp]]:
    if target_set == "initial":
        long_target, short_target, hedge_target = 0.50, 0.40, 0.10
    else:
        long_target, short_target, hedge_target = 0.40, 0.30, 0.08
    opt = "CE" if direction == "CALL_RATIO" else "PE"
    selections = []
    for target, lots, action, reason in [
        (long_target, 1, "BUY", f"{target_set}_long"),
        (short_target, 2, "SELL", f"{target_set}_short"),
        (hedge_target, 1, "BUY", f"{target_set}_hedge"),
    ]:
        r = select_contract(snapshot, opt, target)
        if r is None:
            return None
        selections.append((float(r["strike"]), opt, lots, action, reason))
    common = common_next_open(df, signal_ts, [(s, o) for s, o, *_ in selections])
    if common is None:
        return None
    fill_ts, refs = common
    out: List[Position] = []
    for strike, opt_type, lots, action, reason in selections:
        ref_price = refs[(strike, opt_type)]
        pos = Position(
            key=f"{expiry}|{opt_type}|{strike}|{lots}|{signal_ts}",
            expiry=expiry, strike=strike, option_type=opt_type,
            lots=lots if action == "BUY" else -lots,
            entry_ts=fill_ts, entry_price=ref_price,
        )
        add_order(cycle, expiry, pos, action, fill_ts, ref_price, cost_model, lot_size, reason, lots_override=lots)
        out.append(pos)
    return out, fill_ts

def close_positions(
    positions: List[Position],
    signal_ts: pd.Timestamp,
    df: pd.DataFrame,
    cycle: CycleResult,
    cost_model: CostModel,
    lot_size: int,
    reason: str,
) -> Optional[pd.Timestamp]:
    if not positions:
        return signal_ts
    legs = [(p.strike, p.option_type) for p in positions]
    common = common_next_open(df, signal_ts, legs)
    if common is None:
        return None
    fill_ts, refs = common
    for p in positions:
        ref = refs[(float(p.strike), p.option_type)]
        action = "SELL" if p.lots > 0 else "BUY"
        add_order(cycle, cycle.expiry, p, action, fill_ts, ref, cost_model, lot_size, reason, lots_override=abs(p.lots))
    return fill_ts

def run_cycle(df: pd.DataFrame, expiry: date, rate: float, cost_model: CostModel) -> Optional[CycleResult]:
    dates = trading_dates(df)
    entry_date, exit_date = entry_and_exit_dates(expiry, dates)
    if entry_date is None or exit_date is None:
        return None
    cycle = CycleResult(expiry=expiry, entry_date=entry_date)
    lot_size = lot_size_for_monthly_expiry(expiry)
    entry_target = pd.Timestamp.combine(entry_date, time(9, 20))
    entry_signal = nearest_bar(df, entry_target)
    if entry_signal is None:
        return None
    entry_snapshot = snapshot_at(df, entry_signal)
    sc = select_contract(entry_snapshot, "CE", 0.30)
    sp = select_contract(entry_snapshot, "PE", 0.30)
    hc = select_contract(entry_snapshot, "CE", 0.10)
    hp = select_contract(entry_snapshot, "PE", 0.10)
    if any(x is None for x in [sc, sp, hc, hp]):
        return None
    selections = [
        (float(sc["strike"]), "CE", 1, "SELL", "IC_short_call"),
        (float(sp["strike"]), "PE", 1, "SELL", "IC_short_put"),
        (float(hc["strike"]), "CE", 1, "BUY", "IC_long_call"),
        (float(hp["strike"]), "PE", 1, "BUY", "IC_long_put"),
    ]
    common = common_next_open(df, entry_signal, [(s, o) for s, o, *_ in selections])
    if common is None:
        return None
    fill_ts, refs = common
    positions = []
    for strike, option_type, lots, action, reason in selections:
        ref = refs[(strike, option_type)]
        pos = Position(
            key=f"{expiry}|{option_type}|{strike}|{lots}|{fill_ts}",
            expiry=expiry, strike=strike, option_type=option_type,
            lots=lots if action == "BUY" else -lots,
            entry_ts=fill_ts, entry_price=ref,
        )
        add_order(cycle, expiry, pos, action, fill_ts, ref, cost_model, lot_size, reason, lots_override=1)
        positions.append(pos)

    state = "IC_ACTIVE"
    direction = None
    prev_dc = np.nan
    prev_dp = np.nan
    signal_times = sorted(pd.to_datetime(df["timestamp"].unique()))
    exit_target = pd.Timestamp.combine(exit_date, time(15, 20))
    for ts in signal_times:
        if ts <= entry_signal or ts > exit_target:
            continue
        snap = snapshot_at(df, ts)
        if snap.empty:
            continue

        # Planned end-of-cycle exit.
        if ts.date() == exit_date and ts.time() >= time(15, 20):
            fill = ts
            for p in positions:
                row = snap[(snap["strike"] == p.strike) & (snap["option_type"] == p.option_type)]
                if row.empty:
                    return None
                ref = float(row.iloc[0]["close"])
                action = "SELL" if p.lots > 0 else "BUY"
                add_order(cycle, expiry, p, action, fill, ref, cost_model, lot_size, "scheduled_exit", lots_override=abs(p.lots))
            positions = []
            return cycle

        if state == "IC_ACTIVE":
            short_positions = [p for p in positions if p.lots < 0]
            deltas = {}
            for p in short_positions:
                row = snap[(snap["strike"] == p.strike) & (snap["option_type"] == p.option_type)]
                if row.empty or pd.isna(row.iloc[0]["delta"]):
                    deltas[p.option_type] = np.nan
                else:
                    deltas[p.option_type] = abs(float(row.iloc[0]["delta"]))
            dc, dp = deltas.get("CE", np.nan), deltas.get("PE", np.nan)
            trigger = choose_ic_trigger(dc, dp, 0.10, prev_dc, prev_dp)
            prev_dc, prev_dp = dc, dp
            if trigger is not None:
                fill_ts = close_positions(positions, ts, df, cycle, cost_model, lot_size, "IC_to_ratio")
                if fill_ts is None:
                    return None
                direction = "CALL_RATIO" if trigger == "CALL" else "PUT_RATIO"
                snapshot_for_select = snap
                built = build_ratio(snapshot_for_select, direction, "initial", ts, expiry, df, cycle, cost_model, lot_size)
                if built is None:
                    return None
                new_positions, fill_ts = built
                positions = new_positions
                state = "RATIO_ACTIVE"
                cycle.state_transitions.append({"timestamp": str(ts), "from": "IC_ACTIVE", "to": "RATIO_ACTIVE", "trigger": trigger})
                continue

        if state == "RATIO_ACTIVE" and len(positions) == 3:
            short_positions = [p for p in positions if p.lots < 0]
            short_deltas = []
            for p in short_positions:
                row = snap[(snap["strike"] == p.strike) & (snap["option_type"] == p.option_type)]
                if row.empty or pd.isna(row.iloc[0]["delta"]):
                    short_deltas.append(np.nan)
                else:
                    short_deltas.append(abs(float(row.iloc[0]["delta"])))
            if all(np.isfinite(short_deltas)):
                s = float(sum(short_deltas))
                if s <= 0.20 or s >= 1.20:
                    fill_ts = close_positions(positions, ts, df, cycle, cost_model, lot_size, "ratio_reset")
                    if fill_ts is None:
                        return None
                    if s <= 0.20:
                        new_direction = direction
                        target_set = "continuation"
                        reason = "ratio_continuation"
                    else:
                        new_direction = "PUT_RATIO" if direction == "CALL_RATIO" else "CALL_RATIO"
                        target_set = "initial"
                        reason = "ratio_reversal"
                    built = build_ratio(snap, new_direction, target_set, ts, expiry, df, cycle, cost_model, lot_size)
                    if built is None:
                        return None
                    new_positions, fill_ts = built
                    cycle.state_transitions.append({"timestamp": str(ts), "from": "RATIO_ACTIVE", "to": "RATIO_ACTIVE", "trigger": reason, "short_delta_sum": s, "direction_from": direction, "direction_to": new_direction})
                    positions = new_positions
                    direction = new_direction
    return cycle


def summarize(cycles: List[CycleResult]) -> pd.DataFrame:
    rows = []
    for c in cycles:
        rows.append({
            "expiry": c.expiry,
            "entry_date": c.entry_date,
            "gross_pnl": c.pnl_gross,
            "costs": c.total_costs,
            "net_pnl": c.pnl_net,
            "orders": c.order_count,
            "transitions": len(c.state_transitions),
        })
    return pd.DataFrame(rows)


def metrics_df(trades: pd.DataFrame, capital: float = 100000.0) -> Dict[str, float]:
    if trades.empty:
        return {}
    x = trades["net_pnl"].astype(float)
    eq = x.cumsum()
    peaks = eq.cummax()
    dd = eq - peaks
    profit = x[x > 0].sum()
    loss = -x[x < 0].sum()
    pf = profit / loss if loss > 0 else float("inf")
    r = x / capital
    sharpe = float(np.sqrt(12) * r.mean() / r.std(ddof=1)) if len(r) > 1 and r.std(ddof=1) > 0 else float("nan")
    return {
        "trades": int(len(x)),
        "total_net_pnl": float(x.sum()),
        "avg_net_pnl": float(x.mean()),
        "median_net_pnl": float(x.median()),
        "win_rate": float((x > 0).mean()),
        "profit_factor": float(pf),
        "max_drawdown": float(dd.min()),
        "p05_pnl": float(x.quantile(0.05)),
        "p95_pnl": float(x.quantile(0.95)),
        "roi_on_1L_capital": float(x.sum() / capital),
        "annualized_monthly_sharpe_proxy": sharpe,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="2025-01-01")
    ap.add_argument("--end", default="2026-09-30")
    ap.add_argument("--rate", type=float, default=0.0)
    ap.add_argument("--brokerage", type=float, default=20.0)
    ap.add_argument("--slippage-ticks", type=int, default=1)
    ap.add_argument("--out", default="results")
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    cache_root = Path(os.getenv("HF_HOME", out / "hf_cache"))
    cache_root.mkdir(parents=True, exist_ok=True)

    start, end = date.fromisoformat(args.start), date.fromisoformat(args.end)
    paths = download_data(cache_root)
    expiry_list = load_expiry_list(paths, start, end)
    expiry_list = [e for e in expiry_list if start <= e <= end and e >= date(2025, 1, 27)]

    all_cycles = []
    quality = []
    all_orders = []

    for expiry in expiry_list:
        entry_start = expiry - timedelta(days=35)
        df = load_cycle_data(paths, expiry, entry_start, expiry - timedelta(days=1))
        if df.empty:
            quality.append({"expiry": str(expiry), "status": "EMPTY"})
            continue
        dup = int(df.duplicated(["timestamp", "strike", "option_type"]).sum())
        neg_volume = int((df["volume"] < 0).sum())
        non_monotonic_contracts = 0
        for _, g in df.sort_values(["strike", "option_type", "timestamp"]).groupby(["strike", "option_type"], sort=False):
            if not g["timestamp"].is_monotonic_increasing:
                non_monotonic_contracts += 1
        df = add_forward_and_delta(df, expiry, args.rate)
        forward_coverage = float(df["forward"].notna().mean()) if "forward" in df else 0.0
        delta_coverage = float(df["delta"].notna().mean()) if "delta" in df else 0.0
        quality.append({
            "expiry": str(expiry), "rows": len(df),
            "duplicates_after_filter": dup, "negative_volume_rows": neg_volume,
            "non_monotonic_contracts": non_monotonic_contracts,
            "forward_coverage": forward_coverage, "delta_coverage": delta_coverage,
        })
        cm = CostModel(brokerage_per_order=args.brokerage, slippage_ticks=args.slippage_ticks)
        try:
            cycle = run_cycle(df, expiry, args.rate, cm)
            if cycle is not None:
                all_cycles.append(cycle)
                for o in cycle.orders:
                    all_orders.append({
                        "expiry": o.cycle_expiry,
                        "timestamp": o.timestamp,
                        "action": o.action,
                        "option_type": o.option_type,
                        "strike": o.strike,
                        "lots": o.lots,
                        "price": o.price,
                        "gross_cashflow": o.gross_cashflow,
                        "cost": o.costs["total"],
                        "reason": o.reason,
                    })
        except Exception as exc:
            quality.append({"expiry": str(expiry), "status": "ERROR", "error": repr(exc)})

    trades = summarize(all_cycles)
    trades.to_csv(out / "trade_summary.csv", index=False)
    pd.DataFrame(all_orders).to_csv(out / "order_log.csv", index=False)
    pd.DataFrame(quality).to_csv(out / "data_quality.csv", index=False)

    metrics = metrics_df(trades)
    (out / "metrics.json").write_text(json.dumps(metrics, indent=2, default=str))

    if not trades.empty:
        eq = trades.assign(equity=trades["net_pnl"].cumsum())
        plt.figure(figsize=(10, 5))
        plt.plot(pd.to_datetime(eq["expiry"]), eq["equity"])
        plt.title("Iron Condor -> Ratio Spread cumulative net P&L")
        plt.xlabel("Monthly expiry")
        plt.ylabel("Cumulative net P&L (Rs)")
        plt.tight_layout()
        plt.savefig(out / "equity_curve.png", dpi=160)
        plt.close()

        plt.figure(figsize=(8, 5))
        plt.hist(trades["net_pnl"], bins=min(20, len(trades)))
        plt.title("Monthly net P&L distribution")
        plt.xlabel("Net P&L (Rs)")
        plt.ylabel("Count")
        plt.tight_layout()
        plt.savefig(out / "pnl_distribution.png", dpi=160)
        plt.close()

    manifest = {
        "repository": "vishnuvcr/Iron-condor-to-ratio-v2",
        "data_repository": REPO_ID,
        "files": REMOTE_FILES,
        "start": args.start,
        "end": args.end,
        "expiry_count": len(expiry_list),
        "rate": args.rate,
        "brokerage": args.brokerage,
        "slippage_ticks": args.slippage_ticks,
        "tick": TICK,
        "created_utc": datetime.utcnow().isoformat() + "Z",
    }
    (out / "run_manifest.json").write_text(json.dumps(manifest, indent=2))
    print(json.dumps({"metrics": metrics, "expiries": [str(x) for x in expiry_list]}, indent=2))


if __name__ == "__main__":
    main()
