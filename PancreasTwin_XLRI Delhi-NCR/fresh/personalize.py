"""Closing the loop: does the twin get better as it watches one patient?

A population model is a "digital shadow". A digital twin (NASEM 2024 definition) is also updated with data
from its own physical counterpart. This script tests the simplest honest version of that update.

For every patient, in time order, the twin compares its own past forecasts with the readings that later
arrived. At anchor time t it only uses forecasts whose target time (t_j + H) is already in the past, so
nothing from the future leaks in. The mean of those recent errors (trailing window W hours), shrunk toward
zero by n / (n + K), is added to the population forecast. That is a per-patient bias correction learned
on-device from the patient's own CGM, with no retraining and no data leaving the phone.

Population model = the headline LightGBM (CGM + carbs + static EHR), same 5 patient-disjoint folds as
train_eval.py, so the base numbers reproduce results.json. The update settings (W = 24 h, K = 100) were
fixed before looking at test error; a small sensitivity grid is reported alongside, not used to pick.

Run from the repo root: python fresh/personalize.py
Needs fresh/data/features.csv.gz (written by train_eval.py).
"""
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon
from sklearn.model_selection import StratifiedGroupKFold

from train_eval import CARB, DYN, STATIC, clarke_zones, lgb_model

HERE = Path("fresh")
DATA = HERE / "data"
HORIZONS = [60, 120]
W_HOURS, K = 24, 100  # pre-registered
GRID = [(6, 100), (24, 30), (24, 300), (72, 100)]


def oof_predictions(F, H, folds):
    y = F[f"y{H}"]
    D = F[y.notna() & F.d15.notna()].reset_index(drop=True)
    w = 1.0 / D.groupby("patient_id").patient_id.transform("size")
    cols = DYN + CARB + STATIC
    p = np.full(len(D), np.nan)
    fold_id = np.full(len(D), -1)
    for k, (tr_p, te_p) in enumerate(folds):
        tr, te = D.patient_id.isin(tr_p).values, D.patient_id.isin(te_p).values
        fold_id[te] = k
        m = lgb_model()
        m.fit(D.loc[tr, cols], (D.loc[tr, f"y{H}"] - D.loc[tr, "g0"]).values, sample_weight=w[tr])
        p[te] = D.loc[te, "g0"].values + m.predict(D.loc[te, cols])
    return D, p, fold_id


def causal_correction(D, p, H, w_hours, k):
    """Per-patient trailing mean of already-observed forecast errors, shrunk by n / (n + k)."""
    corr = np.zeros(len(D))
    err = D[f"y{H}"].values - p
    for _, idx in D.groupby("patient_id").indices.items():
        idx = idx[np.argsort(D.time.values[idx])]
        t = D.time.values[idx].astype("datetime64[m]").astype(np.int64)
        seen = t + H  # minute at which each forecast's target becomes observable
        e = err[idx]
        cs = np.r_[0.0, np.cumsum(e)]
        hi = np.searchsorted(seen, t, side="right")             # targets observed by now
        lo = np.searchsorted(seen, t - w_hours * 60, side="left")  # inside the trailing window
        n = hi - lo
        mean = np.where(n > 0, (cs[hi] - cs[lo]) / np.maximum(n, 1), 0.0)
        corr[idx] = mean * n / (n + k)
    return p + corr


def score(D, p, y, fold_id):
    err = p - y
    per_pat = pd.Series(err ** 2).groupby(D.patient_id.values).mean() ** 0.5
    fr = [np.sqrt(np.mean(err[fold_id == f] ** 2)) for f in range(fold_id.max() + 1)]
    z = clarke_zones(y, p)
    return {"rmse": float(np.sqrt(np.mean(err ** 2))), "fold_rmse_mean": float(np.mean(fr)),
            "fold_rmse_std": float(np.std(fr)), "macro_rmse": float(per_pat.mean()),
            "clarke_AB": float(np.isin(z, ["A", "B"]).mean()), "clarke_E": float((z == "E").mean())}, per_pat


def main():
    t0 = time.time()
    F = pd.read_csv(DATA / "features.csv.gz", parse_dates=["time"])
    pats = F.drop_duplicates("patient_id")[["patient_id", "cohort"]]
    sgkf = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=7)
    folds = [(pats.patient_id.values[a], pats.patient_id.values[b])
             for a, b in sgkf.split(pats, pats.cohort, groups=pats.patient_id)]
    out = {"settings": {"window_hours": W_HOURS, "shrink_k": K, "preregistered": True}, "horizons": {}}
    for H in HORIZONS:
        D, p, fold_id = oof_predictions(F, H, folds)
        y = D[f"y{H}"].values
        base, base_pp = score(D, p, y, fold_id)
        pers, pers_pp = score(D, causal_correction(D, p, H, W_HOURS, K), y, fold_id)
        diff = (base_pp - pers_pp).values
        by_cohort = {}
        pc = causal_correction(D, p, H, W_HOURS, K)
        for c in sorted(D.cohort.unique()):
            m = (D.cohort == c).values
            by_cohort[c] = {"population": float(np.sqrt(np.mean((p[m] - y[m]) ** 2))),
                            "personalised": float(np.sqrt(np.mean((pc[m] - y[m]) ** 2)))}
        grid = {f"W{w}h_K{k}": score(D, causal_correction(D, p, H, w, k), y, fold_id)[0]["rmse"] for w, k in GRID}
        out["horizons"][str(H)] = {
            "population": base, "personalised": pers, "by_cohort": by_cohort, "sensitivity_rmse": grid,
            "per_patient": {"n": int(len(diff)), "improved": int((diff > 0).sum()),
                            "mean_gain_mgdl": float(diff.mean()), "wilcoxon_p": float(wilcoxon(diff).pvalue)},
        }
        print(H, f"population {base['rmse']:.2f} -> personalised {pers['rmse']:.2f}",
              f"| improved {(diff > 0).sum()}/{len(diff)} | {time.time() - t0:.0f}s")
    (HERE / "personalize_results.json").write_text(json.dumps(out, indent=2))
    print("done", f"{time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
