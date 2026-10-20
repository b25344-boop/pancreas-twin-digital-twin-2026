"""
Fetch the open datasets used by Project Pancreas Twin into data/raw/ (relative to the project folder).

Raw data is NOT bundled with the repository. Each dataset keeps its own licence (see DATA_SOURCES.md);
by running this script you accept those terms.

Usage (from anywhere):
    python scripts/download_data.py --list              # show datasets, URLs, licences
    python scripts/download_data.py --dry-run           # show what would be downloaded
    python scripts/download_data.py                     # fetch the four modelling cohorts
    python scripts/download_data.py cgmacros shanghai   # fetch selected cohorts only

Layout produced (the paths the pipeline scripts expect inside the submission repo):
    data/raw/cgmacros/extracted/CGMacros/CGMacros-0xx/...       PhysioNet CGMacros 1.0.0
    data/raw/big_ideas/{Demographics.csv, 001..016/}             PhysioNet BIG IDEAs 1.1.2
    data/raw/shanghai_t2dm/{Shanghai_T2DM/, Shanghai_T2DM_Summary.xlsx}
    data/raw/hupa_ucm/HUPA-UCM Diabetes Dataset/{Raw_Data, Preprocessed}

HUPA-UCM is hosted on Mendeley Data, which has no stable unauthenticated file API. Download the zip by hand
from the landing page and save it as data/raw/hupa_ucm/hupa_ucm.zip; this script then extracts it.
"""

import argparse
import shutil
import sys
import zipfile
from pathlib import Path

try:
    import requests
except ImportError:  # pragma: no cover
    sys.exit("This script needs the 'requests' package: pip install requests")

PROJECT = Path(__file__).resolve().parent.parent
RAW = PROJECT / "data" / "raw"
UA = {"User-Agent": "PancreasTwin-data-fetch/1.0 (research use)"}

DATASETS = {
    "cgmacros": {
        "name": "PhysioNet CGMacros v1.0.0",
        "landing": "https://physionet.org/content/cgmacros/1.0.0/",
        "licence": "CC BY-NC-SA 4.0 (open access, no DUA)",
        "auto": True,
    },
    "big_ideas": {
        "name": "PhysioNet BIG IDEAs Lab Glycemic Variability and Wearable Device Data v1.1.2",
        "landing": "https://physionet.org/content/big-ideas-glycemic-wearable/1.1.2/",
        "licence": "Open Data Commons Attribution v1.0 (open access, no DUA)",
        "auto": True,
    },
    "shanghai": {
        "name": "Shanghai T1DM/T2DM diabetes datasets (Zhao et al., Scientific Data 2023)",
        "landing": "https://doi.org/10.6084/m9.figshare.21600933",
        "licence": "CC BY 4.0",
        "auto": True,
    },
    "hupa_ucm": {
        "name": "HUPA-UCM Diabetes Dataset v1",
        "landing": "https://data.mendeley.com/datasets/3hbcscwz44/1",
        "licence": "CC BY 4.0",
        "auto": False,
    },
}


def fetch(url, target, dry_run=False):
    target = Path(target)
    if target.exists() and target.stat().st_size > 0:
        print(f"  [cached] {target.relative_to(PROJECT)}")
        return True
    if dry_run:
        print(f"  [would fetch] {url} -> {target.relative_to(PROJECT)}")
        return True
    target.parent.mkdir(parents=True, exist_ok=True)
    part = target.with_suffix(target.suffix + ".part")
    try:
        with requests.get(url, headers=UA, stream=True, timeout=60) as r:
            r.raise_for_status()
            with open(part, "wb") as f:
                for chunk in r.iter_content(chunk_size=1 << 20):
                    f.write(chunk)
        part.replace(target)
        print(f"  [ok] {target.relative_to(PROJECT)} ({target.stat().st_size / 1e6:.1f} MB)")
        return True
    except Exception as exc:  # network errors are reported, not fatal for the other datasets
        print(f"  [FAIL] {url}: {exc}")
        if part.exists():
            part.unlink()
        return False


def extract(zip_path, dest, dry_run=False):
    if dry_run:
        print(f"  [would extract] {zip_path.name} -> {dest.relative_to(PROJECT)}")
        return
    dest.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as z:
        z.extractall(dest)
    print(f"  [extracted] {zip_path.name} -> {dest.relative_to(PROJECT)}")


def get_cgmacros(dry_run):
    out = RAW / "cgmacros"
    z = out / "CGMacros_dateshifted365.zip"
    ok = fetch("https://physionet.org/files/cgmacros/1.0.0/CGMacros_dateshifted365.zip", z, dry_run)
    if ok and not (out / "extracted" / "CGMacros").exists():
        extract(z, out / "extracted", dry_run)
    return ok


