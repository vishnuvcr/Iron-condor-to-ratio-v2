import datetime as dt

from src.nse_calendar import nse_fno_holidays, nse_fno_sessions


def test_nse_fno_holiday_file_has_all_years():
    holidays = nse_fno_holidays()
    assert all(year in {d.year for d in holidays} for year in range(2021, 2027))


def test_nse_fno_2025_holiday_is_not_a_normal_session():
    sessions = set(nse_fno_sessions(dt.date(2025, 2, 24), dt.date(2025, 2, 28)))
    assert dt.date(2025, 2, 26) not in sessions


def test_nse_fno_2026_holiday_is_not_a_normal_session():
    sessions = set(nse_fno_sessions(dt.date(2026, 5, 25), dt.date(2026, 5, 29)))
    assert dt.date(2026, 5, 28) not in sessions


def test_weekend_is_not_a_normal_nse_fno_session():
    sessions = set(nse_fno_sessions(dt.date(2025, 1, 3), dt.date(2025, 1, 6)))
    assert dt.date(2025, 1, 4) not in sessions
    assert dt.date(2025, 1, 5) not in sessions
    assert dt.date(2025, 1, 6) in sessions


def test_2023_fno_calendar_does_not_silently_import_capital_market_only_holiday():
    sessions = set(nse_fno_sessions(dt.date(2023, 3, 20), dt.date(2023, 3, 24)))
    # March 22, 2023 was not in the official F&O holiday list used for this project.
    assert dt.date(2023, 3, 22) in sessions
