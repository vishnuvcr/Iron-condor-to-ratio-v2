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