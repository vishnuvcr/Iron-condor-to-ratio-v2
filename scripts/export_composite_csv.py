from pathlib import Path
import duckdb

src = Path("results/composite/nifty_options_composite.parquet")
dst = Path("results/composite/consolidated_options_data.csv")
dst.parent.mkdir(parents=True, exist_ok=True)

if not src.exists():
    raise SystemExit("Composite parquet not found; run composite_data.py first.")

con = duckdb.connect()
con.execute(
    "COPY (SELECT * FROM read_parquet(?) ORDER BY expiry, timestamp, strike, option_type) TO ? "
    "(FORMAT CSV, HEADER TRUE)",
    [str(src), str(dst)],
)
con.close()
print(dst)
