from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass

import pandas as pd

IST = "Asia/Kolkata"

CANON = [
    "timestamp", "expiry", "expiry_source", "expiry_month_key", "strike", "option_type",
    "open", "high", "low", "close", "volume", "open_interest",
    "price_source", "oi_source", "source_file", "source_revision", "source_row_hash",
]

@dataclass(frozen=True)
class SourceSpec:
    name: str
    priority: int

SOURCES = [
    SourceSpec("thetrademarkk", 1),
    SourceSpec("cloudtrader", 2),
    SourceSpec("artist23", 3),
    SourceSpec("zenodo", 4),
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

def normalize_frame(df: pd.DataFrame, source: str, source_file: str, source_revision: str = "unknown") -> pd.DataFrame:
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
    ts = pd.to_datetime(ts_values, errors="coerce", utc=True)
    out["timestamp"] = ts.dt.tz_convert(IST)

    symbol_series = df[symbol_col].astype(str) if symbol_col else None
    if strike_col:
        out["strike"] = pd.to_numeric(df[strike_col], errors="coerce")
    elif symbol_series is not None:
        parsed_strike = symbol_series.str.extract(r"(\\d+(?:\\.\\d+)?)(?:CE|PE)$", expand=False)
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
        parsed = pd.to_datetime(df[expiry_col], errors="coerce")
        out["expiry"] = parsed.dt.date
        out["expiry_source"] = "EXPLICIT_SOURCE_FIELD"
    else:
        out["expiry"] = pd.NaT
        out["expiry_source"] = "MISSING"

    out["expiry_month_key"] = pd.Series(pd.NA, index=out.index, dtype="string")
    if symbol_col:
        symbols = df[symbol_col].astype(str)
        month_key = symbol_month_key(symbols)
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
    out["source_row_hash"] = (
        out[["timestamp", "expiry", "strike", "option_type", "open", "high", "low", "close", "volume"]]
        .astype(str).agg("|".join, axis=1)
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
    x = x.drop_duplicates(["timestamp", "expiry", "strike", "option_type"], keep="last")
    return x, {"input_rows": int(before), "valid_rows": int(len(x)), "rejected_rows": int(before - len(x))}

def resolve_cross_source_expiry(frames: list[pd.DataFrame]) -> list[pd.DataFrame]:
    explicit_calendar = {}
    for frame in frames:
        if frame.empty:
            continue
        explicit = frame[frame["expiry_source"] == "EXPLICIT_SOURCE_FIELD"]
        for e in explicit["expiry"].dropna().unique():
            ts = pd.Timestamp(e)
            explicit_calendar[f"{ts.year:04d}-{ts.month:02d}"] = ts.date()

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
    if not frames:
        return pd.DataFrame(columns=CANON), {"rows": 0}

    frames = resolve_cross_source_expiry(frames)
    cleaned = []
    for f in frames:
        c, _ = validate_rows(f)
        if not c.empty:
            cleaned.append(c)

    if not cleaned:
        return pd.DataFrame(columns=CANON), {"rows": 0}

    rank = {s.name: s.priority for s in SOURCES}
    base = pd.concat(cleaned, ignore_index=True, sort=False)
    key = ["timestamp", "expiry", "strike", "option_type"]
    base["_rank"] = base["price_source"].map(rank).fillna(999)
    base = base.sort_values(key + ["_rank"])

    chosen = base.drop_duplicates(key, keep="first").copy()

    oi_candidates = base[base["open_interest"].notna()].sort_values(key + ["_rank"])
    oi_candidates = oi_candidates.drop_duplicates(key, keep="first")[key + ["open_interest", "price_source"]]
    oi_candidates = oi_candidates.rename(
        columns={"open_interest": "_oi_fill", "price_source": "oi_source_fill"}
    )
    chosen = chosen.merge(oi_candidates, on=key, how="left")
    fill_mask = chosen["open_interest"].isna() & chosen["_oi_fill"].notna()
    chosen.loc[fill_mask, "open_interest"] = chosen.loc[fill_mask, "_oi_fill"]
    chosen.loc[fill_mask, "oi_source"] = chosen.loc[fill_mask, "oi_source_fill"]
    chosen = chosen.drop(columns=["_oi_fill", "oi_source_fill", "_rank"])
    chosen = chosen.sort_values(key).reset_index(drop=True)

    return chosen, {
        "rows": int(len(chosen)),
        "price_rows_by_source": {str(k): int(v) for k, v in chosen["price_source"].value_counts().items()},
        "oi_supplement_rows": int(fill_mask.sum()),
    }

def overlap_audit(frames: list[pd.DataFrame]) -> pd.DataFrame:
    cleaned = [validate_rows(f)[0] for f in frames]
    key = ["timestamp", "expiry", "strike", "option_type"]
    parts = []
    for i in range(len(cleaned)):
        for j in range(i + 1, len(cleaned)):
            if cleaned[i].empty or cleaned[j].empty:
                continue
            a = cleaned[i].merge(cleaned[j], on=key, suffixes=("_a", "_b"))
            if a.empty:
                continue
            src_a = frames[i]["price_source"].iloc[0]
            src_b = frames[j]["price_source"].iloc[0]
            a["source_a"] = src_a
            a["source_b"] = src_b
            for fld in ["open", "high", "low", "close"]:
                a[f"{fld}_abs_diff"] = (a[f"{fld}_a"] - a[f"{fld}_b"]).abs()
                denom = a[[f"{fld}_a", f"{fld}_b"]].abs().max(axis=1).replace(0, pd.NA)
                a[f"{fld}_rel_diff"] = a[f"{fld}_abs_diff"] / denom
            parts.append(a)
    return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="results/composite")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    manifest = {
        "created_utc": datetime.utcnow().isoformat() + "Z",
        "protocol": "research/COMPOSITE_DATA_PROTOCOL.md",
        "sources_attempted": [s.name for s in SOURCES],
        "notes": [],
    }

    staged = sorted(Path("data/cache/thetrademarkk").glob("*.parquet")) + sorted(Path("data/cache/cloudtrader").glob("**/*.csv")) + sorted(Path("data/cache/artist23").glob("**/*.parquet"))
    frames = []
    source_stats = []

    for path in staged:
        source = next((s.name for s in SOURCES if s.name in str(path).lower()), None)
        if not source:
            manifest["notes"].append(f"unclassified_file:{path}")
            continue
        try:
            raw = pd.read_parquet(path) if path.suffix.lower() == ".parquet" else pd.read_csv(path)
            revision_file = path.with_suffix(path.suffix + ".revision")
            revision = revision_file.read_text().strip() if revision_file.exists() else "unknown"
            nf = normalize_frame(raw, source, str(path), revision)
            cleaned, stats = validate_rows(nf)
            frames.append(cleaned)
            stats.update({"source": source, "file": str(path), "sha256": sha256_file(path)})
            source_stats.append(stats)
        except Exception as exc:
            manifest["notes"].append(f"load_failed:{path}:{type(exc).__name__}:{exc}")

    if not frames:
        manifest["status"] = "NO_STAGED_DATA"
        (out / "composite_manifest.json").write_text(json.dumps(manifest, indent=2))
        return

    composite, stats = compose(frames)
    composite.to_parquet(out / "nifty_options_composite.parquet", index=False)
    overlap = overlap_audit(frames)
    overlap.to_parquet(out / "source_overlap.parquet", index=False)

    manifest["status"] = "BUILT"
    manifest["source_stats"] = source_stats
    manifest["composition_stats"] = stats
    manifest["composite_sha256"] = sha256_file(out / "nifty_options_composite.parquet")
    manifest["overlap_rows"] = int(len(overlap))
    (out / "composite_manifest.json").write_text(json.dumps(manifest, indent=2))

if __name__ == "__main__":
    main()
