"""Fresh, independent data layer for the Pancreas Twin: true CGM readings only, at each sensor's native cadence.

Unlike harmonize_5min.py, this never resamples or interpolates glucose. Every row in readings.csv.gz is a reading
the sensor actually reported. That removes the look-ahead leak created by interpolating between a reading at t and
one at t+15 min, and it lets targets be matched to real future readings by time rather than by row shift.

Outputs (fresh/data/):
    readings.csv.gz  subject_id, patient_id, cohort, time, glucose, cadence_min
    carbs.csv.gz     subject_id, time, carbs_g
    static.csv       patient_id, age, bmi, hba1c_pct, static_source
Run from the repo root: python fresh/build_dataset.py
"""
import re
from pathlib import Path

import numpy as np
import pandas as pd

DT = Path(".")
OUT = DT / "fresh" / "data"
CGMACROS = DT / "strawberry/data/raw/cgmacros/extracted/CGMacros"
BIGIDEAS = DT / "strawberry/data/raw/big_ideas"
HUPA = DT / "data/raw/hupa_ucm/HUPA-UCM Diabetes Dataset/Raw_Data"
SHANGHAI = DT / "data/raw/shanghai_t2dm/Shanghai_T2DM"
SHANGHAI_SUMMARY = DT / "data/raw/shanghai_t2dm/Shanghai_T2DM_Summary.xlsx"


def dexcom_knots(ts: pd.Series, v: pd.Series) -> pd.DataFrame:
    """CGMacros ships Dexcom linearly interpolated to 1 min. Recover the true 5-min readings: integer values
    at the points where the slope changes, then any integer value exactly 5 min after a kept reading
    (a knot that sits on a straight line has no slope change)."""
    v = v.to_numpy(dtype=float)
    t = ts.to_numpy()
    d2 = np.r_[1.0, np.abs(np.diff(v, 2)), 1.0]
    is_int = np.isclose(v, np.round(v))
    keep = (d2 > 1e-6) & is_int
    tset = pd.Series(np.arange(len(t)), index=pd.DatetimeIndex(t))
    kept = set(np.flatnonzero(keep))
    for i in sorted(kept):
        nxt = pd.Timestamp(t[i]) + pd.Timedelta(minutes=5)
        while nxt in tset.index:
            j = int(tset.loc[nxt]) if np.ndim(tset.loc[nxt]) == 0 else int(tset.loc[nxt].iloc[0])
            if not is_int[j] or j in kept:
                break
            kept.add(j)
            nxt += pd.Timedelta(minutes=5)
    idx = sorted(kept)
    return pd.DataFrame({"time": t[idx], "glucose": v[idx]})


def load_cgmacros():
    reads, carbs = [], []
    for f in sorted(CGMACROS.glob("CGMacros-*/*.csv")):
        pid = f"CGM_{int(re.search(r'(\d+)', f.stem).group(1)):03d}"
        d = pd.read_csv(f, parse_dates=["Timestamp"]).sort_values("Timestamp")
        dx = d.dropna(subset=["Dexcom GL"])
        if len(dx) > 500:
            k = dexcom_knots(dx["Timestamp"], dx["Dexcom GL"])
            k["cadence_min"] = 5
        else:
            continue
        k["subject_id"] = pid
        k["patient_id"] = pid
        k["cohort"] = "cgmacros"
        reads.append(k)
        c = d[pd.to_numeric(d["Carbs"], errors="coerce") > 0][["Timestamp", "Carbs"]]
        carbs.append(pd.DataFrame({"subject_id": pid, "time": c["Timestamp"], "carbs_g": c["Carbs"].astype(float)}))
    return reads, carbs


