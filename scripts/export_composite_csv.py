from pathlib import Path
import duckdb

src = Path("results/composite/nifty_options_composite.parquet")
dst = Path("results/composite/consolidated_options_data.csv")
dst.parent.mkdir(parents=True, exist_ok=True)

if not src.exists():
    raise SystemExit("Composite parquet not found; run composite_data.py first.")

con = duckdb.connect()
src_sql = str(src).replace("'", "''")
dst_sql = str(dst).replace("'", "''")
con.execute(
    f"COPY (SELECT * FROM read_parquet('{src_sql}') ORDER BY expiry, timestamp, strike, option_type) "
    f"TO '{dst_sql}' (FORMAT CSV, HEADER TRUE)"
)
con.close()
print(dst)
