"""
Fusion Ablation for the Digital Twin Challenge 2026 (Project Pancreas Twin).

Answers the one question the research scan identifies as unclaimed ground and the
one the discussion room left open: does the static EHR + exogenous-driver signal
add anything over CGM history alone at a 60-minute and 120-minute horizon, using
the SAME architecture and the SAME subject-disjoint split?

Ablation ladder (identical LightGBM config, identical seed, identical split):
  L0  Persistence (zero-order hold)                 no training, the floor
  L1  CGM history only                              glucose + velocity + accel + rolling + clock
  L2  L1 + cardiorespiratory effort (HR, METs)
  L3  L2 + nutrition (carbs, calories)
  L4  L3 + static EHR phenotype (age, BMI, HbA1c, insulin, metformin)   full multimodal

Reported per level, per horizon: RMSE, MAE, Clarke Error Grid A+B%, spike ROC-AUC,
and Delta-RMSE against L1 (the measured driver contribution, the honest fusion test).
Per-subject paired Delta (L4 vs L1) is reported because n is small (held-out subjects).

Writes:
  fusion_ablation_results.json
  FUSION_ABLATION.md
"""

import sys
import json
import math
import numpy as np
import pandas as pd
from pathlib import Path

from sklearn.metrics import mean_squared_error, mean_absolute_error, roc_auc_score

try:
    import lightgbm as lgb
    LGB_AVAILABLE = True
except ImportError:
    LGB_AVAILABLE = False

sys.path.insert(0, str(Path(__file__).parent.resolve()))
from clarke_error_grid import clarke_error_grid

DATA_FILE = Path("data/processed/harmonized_5min.csv.gz")
RESULTS_FILE = Path("fusion_ablation_results.json")
REPORT_FILE = Path("FUSION_ABLATION.md")

CGM_HISTORY = [
    "glucose", "glucose_velocity", "glucose_accel",
    "rolling_mean_30", "rolling_std_60", "sin_time", "cos_time",
]
EFFORT = ["hr", "mets"]
NUTRITION = ["carbs", "calories"]
STATIC_EHR = ["static_age", "static_bmi", "static_hba1c", "static_insulin_user", "static_metformin_user"]

LEVELS = [
    ("L1_cgm_history", "CGM history only", CGM_HISTORY),
    ("L2_cgm_effort", "CGM + cardiorespiratory effort (HR, METs)", CGM_HISTORY + EFFORT),
    ("L3_cgm_effort_nutrition", "CGM + effort + nutrition (carbs, calories)", CGM_HISTORY + EFFORT + NUTRITION),
    ("L4_full_multimodal", "CGM + effort + nutrition + static EHR (full multimodal)", CGM_HISTORY + EFFORT + NUTRITION + STATIC_EHR),
]

# Frozen LightGBM config. Identical for every level; no per-level tuning, so the
# only thing that changes between rows is the feature set.
LGB_PARAMS = {
    "objective": "regression",
    "metric": "rmse",
    "learning_rate": 0.05,
    "num_leaves": 31,
    "n_estimators": 100,
    "verbose": -1,
    "random_state": 42,
}


def load_data():
    df = pd.read_csv(DATA_FILE, compression="gzip", low_memory=False)
    all_cols = CGM_HISTORY + EFFORT + NUTRITION + STATIC_EHR
    for col in all_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    # Median impute from TRAIN only, to avoid leaking test statistics.
    train_df = df[df["split"] == "train"].copy()
    medians = train_df[all_cols].median()
    for col in all_cols:
        df[col] = df[col].fillna(medians[col])
    val_df = df[df["split"] == "val"].copy()
    test_df = df[df["split"] == "test"].copy()
    print(f"Loaded split: train={len(train_df):,}, val={len(val_df):,}, test={len(test_df):,}")
    return train_df, val_df, test_df


def metrics(y_true, y_pred):
    mask = ~np.isnan(y_true) & ~np.isnan(y_pred)
    yt, yp = y_true[mask], y_pred[mask]
    if len(yt) == 0:
        return None
    rmse = math.sqrt(mean_squared_error(yt, yp))
    mae = mean_absolute_error(yt, yp)
    ceg = clarke_error_grid(yt, yp)
    true_spike = (yt > 180.0).astype(int)
    try:
        auc = roc_auc_score(true_spike, yp)
    except Exception:
        auc = float("nan")
    return {
        "rmse": round(rmse, 2),
        "mae": round(mae, 2),
        "zone_a_plus_b_pct": ceg["zone_a_plus_b_pct"],
        "zone_e_pct": ceg["zone_e_pct"],
        "spike_roc_auc": round(float(auc), 3) if not math.isnan(auc) else None,
        "n": int(mask.sum()),
    }


