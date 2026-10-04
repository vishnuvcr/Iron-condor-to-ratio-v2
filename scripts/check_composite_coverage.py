from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import duckdb
import pandas as pd

from scripts.backtest import entry_and_exit_dates
from src.strategy_engine import monthly_expiries


def main():
    p = Path("results/composite/nifty_options_composite.parquet")
    out = Path("results/composite/cycle_coverage.csv")
    if not p.exists():
        Path("results/composite/cycle_coverage.json").write_text(json.dumps({"status": "NO_COMPOSITE"}))
        return

    con = duckdb.connect()
    summary = con.execute(
        """
        SELECT
            CAST(expiry AS DATE) AS expiry,
            MIN(CAST(timestamp AS DATE)) AS first_available,
            MAX(CAST(timestamp AS DATE)) AS last_available,
            COUNT(*) AS rows,
            SUM(CASE WHEN price_source = 'thetrademarkk' THEN 1 ELSE 0 END) AS price_rows_primary,
            SUM(CASE WHEN price_source = 'cloudtrader' THEN 1 ELSE 0 END) AS price_rows_cloudtrader,
            SUM(CASE WHEN price_source = 'rissin' THEN 1 ELSE 0 END) AS price_rows_rissin,
            SUM(CASE WHEN price_source = 'artist23' THEN 1 ELSE 0 END) AS price_rows_artist23,
            SUM(CASE WHEN expiry_source <> 'EXPLICIT_SOURCE_FIELD' THEN 1 ELSE 0 END) AS non_explicit_expiry_rows
        FROM read_parquet(?)
        WHERE expiry IS NOT NULL AND timestamp IS NOT NULL
        GROUP BY 1
        ORDER BY 1
        """,
        [str(p)],
    ).fetchdf()
    con.close()

    if summary.empty:
        summary.to_csv(out, index=False)
        return

    expiries = monthly_expiries([x.date() for x in pd.to_datetime(summary["expiry"])])
    by_expiry = {pd.Timestamp(row["expiry"]).date(): row for _, row in summary.iterrows()}

    rows = []
    for expiry in expiries:
        row = by_expiry[expiry]
        dates = [
            pd.Timestamp(row["first_available"]).date(),
            pd.Timestamp(row["last_available"]).date(),
        ]
        entry, exit_date = entry_and_exit_dates(expiry, dates)
        source_total = int(row["rows"])
        fallback_rows = source_total - int(row["price_rows_primary"])
        rows.append({
            "expiry": expiry.isoformat(),
            "target_32dte": (expiry - pd.Timedelta(days=32)).isoformat(),
            "first_available": row["first_available"].isoformat(),
            "last_available": row["last_available"].isoformat(),
            "entry_date": entry.isoformat() if entry else "",
            "exit_date": exit_date.isoformat() if exit_date else "",
            "status": "COMPLETE" if entry and exit_date else "INCOMPLETE",
            "rows": source_total,
            "price_rows_primary": int(row["price_rows_primary"]),
            "price_rows_cloudtrader": int(row["price_rows_cloudtrader"]),
            "price_rows_rissin": int(row["price_rows_rissin"]),
            "price_rows_artist23": int(row["price_rows_artist23"]),
            "uses_fallback_price_rows": bool(fallback_rows > 0),
            "non_explicit_expiry_rows": int(row["non_explicit_expiry_rows"]),
        })

    pd.DataFrame(rows).to_csv(out, index=False)


if __name__ == "__main__":
    main()
