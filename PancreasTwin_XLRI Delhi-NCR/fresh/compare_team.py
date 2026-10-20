"""Head-to-head against the team pipeline (harmonize_5min.py + train_baselines.py).

Experiment A: the fresh pipeline on the team's own 17 test patients (trained on every other patient), so the
             comparison with the team's 27.93 / 39.54 uses the same people.
Experiment B: the size of the interpolation look-ahead in the team data. Persistence RMSE on the team's own
             harmonized rows, split by whether the anchor row is a real sensor reading or an interpolated one.
Experiment C: the team split's two patient leaks (Shanghai 2001 and 2014).
Run from the repo root: python fresh/compare_team.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import train_eval as te  # noqa: E402

HERE = Path("fresh")
TEAM_TEST = ['BIGIDEAS_002', 'BIGIDEAS_003', 'BIGIDEAS_015', 'CGMACROS_CGMacros-005', 'CGMACROS_CGMacros-006',
             'CGMACROS_CGMacros-008', 'CGMACROS_CGMacros-039', 'CGMACROS_CGMacros-041', 'CGMACROS_CGMacros-049',
             'HUPA_HUPA0014P', 'HUPA_HUPA0017P', 'HUPA_HUPA0025P', 'SHANGHAI_2000_0_20201230',
             'SHANGHAI_2001_0_20201102', 'SHANGHAI_2005_0_20211201', 'SHANGHAI_2009_0_20211103',
             'SHANGHAI_2014_1_20210317']


def to_fresh_pid(s):
    if s.startswith("BIGIDEAS_"):
        return "BIG_" + s.split("_")[1]
    if s.startswith("CGMACROS_"):
        return "CGM_" + s.split("-")[1]
    if s.startswith("HUPA_"):
        return s
    return "SH_" + s.split("_")[1]


def main():
    out = {}
    # ---------------- A: same 17 people
    F = pd.read_csv(HERE / "data/features.csv.gz", parse_dates=["time"])
    test_p = sorted({to_fresh_pid(s) for s in TEAM_TEST})
    missing = [p for p in test_p if p not in set(F.patient_id)]
    train_p = sorted(set(F.patient_id) - set(test_p))
    out["A_team_test_patients"] = {"n_test_patients": len(test_p), "missing_in_fresh": missing}
    for H in (60, 120):
        D, preds, fold = te.run(F, H, [(np.array(train_p), np.array(test_p))])
        y = D[f"y{H}"].values
        m = fold == 0
        row = {}
        for k in ("persistence", "ridge", "lgb_cgm", "lgb_cgm_carb", "lgb_full"):
            e = preds[k][m] - y[m]
            row[k] = round(float(np.sqrt(np.mean(e ** 2))), 2)
        out["A_team_test_patients"][str(H)] = row
        print("A", H, row)
    # ---------------- B: interpolation look-ahead inside the team data
    T = pd.read_csv("data/processed/harmonized_5min.csv.gz",
                    usecols=["subject_id", "source_cohort", "datetime", "glucose", "target_glucose_60m", "split"],
                    parse_dates=["datetime"])
    R = pd.read_csv(HERE / "data/readings.csv.gz", parse_dates=["time"])
    sh = T[T.source_cohort == "shanghai_t2dm"].copy()
    sh["sid"] = "SH_" + sh.subject_id.str.replace("SHANGHAI_", "", regex=False)
    real = R[R.cohort == "shanghai_t2dm"][["subject_id", "time"]].rename(columns={"subject_id": "sid"})
    # The team bins with resample("5min"): a real reading at 14:09 lands in the 14:05 bin.
    real["datetime"] = real.time.dt.floor("5min")
    real["is_real"] = True
    sh = sh.merge(real[["sid", "datetime", "is_real"]].drop_duplicates(["sid", "datetime"]), on=["sid", "datetime"], how="left")
    sh["is_real"] = sh.is_real.fillna(False).astype(bool)
    sh = sh.dropna(subset=["target_glucose_60m"])
    e = sh.target_glucose_60m - sh.glucose
    b = {"rows": int(len(sh)), "share_interpolated": round(float((~sh.is_real).mean()), 3),
         "persistence_rmse_60_real_anchor": round(float(np.sqrt((e[sh.is_real] ** 2).mean())), 2),
         "persistence_rmse_60_interpolated_anchor": round(float(np.sqrt((e[~sh.is_real] ** 2).mean())), 2)}
    out["B_shanghai_interpolation"] = b
    print("B", b)
    # ---------------- C: patient leakage in the team split
    t = T.drop_duplicates("subject_id")[["subject_id", "source_cohort", "split"]]
    t = t[t.source_cohort == "shanghai_t2dm"].copy()
    t["pid"] = t.subject_id.str.split("_").str[1]
    leak = t.groupby("pid").split.agg(lambda s: sorted(set(s)))
    out["C_patients_across_splits"] = {k: v for k, v in leak.items() if len(v) > 1}
    print("C", out["C_patients_across_splits"])
    (HERE / "compare_team.json").write_text(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
