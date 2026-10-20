"""
Data Harmonization Pipeline for Digital Twin Challenge 2026.
Standardizes multi-modal continuous CGM, Heart Rate, Physical Activity (METs/Steps),
and Meals/Carbs into uniform 5-minute epochs and links static patient EHR vectors.
Now integrates:
1. PhysioNet CGMacros (45 subjects, Dexcom G6 + Fitbit HR/Steps)
2. PhysioNet BIG IDEAs (16 subjects, Dexcom CGM + Fitbit)
3. HUPA-UCM Diabetes Dataset (25 subjects, FreeStyle Libre 2 CGM + Zephyr HR/Steps/Carbs)
4. Shanghai T2DM Dataset (20 real clinical T2D patients with laboratory biomarkers)
Exports clean train/val/test splits without subject-level data leakage.
Computes multi-horizon targets up to 120 minutes (2 hours).
"""

import os
import sys
import math
import numpy as np
import pandas as pd
from pathlib import Path

PROCESSED_DIR = Path("data/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

CGMACROS_DIR = Path("strawberry/data/raw/cgmacros/extracted/CGMacros")
BIGIDEAS_DIR = Path("strawberry/data/raw/big_ideas")
HUPA_UCM_DIR = Path("data/raw/hupa_ucm/HUPA-UCM Diabetes Dataset/Preprocessed")
SHANGHAI_DIR = Path("data/raw/shanghai_t2dm/Shanghai_T2DM")
SHANGHAI_SUMMARY = Path("data/raw/shanghai_t2dm/Shanghai_T2DM_Summary.xlsx")


def process_cgmacros_subject(subject_dir):
    sub_id = subject_dir.name
    csv_file = subject_dir / f"{sub_id}.csv"
    if not csv_file.exists():
        return None

    try:
        df = pd.read_csv(csv_file, low_memory=False)
    except Exception as e:
        print(f"Error reading {csv_file}: {e}")
        return None

    if "Timestamp" not in df.columns:
        return None

    df["datetime"] = pd.to_datetime(df["Timestamp"], errors="coerce")
    df = df.dropna(subset=["datetime"]).sort_values("datetime")

    # Glucose selection: prefer Dexcom GL, fallback to Libre GL
    if "Dexcom GL" in df.columns and "Libre GL" in df.columns:
        glucose = df["Dexcom GL"].fillna(df["Libre GL"])
    elif "Dexcom GL" in df.columns:
        glucose = df["Dexcom GL"]
    elif "Libre GL" in df.columns:
        glucose = df["Libre GL"]
    else:
        return None

    df["glucose"] = pd.to_numeric(glucose, errors="coerce")
    df["hr"] = pd.to_numeric(df["HR"], errors="coerce") if "HR" in df.columns else np.nan
    df["mets"] = pd.to_numeric(df["METs"], errors="coerce").fillna(1.0) if "METs" in df.columns else 1.0
    df["carbs"] = pd.to_numeric(df["Carbs"], errors="coerce").fillna(0.0) if "Carbs" in df.columns else 0.0
    df["calories"] = pd.to_numeric(df["Calories"], errors="coerce").fillna(0.0) if "Calories" in df.columns else 0.0

    df = df.dropna(subset=["glucose"]).set_index("datetime").sort_index()

    # Direct resampling on DataFrame
    res = df[["glucose", "hr", "mets", "carbs", "calories"]].resample("5min").mean()
    res["glucose"] = res["glucose"].interpolate(method="linear", limit=3)
    res["hr"] = res["hr"].interpolate(method="linear", limit=3)
    res["mets"] = res["mets"].fillna(1.0)
    res["carbs"] = res["carbs"].fillna(0.0)
    res["calories"] = res["calories"].fillna(0.0)
    res = res.dropna(subset=["glucose"])

    if len(res) < 200:
        return None

    res = res.reset_index()
    res["subject_id"] = f"CGMACROS_{sub_id}"
    res["source_cohort"] = "cgmacros"
    return res


def process_bigideas_subject(sub_dir, sub_id):
    cgm_files = list(sub_dir.glob(f"Dexcom_{sub_id}.csv")) + list(sub_dir.glob("Dexcom_*.csv"))
    if not cgm_files:
        return None

    cgm_file = cgm_files[0]
    try:
        df_cgm = pd.read_csv(cgm_file, low_memory=False)
    except Exception:
        return None

    time_col = None
    for c in df_cgm.columns:
        if "time" in c.lower() or "date" in c.lower():
            time_col = c
            break

    gl_col = None
    for c in df_cgm.columns:
        if "glucose" in c.lower() or "value" in c.lower() or "gl" in c.lower():
            gl_col = c
            break

    if not time_col or not gl_col:
        return None

    df_cgm["datetime"] = pd.to_datetime(df_cgm[time_col], errors="coerce")
    df_cgm["glucose"] = pd.to_numeric(df_cgm[gl_col], errors="coerce")
    df_cgm = df_cgm.dropna(subset=["datetime", "glucose"]).set_index("datetime").sort_index()

    res = df_cgm[["glucose"]].resample("5min").mean()
    res["glucose"] = res["glucose"].interpolate(method="linear", limit=3)
    res = res.dropna(subset=["glucose"])

    if len(res) < 200:
        return None

    res["hr"] = np.nan
    res["mets"] = 1.0
    res["carbs"] = 0.0
    res["calories"] = 0.0

    res = res.reset_index()
    res["subject_id"] = f"BIGIDEAS_{sub_id}"
    res["source_cohort"] = "big_ideas"
    return res


def process_hupa_ucm_subject(csv_file):
    sub_id = csv_file.stem
    try:
        df = pd.read_csv(csv_file, sep=";", low_memory=False)
    except Exception as e:
        print(f"Error reading HUPA file {csv_file}: {e}")
        return None

    if "time" not in df.columns or "glucose" not in df.columns:
        return None

    df["datetime"] = pd.to_datetime(df["time"], errors="coerce")
    df["glucose"] = pd.to_numeric(df["glucose"], errors="coerce")
    df["hr"] = pd.to_numeric(df["heart_rate"], errors="coerce") if "heart_rate" in df.columns else np.nan
    df["calories"] = pd.to_numeric(df["calories"], errors="coerce").fillna(0.0) if "calories" in df.columns else 0.0
    df["carbs"] = pd.to_numeric(df["carb_input"], errors="coerce").fillna(0.0) if "carb_input" in df.columns else 0.0
    steps = pd.to_numeric(df["steps"], errors="coerce").fillna(0.0) if "steps" in df.columns else 0.0
    df["mets"] = 1.0 + (steps / 150.0)

    df = df.dropna(subset=["datetime", "glucose"]).set_index("datetime").sort_index()

    res = df[["glucose", "hr", "mets", "carbs", "calories"]].resample("5min").mean()
    res["glucose"] = res["glucose"].interpolate(method="linear", limit=3)
    res["hr"] = res["hr"].interpolate(method="linear", limit=3)
    res["mets"] = res["mets"].fillna(1.0)
    res["carbs"] = res["carbs"].fillna(0.0)
    res["calories"] = res["calories"].fillna(0.0)
    res = res.dropna(subset=["glucose"])

    if len(res) < 200:
        return None

    res = res.reset_index()
    res["subject_id"] = f"HUPA_{sub_id}"
    res["source_cohort"] = "hupa_ucm"
    return res


def process_shanghai_t2dm_subject(excel_file):
    sub_id = excel_file.stem
    try:
        df = pd.read_excel(excel_file)
    except Exception as e:
        print(f"Error reading Shanghai Excel {excel_file}: {e}")
        return None

    date_col = None
    for c in df.columns:
        if "date" in c.lower() or "time" in c.lower():
            date_col = c
            break

    cgm_col = None
    for c in df.columns:
        if "cgm" in c.lower() or "glucose" in c.lower():
            cgm_col = c
            break

    if not date_col or not cgm_col:
        return None

    df["datetime"] = pd.to_datetime(df[date_col], errors="coerce")
    df["glucose"] = pd.to_numeric(df[cgm_col], errors="coerce")

    diet_col = [c for c in df.columns if "diet" in c.lower() or "carb" in c.lower()]
    if diet_col:
        df["carbs"] = pd.to_numeric(df[diet_col[0]], errors="coerce").fillna(0.0)
    else:
        df["carbs"] = 0.0

    df["hr"] = np.nan
    df["calories"] = 0.0
    df["mets"] = 1.0

    df = df.dropna(subset=["datetime", "glucose"]).set_index("datetime").sort_index()

    res = df[["glucose", "carbs"]].resample("5min").mean()
    res["glucose"] = res["glucose"].interpolate(method="linear", limit=3)
    res["carbs"] = res["carbs"].fillna(0.0)
    res["hr"] = np.nan
    res["calories"] = 0.0
    res["mets"] = 1.0
    res = res.dropna(subset=["glucose"])

    if len(res) < 200:
        return None

    res = res.reset_index()
    res["subject_id"] = f"SHANGHAI_{sub_id}"
    res["source_cohort"] = "shanghai_t2dm"
    return res


def compute_derived_features(df):
    """
    Computes velocity, acceleration, rolling volatility, cyclical time, and multi-horizon targets.
    Supports horizons: 15, 30, 45, 60, and 120 minutes (up to 2 hours).
    """
    df = df.sort_values(["subject_id", "datetime"]).copy()

    # Time-of-day cyclical encoding (24 hours = 1440 mins)
    mins = df["datetime"].dt.hour * 60 + df["datetime"].dt.minute
    df["sin_time"] = np.sin(2 * np.pi * mins / 1440.0)
    df["cos_time"] = np.cos(2 * np.pi * mins / 1440.0)

    # Grouped feature engineering
    processed_groups = []
    for sub, grp in df.groupby("subject_id"):
        grp = grp.copy()
        # Glucose velocity: dG/dt (mg/dL per minute over 15 mins = 3 steps)
        grp["glucose_velocity"] = (grp["glucose"] - grp["glucose"].shift(3)) / 15.0
        grp["glucose_accel"] = (grp["glucose_velocity"] - grp["glucose_velocity"].shift(3)) / 15.0

        # Rolling statistics
        grp["rolling_mean_30"] = grp["glucose"].rolling(6, min_periods=1).mean()
        grp["rolling_std_60"] = grp["glucose"].rolling(12, min_periods=2).std().fillna(0.0)

        # Multi-horizon targets (15m, 30m, 45m, 60m, 120m -> 3, 6, 9, 12, 24 steps ahead)
        grp["target_glucose_15m"] = grp["glucose"].shift(-3)
        grp["target_glucose_30m"] = grp["glucose"].shift(-6)
        grp["target_glucose_45m"] = grp["glucose"].shift(-9)
        grp["target_glucose_60m"] = grp["glucose"].shift(-12)
        grp["target_glucose_120m"] = grp["glucose"].shift(-24)

        # Classification targets: Acute Hyperglycemia (>180) and Hypoglycemia (<70)
        grp["target_spike_60m"] = (grp["target_glucose_60m"] > 180.0).astype(float)
        grp["target_crash_60m"] = (grp["target_glucose_60m"] < 70.0).astype(float)
        grp["target_spike_120m"] = (grp["target_glucose_120m"] > 180.0).astype(float)
        grp["target_crash_120m"] = (grp["target_glucose_120m"] < 70.0).astype(float)

        # Drop boundary tail where 60-min target is unavailable
        grp = grp.dropna(subset=["target_glucose_60m", "glucose_velocity"])
        processed_groups.append(grp)

    return pd.concat(processed_groups, ignore_index=True)


def _load_cgmacros_bio():
    """CGMacros bio.csv holds real static labs (Age, BMI, lab A1c) for the same 45 subjects as the sensors."""
    out = {}
    bio_path = CGMACROS_DIR / "bio.csv"
    if not bio_path.exists():
        return out
    try:
        b = pd.read_csv(bio_path)
        b.columns = [str(c).strip() for c in b.columns]
        for _, r in b.iterrows():
            try:
                sid = int(float(str(r["subject"]).strip()))
            except Exception:
                continue
            out[sid] = {
                "age": pd.to_numeric(r.get("Age"), errors="coerce"),
                "bmi": pd.to_numeric(r.get("BMI"), errors="coerce"),
                "hba1c": pd.to_numeric(r.get("A1c PDL (Lab)"), errors="coerce"),
            }
    except Exception as e:
        print(f"[WARN] CGMacros bio.csv read failed: {e}")
    return out


def _load_bigideas_demographics():
    """BIG IDEAs Demographics.csv holds a measured HbA1c per subject (no age or BMI column)."""
    out = {}
    p = BIGIDEAS_DIR / "Demographics.csv"
    if not p.exists():
        return out
    try:
        d = pd.read_csv(p)
        d.columns = [str(c).strip() for c in d.columns]
        for _, r in d.iterrows():
            try:
                sid = int(float(str(r["ID"]).strip()))
            except Exception:
                continue
            out[sid] = {"hba1c": pd.to_numeric(r.get("HbA1c"), errors="coerce")}
    except Exception as e:
        print(f"[WARN] BIG IDEAs Demographics.csv read failed: {e}")
    return out


def attach_static_ehr_profiles(df):
    """
    Assigns static clinical phenotype vectors (Age, BMI, Baseline HbA1c, Meds).

    Real measured values are used wherever the source cohort carries them:
      - CGMacros  : bio.csv gives Age, BMI and lab A1c for the same subjects as the sensors
      - BIG IDEAs : Demographics.csv gives a measured HbA1c per subject
      - Shanghai  : Shanghai_T2DM_Summary.xlsx gives Age, BMI, HbA1c (mmol/mol) and meds

    Cohorts without a static file (HUPA-UCM) fall back to a demographic prior drawn from
    the measured cohorts. Medication flags are measured for Shanghai only and are prior-filled
    elsewhere. Every row carries static_ehr_source (measured_full, measured_hba1c_only or
    synthetic) so downstream code and the write-up can separate measured from synthesized
    static features instead of implying that all of it was measured.
    """
    cgm_bio = _load_cgmacros_bio()
    big_demo = _load_bigideas_demographics()

    shanghai_summary_map = {}
    if SHANGHAI_SUMMARY.exists():
        try:
            df_sh = pd.read_excel(SHANGHAI_SUMMARY)
            for _, r in df_sh.iterrows():
                p_num = str(r.get("Patient Number", "")).strip()
                age = pd.to_numeric(r.get("Age (years)"), errors="coerce")
                bmi = pd.to_numeric(r.get("BMI (kg/m2)"), errors="coerce")
                hba1c_val = pd.to_numeric(r.get("HbA1c (mmol/mol)"), errors="coerce")
                # Skip rows without a patient id or non-numeric labs (the sheet carries unit/blank rows).
                if not p_num or pd.isna(age) or pd.isna(bmi) or pd.isna(hba1c_val):
                    continue
                age = float(age)
                bmi = float(bmi)
                hba1c_val = float(hba1c_val)
                hba1c_pct = round((0.09148 * hba1c_val) + 2.152, 1) if hba1c_val > 20 else round(hba1c_val, 1)
                meds = str(r.get("Hypoglycemic Agents", "")).lower()
                shanghai_summary_map[p_num] = {
                    "age": int(age), "bmi": bmi, "hba1c": hba1c_pct,
                    "is_insulin": 1 if "insulin" in meds else 0,
                    "is_metformin": 1 if "metformin" in meds else 0,
                }
        except Exception as e:
            print(f"[WARN] Error reading Shanghai Summary: {e}")

    print(f"  Real static EHR sources loaded: CGMacros={len(cgm_bio)}, BIGIDEAs={len(big_demo)}, Shanghai={len(shanghai_summary_map)}")

    subjects = df["subject_id"].unique()
    np.random.seed(42)
    ehr_records = []
    for sub in subjects:
        age = bmi = hba1c = None
        is_insulin = 1 if np.random.rand() > 0.65 else 0
        is_metformin = 1 if np.random.rand() > 0.20 else 0
        source = "synthetic"

        if sub.startswith("CGMACROS_"):
            digits = "".join(ch for ch in sub.split("_", 1)[1] if ch.isdigit())
            rec = cgm_bio.get(int(digits)) if digits else None
            if rec:
                if pd.notna(rec["age"]):
                    age = rec["age"]
                if pd.notna(rec["bmi"]):
                    bmi = rec["bmi"]
                if pd.notna(rec["hba1c"]):
                    hba1c = rec["hba1c"]
                if age is not None and bmi is not None and hba1c is not None:
                    source = "measured_full"

        elif sub.startswith("BIGIDEAS_"):
            digits = "".join(ch for ch in sub.split("_", 1)[1] if ch.isdigit())
            rec = big_demo.get(int(digits)) if digits else None
            if rec and pd.notna(rec["hba1c"]):
                hba1c = rec["hba1c"]
                source = "measured_hba1c_only"

        elif "SHANGHAI_" in sub:
            for p_num, p_data in shanghai_summary_map.items():
                if p_num in sub:
                    age = p_data["age"]
                    bmi = p_data["bmi"]
                    hba1c = p_data["hba1c"]
                    is_insulin = p_data["is_insulin"]
                    is_metformin = p_data["is_metformin"]
                    source = "measured_full"
                    break

        if age is None:
            age = int(max(35, min(75, np.random.normal(54.0, 9.0))))
        if bmi is None:
            bmi = round(float(np.random.normal(29.8, 4.2)), 1)
        if hba1c is None:
            hba1c = round(float(np.random.normal(7.4, 1.1)), 1)

        ehr_records.append({
            "subject_id": sub,
            "static_age": age,
            "static_bmi": bmi,
            "static_hba1c": hba1c,
            "static_insulin_user": is_insulin,
            "static_metformin_user": is_metformin,
            "static_ehr_source": source,
        })

    df_ehr = pd.DataFrame(ehr_records)
    n_full = int((df_ehr["static_ehr_source"] == "measured_full").sum())
    n_part = int((df_ehr["static_ehr_source"] == "measured_hba1c_only").sum())
    n_syn = int((df_ehr["static_ehr_source"] == "synthetic").sum())
    print(f"  Static EHR provenance: measured_full={n_full}, measured_hba1c_only={n_part}, synthetic={n_syn}")
    return pd.merge(df, df_ehr, on="subject_id", how="left")


def main():
    print("=" * 60)
    print("STARTING MULTI-COHORT DATA HARMONIZATION PIPELINE (5-MIN EPOCHS)")
    print("=" * 60)

    all_dfs = []

    # 1. Ingest CGMacros subjects
    if CGMACROS_DIR.exists():
        sub_dirs = [d for d in CGMACROS_DIR.iterdir() if d.is_dir() and "CGMacros" in d.name]
        print(f"\n[1/4] Processing {len(sub_dirs)} subjects from PhysioNet CGMacros...")
        count = 0
        for sdir in sorted(sub_dirs):
            sdf = process_cgmacros_subject(sdir)
            if sdf is not None:
                all_dfs.append(sdf)
                count += 1
        print(f"  Successfully extracted {count} CGMacros subjects.")
    else:
        print("[WARN] CGMacros directory not found.")

    # 2. Ingest BIG IDEAs subjects
    if BIGIDEAS_DIR.exists():
        sub_dirs = [d for d in BIGIDEAS_DIR.iterdir() if d.is_dir() and d.name.isdigit()]
        print(f"\n[2/4] Processing {len(sub_dirs)} subjects from PhysioNet BIG IDEAs...")
        count = 0
        for sdir in sorted(sub_dirs):
            sub_id = sdir.name
            sdf = process_bigideas_subject(sdir, sub_id)
            if sdf is not None:
                all_dfs.append(sdf)
                count += 1
        print(f"  Successfully extracted {count} BIG IDEAs subjects.")
    else:
        print("[WARN] BIG IDEAs directory not found.")

    # 3. Ingest HUPA-UCM subjects
    if HUPA_UCM_DIR.exists():
        hupa_files = sorted(list(HUPA_UCM_DIR.glob("*.csv")))
        print(f"\n[3/4] Processing {len(hupa_files)} subjects from HUPA-UCM...")
        count = 0
        for hf in hupa_files:
            sdf = process_hupa_ucm_subject(hf)
            if sdf is not None:
                all_dfs.append(sdf)
                count += 1
        print(f"  Successfully extracted {count} HUPA-UCM subjects.")
    else:
        print("[WARN] HUPA-UCM directory not found.")

    # 4. Ingest Shanghai T2DM subjects
    if SHANGHAI_DIR.exists():
        sh_files = sorted(list(SHANGHAI_DIR.glob("*.xlsx")))
        print(f"\n[4/4] Processing {len(sh_files)} subjects from Shanghai T2DM...")
        count = 0
        for sf in sh_files:
            sdf = process_shanghai_t2dm_subject(sf)
            if sdf is not None:
                all_dfs.append(sdf)
                count += 1
        print(f"  Successfully extracted {count} Shanghai T2DM subjects.")
    else:
        print("[WARN] Shanghai T2DM directory not found.")

    if not all_dfs:
        print("[FAIL] No valid subject time series extracted.")
        return 1

    master_df = pd.concat(all_dfs, ignore_index=True)
    print(f"\nCombined raw points: {len(master_df):,} across {master_df['subject_id'].nunique()} subjects.")

    # 5. Compute derived features & multi-horizon targets
    print("\nComputing velocities, rolling volatility, and multi-horizon targets (up to 120m)...")
    feat_df = compute_derived_features(master_df)

    # 6. Attach Static EHR Vectors
    print("Attaching static patient EHR vectors (Age, BMI, HbA1c, Meds)...")
    final_df = attach_static_ehr_profiles(feat_df)

    # 7. Split train/val/test by subject_id (no data leakage)
    subjects = list(final_df["subject_id"].unique())
    np.random.seed(42)
    np.random.shuffle(subjects)

    n_train = int(len(subjects) * 0.70)
    n_val = int(len(subjects) * 0.15)
    train_subs = set(subjects[:n_train])
    val_subs = set(subjects[n_train:n_train + n_val])
    test_subs = set(subjects[n_train + n_val:])

    final_df["split"] = "train"
    final_df.loc[final_df["subject_id"].isin(val_subs), "split"] = "val"
    final_df.loc[final_df["subject_id"].isin(test_subs), "split"] = "test"

    # Export datasets
    out_gz = PROCESSED_DIR / "harmonized_5min.csv.gz"
    out_csv = PROCESSED_DIR / "harmonized_5min_sample.csv"

    print(f"\nSaving master dataset to {out_gz} (compressed CSV)...")
    final_df.to_csv(out_gz, index=False, compression="gzip")
    final_df.head(500).to_csv(out_csv, index=False)

    # Summary report
    print("\n" + "=" * 60)
    print("MULTI-COHORT DATA HARMONIZATION SUMMARY")
    print("=" * 60)
    print(f"Total Subjects:       {final_df['subject_id'].nunique()}")
    print(f"Cohorts Included:     {', '.join(sorted(final_df['source_cohort'].unique()))}")
    print(f"Total 5-min Records:  {len(final_df):,}")
    print(f"Train Records:        {len(final_df[final_df['split']=='train']):,} ({len(train_subs)} subjects)")
    print(f"Val Records:          {len(final_df[final_df['split']=='val']):,} ({len(val_subs)} subjects)")
    print(f"Test Records:         {len(final_df[final_df['split']=='test']):,} ({len(test_subs)} subjects)")
    print(f"Acute Spikes (>180):  {int(final_df['target_spike_60m'].sum()):,} ({final_df['target_spike_60m'].mean()*100:.2f}%)")
    print(f"Acute Crashes (<70):  {int(final_df['target_crash_60m'].sum()):,} ({final_df['target_crash_60m'].mean()*100:.2f}%)")
    if "target_spike_120m" in final_df.columns:
        print(f"120m Spikes (>180):   {int(final_df['target_spike_120m'].dropna().sum()):,} occurrences")
    print(f"Mean Glucose:         {final_df['glucose'].mean():.1f} mg/dL")
    print(f"Glucose Range:        {final_df['glucose'].min():.1f} - {final_df['glucose'].max():.1f} mg/dL")
    print("=" * 60)
    print(f"[SUCCESS] Harmonization complete. Expanded multi-cohort dataset ready!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
