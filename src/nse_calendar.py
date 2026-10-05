from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import pandas as pd

HOLIDAY_FILE = Path(__file__).resolve().parent.parent / "research" / "NSE_FNO_HOLIDAYS_2021_2026.csv"


def nse_fno_holidays() -> set[date]:
    df = pd.read_csv(HOLIDAY_FILE, parse_dates=["date"])
    return {ts.date() for ts in df["date"].dropna()}


def nse_fno_sessions(start: date, end: date) -> list[date]:
    if end < start:
        return []
    holidays = nse_fno_holidays()
    out = []
    current = start
    while current <= end:
        if current.weekday() < 5 and current not in holidays:
            out.append(current)
        current += timedelta(days=1)
    return out


def nifty_monthly_expiry_for_month(year: int, month: int) -> date:
    """Return the NIFTY monthly expiry for a calendar month.

    NIFTY monthly expiries were Thursday-based through the August 2025
    expiry; contracts expiring from September 2025 onward use the last
    Tuesday, with a holiday moved to the previous trading session.
    """
    import calendar

    last_day = calendar.monthrange(year, month)[1]
    weekday = 1 if (year, month) >= (2025, 9) else 3  # Tuesday / Thursday
    candidate = date(year, month, last_day)
    candidate -= timedelta(days=(candidate.weekday() - weekday) % 7)

    sessions = nse_fno_sessions(candidate - timedelta(days=7), candidate)
    if candidate not in sessions:
        eligible = [d for d in sessions if d <= candidate]
        if not eligible:
            raise ValueError(f"No NSE F&O session available near monthly expiry {year}-{month:02d}")
        candidate = eligible[-1]
    return candidate


def previous_nifty_monthly_expiry(expiry: date) -> date:
    """Return the actual NIFTY monthly expiry immediately preceding expiry."""
    if expiry.month == 1:
        year, month = expiry.year - 1, 12
    else:
        year, month = expiry.year, expiry.month - 1
    return nifty_monthly_expiry_for_month(year, month)