def load_bigideas():
    reads, carbs = [], []
    for sub in sorted(p for p in BIGIDEAS.iterdir() if p.is_dir()):
        pid = f"BIG_{sub.name}"
        d = pd.read_csv(sub / f"Dexcom_{sub.name}.csv")
        tcol = [c for c in d.columns if c.startswith("Timestamp")][0]
        d = d[d["Event Type"] == "EGV"]
        g = pd.to_numeric(d["Glucose Value (mg/dL)"], errors="coerce")
        k = pd.DataFrame({"time": pd.to_datetime(d[tcol], errors="coerce"), "glucose": g}).dropna()
        k["cadence_min"] = 5
        k["subject_id"] = pid
        k["patient_id"] = pid
        k["cohort"] = "big_ideas"
        reads.append(k)
        fl = sub / f"Food_Log_{sub.name}.csv"
        if fl.exists():
            f = pd.read_csv(fl, encoding="utf-8-sig")
            if "time_begin" in f.columns:
                t, cg = f["time_begin"], f["total_carb"]
            else:
                # One subject's log ships without a header row and without time_end.
                f = pd.read_csv(fl, encoding="utf-8-sig", header=None)
                t, cg = f[2], f[8]
            carbs.append(pd.DataFrame({"subject_id": pid, "time": pd.to_datetime(t, errors="coerce"),
                                       "carbs_g": pd.to_numeric(cg, errors="coerce")}).dropna())
    return reads, carbs


def read_libre_export(f: Path):
    """HUPA LibreView exports come in at least four layouts: ; or , or tab separated, CR-only line endings,
    and a patient banner that is sometimes glued onto the header line. Find the header by content."""
    import io
    text = f.read_bytes().decode("utf-8-sig", errors="replace").replace("\r\n", "\n").replace("\r", "\n")
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if "Tipo de registro" in line:
            for start in ("ID", "Dispositivo"):
                j = line.find(start + ";") if (start + ";") in line else line.find(start + ",")
                if j == -1:
                    j = line.find(start + "\t")
                if j > 0:
                    line = line[j:]
                    break
            sep = max(";,\t", key=line.count)
            body = "\n".join([line] + lines[i + 1:])
            d = pd.read_csv(io.StringIO(body), sep=sep, dtype=str, on_bad_lines="skip")
            d.columns = [str(c).strip() for c in d.columns]
            return d
    return None


def load_hupa():
    reads, carbs = [], []
    for sub in sorted(p for p in HUPA.iterdir() if p.is_dir()):
        pid = f"HUPA_{sub.name}"
        frames = []
        for f in sorted((sub / "free_style_sensor").glob("*.csv")):
            d = read_libre_export(f)
            if d is None:
                continue
            tcol = next(c for c in d.columns if c in ("Hora", "Sello de tiempo del dispositivo"))
            hist = next(c for c in d.columns if c.startswith(("Histórico glucosa", "Historial de glucosa")))
            carb = [c for c in d.columns if c.startswith("Carbohidratos")]
            raw_t = d[tcol].astype(str).str.strip()
            t = pd.to_datetime(raw_t, format="%Y/%m/%d %H:%M", errors="coerce")
            t = t.fillna(pd.to_datetime(raw_t, format="%d-%m-%Y %H:%M", errors="coerce"))
            t = t.fillna(pd.to_datetime(raw_t, format="%d/%m/%Y %H:%M", errors="coerce"))
            t = t.fillna(pd.to_datetime(raw_t, format="%d/%m/%y %H:%M", errors="coerce"))
            d["time"] = t
            h = d[pd.to_numeric(d["Tipo de registro"], errors="coerce") == 0]
            frames.append(pd.DataFrame({"time": h["time"], "glucose": pd.to_numeric(h[hist], errors="coerce")}))
            if carb:
                c = pd.to_numeric(d[carb[0]], errors="coerce")
                m = c > 0
                # Older exports log carbohydrate "raciones" (one racion = 10 g); newer ones log grams.
                scale = 10.0 if "raciones" in carb[0] else 1.0
                carbs.append(pd.DataFrame({"subject_id": pid, "time": d.loc[m, "time"], "carbs_g": c[m] * scale}))
        if not frames:
            continue
        k = pd.concat(frames).dropna().drop_duplicates("time")
        k["cadence_min"] = 15
        k["subject_id"] = pid
        k["patient_id"] = pid
        k["cohort"] = "hupa_ucm"
        reads.append(k)
    return reads, carbs