def per_subject_rmse(test_df, col_true, col_pred):
    out = {}
    for sid, grp in test_df.groupby("subject_id"):
        yt = grp[col_true].values
        yp = grp[col_pred].values
        m = ~np.isnan(yt) & ~np.isnan(yp)
        if m.sum() == 0:
            continue
        out[sid] = float(math.sqrt(mean_squared_error(yt[m], yp[m])))
    return out


def run_horizon(train_df, test_df, target_col, horizon_label, results):
    print(f"\n{'='*70}\nHORIZON {horizon_label} (target={target_col})\n{'='*70}")
    y_train = train_df[target_col].values
    y_test = test_df[target_col].values
    mask_train = ~np.isnan(y_train)

    level_rows = []

    # L0 persistence
    m0 = metrics(y_test, test_df["glucose"].values)
    print(f"  L0 persistence:            RMSE={m0['rmse']} MAE={m0['mae']} A+B={m0['zone_a_plus_b_pct']}%")
    results.append({"horizon": horizon_label, "level": "L0_persistence",
                    "desc": "Zero-order hold (floor)", "features": 0, **m0})

    fitted = {}
    importances = {}
    for key, desc, feats in LEVELS:
        Xtr = train_df.loc[mask_train, feats].values
        ytr = y_train[mask_train]
        Xte = test_df[feats].values
        model = lgb.train(LGB_PARAMS, lgb.Dataset(Xtr, label=ytr))
        pred = model.predict(Xte)
        test_df[f"pred_{key}"] = pred
        m = metrics(y_test, pred)
        row = {"horizon": horizon_label, "level": key, "desc": desc,
               "features": len(feats), **m}
        results.append(row)
        level_rows.append(row)
        importances[key] = dict(zip(feats, [round(float(x), 1) for x in model.feature_importance(importance_type="gain")]))
        print(f"  {key:<24} RMSE={m['rmse']} MAE={m['mae']} A+B={m['zone_a_plus_b_pct']}% AUC={m['spike_roc_auc']}")

    # Delta vs L1 (driver contribution)
    l1 = next(r for r in level_rows if r["level"] == "L1_cgm_history")
    for r in level_rows:
        r["delta_rmse_vs_L1"] = round(l1["rmse"] - r["rmse"], 2)
    print(f"  Driver contribution (L1 - L4) = {round(l1['rmse'] - next(r for r in level_rows if r['level']=='L4_full_multimodal')['rmse'], 2)} mg/dL")

    # Per-subject paired test L4 vs L1
    ps1 = per_subject_rmse(test_df, target_col, "pred_L1_cgm_history")
    ps4 = per_subject_rmse(test_df, target_col, "pred_L4_full_multimodal")
    common = sorted(set(ps1) & set(ps4))
    deltas = [ps1[s] - ps4[s] for s in common]  # positive = L4 better
    paired = {
        "n_subjects": len(common),
        "mean_delta_rmse_mgdl": round(float(np.mean(deltas)), 2) if deltas else None,
        "median_delta_rmse_mgdl": round(float(np.median(deltas)), 2) if deltas else None,
        "subjects_L4_better": int(sum(1 for d in deltas if d > 0)),
        "subjects_L1_better": int(sum(1 for d in deltas if d < 0)),
        "per_subject_delta": {s: round(float(ps1[s] - ps4[s]), 2) for s in common},
    }
    try:
        from scipy.stats import wilcoxon
        if len(deltas) >= 6:
            stat, p = wilcoxon(deltas)
            paired["wilcoxon_p"] = round(float(p), 4)
    except Exception:
        paired["wilcoxon_p"] = None
    print(f"  Paired (L4 vs L1) over {paired['n_subjects']} subjects: mean delta={paired['mean_delta_rmse_mgdl']} mg/dL, "
          f"L4 better in {paired['subjects_L4_better']}/{paired['n_subjects']} (p={paired.get('wilcoxon_p')})")

    return {"horizon": horizon_label, "level_rows": level_rows, "paired_L4_vs_L1": paired,
            "feature_gain": importances}


