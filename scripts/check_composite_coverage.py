from __future__ import annotations

import calendar
import json
import re
import sys
from datetime import date
from pathlib import Path

import duckdb
import pandas as pd

from scripts.backtest import entry_and_exit_dates


def is_monthly_expiry_candidate(expiry: date) -> bool:
    month_end = date(
        expiry.year,
        expiry.month,
        calendar.monthrange(expiry.year, expiry.month)[1],
    )
    return month_end - pd.Timedelta(days=6) <= pd.Timestamp(expiry).date() <= month_end


def expected_monthly_candidates(
    manifest_path: Path = Path("results/composite/source_staging_manifest.json"),
) -> list[dict]:
    if not manifest_path.exists():
        return []

    manifest = json.loads(manifest_path.read_text())
    start = date.fromisoformat(manifest["start"])
    end = date.fromisoformat(manifest["end"])

    primary_by_month: dict[tuple[int, int], date] = {}
    for value in manifest.get("thetrademarkk", {}).get("files", []):
        stem = Path(str(value)).stem
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", stem):
            continue
        try:
            expiry = date.fromisoformat(stem)
        except ValueError:
            continue
        key = (expiry.year, expiry.month)
        primary_by_month[key] = max(primary_by_month.get(key, expiry), expiry)

    months = []
    cursor = date(start.year, start.month, 1)
    last_month = date(end.year, end.month, 1)
    while cursor <= last_month:
        key = (cursor.year, cursor.month)
        months.append(
            {
                "month": key,
                "primary_expiry": primary_by_month.get(key),
                "primary_file_available": key in primary_by_month,
            }
        )
        if cursor.month == 12:
            cursor = date(cursor.year + 1, 1, 1)
        else:
            cursor = date(cursor.year, cursor.month + 1, 1)

    return months


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--research-use", action="store_true", help="Report strict failures but permit a research-use backtest on the best available data.")
    args = parser.parse_args()
    p = Path("results/composite/nifty_options_composite.parquet")
    out = Path("results/composite/cycle_coverage.csv")
    if not p.exists():
        Path("results/composite/cycle_coverage.json").write_text(
            json.dumps({"status": "NO_COMPOSITE"})
        )
        print("NO_COMPOSITE", file=sys.stderr)
        return 2

    expected_months = expected_monthly_candidates()
    if not expected_months:
        Path("results/composite/cycle_coverage.json").write_text(
            json.dumps({"status": "NO_EXPECTED_MONTHS"})
        )
        print("No requested months found in staging manifest", file=sys.stderr)
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

    by_expiry = {pd.Timestamp(row["expiry"]).date(): row for _, row in summary.iterrows()}
    observed_expiry_by_month: dict[tuple[int, int], date] = {}
    for expiry in by_expiry:
        if not is_monthly_expiry_candidate(expiry):
            continue
        key = (expiry.year, expiry.month)
        observed_expiry_by_month[key] = max(observed_expiry_by_month.get(key, expiry), expiry)

    rows = []
    failures = []

    for expected in expected_months:
        key = expected["month"]
        raw_primary_expiry = expected["primary_expiry"]
        primary_monthly_ok = bool(
            raw_primary_expiry and is_monthly_expiry_candidate(raw_primary_expiry)
        )
        primary_expiry = raw_primary_expiry if primary_monthly_ok else None
        fallback_expiry = observed_expiry_by_month.get(key) if primary_expiry is None else None
        expiry = primary_expiry or fallback_expiry
        primary_available = bool(expected["primary_file_available"])
        fallback_monthly_ok = (
            True if primary_expiry is not None
            else bool(fallback_expiry and is_monthly_expiry_candidate(fallback_expiry))
        )
        coverage_basis = "PRIMARY_MANIFEST" if primary_expiry else (
            "FALLBACK_COMPOSITE_MAX_EXPIRY" if fallback_expiry else "MISSING"
        )

        if expiry is None:
            month_label = f"{key[0]:04d}-{key[1]:02d}"
            failures.append(f"{month_label}: requested calendar month missing from composite")
            rows.append({
                "calendar_month": month_label,
                "expiry": "",
                "coverage_basis": coverage_basis,
                "primary_file_available": primary_available,
                "primary_monthly_candidate": bool(primary_expiry and is_monthly_expiry_candidate(primary_expiry)),
                "fallback_monthly_candidate": fallback_monthly_ok,
                "target_entry_month_start": "",
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

        if primary_available and not primary_monthly_ok and fallback_expiry is None:
            month_label = f"{key[0]:04d}-{key[1]:02d}"
            failures.append(
                f"{month_label}: primary file exists but its expiry {raw_primary_expiry} is not a month-end monthly expiry"
            )
            rows.append({
                "calendar_month": month_label,
                "expiry": raw_primary_expiry.isoformat() if raw_primary_expiry else "",
                "coverage_basis": "PRIMARY_NON_MONTHLY",
                "primary_file_available": True,
                "primary_monthly_candidate": False,
                "fallback_monthly_candidate": False,
                "target_entry_month_start": (date(raw_primary_expiry.year, raw_primary_expiry.month, 1).isoformat() if raw_primary_expiry else ""),
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

        if not fallback_monthly_ok:
            month_label = f"{key[0]:04d}-{key[1]:02d}"
            failures.append(
                f"{month_label}: fallback expiry {expiry} is not a defensible month-end monthly expiry"
            )
            rows.append({
                "calendar_month": month_label,
                "expiry": expiry.isoformat(),
                "coverage_basis": coverage_basis,
                "primary_file_available": primary_available,
                "fallback_monthly_candidate": False,
                "target_entry_month_start": date(expiry.year, expiry.month, 1).isoformat(),
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

        row = by_expiry.get(expiry)
        if row is None:
            month_label = f"{key[0]:04d}-{key[1]:02d}"
            failures.append(
                f"{month_label}: expected monthly expiry {expiry} is missing from composite"
            )
            rows.append({
                "calendar_month": month_label,
                "expiry": expiry.isoformat(),
                "coverage_basis": coverage_basis,
                "primary_file_available": primary_available,
                "fallback_monthly_candidate": fallback_monthly_ok,
                "target_entry_month_start": date(expiry.year, expiry.month, 1).isoformat(),
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
            expected = set(nse_fno_sessions(entry, exit_date))
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
                    f"{expiry}: missing {missing_sessions} expected exchange sessions"
                )

        fallback_rows = int(row["rows"]) - int(row["price_rows_primary"])
        non_explicit = int(row["non_explicit_expiry_rows"])

        if non_explicit:
            status = "INCOMPLETE"
            failures.append(
                f"{expiry}: {non_explicit} rows lack explicit/resolved expiry provenance"
            )

        if status != "COMPLETE" and (not entry or not exit_date):
            failures.append(
                f"{expiry}: does not span deterministic first-session-of-expiry-month entry to pre-expiry exit"
            )

        rows.append({
            "calendar_month": f"{key[0]:04d}-{key[1]:02d}",
            "expiry": expiry.isoformat(),
            "coverage_basis": coverage_basis,
            "primary_file_available": primary_available,
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
    fallback_months = int(((result["status"] == "COMPLETE") & (~result["primary_file_available"])).sum())
    print(f"cycle_coverage: {complete}/{total} requested calendar months complete")
    print(f"cycle_coverage: {fallback_months} complete months supplied without a primary monthly file")
    unexpected = sorted(
        set(by_expiry) - {expected["primary_expiry"] for expected in expected_months if expected["primary_expiry"] is not None}
    )
    if unexpected:
        print(
            f"Non-monthly/unexpected composite expiries retained for audit: {len(unexpected)}"
        )
    if failures:
        print("Gate 2 coverage failures:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        if args.research_use:
            research_eligible = int(((result["first_available"] != "") & (result["exit_date"] != "")).sum())
            (out.parent / "research_use_data_status.json").write_text(json.dumps({
                "mode": "research_use_partial",
                "strict_gate": "FAILED",
                "research_eligible_cycles_with_observed_entry_window": research_eligible,
                "total_requested_months": total,
                "complete_cycles": complete,
                "failure_count": len(failures),
                "limitations": [
                    "The strict first-session-of-expiry-month lifecycle gate is not satisfied.",
                    "The research-use backtest may start at the first observed session available in the expiry month.",
                    "Results must not be presented as a fully covered historical validation."
                ]
            }, indent=2))
            print("RESEARCH-USE MODE: strict Gate 2 remains FAILED; continuing only for explicitly labelled partial-data analysis.")
            return 0
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