def load_shanghai():
    reads = []
    for f in sorted(SHANGHAI.glob("*.xls*")):
        d = pd.read_excel(f)
        cgm = next((c for c in d.columns if str(c).strip().upper().startswith("CGM")), None)
        date = next((c for c in d.columns if "date" in str(c).lower()), d.columns[0])
        if cgm is None:
            print("  no CGM column in", f.name, list(d.columns)[:4])
            continue
        g = pd.to_numeric(d[cgm], errors="coerce")
        k = pd.DataFrame({"time": pd.to_datetime(d[date], errors="coerce"), "glucose": g}).dropna()
        k["cadence_min"] = 15
        # A patient can have several recording files (2001_0, 2001_1). Split on patient, not on file.
        k["subject_id"] = f"SH_{f.stem}"
        k["patient_id"] = f"SH_{f.stem.split('_')[0]}"
        k["cohort"] = "shanghai_t2dm"
        reads.append(k)
    return reads, []


def load_static():
    rows = []
    bio = pd.read_csv(CGMACROS / "bio.csv")
    for _, r in bio.iterrows():
        rows.append({"patient_id": f"CGM_{int(r['subject']):03d}", "age": r["Age"], "bmi": r["BMI"],
                     "hba1c_pct": r["A1c PDL (Lab)"], "static_source": "measured"})
    dem = pd.read_csv(BIGIDEAS / "Demographics.csv", encoding="utf-8-sig")
    for _, r in dem.iterrows():
        rows.append({"patient_id": f"BIG_{int(r['ID']):03d}", "age": np.nan, "bmi": np.nan,
                     "hba1c_pct": r["HbA1c"], "static_source": "measured_hba1c_only"})
    s = pd.read_excel(SHANGHAI_SUMMARY)
    for _, r in s.iterrows():
        mmol = pd.to_numeric(r["HbA1c (mmol/mol)"], errors="coerce")
        rows.append({"patient_id": f"SH_{str(r['Patient Number']).split('_')[0]}", "age": r["Age (years)"],
                     "bmi": r["BMI (kg/m2)"],
                     # IFCC mmol/mol to NGSP percent
                     "hba1c_pct": mmol / 10.929 + 2.15 if pd.notna(mmol) else np.nan,
                     "static_source": "measured"})
    # HUPA-UCM ships no per-subject static file: left missing, never simulated.
    return pd.DataFrame(rows).drop_duplicates("patient_id")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    reads, carbs = [], []
    for fn in (load_cgmacros, load_bigideas, load_hupa, load_shanghai):
        r, c = fn()
        reads += r
        carbs += c
        print(fn.__name__, len(r), "subjects", sum(len(x) for x in r), "readings")
    R = pd.concat(reads, ignore_index=True)
    R = R[(R.glucose >= 39) & (R.glucose <= 450)].sort_values(["subject_id", "time"])
    R = R.drop_duplicates(["subject_id", "time"])
    R[["subject_id", "patient_id", "cohort", "time", "glucose", "cadence_min"]].to_csv(OUT / "readings.csv.gz", index=False)
    C = pd.concat(carbs, ignore_index=True).dropna()
    C.to_csv(OUT / "carbs.csv.gz", index=False)
    S = load_static()
    S.to_csv(OUT / "static.csv", index=False)
    print("readings", len(R), "subjects", R.subject_id.nunique(), "patients", R.patient_id.nunique())
    print(R.groupby("cohort").agg(subjects=("subject_id", "nunique"), patients=("patient_id", "nunique"), n=("glucose", "size")))
    print("carb events", len(C), "static rows", len(S))


if __name__ == "__main__":
    main()