def main():
    if not LGB_AVAILABLE:
        print("[FAIL] lightgbm not available")
        return 1
    train_df, val_df, test_df = load_data()
    results = []
    details = []
    details.append(run_horizon(train_df, test_df.copy(), "target_glucose_60m", "60m", results))
    details.append(run_horizon(train_df, test_df.copy(), "target_glucose_120m", "120m", results))

    payload = {
        "note": "Identical LightGBM architecture across levels; only the feature set changes. Split is subject-disjoint (no patient leakage).",
        "persistence_floor_statement": "Every level is reported against the measured zero-order-hold floor on this split.",
        "results": results,
        "details": details,
    }
    with open(RESULTS_FILE, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"\n[OK] {RESULTS_FILE}")

    write_report(payload, test_df)
    return 0


def write_report(payload, test_df):
    n_sub = test_df["subject_id"].nunique()
    lines = []
    lines.append("# Fusion Ablation - Project Pancreas Twin")
    lines.append("")
    lines.append("Does static EHR plus exogenous drivers add anything over CGM history alone, "
                 "at a 60-minute and 120-minute horizon, on the same subject-disjoint held-out split? "
                 "Identical LightGBM architecture at every level; only the feature set changes, so any "
                 "RMSE move is attributable to the added signal and nothing else.")
    lines.append("")
    lines.append(f"Held-out test: {n_sub} unseen subjects, zero patient leakage. Imputation medians taken from train only.")
    lines.append("")
    for d in payload["details"]:
        h = d["horizon"]
        lines.append(f"## {h} horizon")
        lines.append("")
        lines.append("| Level | Feature set | RMSE | MAE | Clarke A+B% | Spike AUC | Delta vs CGM-only (mg/dL) |")
        lines.append("|---|---|---|---|---|---|---|")
        rows = [r for r in payload["results"] if r["horizon"] == h]
        l0 = next(r for r in rows if r["level"] == "L0_persistence")
        lines.append(f"| L0 | Persistence (floor) | {l0['rmse']} | {l0['mae']} | {l0['zone_a_plus_b_pct']} | {l0['spike_roc_auc']} | {round(l0['rmse'] - next(r for r in rows if r['level']=='L1_cgm_history')['rmse'],2)} |")
        for r in rows:
            if r["level"] == "L0_persistence":
                continue
            lines.append(f"| {r['level'].split('_')[0]} | {r['desc']} | {r['rmse']} | {r['mae']} | "
                         f"{r['zone_a_plus_b_pct']} | {r['spike_roc_auc']} | {r['delta_rmse_vs_L1']} |")
        lines.append("")
        p = d["paired_L4_vs_L1"]
        lines.append(f"Paired per-subject check, full multimodal (L4) vs CGM-only (L1), {p['n_subjects']} subjects: "
                     f"mean Delta-RMSE {p['mean_delta_rmse_mgdl']} mg/dL, median {p['median_delta_rmse_mgdl']} mg/dL, "
                     f"L4 better in {p['subjects_L4_better']} of {p['n_subjects']}, "
                     f"L1 better in {p['subjects_L1_better']} of {p['n_subjects']}"
                     + (f", Wilcoxon p={p['wilcoxon_p']}." if p.get("wilcoxon_p") is not None else "."))
        lines.append("")
    lines.append("## Reading")
    lines.append("")
    lines.append("The column that matters is Delta vs CGM-only. It is the measured driver contribution "
                 "on this cohort and split. The published field result (driver-blindness, 2025) is that "
                 "exogenous drivers add roughly 5 to 20 percent RMSE at these horizons; our numbers should "
                 "be read against that band, not against a hoped-for large jump. If a level does not move "
                 "the metric, the honest finding is that the added signal is not yet earning its place, "
                 "and that is reported as such rather than buried.")
    lines.append("")
    lines.append("**Static EHR caveat.** Only the Shanghai T2DM subjects carry measured static laboratory "
                 "phenotypes (age, BMI, HbA1c, medication class). For the other cohorts the static vector is "
                 "synthesized from a demographic prior and is disclosed as a limitation. The fusion ablation "
                 "is the test of whether even that signal helps; the dynamic CGM tower is real measured data "
                 "in every cohort.")
    lines.append("")
    Path(REPORT_FILE).write_text("\n".join(lines), encoding="utf-8")
    print(f"[OK] {REPORT_FILE}")


if __name__ == "__main__":
    sys.exit(main())