def get_big_ideas(dry_run):
    base = "https://physionet.org/files/big-ideas-glycemic-wearable/1.1.2"
    out = RAW / "big_ideas"
    ok = True
    for rel in ("Demographics.csv", "LICENSE.txt", "SHA256SUMS.txt"):
        ok &= fetch(f"{base}/{rel}", out / rel, dry_run)
    for i in range(1, 17):
        sub = f"{i:03d}"
        for stem in ("Dexcom", "Food_Log", "HR"):
            ok &= fetch(f"{base}/{sub}/{stem}_{sub}.csv", out / sub / f"{stem}_{sub}.csv", dry_run)
    return ok


def get_shanghai(dry_run):
    out = RAW / "shanghai_t2dm"
    if (out / "Shanghai_T2DM").exists() and (out / "Shanghai_T2DM_Summary.xlsx").exists():
        print("  [cached] data/raw/shanghai_t2dm")
        return True
    api = "https://api.figshare.com/v2/articles/21600933"
    if dry_run:
        print(f"  [would query] {api} and fetch diabetes_datasets.zip -> data/raw/shanghai_t2dm")
        return True
    try:
        files = requests.get(api, headers=UA, timeout=60).json()["files"]
    except Exception as exc:
        print(f"  [FAIL] figshare API: {exc}")
        return False
    ok = True
    for f in files:
        z = out / f["name"]
        ok &= fetch(f["download_url"], z, dry_run)
        if ok and z.suffix == ".zip":
            extract(z, out / "_extract", dry_run)
    # Place the T2DM folder and its summary sheet where the pipeline expects them.
    folder = next((p for p in (out / "_extract").rglob("Shanghai_T2DM") if p.is_dir()), None)
    summary = next((p for p in (out / "_extract").rglob("Shanghai_T2DM_Summary.xlsx")), None)
    if folder is None or summary is None:
        print("  [FAIL] Shanghai_T2DM folder or summary sheet not found inside the archive")
        return False
    shutil.copytree(folder, out / "Shanghai_T2DM", dirs_exist_ok=True)
    shutil.copy2(summary, out / "Shanghai_T2DM_Summary.xlsx")
    print("  [ok] data/raw/shanghai_t2dm/Shanghai_T2DM and Shanghai_T2DM_Summary.xlsx")
    return True


def get_hupa(dry_run):
    out = RAW / "hupa_ucm"
    z = out / "hupa_ucm.zip"
    if (out / "HUPA-UCM Diabetes Dataset").exists():
        print("  [cached] data/raw/hupa_ucm/HUPA-UCM Diabetes Dataset")
        return True
    if not z.exists():
        print("  [MANUAL] Download the dataset zip from https://data.mendeley.com/datasets/3hbcscwz44/1")
        print(f"           and save it as {z.relative_to(PROJECT)}, then re-run this script.")
        return False
    extract(z, out, dry_run)
    return True


HANDLERS = {"cgmacros": get_cgmacros, "big_ideas": get_big_ideas, "shanghai": get_shanghai, "hupa_ucm": get_hupa}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("datasets", nargs="*", help=f"subset to fetch: {', '.join(DATASETS)} (default: all)")
    ap.add_argument("--list", action="store_true", help="list datasets and exit")
    ap.add_argument("--dry-run", action="store_true", help="print actions without downloading")
    ap.add_argument("--root", help="project folder to download into (default: the folder above scripts/)")
    args = ap.parse_args()
    unknown = [d for d in args.datasets if d not in DATASETS]
    if unknown:
        ap.error(f"unknown dataset(s): {', '.join(unknown)}; choose from {', '.join(DATASETS)}")
    if args.root:
        global PROJECT, RAW
        PROJECT = Path(args.root).resolve()
        RAW = PROJECT / "data" / "raw"

    if args.list:
        for key, d in DATASETS.items():
            mode = "automatic" if d["auto"] else "manual download, then auto-extract"
            print(f"{key:10s} {d['name']}\n           {d['landing']}\n           licence: {d['licence']} | {mode}")
        return 0

    chosen = args.datasets or list(DATASETS)
    results = {}
    for key in chosen:
        print(f"\n== {DATASETS[key]['name']} ({DATASETS[key]['licence']})")
        results[key] = HANDLERS[key](args.dry_run)
    print("\nSummary: " + ", ".join(f"{k}={'ok' if v else 'needs attention'}" for k, v in results.items()))
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
