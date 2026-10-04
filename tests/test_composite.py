import pandas as pd
from scripts.composite_data import normalize_frame, validate_rows, compose

def test_composite_uses_fallback_whole_row_without_price_mixing():
    ts = pd.Timestamp('2025-01-02 09:20:00+05:30')
    primary = pd.DataFrame([{'timestamp': ts, 'expiry': '2025-01-30', 'strike': 24000, 'option_type': 'CE', 'open': 0.0, 'high': 0.0, 'low': 0.0, 'close': 0.0, 'volume': 100, 'oi': 10}])
    fallback = pd.DataFrame([{'timestamp': ts, 'expiry': '2025-01-30', 'strike': 24000, 'option_type': 'CE', 'open': 10.0, 'high': 11.0, 'low': 9.0, 'close': 10.5, 'volume': 100, 'oi': 20}])
    a = normalize_frame(primary, 'thetrademarkk', 'x.parquet')
    b = normalize_frame(fallback, 'cloudtrader', 'y.csv')
    out, _ = compose([a, b])
    assert len(out) == 1
    assert out.iloc[0]['price_source'] == 'cloudtrader'
    assert out.iloc[0]['close'] == 10.5

def test_validate_rejects_impossible_ohlc():
    df = pd.DataFrame([{'timestamp': '2025-01-02T09:20:00+05:30', 'expiry': '2025-01-30', 'strike': 24000, 'option_type': 'CE', 'open': 10, 'high': 9, 'low': 8, 'close': 9, 'volume': 1, 'open_interest': 1, 'price_source': 'thetrademarkk', 'oi_source': 'thetrademarkk', 'source_file': 'x', 'source_revision': 'r', 'source_row_hash': 'h'}])
    out, stats = validate_rows(df)
    assert out.empty
    assert stats['rejected_rows'] == 1

def test_cloudtrader_symbol_date_time_normalization():
    raw = pd.DataFrame([{
        "Symbol": "NIFTY25JAN24000CE",
        "Date": "2025-01-02",
        "Time": "09:20:00",
        "Open": 10.0,
        "High": 11.0,
        "Low": 9.0,
        "Close": 10.5,
        "Volume": 100,
        "Open Interest": 1000,
    }])
    # Normalize the schema names exactly as the public provider documents them.
    raw = raw.rename(columns={"Open Interest": "Open Interest"})
    out = normalize_frame(raw, "cloudtrader", "sample.csv")
    assert out.iloc[0]["strike"] == 24000
    assert out.iloc[0]["option_type"] == "CE"
    assert out.iloc[0]["timestamp"].tz is not None


def test_cloudtrader_expiry_is_marked_inferred():
    raw = pd.DataFrame([{
        "Symbol": "NIFTY25JAN24000CE",
        "Date": "2025-01-02",
        "Time": "09:20:00",
        "Open": 10.0, "High": 11.0, "Low": 9.0, "Close": 10.5,
        "Volume": 100, "OI": 1000,
    }])
    out = normalize_frame(raw, "cloudtrader", "sample.csv")
    assert out.iloc[0]["expiry_source"] == "SYMBOL_MONTH_HINT_UNRESOLVED"
    assert out.iloc[0]["expiry_month_key"] == "2025-01"

def test_explicit_expiry_survives_composite_priority():
    primary = pd.DataFrame([{
        "timestamp": "2025-01-02T09:20:00+05:30", "expiry": "2025-01-30", "strike": 24000,
        "option_type": "CE", "open": 10, "high": 11, "low": 9, "close": 10.5, "volume": 10,
        "open_interest": 100,
    }])
    out = normalize_frame(primary, "thetrademarkk", "x.parquet")
    assert out.iloc[0]["expiry_source"] == "EXPLICIT_SOURCE_FIELD"

def test_composite_backtest_loader_accepts_exact_fallback_row(tmp_path):
    import datetime as dt
    from scripts.backtest import load_cycle_data
    df = pd.DataFrame([{
        "timestamp": pd.Timestamp("2025-01-02 09:20:00", tz="Asia/Kolkata"),
        "expiry": pd.Timestamp("2025-01-30"), "expiry_source": "EXPLICIT_SOURCE_FIELD",
        "strike": 24000.0, "option_type": "CE", "open": 10.0, "high": 11.0,
        "low": 9.0, "close": 10.5, "volume": 100.0,
    }])
    p = tmp_path / "nifty_options_composite.parquet"
    df.to_parquet(p, index=False)
    out = load_cycle_data([p], dt.date(2025, 1, 30), dt.date(2024, 12, 20), dt.date(2025, 1, 29))
    assert len(out) == 1

