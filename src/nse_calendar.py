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
