from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

from scripts.backtest import entry_and_exit_dates
from src.strategy_engine import monthly_expiries


def main():
    p = Path("results/composite/nifty_options_composite.parquet")
    out = Path("results/composite/cycle_coverage.csv")
    if not p.exists():
        Path("results/composite/cycle_coverage.json").write_text(json.dumps({"status": "NO_COMPOSITE"}))
        return

    df = pd.read_parquet(p, columns=["timestamp", "expiry", "expiry_source", "price_source"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True).dt.tz_convert("Asia/Kolkata")
    df["date"] = df["timestamp"].dt.date
    expiries = monthly_expiries([d for d in pd.to_datetime(df["expiry"], errors="coerce").dt.date.dropna().unique()])
    rows = []
    for expiry in expiries:
        dates = sorted(df.loc[df["expiry"] == expiry, "date"].unique())
        entry, exit_date = entry_and_exit_dates(expiry, list(dates))
        target = expiry - timedelta(days=32)
        source_counts = df.loc[df["expiry"] == expiry, "price_source"].value_counts().to_dict()
        inferred_count = int((df.loc[df["expiry"] == expiry, "expiry_source"] != "EXPLICIT_SOURCE_FIELD").sum())
        rows.append({
            "expiry": expiry.isoformat(),
            "target_32dte": target.isoformat(),
            "first_available": dates[0].isoformat() if dates else "",
            "last_available": dates[-1].isoformat() if dates else "",
            "entry_date": entry.isoformat() if entry else "",
            "exit_date": exit_date.isoformat() if exit_date else "",
            "status": "COMPLETE" if entry and exit_date else "INCOMPLETE",
            "rows": int(len(df[df["expiry"] == expiry])),
            "price_rows_primary": int(source_counts.get("thetrademarkk", 0)),
            "price_rows_cloudtrader": int(source_counts.get("cloudtrader", 0)),
            "price_rows_artist23": int(source_counts.get("artist23", 0)),
            "uses_fallback_price_rows": bool(any(k != "thetrademarkk" for k in source_counts)),
            "inferred_expiry_rows": inferred_count,
        })
    pd.DataFrame(rows).to_csv(out, index=False)
    print(pd.DataFrame(rows).to_string(index=False))


if __name__ == "__main__":
    main()