def test_inferred_only_expiry_is_not_production_eligible(tmp_path):
    import datetime as dt
    p = tmp_path / "nifty_options_composite.parquet"
    pd.DataFrame([{
        "expiry": pd.Timestamp("2025-01-30"), "expiry_source": "INFERRED_LAST_OBSERVED"
    }]).to_parquet(p, index=False)
    import duckdb
    con = duckdb.connect()
    df = con.execute(
        "SELECT DISTINCT CAST(expiry AS DATE) AS expiry "
        "FROM read_parquet(?) WHERE expiry IS NOT NULL "
        "AND expiry_source = 'EXPLICIT_SOURCE_FIELD' ORDER BY 1",
        [str(p)],
    ).fetchdf()
    con.close()
    remote = ["COMPOSITE::" + x.date().isoformat() for _, x in df.iterrows()]
    from scripts.backtest import load_expiry_list
    assert load_expiry_list(remote, dt.date(2025, 1, 1), dt.date(2025, 12, 31)) == []


def test_symbol_month_resolves_against_explicit_source():
    cloud = pd.DataFrame([{
        "Symbol": "NIFTY25JAN24000CE",
        "Date": "2025-01-02",
        "Time": "09:20:00",
        "Open": 10.0, "High": 11.0, "Low": 9.0, "Close": 10.5,
        "Volume": 100, "OI": 1000,
    }])
    explicit = pd.DataFrame([{
        "timestamp": "2025-01-02T09:20:00+05:30",
        "expiry": "2025-01-30",
        "strike": 24000,
        "option_type": "CE",
        "open": 10.0, "high": 11.0, "low": 9.0, "close": 10.5,
        "volume": 100, "open_interest": 1000,
    }])
    from scripts.composite_data import normalize_frame, compose
    cloud_n = normalize_frame(cloud, "cloudtrader", "cloud.csv")
    explicit_n = normalize_frame(explicit, "thetrademarkk", "explicit.parquet")
    out, _ = compose([explicit_n, cloud_n])
    cloud_rows = out[out["price_source"] == "cloudtrader"]
    assert len(cloud_rows) == 1
    assert cloud_rows.iloc[0]["expiry"].isoformat() == "2025-01-30"
    assert cloud_rows.iloc[0]["expiry_source"] == "RESOLVED_FROM_EXPLICIT_SOURCE"

def test_unresolved_symbol_month_does_not_enter_composite_as_production_cycle():
    from scripts.composite_data import normalize_frame, compose
    cloud = pd.DataFrame([{
        "Symbol": "NIFTY25JAN24000CE",
        "Date": "2025-01-02",
        "Time": "09:20:00",
        "Open": 10.0, "High": 11.0, "Low": 9.0, "Close": 10.5,
        "Volume": 100, "OI": 1000,
    }])
    out, _ = compose([normalize_frame(cloud, "cloudtrader", "cloud.csv")])
    assert out.empty


def test_source_row_hash_is_generated_for_mixed_types():
    raw = pd.DataFrame([{
        "timestamp": "2025-01-02T09:20:00+05:30",
        "expiry": "2025-01-30",
        "strike": 24000.0,
        "option_type": "CE",
        "open": 10.0, "high": 11.0, "low": 9.0, "close": 10.5,
        "volume": 100, "open_interest": 1000,
    }])
    out = normalize_frame(raw, "thetrademarkk", "sample.parquet")
    assert isinstance(out.iloc[0]["source_row_hash"], str)
    assert len(out.iloc[0]["source_row_hash"]) == 64

def test_naive_date_time_is_localized_to_ist_without_shift():
    raw = pd.DataFrame([{
        "Symbol": "NIFTY25JAN24000CE",
        "Date": "2025-01-02",
        "Time": "09:20:00",
        "Open": 10.0, "High": 11.0, "Low": 9.0, "Close": 10.5,
        "Volume": 100, "OI": 1000,
    }])
    out = normalize_frame(raw, "cloudtrader", "sample.csv")
    assert str(out.iloc[0]["timestamp"]) == "2025-01-02 09:20:00+05:30"


def test_requested_months_are_independent_of_primary_file_presence(tmp_path):
    import json
    from scripts.check_composite_coverage import expected_monthly_candidates

    manifest = tmp_path / "source_staging_manifest.json"
    manifest.write_text(json.dumps({
        "start": "2021-01-01",
        "end": "2026-09-30",
        "thetrademarkk": {
            "files": [
                "data/cache/thetrademarkk/2021-05-27.parquet",
                "data/cache/thetrademarkk/2026-08-04.parquet",
            ]
        },
    }))
    candidates = expected_monthly_candidates(manifest)
    assert len(candidates) == 69
    by_month = {x["month"]: x for x in candidates}
    assert by_month[(2021, 1)]["primary_file_available"] is False
    assert by_month[(2021, 5)]["primary_file_available"] is True
    assert by_month[(2026, 9)]["primary_file_available"] is False
