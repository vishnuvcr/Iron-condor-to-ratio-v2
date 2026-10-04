from pathlib import Path
import argparse
import duckdb
import hashlib
import json

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--partitions", default="results/partitions")
    ap.add_argument("--out", default="results/composite")
    args = ap.parse_args()

    partitions = sorted(Path(args.partitions).glob("*/nifty_options_composite.parquet"))
    if not partitions:
        raise SystemExit("No partition Parquet files found")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    target = out / "nifty_options_composite.parquet"
    work = out / "partition_merge.duckdb"

    con = duckdb.connect(str(work))
    con.execute("SET memory_limit='4GB'")
    con.execute("SET threads=2")
    paths = [str(p) for p in partitions]
    con.execute(
        "CREATE OR REPLACE TABLE composite AS "
        "SELECT * FROM read_parquet(?, union_by_name=true) "
        "ORDER BY expiry, timestamp, strike, option_type",
        [paths],
    )
    con.execute(
        "COPY composite TO ? (FORMAT PARQUET, COMPRESSION ZSTD)",
        [str(target)],
    )
    total = con.execute("SELECT COUNT(*) FROM composite").fetchone()[0]
    by_source = con.execute(
        "SELECT price_source, COUNT(*) FROM composite GROUP BY 1 ORDER BY 1"
    ).fetchall()
    con.close()

    manifest = {
        "status": "BUILT",
        "partition_count": len(partitions),
        "partitions": [str(p) for p in partitions],
        "rows": int(total),
        "price_rows_by_source": {str(k): int(v) for k, v in by_source},
        "composite_sha256": sha256_file(target),
    }
    (out / "composite_manifest.json").write_text(json.dumps(manifest, indent=2))

if __name__ == "__main__":
    main()
