from __future__ import annotations

import argparse
import calendar
import hashlib
import json
import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path

import duckdb
import pandas as pd

IST = "Asia/Kolkata"

CANON = [
    "timestamp", "expiry", "expiry_source", "expiry_month_key", "strike", "option_type",
    "open", "high", "low", "close", "volume", "open_interest",
    "price_source", "oi_source", "source_file", "source_revision", "source_row_hash",
]

KEY = ["timestamp", "expiry", "strike", "option_type"]


@dataclass(frozen=True)
class SourceSpec:
    name: str
    priority: int


SOURCES = [
    SourceSpec("thetrademarkk", 1),
    SourceSpec("rissin", 2),
    SourceSpec("cloudtrader", 3),
    SourceSpec("artist23", 4),
    SourceSpec("zenodo", 5),
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def normalize_option_type(value):
    s = str(value).strip().upper()
    if s in {"CE", "CALL"}:
        return "CE"
    if s in {"PE", "PUT"}:
        return "PE"
    return None


def symbol_month_key(symbols: pd.Series) -> pd.Series:
    months = {m: i for i, m in enumerate(
        ["JAN", "FEB", "MAR", "APR", "MAY", "JUN",
         "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"], 1
    )}
    extracted = symbols.str.upper().str.extract(r"NIFTY(?P<yy>\d{2})(?P<mon>[A-Z]{3})")
    values = []
    for yy, mon in extracted.itertuples(index=False):
        if pd.isna(yy) or mon not in months:
            values.append(pd.NA)
        else:
            values.append(f"{2000 + int(yy):04d}-{months[mon]:02d}")
    return pd.Series(values, index=symbols.index, dtype="string")


def normalize_frame(
    df: pd.DataFrame,
    source: str,
    source_file: str,
    source_revision: str = "unknown",
) -> pd.DataFrame:
    cols = {str(c).strip().lower().replace(" ", "_"): c for c in df.columns}

    def pick(*names):
        for name in names:
            if name in cols:
                return cols[name]
        return None

    ts_col = pick("timestamp", "datetime", "date_time")
    date_col = pick("date", "trading_date")
    time_col = pick("time", "trading_time")
    strike_col = pick("strike", "strike_price")
    type_col = pick("option_type", "opt_type", "type", "right")
    expiry_col = pick("expiry", "expiry_date", "expiry_dt")
    symbol_col = pick("symbol", "contract_symbol", "instrument")

    if not ts_col and date_col and time_col:
        ts_values = df[date_col].astype(str).str.strip() + " " + df[time_col].astype(str).str.strip()
    elif ts_col:
        ts_values = df[ts_col]
    else:
        raise ValueError(f"{source}: missing timestamp or date/time in {source_file}")

    out = pd.DataFrame()
    parsed_ts = pd.to_datetime(ts_values, errors="coerce")
    if getattr(parsed_ts.dt, "tz", None) is None:
        out["timestamp"] = parsed_ts.dt.tz_localize(IST)
    else:
        out["timestamp"] = parsed_ts.dt.tz_convert(IST)

    symbol_series = df[symbol_col].astype(str) if symbol_col else None

    if strike_col:
        out["strike"] = pd.to_numeric(df[strike_col], errors="coerce")
    elif symbol_series is not None:
        parsed_strike = symbol_series.str.extract(r"(\d+(?:\.\d+)?)(?:CE|PE)$", expand=False)
        out["strike"] = pd.to_numeric(parsed_strike, errors="coerce")
    else:
        raise ValueError(f"{source}: missing strike and symbol in {source_file}")

    if type_col:
        out["option_type"] = df[type_col].map(normalize_option_type)
    elif symbol_series is not None:
        out["option_type"] = symbol_series.str.extract(r"(CE|PE)$", expand=False).map(normalize_option_type)
    else:
        raise ValueError(f"{source}: missing option type and symbol in {source_file}")

    if expiry_col:
        out["expiry"] = pd.to_datetime(df[expiry_col], errors="coerce").dt.date
        out["expiry_source"] = "EXPLICIT_SOURCE_FIELD"
    else:
        out["expiry"] = pd.NaT
        out["expiry_source"] = "MISSING"

    out["expiry_month_key"] = pd.Series(pd.NA, index=out.index, dtype="string")
    if symbol_col:
        month_key = symbol_month_key(symbol_series)
        missing = out["expiry"].isna()
        out.loc[missing, "expiry_month_key"] = month_key[missing]
        out.loc[missing & month_key.notna(), "expiry_source"] = "SYMBOL_MONTH_HINT_UNRESOLVED"

    for dest, aliases in {
        "open": ("open",),
        "high": ("high",),
        "low": ("low",),
        "close": ("close",),
        "volume": ("volume",),
        "open_interest": ("open_interest", "oi"),
    }.items():
        col = pick(*aliases)
        out[dest] = pd.to_numeric(df[col], errors="coerce") if col else pd.NA

    out["price_source"] = source
    out["oi_source"] = source
    out["source_file"] = source_file
    out["source_revision"] = source_revision
    hash_cols = ["timestamp", "expiry", "strike", "option_type", "open", "high", "low", "close", "volume"]
    out["source_row_hash"] = (
        out[hash_cols].apply(lambda row: "|".join(map(str, row.tolist())), axis=1)
        .map(lambda x: hashlib.sha256(x.encode()).hexdigest())
    )
    return out[CANON]


def validate_rows(df: pd.DataFrame):
    x = df.copy()
    before = len(x)
    x = x.dropna(subset=["timestamp", "expiry", "strike", "option_type"])
    x = x[x["option_type"].isin(["CE", "PE"])]
    x = x[x["strike"] > 0]
    for c in ["open", "high", "low", "close", "volume", "open_interest"]:
        x[c] = pd.to_numeric(x[c], errors="coerce")
    price_ok = (
        x["open"].gt(0) & x["high"].gt(0) & x["low"].gt(0) & x["close"].gt(0)
        & x["volume"].ge(0)
        & x["high"].ge(x[["open", "close"]].max(axis=1))
        & x["low"].le(x[["open", "close"]].min(axis=1))
    )
    x = x[price_ok]
    x = x.drop_duplicates(KEY, keep="last")
    return x, {"input_rows": int(before), "valid_rows": int(len(x)), "rejected_rows": int(before - len(x))}


def resolve_cross_source_expiry(frames: list[pd.DataFrame]) -> list[pd.DataFrame]:
    explicit_calendar = {}
    for frame in frames:
        if frame.empty:
            continue
        explicit = frame[frame["expiry_source"] == "EXPLICIT_SOURCE_FIELD"]
        for e in explicit["expiry"].dropna().unique():
            ts = pd.Timestamp(e)
            ym = f"{ts.year:04d}-{ts.month:02d}"
            explicit_calendar[ym] = max(explicit_calendar.get(ym, ts.date()), ts.date())

    resolved = []
    for frame in frames:
        x = frame.copy()
        mask = x["expiry"].isna() & x["expiry_month_key"].notna()
        if mask.any():
            mapped = x.loc[mask, "expiry_month_key"].map(explicit_calendar)
            ok = mapped.notna()
            idx = mapped.index[ok]
            x.loc[idx, "expiry"] = mapped.loc[idx]
            x.loc[idx, "expiry_source"] = "RESOLVED_FROM_EXPLICIT_SOURCE"
        resolved.append(x)
    return resolved


def compose(frames: list[pd.DataFrame]):
    frames = resolve_cross_source_expiry(frames)
    if not frames:
        return pd.DataFrame(columns=CANON), {"rows": 0}

    # Keep canonical expiry dtype stable across source-specific frames.
    # Cross-source resolution can otherwise produce Python date in one frame
    # and pandas Timestamp in another, which Pandas 3.x refuses to order.
    normalized_frames = []
    for frame in frames:
        x = frame.copy()
        x["expiry"] = pd.to_datetime(x["expiry"], errors="coerce").dt.date
        normalized_frames.append(x)
    frames = normalized_frames

    cleaned = []
    for f in frames:
        c, _ = validate_rows(f)
        if not c.empty:
            cleaned.append(c)

    if not cleaned:
        return pd.DataFrame(columns=CANON), {"rows": 0}

    rank = {s.name: s.priority for s in SOURCES}
    base = pd.concat(cleaned, ignore_index=True, sort=False)
    base["_rank"] = base["price_source"].map(rank).fillna(999)
    base = base.sort_values(KEY + ["_rank"])
    chosen = base.drop_duplicates(KEY, keep="first").copy()

    oi_candidates = base[base["open_interest"].notna()].sort_values(KEY + ["_rank"])
    oi_candidates = oi_candidates.drop_duplicates(KEY, keep="first")[KEY + ["open_interest", "price_source"]]
    oi_candidates = oi_candidates.rename(columns={"open_interest": "_oi_fill", "price_source": "oi_source_fill"})
    chosen = chosen.merge(oi_candidates, on=KEY, how="left")
    fill_mask = chosen["open_interest"].isna() & chosen["_oi_fill"].notna()
    chosen.loc[fill_mask, "open_interest"] = chosen.loc[fill_mask, "_oi_fill"]
    chosen.loc[fill_mask, "oi_source"] = chosen.loc[fill_mask, "oi_source_fill"]
    chosen = chosen.drop(columns=["_oi_fill", "oi_source_fill", "_rank"]).sort_values(KEY).reset_index(drop=True)

    return chosen, {
        "rows": int(len(chosen)),
        "price_rows_by_source": {str(k): int(v) for k, v in chosen["price_source"].value_counts().items()},
        "oi_supplement_rows": int(fill_mask.sum()),
    }


def staged_files():
    root = Path("data/cache")
    groups = {
        "thetrademarkk": sorted((root / "thetrademarkk").glob("*.parquet")),
        "rissin": sorted((root / "rissin").glob("*.parquet")),
        "cloudtrader": sorted((root / "cloudtrader").glob("**/*.csv")),
        "artist23": sorted((root / "artist23").glob("**/*.parquet")),
        "zenodo": sorted((root / "zenodo").glob("**/*.parquet")),
    }
    order = {s.name: s.priority for s in SOURCES}
    return [(name, p) for name, files in groups.items() for p in files if name in order]


def explicit_calendar_from_staged(files):
    expiry_calendar = {}
    for source, path in files:
        if source != "thetrademarkk":
            continue
        try:
            e = pd.Timestamp(path.stem).date()
        except Exception:
            continue
        month_end = date(
            e.year,
            e.month,
            calendar.monthrange(e.year, e.month)[1],
        )
        if e < month_end - timedelta(days=6) or e > month_end:
            continue
        ym = f"{e.year:04d}-{e.month:02d}"
        expiry_calendar[ym] = max(expiry_calendar.get(ym, e), e)
    return expiry_calendar


def _read_source_file(path: Path):
    return pd.read_parquet(path) if path.suffix.lower() == ".parquet" else pd.read_csv(path)


def build_disk_backed(files, out: Path, manifest: dict, revision_by_file: dict):
    work_db = out / "composite_work.duckdb"
    con = duckdb.connect(str(work_db))
    con.execute("SET memory_limit='4GB'")
    con.execute("SET threads=2")
    out.mkdir(parents=True, exist_ok=True)

    grouped = {}
    for source, path in files:
        grouped.setdefault(source, []).append(path)

    overlap_rows = []
    source_stats = []

    # Ingest primary partitions sequentially into the disk-backed DuckDB table.
    # This avoids materializing the full multi-year option chain at once.
    primary = sorted(grouped.get("thetrademarkk", []))
    calendar = explicit_calendar_from_staged(files)

    for idx, path in enumerate(primary):
        revision = revision_by_file.get(str(path), "unknown")
        action = "CREATE TABLE composite AS" if idx == 0 else "INSERT INTO composite"
        con.execute(
            f"""
            {action}
            SELECT
                timestamp,
                CAST(expiry AS DATE) AS expiry,
                'EXPLICIT_SOURCE_FIELD' AS expiry_source,
                CAST(NULL AS VARCHAR) AS expiry_month_key,
                strike,
                UPPER(option_type) AS option_type,
                open,
                high,
                low,
                close,
                volume,
                open_interest,
                'thetrademarkk' AS price_source,
                'thetrademarkk' AS oi_source,
                filename AS source_file,
                ? AS source_revision,
                sha256(concat_ws('|',
                    CAST(timestamp AS VARCHAR), CAST(expiry AS VARCHAR),
                    CAST(strike AS VARCHAR), CAST(option_type AS VARCHAR),
                    CAST(open AS VARCHAR), CAST(high AS VARCHAR),
                    CAST(low AS VARCHAR), CAST(close AS VARCHAR),
                    CAST(volume AS VARCHAR)
                )) AS source_row_hash
            FROM read_parquet(?, union_by_name=true, filename=true)
            WHERE timestamp IS NOT NULL
              AND expiry IS NOT NULL
              AND strike > 0
              AND UPPER(option_type) IN ('CE', 'PE')
              AND open > 0 AND high > 0 AND low > 0 AND close > 0
              AND volume >= 0
              AND high >= GREATEST(open, close)
              AND low <= LEAST(open, close)
              AND CAST(expiry AS DATE) >= CAST(timestamp AS DATE)
            QUALIFY ROW_NUMBER() OVER (
                PARTITION BY timestamp, CAST(expiry AS DATE), strike, UPPER(option_type)
                ORDER BY filename
            ) = 1
            """,
            [revision, str(path)],
        )
        valid_rows = int(
            con.execute(
                "SELECT COUNT(*) FROM composite WHERE source_file = ?",
                [str(path)],
            ).fetchone()[0]
        )
        source_stats.append(
            {
                "source": "thetrademarkk",
                "file": str(path),
                "valid_rows": valid_rows,
                "sha256": sha256_file(path),
                "source_revision": revision,
            }
        )

    # Lower-priority sources are small enough to normalize one file at a time.
    lower = []
    for source, paths in grouped.items():
        if source != "thetrademarkk":
            lower.extend((source, p) for p in sorted(paths))

    for source, path in lower:
        raw = _read_source_file(path)
        frame = normalize_frame(raw, source, str(path), revision_by_file.get(str(path), "unknown"))

        mask = frame["expiry"].isna() & frame["expiry_month_key"].notna()
        if mask.any() and calendar:
            mapped = frame.loc[mask, "expiry_month_key"].map(calendar)
            ok = mapped.notna()
            idx = mapped.index[ok]
            frame.loc[idx, "expiry"] = mapped.loc[idx]
            frame.loc[idx, "expiry_source"] = "RESOLVED_FROM_EXPLICIT_SOURCE"

        clean, stats = validate_rows(frame)
        stats.update({"source": source, "file": str(path), "sha256": sha256_file(path)})
        source_stats.append(stats)
        if clean.empty or "composite" not in [x[0] for x in con.execute("SHOW TABLES").fetchall()]:
            if clean.empty:
                continue

        con.register("stage_df", clean)
        row = con.execute(
            """SELECT
                 COUNT(*) AS overlap_rows,
                 AVG(ABS(c.close - s.close) / NULLIF(GREATEST(ABS(c.close), ABS(s.close)), 0)) AS close_rel_diff_mean,
                 MAX(ABS(c.close - s.close) / NULLIF(GREATEST(ABS(c.close), ABS(s.close)), 0)) AS close_rel_diff_max
               FROM composite c
               JOIN stage_df s
                 ON c.timestamp = s.timestamp
                AND c.expiry = s.expiry
                AND c.strike = s.strike
                AND c.option_type = s.option_type
              WHERE c.price_source <> s.price_source"""
        ).fetchone()
        overlap_rows.append({
            "source": source,
            "file": str(path),
            "overlap_rows": int(row[0] or 0),
            "close_rel_diff_mean": float(row[1]) if row[1] is not None else None,
            "close_rel_diff_max": float(row[2]) if row[2] is not None else None,
        })

        con.execute(
            """UPDATE composite AS c
               SET open_interest = s.open_interest,
                   oi_source = s.price_source
               FROM stage_df AS s
               WHERE c.timestamp = s.timestamp
                 AND c.expiry = s.expiry
                 AND c.strike = s.strike
                 AND c.option_type = s.option_type
                 AND c.open_interest IS NULL
                 AND s.open_interest IS NOT NULL"""
        )
        con.execute(
            """INSERT INTO composite
               SELECT s.*
               FROM stage_df s
               ANTI JOIN composite c
                 ON c.timestamp = s.timestamp
                AND c.expiry = s.expiry
                AND c.strike = s.strike
                AND c.option_type = s.option_type"""
        )
        con.unregister("stage_df")

    tables = {r[0] for r in con.execute("SHOW TABLES").fetchall()}
    if "composite" not in tables:
        con.close()
        manifest["status"] = "NO_VALID_STAGED_DATA"
        (out / "composite_manifest.json").write_text(json.dumps(manifest, indent=2))
        return

    output_parquet = out / "nifty_options_composite.parquet"
    con.execute(
        "COPY (SELECT * FROM composite ORDER BY expiry, timestamp, strike, option_type) TO ? (FORMAT PARQUET, COMPRESSION ZSTD)",
        [str(output_parquet)],
    )
    counts = con.execute("SELECT price_source, COUNT(*) FROM composite GROUP BY 1 ORDER BY 1").fetchall()
    oi_sources = con.execute("SELECT oi_source, COUNT(*) FROM composite GROUP BY 1 ORDER BY 1").fetchall()
    total = con.execute("SELECT COUNT(*) FROM composite").fetchone()[0]
    con.close()

    pd.DataFrame(overlap_rows).to_csv(out / "source_overlap.csv", index=False)
    manifest["status"] = "BUILT"
    manifest["source_stats"] = source_stats
    manifest["composition_stats"] = {
        "rows": int(total),
        "price_rows_by_source": {str(k): int(v) for k, v in counts},
        "oi_rows_by_source": {str(k): int(v) for k, v in oi_sources},
    }
    manifest["composite_sha256"] = sha256_file(output_parquet)
    manifest["overlap_file"] = "source_overlap.csv"
    (out / "composite_manifest.json").write_text(json.dumps(manifest, indent=2)
)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="results/composite")
    ap.add_argument("--start", default=None)
    ap.add_argument("--end", default=None)
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    files = staged_files()
    if args.start or args.end:
        start = pd.Timestamp(args.start or "1900-01-01").date()
        end = pd.Timestamp(args.end or "2100-12-31").date()
        selected = []
        for source, path in files:
            if source == "thetrademarkk":
                try:
                    d = pd.Timestamp(path.stem).date()
                except Exception:
                    continue
                if start <= d <= end:
                    selected.append((source, path))
            elif source == "rissin":
                # Year-partitioned rissin files are retained when their year
                # overlaps the requested partition.
                m = re.search(r"(20\\d{2})", path.stem)
                if m and start.year <= int(m.group(1)) <= end.year:
                    selected.append((source, path))
            else:
                selected.append((source, path))
        files = selected
    manifest = {
        "created_utc": datetime.utcnow().isoformat() + "Z",
        "protocol": "research/COMPOSITE_DATA_PROTOCOL.md",
        "sources_attempted": sorted({s for s, _ in files}),
        "production_expiry_sources": ["EXPLICIT_SOURCE_FIELD", "RESOLVED_FROM_EXPLICIT_SOURCE"],
        "staged_file_count": len(files),
        "notes": [],
    }

    revision_by_file = {}
    for _, path in files:
        rev = path.with_suffix(path.suffix + ".revision")
        revision_by_file[str(path)] = rev.read_text().strip() if rev.exists() else "unknown"

    build_disk_backed(files, out, manifest, revision_by_file)


if __name__ == "__main__":
    main()
