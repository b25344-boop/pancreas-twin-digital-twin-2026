"""Fresh, independent forecasting benchmark for the Pancreas Twin.

Design choices (each one differs on purpose from the team pipeline):
  * Anchors are real sensor readings. Features use only readings at or before the anchor (as-of joins).
  * Targets are the real reading nearest t+H, within half the sensor cadence. No row shifting.
  * The model predicts the change from the current reading, so persistence is the natural zero point.
  * 5-fold StratifiedGroupKFold on patient_id (stratified by cohort), so every patient is tested exactly once
    and multi-file patients never straddle train and test.
  * Training rows are weighted 1/n per patient, so one 1.5-year HUPA patient cannot dominate.
  * Both pooled (row-weighted) and macro (per-patient mean) RMSE are reported.
Run from the repo root: python fresh/train_eval.py
"""
import json
import time
from pathlib import Path

import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer

HERE = Path("fresh")
DATA = HERE / "data"
HORIZONS = [30, 60, 120]
LAGS = [15, 30, 45, 60, 90, 120, 180]


def clarke_zones(ref, pred):
    """Clarke error grid zone per point (Clarke et al. 1987), mg/dL."""
    ref = np.asarray(ref, float)
    pred = np.asarray(pred, float)
    z = np.full(len(ref), "B", dtype=object)
    a = (np.abs(pred - ref) <= 0.2 * ref) | ((ref < 70) & (pred < 70))
    e = ((ref <= 70) & (pred >= 180)) | ((ref >= 180) & (pred <= 70))
    c = ((ref >= 70) & (ref <= 290) & (pred >= ref + 110)) | ((ref >= 130) & (ref <= 180) & (pred <= (7 / 5) * ref - 182))
    d = ((ref >= 240) & (pred >= 70) & (pred <= 180)) | ((ref <= 175 / 3) & (pred <= 180) & (pred >= 70)) | \
        ((ref >= 175 / 3) & (ref <= 70) & (pred >= (6 / 5) * ref))
    z[d] = "D"
    z[c] = "C"
    z[e] = "E"
    z[a] = "A"
    return z


def build_features(R: pd.DataFrame, C: pd.DataFrame, S: pd.DataFrame) -> pd.DataFrame:
    out = []
    for sid, g in R.groupby("subject_id", sort=False):
        g = g.sort_values("time").reset_index(drop=True)
        cad = int(g.cadence_min.iloc[0])
        base = g[["time", "glucose"]].rename(columns={"glucose": "g0"})
        f = g[["subject_id", "patient_id", "cohort", "time", "cadence_min"]].copy()
        f["g0"] = g.glucose.values
        tol = pd.Timedelta(minutes=max(10, cad + 5))
        for L in LAGS:
            q = pd.DataFrame({"time": g.time - pd.Timedelta(minutes=L)})
            m = pd.merge_asof(q, base, on="time", direction="backward", tolerance=tol)
            f[f"d{L}"] = f.g0.values - m.g0.values
        s = g.set_index("time").glucose
        for w in (60, 180):
            r = s.rolling(f"{w}min", closed="both")
            f[f"mean{w}"] = r.mean().values - f.g0.values
            f[f"std{w}"] = r.std().values
            f[f"min{w}"] = r.min().values - f.g0.values
            f[f"max{w}"] = r.max().values - f.g0.values
        # Carbs: causal windows only.
        c = C[C.subject_id == sid].sort_values("time")
        if len(c):
            cs = c.set_index("time").carbs_g
            ct = cs.index.values
            cum = np.r_[0, np.cumsum(cs.values)]
            t = g.time.values
            for lo, hi, name in ((0, 120, "carb_0_2h"), (120, 240, "carb_2_4h")):
                i_hi = np.searchsorted(ct, t - np.timedelta64(lo, "m"), side="right")
                i_lo = np.searchsorted(ct, t - np.timedelta64(hi, "m"), side="right")
                f[name] = cum[i_hi] - cum[i_lo]
            last = np.searchsorted(ct, t, side="right") - 1
            since = np.where(last >= 0, (t - ct[np.clip(last, 0, None)]) / np.timedelta64(1, "m"), np.nan)
            f["min_since_meal"] = np.clip(since, 0, 720)
            f["carb_logged"] = 1
        else:
            f["carb_0_2h"] = np.nan
            f["carb_2_4h"] = np.nan
            f["min_since_meal"] = np.nan
            f["carb_logged"] = 0
        # Targets: the real reading nearest t+H, within half a cadence.
        ttol = pd.Timedelta(minutes=cad / 2 + 0.5)
        for H in HORIZONS:
            q = pd.DataFrame({"time": g.time + pd.Timedelta(minutes=H)})
            m = pd.merge_asof(q, base, on="time", direction="nearest", tolerance=ttol)
            f[f"y{H}"] = m.g0.values
        out.append(f)
    F = pd.concat(out, ignore_index=True)
    mins = F.time.dt.hour * 60 + F.time.dt.minute
    F["tod_sin"] = np.sin(2 * np.pi * mins / 1440)
    F["tod_cos"] = np.cos(2 * np.pi * mins / 1440)
    F = F.merge(S[["patient_id", "age", "bmi", "hba1c_pct"]], on="patient_id", how="left")
    F["cad15"] = (F.cadence_min == 15).astype(int)
    return F


DYN = [f"d{L}" for L in LAGS] + [f"{s}{w}" for w in (60, 180) for s in ("mean", "std", "min", "max")] + ["g0", "tod_sin", "tod_cos", "cad15"]
CARB = ["carb_0_2h", "carb_2_4h", "min_since_meal", "carb_logged"]
STATIC = ["age", "bmi", "hba1c_pct"]


