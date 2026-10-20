# Fusion Ablation - Project Pancreas Twin

Does static EHR plus exogenous drivers add anything over CGM history alone, at a 60-minute and 120-minute horizon, on the same subject-disjoint held-out split? Identical LightGBM architecture at every level; only the feature set changes, so any RMSE move is attributable to the added signal and nothing else.

Held-out test: 17 unseen subjects, zero patient leakage. Imputation medians taken from train only.

## 60m horizon

| Level | Feature set | RMSE | MAE | Clarke A+B% | Spike AUC | Delta vs CGM-only (mg/dL) |
|---|---|---|---|---|---|---|
| L0 | Persistence (floor) | 32.66 | 21.87 | 97.65 | 0.914 | 3.81 |
| L1 | CGM history only | 28.85 | 19.58 | 97.15 | 0.925 | 0.0 |
| L2 | CGM + cardiorespiratory effort (HR, METs) | 28.94 | 19.7 | 97.07 | 0.926 | -0.09 |
| L3 | CGM + effort + nutrition (carbs, calories) | 28.83 | 19.62 | 97.03 | 0.927 | 0.02 |
| L4 | CGM + effort + nutrition + static EHR (full multimodal) | 28.11 | 19.44 | 97.09 | 0.933 | 0.74 |

Paired per-subject check, full multimodal (L4) vs CGM-only (L1), 17 subjects: mean Delta-RMSE 0.93 mg/dL, median 0.76 mg/dL, L4 better in 14 of 17, L1 better in 3 of 17, Wilcoxon p=0.0056.

## 120m horizon

| Level | Feature set | RMSE | MAE | Clarke A+B% | Spike AUC | Delta vs CGM-only (mg/dL) |
|---|---|---|---|---|---|---|
| L0 | Persistence (floor) | 48.07 | 32.84 | 94.36 | 0.818 | 6.94 |
| L1 | CGM history only | 41.13 | 28.73 | 94.69 | 0.831 | 0.0 |
| L2 | CGM + cardiorespiratory effort (HR, METs) | 41.06 | 28.73 | 94.75 | 0.832 | 0.07 |
| L3 | CGM + effort + nutrition (carbs, calories) | 40.71 | 28.44 | 94.69 | 0.836 | 0.42 |
| L4 | CGM + effort + nutrition + static EHR (full multimodal) | 39.8 | 28.33 | 95.2 | 0.856 | 1.33 |

Paired per-subject check, full multimodal (L4) vs CGM-only (L1), 17 subjects: mean Delta-RMSE 1.43 mg/dL, median 1.45 mg/dL, L4 better in 12 of 17, L1 better in 5 of 17, Wilcoxon p=0.0348.

## Reading

The column that matters is Delta vs CGM-only. It is the measured driver contribution on this cohort and split. The published field result (driver-blindness, 2025) is that exogenous drivers add roughly 5 to 20 percent RMSE at these horizons; our numbers should be read against that band, not against a hoped-for large jump. If a level does not move the metric, the honest finding is that the added signal is not yet earning its place, and that is reported as such rather than buried.

**Static EHR caveat.** Only the Shanghai T2DM subjects carry measured static laboratory phenotypes (age, BMI, HbA1c, medication class). For the other cohorts the static vector is synthesized from a demographic prior and is disclosed as a limitation. The fusion ablation is the test of whether even that signal helps; the dynamic CGM tower is real measured data in every cohort.
