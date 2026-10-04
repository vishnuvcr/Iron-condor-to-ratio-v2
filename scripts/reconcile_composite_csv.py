from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path

import duckdb


ROOT = Path("results/composite")
PARQUET = ROOT / "nifty_options_composite.parquet"
CSV = ROOT / "consolidated_options_data.csv"
REPORT = ROOT / "csv_reconciliation.json"

EXPECTED = [
    "timestamp",
    "expiry",
    "expiry_source",
    "expiry_month_key",
    "strike",
    "option_type",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "open_interest",
    "price_source",
    "oi_source",
    "source_file",
    "source_revision",
    "source_row_hash",
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    if not PARQUET.exists() or not CSV.exists():
        REPORT.write_text(json.dumps({
            "status": "FAIL",
            "reason": "missing_parquet_or_csv",
        }, indent=2))
        raise SystemExit("Parquet/CSV reconciliation inputs missing")

    con = duckdb.connect()
    parquet_cols = [
        r[0] for r in con.execute(
            "DESCRIBE SELECT * FROM read_parquet(?)",
            [str(PARQUET)],
        ).fetchall()
    ]
    csv_cols = [
        r[0] for r in con.execute(
            "DESCRIBE SELECT * FROM read_csv_auto(?, HEADER=TRUE)",
            [str(CSV)],
        ).fetchall()
    ]
    parquet_count = int(con.execute(
        "SELECT COUNT(*) FROM read_parquet(?)",
        [str(PARQUET)],
    ).fetchone()[0])
    csv_count = int(con.execute(
        "SELECT COUNT(*) FROM read_csv_auto(?, HEADER=TRUE)",
        [str(CSV)],
    ).fetchone()[0])

    parquet_bounds = con.execute(
        """
        SELECT
            MIN(timestamp),
            MAX(timestamp),
            MIN(expiry),
            MAX(expiry)
        FROM read_parquet(?)
        """,
        [str(PARQUET)],
    ).fetchone()
    csv_bounds = con.execute(
        """
        SELECT
            MIN(timestamp),
            MAX(timestamp),
            MIN(expiry),
            MAX(expiry)
        FROM read_csv_auto(?, HEADER=TRUE)
        """,
        [str(CSV)],
    ).fetchone()

    # Re-create the deterministic CSV from the canonical Parquet and compare bytes.
    with tempfile.TemporaryDirectory() as tmp:
        recreated = Path(tmp) / "recreated.csv"
        con.execute(
            """
            COPY (
                SELECT *
                FROM read_parquet(?)
                ORDER BY expiry, timestamp, strike, option_type
            )
            TO ? (FORMAT CSV, HEADER TRUE)
            """,
            [str(PARQUET), str(recreated)],
        )
        recreated_hash = sha256_file(recreated)

    con.close()

    report = {
        "status": "PASS" if (
            parquet_cols == EXPECTED
            and csv_cols == EXPECTED
            and parquet_count == csv_count
            and parquet_bounds == csv_bounds
            and recreated_hash == sha256_file(CSV)
        ) else "FAIL",
        "expected_schema": EXPECTED,
        "parquet_schema": parquet_cols,
        "csv_schema": csv_cols,
        "parquet_rows": parquet_count,
        "csv_rows": csv_count,
        "parquet_bounds": [str(x) for x in parquet_bounds],
        "csv_bounds": [str(x) for x in csv_bounds],
        "recreated_csv_sha256": recreated_hash,
        "published_csv_sha256": sha256_file(CSV),
    }
    REPORT.write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    if report["status"] != "PASS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