def lgb_model(obj="regression"):
    return lgb.LGBMRegressor(n_estimators=600, learning_rate=0.03, num_leaves=31, min_child_samples=200,
                             subsample=0.8, subsample_freq=1, colsample_bytree=0.8, reg_lambda=1.0,
                             objective=obj, verbose=-1, n_jobs=8)


def trend_pred(te, H):
    # Damped linear extrapolation from the 30-minute slope.
    slope = te["d30"].fillna(te["d15"] * 2).fillna(0) / 30.0
    return te.g0 + np.clip(slope * H * 0.5, -80, 80)


def run(F: pd.DataFrame, H: int, folds):
    y = F[f"y{H}"]
    ok = y.notna() & F.d15.notna()
    D = F[ok].reset_index(drop=True)
    w = 1.0 / D.groupby("patient_id").patient_id.transform("size")
    preds = {k: np.full(len(D), np.nan) for k in
             ("persistence", "trend", "ridge", "lgb_cgm", "lgb_cgm_carb", "lgb_full", "ensemble")}
    fold_id = np.full(len(D), -1)
    for k, (tr_p, te_p) in enumerate(folds):
        tr = D.patient_id.isin(tr_p).values
        te = D.patient_id.isin(te_p).values
        fold_id[te] = k
        Dtr, Dte = D[tr], D[te]
        dy = (Dtr[f"y{H}"] - Dtr.g0).values
        preds["persistence"][te] = Dte.g0
        preds["trend"][te] = trend_pred(Dte, H)
        rg = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), Ridge(alpha=10.0))
        rg.fit(Dtr[DYN + CARB], dy, ridge__sample_weight=w[tr])
        preds["ridge"][te] = Dte.g0 + rg.predict(Dte[DYN + CARB])
        for name, cols in (("lgb_cgm", DYN), ("lgb_cgm_carb", DYN + CARB), ("lgb_full", DYN + CARB + STATIC)):
            m = lgb_model()
            m.fit(Dtr[cols], dy, sample_weight=w[tr])
            preds[name][te] = Dte.g0 + m.predict(Dte[cols])
        preds["ensemble"][te] = 0.5 * preds["lgb_full"][te] + 0.5 * preds["ridge"][te]
    return D, preds, fold_id


def metrics(D, p, y, fold_id):
    err = p - y
    res = {"rmse": float(np.sqrt(np.mean(err ** 2))), "mae": float(np.mean(np.abs(err)))}
    per_pat = pd.DataFrame({"pid": D.patient_id, "e2": err ** 2}).groupby("pid").e2.mean() ** 0.5
    res["macro_rmse"] = float(per_pat.mean())
    fr = [float(np.sqrt(np.mean(err[fold_id == k] ** 2))) for k in range(fold_id.max() + 1)]
    res["fold_rmse_mean"] = float(np.mean(fr))
    res["fold_rmse_std"] = float(np.std(fr))
    z = clarke_zones(y, p)
    res["clarke_AB"] = float(np.isin(z, ["A", "B"]).mean())
    res["clarke_A"] = float((z == "A").mean())
    res["clarke_E"] = float((z == "E").mean())
    res["by_cohort_rmse"] = {c: float(np.sqrt(np.mean(err[(D.cohort == c).values] ** 2))) for c in sorted(D.cohort.unique())}
    return res, per_pat


def main():
    t0 = time.time()
    R = pd.read_csv(DATA / "readings.csv.gz", parse_dates=["time"])
    C = pd.read_csv(DATA / "carbs.csv.gz", parse_dates=["time"])
    S = pd.read_csv(DATA / "static.csv")
    F = build_features(R, C, S)
    print("features", F.shape, f"{time.time() - t0:.0f}s")
    pats = F.drop_duplicates("patient_id")[["patient_id", "cohort"]]
    sgkf = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=7)
    folds = [(pats.patient_id.values[a], pats.patient_id.values[b])
             for a, b in sgkf.split(pats, pats.cohort, groups=pats.patient_id)]
    results = {"n_patients": int(pats.patient_id.nunique()), "n_readings": int(len(F)),
               "patients_by_cohort": pats.cohort.value_counts().to_dict(), "horizons": {}}
    per_patient = {}
    for H in HORIZONS:
        D, preds, fold_id = run(F, H, folds)
        y = D[f"y{H}"].values
        hres = {"n_anchors": int(len(D))}
        for k, p in preds.items():
            hres[k], pp = metrics(D, p, y, fold_id)
            per_patient[(H, k)] = pp
        # Paired per-patient test: static EHR fusion vs CGM+carbs, on patients that have static data.
        from scipy.stats import wilcoxon
        a, b = per_patient[(H, "lgb_cgm_carb")], per_patient[(H, "lgb_full")]
        has_static = set(F[F.hba1c_pct.notna()].patient_id)
        idx = [i for i in a.index if i in has_static]
        diff = (a[idx] - b[idx]).values
        hres["fusion_static_test"] = {"n_patients": len(idx), "mean_gain": float(diff.mean()),
                                      "improved": int((diff > 0).sum()),
                                      "wilcoxon_p": float(wilcoxon(diff).pvalue) if len(idx) > 5 else None}
        results["horizons"][str(H)] = hres
        print(H, {k: round(v["rmse"], 2) for k, v in hres.items() if isinstance(v, dict) and "rmse" in v},
              f"{time.time() - t0:.0f}s")
    (HERE / "results.json").write_text(json.dumps(results, indent=2))
    F.to_csv(DATA / "features.csv.gz", index=False)
    print("done", f"{time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
