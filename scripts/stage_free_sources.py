from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
from datetime import date
from pathlib import Path

import requests
from huggingface_hub import HfApi, hf_hub_download

HF_REPO = "thetrademarkk/india-index-options-1m"
HF_URL = "https://huggingface.co/datasets/thetrademarkk/india-index-options-1m"
CLOUD_DRIVE_ID = "1-GRg9-ScM11OhxhxoovgXrLw6zFqDed7"
ZENODO_URL = "https://zenodo.org/records/10899828/files/Nifty%20Options%20Data.zip?download=1"


def monthly_expiry_files(files: list[str], start: date, end: date) -> list[str]:
    candidates = []
    for f in files:
        m = re.match(r"options/NIFTY/(\d{4}-\d{2}-\d{2})\.parquet$", f)
        if not m:
            continue
        e = date.fromisoformat(m.group(1))
        if start <= e <= end:
            candidates.append((e, f))
    by_month = {}
    for e, f in candidates:
        by_month[(e.year, e.month)] = max(by_month.get((e.year, e.month), (e, f)), (e, f))
    return [f for _, f in sorted(by_month.values())]


def download_hf_monthlies(out: Path, start: date, end: date, manifest: dict):
    token = os.getenv("HF_TOKEN")
    api = HfApi(token=token or None)
    files = api.list_repo_files(repo_id=HF_REPO, repo_type="dataset", revision="main")
    selected = monthly_expiry_files(files, start, end)
    info = api.dataset_info(HF_REPO, revision="main")
    revision = str(info.sha)
    target = out / "thetrademarkk"
    target.mkdir(parents=True, exist_ok=True)
    manifest["thetrademarkk"] = {"revision": revision, "files": []}
    for filename in selected:
        local = hf_hub_download(
            repo_id=HF_REPO,
            filename=filename,
            repo_type="dataset",
            token=token or None,
            cache_dir=str(out / "hf-cache"),
        )
        dst = target / Path(filename).name
        shutil.copy2(local, dst)
        (dst.with_suffix(dst.suffix + ".revision")).write_text(revision)
        manifest["thetrademarkk"]["files"].append(str(dst))
    return selected



def download_rissin(out: Path, start: date, end: date, manifest: dict):
    token = os.getenv("HF_TOKEN")
    api = HfApi(token=token or None)
    target = out / "rissin"
    target.mkdir(parents=True, exist_ok=True)
    years = sorted(set(range(max(start.year, 2024), end.year + 1)))
    info = api.dataset_info("rissin/nse-options-intraday", revision="main")
    revision = str(info.sha)
    manifest["rissin"] = {"revision": revision, "files": []}

    for year in years:
        filename = f"upstox_intraday/NIFTY/NIFTY_{year}.parquet"
        try:
            local = hf_hub_download(
                repo_id="rissin/nse-options-intraday",
                filename=filename,
                repo_type="dataset",
                token=token or None,
                cache_dir=str(out / "hf-cache-rissin"),
            )
            dst = target / f"NIFTY_{year}.parquet"
            shutil.copy2(local, dst)
            dst.with_suffix(dst.suffix + ".revision").write_text(revision)
            manifest["rissin"]["files"].append(str(dst))
        except Exception as exc:
            manifest["rissin"].setdefault("errors", []).append(
                {"file": filename, "error": repr(exc)}
            )

def download_cloudtrader(out: Path, manifest: dict):
    target = out / "cloudtrader"
    target.mkdir(parents=True, exist_ok=True)
    archive = target / "nifty_free_sample"
    existing = list(target.glob("*.csv")) + list(target.glob("*.zip"))
    if existing:
        manifest["cloudtrader"] = {"status": "CACHED", "files": [str(p) for p in existing]}
        return
    cmd = ["gdown", "--id", CLOUD_DRIVE_ID, "-O", str(archive)]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=60)
    except Exception as exc:
        manifest["cloudtrader"] = {"status": "DOWNLOAD_FAILED", "error": repr(exc), "drive_id": CLOUD_DRIVE_ID}
        return
    manifest["cloudtrader"] = {"status": "DOWNLOADED", "file": str(archive)}
    if zipfile_is_archive(archive):
        import zipfile
        with zipfile.ZipFile(archive) as zf:
            zf.extractall(target / "unzipped")
        manifest["cloudtrader"]["unzipped"] = True
    else:
        csv_path = target / "free_sample.csv"
        archive.replace(csv_path)
        manifest["cloudtrader"]["csv_path"] = str(csv_path)


def zipfile_is_archive(path: Path) -> bool:
    import zipfile
    return zipfile.is_zipfile(path)


def download_zenodo(out: Path, manifest: dict):
    target = out / "zenodo"
    target.mkdir(parents=True, exist_ok=True)
    dst = target / "Nifty Options Data.zip"
    if dst.exists() and dst.stat().st_size > 0:
        manifest["zenodo"] = {"status": "CACHED", "file": str(dst)}
        return
    try:
        with requests.get(ZENODO_URL, stream=True, timeout=60) as r:
            r.raise_for_status()
            with dst.open("wb") as fh:
                for chunk in r.iter_content(chunk_size=8 * 1024 * 1024):
                    if chunk:
                        fh.write(chunk)
        manifest["zenodo"] = {"status": "DOWNLOADED", "file": str(dst), "bytes": dst.stat().st_size}
    except Exception as exc:
        manifest["zenodo"] = {"status": "DOWNLOAD_FAILED", "error": repr(exc)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="2021-01-01")
    ap.add_argument("--end", default="2026-09-30")
    ap.add_argument("--cache-root", default="data/cache")
    ap.add_argument("--include-zenodo", action="store_true")
    args = ap.parse_args()

    root = Path(args.cache_root)
    root.mkdir(parents=True, exist_ok=True)
    start = date.fromisoformat(args.start)
    end = date.fromisoformat(args.end)

    manifest = {
        "start": args.start,
        "end": args.end,
        "sources": [],
        "hf_url": HF_URL,
        "cloud_drive_id": CLOUD_DRIVE_ID,
    }

    try:
        selected = download_hf_monthlies(root, start, end, manifest)
        manifest["sources"].append({"name": "thetrademarkk", "selected_monthly_files": len(selected)})
    except Exception as exc:
        manifest["thetrademarkk"] = {"status": "DOWNLOAD_FAILED", "error": repr(exc)}

    download_rissin(root, start, end, manifest)
    manifest["sources"].append({"name": "rissin"})
    download_cloudtrader(root, manifest)
    manifest["sources"].append({"name": "cloudtrader"})

    if args.include_zenodo:
        download_zenodo(root, manifest)
        manifest["sources"].append({"name": "zenodo"})

    out = Path("results/composite")
    out.mkdir(parents=True, exist_ok=True)
    (out / "source_staging_manifest.json").write_text(json.dumps(manifest, indent=2))
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
