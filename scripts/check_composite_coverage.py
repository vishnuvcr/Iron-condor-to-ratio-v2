from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

import duckdb
import exchange_calendars as xc
import pandas as pd

from scripts.backtest import entry_and_exit_dates
from src.strategy_engine import monthly_expiries


def main():
    p = Path("results/composite/nifty_options_composite.parquet")
    out = Path("results/composite/cycle_coverage.csv")
    if not p.exists():
        Path("results/composite/cycle_coverage.json").write_text(
            json.dumps({"status": "NO_COMPOSITE"})
        )
        print("NO_COMPOSITE", file=sys.stderr)
        return 2

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
        print("NO_VALID_EXPIRIES", file=sys.stderr)
        return 2

    expiries = monthly_expiries([x.date() for x in pd.to_datetime(summary["expiry"])])
    by_expiry = {pd.Timestamp(row["expiry"]).date(): row for _, row in summary.iterrows()}
    cal = xc.get_calendar("XBSE")

    rows = []
    failures = []

    for expiry in expiries:
        row = by_expiry.get(expiry)
        if row is None:
            failures.append(f"{expiry}: missing from composite")
            rows.append({
                "expiry": expiry.isoformat(),
                "target_32dte": (expiry - pd.Timedelta(days=32)).isoformat(),
                "first_available": "",
                "last_available": "",
                "entry_date": "",
                "exit_date": "",
                "status": "INCOMPLETE",
                "rows": 0,
                "price_rows_primary": 0,
                "price_rows_cloudtrader": 0,
                "price_rows_rissin": 0,
                "price_rows_artist23": 0,
                "uses_fallback_price_rows": False,
                "non_explicit_expiry_rows": 0,
                "expected_sessions": 0,
                "observed_sessions": 0,
                "missing_sessions": 0,
            })
            continue

        first = pd.Timestamp(row["first_available"]).date()
        last = pd.Timestamp(row["last_available"]).date()
        entry, exit_date = entry_and_exit_dates(expiry, [first, last])

        status = "COMPLETE" if entry and exit_date else "INCOMPLETE"
        expected_sessions = 0
        observed_sessions = 0
        missing_sessions = 0

        if entry and exit_date:
            sessions = cal.sessions_in_range(
                pd.Timestamp(entry),
                pd.Timestamp(exit_date),
            )
            expected = {ts.date() for ts in sessions}
            con = duckdb.connect()
            observed_df = con.execute(
                """
                SELECT DISTINCT CAST(timestamp AS DATE) AS trading_date
                FROM read_parquet(?)
                WHERE expiry = CAST(? AS DATE)
                  AND CAST(timestamp AS DATE) BETWEEN CAST(? AS DATE) AND CAST(? AS DATE)
                """,
                [str(p), expiry.isoformat(), entry.isoformat(), exit_date.isoformat()],
            ).fetchdf()
            con.close()
            observed = {
                pd.Timestamp(x).date()
                for x in observed_df["trading_date"].dropna()
            }
            expected_sessions = len(expected)
            observed_sessions = len(expected & observed)
            missing_sessions = len(expected - observed)
            if missing_sessions:
                status = "INCOMPLETE"
                failures.append(
                    f"{expiry}: missing {missing_sessions} expected trading sessions"
                )

        fallback_rows = int(row["rows"]) - int(row["price_rows_primary"])
        non_explicit = int(row["non_explicit_expiry_rows"])

        if non_explicit:
            status = "INCOMPLETE"
            failures.append(f"{expiry}: {non_explicit} rows lack explicit/resolved expiry provenance")

        if status != "COMPLETE":
            if not entry or not exit_date:
                failures.append(f"{expiry}: does not span deterministic 32-DTE entry to pre-expiry exit")

        rows.append({
            "expiry": expiry.isoformat(),
            "target_32dte": (expiry - pd.Timedelta(days=32)).isoformat(),
            "first_available": first.isoformat(),
            "last_available": last.isoformat(),
            "entry_date": entry.isoformat() if entry else "",
            "exit_date": exit_date.isoformat() if exit_date else "",
            "status": status,
            "rows": int(row["rows"]),
            "price_rows_primary": int(row["price_rows_primary"]),
            "price_rows_cloudtrader": int(row["price_rows_cloudtrader"]),
            "price_rows_rissin": int(row["price_rows_rissin"]),
            "price_rows_artist23": int(row["price_rows_artist23"]),
            "uses_fallback_price_rows": bool(fallback_rows > 0),
            "non_explicit_expiry_rows": non_explicit,
            "expected_sessions": expected_sessions,
            "observed_sessions": observed_sessions,
            "missing_sessions": missing_sessions,
        })

    result = pd.DataFrame(rows)
    result.to_csv(out, index=False)
    complete = int((result["status"] == "COMPLETE").sum())
    total = len(result)
    print(f"cycle_coverage: {complete}/{total} complete")
    if failures:
        print("Gate 2 coverage failures:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
