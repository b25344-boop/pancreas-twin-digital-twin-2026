# Closing the Loop: Per-Patient Twin Update

**Script:** `fresh/personalize.py` | **Results:** `fresh/personalize_results.json` | **Figure:** `fresh/personalize.png`

## Why this experiment

A population model that forecasts glucose is a *digital shadow*. The NASEM (2024) definition of a digital twin also needs the reverse flow: the virtual model is updated with data from its own physical counterpart. A 2025 npj Digital Medicine scoping review found that only about 12% of self-described healthcare digital twins meet that bar. This experiment tests the simplest honest version of the update.

## Method

1. Population model: the headline LightGBM (CGM history + carbs + static EHR), same 5 patient-disjoint folds as `train_eval.py`. Its out-of-fold predictions reproduce the headline: 25.85 +/- 1.03 mg/dL at 60 minutes.
2. For each patient, in time order, the twin compares its own past forecasts with the readings that later arrived. At time t it uses only forecasts whose target time is already in the past, so no future information leaks in.
3. The mean of those errors over the trailing 24 hours, shrunk toward zero by n / (n + 100), is added to the next forecast. No retraining and no data leaves the device.
4. The settings (24 hours, K = 100) were fixed before looking at test error. The grid below is a sensitivity check, not a tuning step.

## Results (5-fold CV, 184 patients, real readings only)

| Horizon | Population model | Personalised twin | Gain | Patients improved | Wilcoxon p |
|---|---|---|---|---|---|
| 60 min | 25.85 +/- 1.03 | **25.47 +/- 1.12** | -0.38 mg/dL | 127 / 184 | 8e-13 |
| 120 min | 35.62 +/- 2.14 | **34.54 +/- 2.30** | -1.08 mg/dL | 128 / 184 | 4e-14 |

Fold RMSE mean +/- standard deviation. Against persistence (31.14 and 44.33) the personalised twin is **18% better at 60 minutes and 22% better at 120 minutes**, up from 17% and 20%.

| Clinical safety | Population | Personalised |
|---|---|---|
| Clarke A+B, 60 min | 97.22% | 97.56% |
| Clarke A+B, 120 min | 95.67% | 95.95% |
| Clarke E, 120 min | 0.060% | 0.056% |

Every cohort improves at both horizons:

| Cohort | 60 min population | 60 min personalised | 120 min population | 120 min personalised |
|---|---|---|---|---|
| BIG IDEAs (prediabetes) | 18.54 | 18.39 | 21.17 | 20.73 |
| CGMacros (mixed) | 24.56 | 24.15 | 30.36 | 29.43 |
| HUPA-UCM (T1D) | 29.18 | 28.83 | 42.36 | 41.19 |
| Shanghai (T2DM) | 23.72 | 23.21 | 34.89 | 33.28 |

Sensitivity (pooled RMSE; pre-registered setting is W24h_K100):

| Setting | 60 min | 120 min |
|---|---|---|
| 6 h window, K = 100 | 25.75 | 35.63 |
| 24 h window, K = 30 | 25.38 | 34.61 |
| **24 h window, K = 100** | **25.38** | **34.66** |
| 24 h window, K = 300 | 25.48 | 35.03 |
| 72 h window, K = 100 | 25.24 | 34.31 |

## Honest reading

- The gain is small in mg/dL but very consistent: about 70% of patients improve, every cohort improves, and safety does not get worse.
- The gain grows with horizon and with history: a 72-hour memory does better than 24 hours, a 6-hour memory barely helps. The twin gets better the longer it knows the patient.
- This is a bias correction, the simplest form of personal learning. Learning each patient's own meal and exercise responses is the next step on the roadmap.
