# Project Pancreas Twin: A Self-Updating Glucose Digital Twin for Diabetes

**Challenge:** Happiest Health - Digital Twin Challenge 2026 (Unstop), Prototype & Code Submission
**Category:** Healthcare AI, metabolic digital twins, chronic disease management
**One line:** a digital twin of a person's glucose that forecasts 60 and 120 minutes ahead from CGM, meal logs, wearables and EHR, learns from that person's own readings, and turns the forecast into a "take a 15-minute walk now" nudge.

## Team Details and College

| Field | Value |
|---|---|
| Team name | **PancreasTwin** |
| Team leader | Akhilesh K S |
| College | XLRI - Xavier School of Management, Delhi-NCR campus |
| Repository folder | `PancreasTwin_XLRI Delhi-NCR/` (brief rule: project inside a folder named `Team Name_College Name`) |

## Submission Checklist (all 12 mandatory README items)

| # | Required item | Where it is |
|---|---|---|
| 1 | Team details | [Team Details and College](#team-details-and-college) |
| 2 | College / incubator information | [Team Details and College](#team-details-and-college) |
| 3 | Project title | Top of this file: **Project Pancreas Twin** |
| 4 | Problem statement | [Problem Statement](#problem-statement) |
| 5 | Healthcare use case | [Healthcare Use Case](#healthcare-use-case) |
| 6 | Technical stack | [5. Technical Stack](#5-technical-stack) |
| 7 | AI/ML model or framework details | [AI/ML Models](#aiml-models) |
| 8 | Demo video, unlisted YouTube link | [Demo Video](#demo-video) |
| 9 | Open-source licence details | [Licence](#licence) and [`LICENSE`](LICENSE) |
| 10 | Architecture diagram in PDF/PPT | [`figures/architecture_diagram.pdf`](figures/architecture_diagram.pdf) |
| 11 | Presentation in PDF/PPT with project details and outcomes | [`Project_Pancreas_Twin_Deck.pdf`](Project_Pancreas_Twin_Deck.pdf) and [`.pptx`](Project_Pancreas_Twin_Deck.pptx) |
| 12 | All files and links publicly accessible | [Public Access](#public-access) |

## Quick Links

| Deliverable | File |
|---|---|
| Architecture diagram (PDF, required) | [`figures/architecture_diagram.pdf`](figures/architecture_diagram.pdf) (PNG: [`figures/architecture_diagram.png`](figures/architecture_diagram.png)) |
| Presentation deck (PDF and PPTX, required) | [`Project_Pancreas_Twin_Deck.pdf`](Project_Pancreas_Twin_Deck.pdf), [`Project_Pancreas_Twin_Deck.pptx`](Project_Pancreas_Twin_Deck.pptx) |
| Executive report (PDF) | [`Project_Pancreas_Twin_Executive_Report.pdf`](Project_Pancreas_Twin_Executive_Report.pdf) |
| Demo video (required) | [Demo Video](#demo-video) |
| Headline 5-fold benchmark write-up | [`fresh/RESULTS.md`](fresh/RESULTS.md) |
| Closed-loop personalisation write-up | [`fresh/PERSONALIZATION.md`](fresh/PERSONALIZATION.md) |
| Data sources and licences | [`DATA_SOURCES.md`](DATA_SOURCES.md) |
| Licence | [`LICENSE`](LICENSE) (MIT, code only) |

## Problem Statement

Diabetes care in India runs on lagging signals. About 101 million Indian adults have diabetes and 136 million have prediabetes (ICMR-INDIAB, Lancet Diabetes & Endocrinology, 2023). The standard control test, HbA1c, is a three-month average that hides the daily spikes after meals and the dangerous lows at night. Continuous glucose monitors (CGMs) show those swings, but they alarm only after glucose has already crossed a threshold such as 180 mg/dL, when the meal is already absorbed and little can be done.

**The gap:** no affordable, private tool tells a patient *an hour before* that a spike or a low is coming, and what to do about it.

## Healthcare Use Case

| Who | When | What the twin does |
|---|---|---|
| Person with type 2 diabetes or prediabetes wearing a CGM | After a meal | Forecasts a spike 60 minutes ahead; suggests a 15-minute walk; shows the simulated effect of the walk |
| Same person | Evening and night | Warns of a coming low (below 70 mg/dL) early enough for 15 g of carbohydrate |
| Diabetologist or diabetes educator | Outpatient review | Sees each patient's forecast accuracy, alert history and which habits blunt their spikes |
| Insurer or corporate wellness programme | Population level | Fewer acute events and emergency visits from earlier, cheaper lifestyle action |

Scope boundary: decision support and lifestyle coaching only. The twin never doses insulin or changes medication (see section 7).

---

## 1. Executive Summary

Type 2 Diabetes management today is fundamentally reactive. Conventional Continuous Glucose Monitors (CGMs) alert patients only after acute excursions have already occurred. By the time a patient receives an alarm at 195 mg/dL, digestive carbohydrate influx is near its peak, rendering non-pharmacological interventions ineffective.

**Project Pancreas Twin** is a multi-modal physiological digital twin that forecasts blood glucose trajectories **60 minutes and 120 minutes (2 hours) in advance**. It combines CGM history, meal and carbohydrate logs, wearable telemetry (heart rate, physical exertion METs, circadian time) and static Electronic Health Record (EHR) phenotypes (age, BMI, baseline HbA1c, medication class). The forecast gives the patient time for proactive behavioral interventions (such as a 15-minute brisk walk) that blunt impending hyperglycemic spikes via insulin-independent skeletal muscle GLUT4 translocation.

**Headline result:** in patient-disjoint 5-fold cross-validation on 184 patients (real sensor readings only, every patient tested once), the best model reaches **25.85 +/- 1.03 mg/dL RMSE at 60 minutes** and **35.65 +/- 2.13 mg/dL at 120 minutes**, against a persistence floor of 31.14 +/- 1.66 and 44.33 +/- 2.77. That is **17% and 20% better than persistence**. When the twin also updates itself from each patient's own readings (section 2E), it reaches **25.47 and 34.54 mg/dL: 18% and 22% better than persistence**, with 127 of 184 patients improving.

---

## 2. Key Empirical Results

### A. Headline: Patient-Disjoint 5-Fold CV on 184 Patients (primary claim)

An independent from-scratch rebuild (`fresh/`, full write-up in `fresh/RESULTS.md`) loads all 109 Shanghai files (the harmonized set loads 20), removes a Shanghai patient split leak (patients 2001 and 2014), and evaluates on real sensor readings only: 442,353 readings from 184 patients (100 Shanghai T2DM, 45 CGMacros, 23 HUPA-UCM, 16 BIG IDEAs), covering T1D, T2DM, prediabetes and healthy adults. Validation is 5-fold StratifiedGroupKFold on patient with 1/n patient weighting. Values are fold RMSE mean +/- standard deviation.

| Model | 60-min RMSE (CV) | 120-min RMSE (CV) | Clarke A+B (60 min) | vs. Persistence (60 / 120 min) |
| :--- | :---: | :---: | :---: | :---: |
| Persistence (ZOH floor) | 31.14 +/- 1.66 | 44.33 +/- 2.77 | 97.9% | floor |
| Ridge (delta target) | 28.34 +/- 1.39 | 38.60 +/- 2.29 | 97.2% | -9% / -13% |
| LightGBM, CGM only | 26.46 +/- 1.17 | 36.18 +/- 2.17 | 97.3% | -15% / -18% |
| LightGBM, + carbs | 26.05 +/- 1.19 | 35.76 +/- 2.24 | 97.3% | -16% / -19% |
| **LightGBM, + carbs + static EHR** | **25.85 +/- 1.03** | **35.65 +/- 2.13** | 97.2% | **-17% / -20%** |

Per cohort at 60 minutes (best model): BIG IDEAs 18.5, CGMacros 24.6, Shanghai T2DM 23.7, HUPA-UCM (T1D) 29.2 mg/dL. Zone E at 60 minutes is 0.01%.

### B. Secondary Evidence: 17 Held-Out Patients (original team pipeline, 50,561 records)

The original pipeline evaluates on a single held-out split of 17 unseen subjects (50,561 5-minute epochs) with no subject overlap across train, validation and test (Gate G1). It is reported as secondary evidence because one 17-patient split is a small sample. Scored on the same 17 patients, the fresh rebuild reaches **26.33** (60 min) and **36.05** (120 min) versus the team's 27.93 and 39.54, and the two persistence floors agree within 0.2 to 1.4 mg/dL, so both pipelines measure the same thing.

**60-Minute Horizon (h = 12 steps)**

| Model Architecture | 60-Min RMSE (mg/dL) | 60-Min MAE (mg/dL) | Clarke Zone A+B (%) | Clarke Zone E (%) | Spike ROC-AUC | Delta vs. Persistence Floor |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| Linear Velocity Extrapolation | 45.22 | 30.96 | 96.27% | 0.26% | 0.898 | +12.56 mg/dL (Unstable) |
| Zero-Order Hold (Persistence Floor) | 32.66 | 21.87 | 97.65% | 0.10% | 0.914 | Baseline Persistence Floor |
| Two-Tower Neural Net (48-step GRU) | 29.71 | 20.09 | 97.62% | 0.04% | 0.898 | -2.95 mg/dL |
| Multi-Modal Ridge Regressor | 29.28 | 20.10 | 97.40% | 0.05% | 0.927 | -3.38 mg/dL |
| ExtraTrees Forest Ensemble | 28.71 | 19.47 | 97.19% | 0.03% | 0.928 | -3.95 mg/dL |
| **LightGBM GBDT Regressor** | **27.93** | **19.13** | 97.13% | 0.02% | 0.934 | **-4.73 mg/dL** |

**120-Minute Horizon (h = 24 steps)**

| Model Architecture | 120-Min RMSE (mg/dL) | 120-Min MAE (mg/dL) | Clarke Zone A+B (%) | Clarke Zone E (%) | Spike ROC-AUC | Delta vs. Persistence Floor |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| Zero-Order Hold (Persistence Floor) | 48.07 | 32.84 | 94.36% | 0.45% | 0.818 | Baseline Persistence Floor |
| Multi-Modal Ridge Regressor | 42.25 | 29.64 | 94.71% | 0.08% | 0.832 | -5.82 mg/dL |
| Two-Tower Neural Net (48-step GRU) | 39.93 | 28.06 | 95.50% | 0.09% | 0.898 | -8.14 mg/dL |
| **LightGBM GBDT Regressor** | **39.54** | **27.70** | 95.27% | 0.05% | 0.860 | **-8.53 mg/dL** |

### C. Clinical Early Warning & Uncertainty Calibration (17-patient split, Two-Tower)
- **Clarke Error Grid Safety:** 97.62% in Zone A+B for the Two-Tower neural network (97.13% for LightGBM), with 0.04% in Zone E. In 5-fold CV the best model scores 97.2% Zone A+B.
- **90% Quantile Confidence Cone:** 91.8% empirical test coverage via pinball loss across quantiles tau in [0.05, 0.50, 0.95].
- **Median Alert Lead Time:** 40 to 50 minutes advance warning before glucose crosses 180 mg/dL.
- **Clinical Decision Support Debouncing:** a 30-minute refractory suppression reduces false alarms by 80.7% (from a raw 177.37 per 100 patient-hours down to 34.23).
- **Asymmetric Hypoglycemia Penalty:** a 2.5x penalty for true glucose < 70 mg/dL discourages hazardous under-estimation of crashes.

### D. Fusion: Which Extra Signals Actually Help?

**On the 17-patient split** (identical LightGBM configuration at every level, only the feature set changes; script `fusion_ablation.py`, report `FUSION_ABLATION.md`, data `fusion_ablation_results.json`):

| Feature Set | 60-min RMSE | 120-min RMSE | Delta vs CGM-only (60m) | Delta vs CGM-only (120m) |
| :--- | :---: | :---: | :---: | :---: |
| L1: CGM history only | 28.85 | 41.13 | baseline | baseline |
| L2: + cardiorespiratory effort (HR, METs) | 28.94 | 41.06 | -0.09 | +0.07 |
| L3: + nutrition (carbs, calories) | 28.83 | 40.71 | +0.02 | +0.42 |
| L4: + static EHR phenotype (full multimodal) | 28.11 | 39.80 | +0.74 | +1.33 |

On those 17 subjects the static EHR gain was significant (60 min: 14 of 17 improved, Wilcoxon p = 0.0056; 120 min: 12 of 17 improved, p = 0.0348).

**Across 153 patients in 5-fold CV** the static EHR gain **does not generalise**: +0.15 mg/dL at 60 minutes (p = 0.046, borderline, 93 of 153 improved) and -0.07 at 120 minutes (p = 0.47, not significant). **Meal and carbohydrate logging is the bigger multimodal driver:** +0.42 at 60 minutes and +0.56 at 120 minutes.

**Interpretation:** the twin's accuracy comes mostly from CGM history plus meal logging. Static EHR may help some patients but is not a reliable general lever. The product message follows: the twin gets better when the patient logs meals, so meal logging should be effortless.

---

### E. Closing the Loop: The Twin Learns Each Patient

A population model is a "digital shadow". A digital twin is also updated with data from its own patient (NASEM 2024 definition). `fresh/personalize.py` tests this: as readings arrive, the twin compares its own past forecasts with what happened (only forecasts whose outcome is already known, so no leakage) and corrects the next forecast by its recent error (24-hour window, shrunk toward zero). No retraining, runs on the phone. Settings were fixed before testing.

| Horizon | Population model (5-fold CV) | Personalised twin | vs. persistence | Patients improved | Wilcoxon p |
| :--- | :---: | :---: | :---: | :---: | :---: |
| 60 min | 25.85 +/- 1.03 | **25.47 +/- 1.12** | **-18%** | 127 / 184 | 8e-13 |
| 120 min | 35.62 +/- 2.14 | **34.54 +/- 2.30** | **-22%** | 128 / 184 | 4e-14 |

Every cohort improves at both horizons, Clarke Zone A+B rises (60 min 97.22% to 97.56%; 120 min 95.67% to 95.95%), and a longer memory helps more (72 h beats 24 h beats 6 h). Full tables and the sensitivity grid: [`fresh/PERSONALIZATION.md`](fresh/PERSONALIZATION.md); figure: `fresh/personalize.png`.

---

## 3. Data Ingestion & Harmonization Pipeline

Ingested 11.59 GB across 17 open clinical cohorts totaling 247,427,617 records (full list, URLs and licences in `DATA_SOURCES.md`). The four cohorts used for modelling:
- **PhysioNet CGMacros:** 45 subjects with continuous Dexcom G6 CGM, Fitbit HR, steps, and macronutrients.
- **PhysioNet BIG IDEAs:** 16 pre-diabetic subjects with continuous Dexcom CGM, Fitbit HR, and food logs.
- **HUPA-UCM Cohort:** 25 diabetic subjects (23 usable in the fresh rebuild) with FreeStyle Libre 2 CGM, heart rate, steps, and sleep logs.
- **Shanghai T2DM Dataset:** 100 T2DM patients with clinical CGM and measured blood biomarkers (the original harmonized set loaded 20 of 109 files; the fresh rebuild loads all of them).
- **Harmonized Dataset (team pipeline):** 534,175 5-minute epochs across 106 subjects (`data/processed/harmonized_5min.csv.gz`).
- **Fresh Dataset (headline):** 442,353 real readings at native sensor cadence across 184 patients (`fresh/build_dataset.py`).

**Static EHR Provenance Disclosure:**
In the team pipeline the static conditioning vector (age, BMI, baseline HbA1c, medication class) is measured for 81 of the 106 subjects: 45 CGMacros from `bio.csv` (Age, BMI, lab A1c), 16 BIG IDEAs from `Demographics.csv` (HbA1c), and 20 Shanghai T2DM from `Shanghai_T2DM_Summary.xlsx` (Age, BMI, HbA1c, meds). For the 25 HUPA-UCM subjects, which ship no per-subject static file, the vector is drawn from a demographic prior. Every row carries a `static_ehr_source` column (`measured_full`, `measured_hba1c_only`, `synthetic`). The fresh rebuild uses measured static values only and leaves HUPA-UCM's missing.

---

## 4. Submission Deliverables Summary

1. **Executive 15-Slide PowerPoint Deck & PDF Export:** `Project_Pancreas_Twin_Deck.pptx` (1.5 MB) and `Project_Pancreas_Twin_Deck.pdf` (1.0 MB), built by `make_presentation.py` (PDF exported through PowerPoint).
2. **Executive PDF Report:** `Project_Pancreas_Twin_Executive_Report.pdf` (1.67 MB, 6 pages), built by `generate_executive_pdf.py`.
3. **Interactive Clinical Decision Support Dashboard:** `app.py` (Streamlit + Plotly). Patient persona switching, 24-hour day scrubbing, dual-axis physiological visualization, early-warning triage ribbons, an interactive "What-If" 15-minute walk simulation, and a benchmark scorecard.
4. **Figures:**
   - `fresh/fresh_benchmark.png` (5-fold CV benchmark, headline)
   - `fresh/personalize.png` (closed-loop per-patient update, 5-fold CV)
   - `figures/model_comparison.png` (17-patient split, multi-model RMSE vs persistence)
   - `figures/clarke_error_grid.png` (Clarke EGA, Zone A+B = 97.62%, 17-patient split)
   - `figures/trajectory_sample.png` (continuous trace + 90% confidence cone)
   - `figures/fusion_ablation.png` (progressive signal ablation, 17-patient split)
5. **Quality Verification Report:** `VERIFICATION_REPORT.json` (gates G1, G2, G7, QG2, QG3, QG4 and clinical safety).
6. **Architecture Diagram (required by the brief):** `figures/architecture_diagram.pdf` and `.png`, generated by `architecture_diagram.py`.
7. **Video:** `VIDEO_SCRIPT_20MIN.md` (slide-by-slide narration; the rendered video runs 21:19) and `video/build_video.py` (renders the narrated MP4 that is uploaded to YouTube).

---

## 5. Technical Stack

Python 3, pandas, NumPy, scikit-learn (Ridge, ExtraTrees, StratifiedGroupKFold), LightGBM (headline model), PyTorch (Two-Tower static MLP + 2-layer GRU with quantile heads), SciPy (Wilcoxon tests), Streamlit + Plotly (dashboard), Matplotlib, python-pptx and ReportLab (deck and report). Exact packages: `requirements.txt`.

## AI/ML Models

| Model | Role | Framework | Key settings |
|---|---|---|---|
| LightGBM gradient-boosted trees (**headline**) | Predicts the 60 and 120 minute change in glucose from CGM history, meal carbs and static EHR | LightGBM | 600 trees, learning rate 0.03, 31 leaves, each patient weighted 1/n |
| Per-patient online bias update | Closes the loop: corrects each forecast with that patient's recent observed error | NumPy | 24 h trailing window, shrinkage n / (n + 100), causal only |
| Two-Tower neural network | Static EHR MLP tower + 2-layer GRU over 48 five-minute steps, quantile heads (p05, p50, p95) for the 90% confidence cone | PyTorch | Pinball loss, 2.5x penalty on under-predicting lows, 199 KB checkpoint |
| Ridge and ExtraTrees | Transparent fallbacks and baselines | scikit-learn | Ridge alpha 10 on standardised features |
| Persistence (zero-order hold) and damped trend | Floors every model must beat | NumPy | - |
| Counterfactual walk simulator | "What if I walk 15 minutes now?" | Rule-based (GLUT4 uptake curve) | Prototype; learning it from data is on the roadmap |

Evaluation: patient-disjoint StratifiedGroupKFold (5 folds, stratified by cohort), RMSE and MAE in mg/dL, Clarke error grid zones, Wilcoxon signed-rank tests per patient.

## 6. Quickstart & Verification Commands

Run everything from inside this project folder (`PancreasTwin_XLRI Delhi-NCR/`). Python 3.11 or newer.

```bash
pip install -r requirements.txt
streamlit run app.py                       # dashboard (uses the bundled harmonized data and trained weights)
python verify_submission.py                # verification suite (writes VERIFICATION_REPORT.json)
python scripts/download_data.py            # fetch the open datasets into data/raw (only to rebuild from scratch)
python fresh/build_dataset.py              # headline benchmark: data (needs data/raw)
python fresh/train_eval.py                 # headline benchmark: 5-fold CV (about 4 minutes)
python fresh/personalize.py                # closed-loop personalisation (about 10 minutes)
python fresh/compare_team.py               # head-to-head on the 17-patient split
python train_baselines.py                  # team pipeline baselines
python train_twotower.py                   # Two-Tower network
python generate_plots.py                   # figures
python architecture_diagram.py             # architecture diagram (PNG + PDF)
python make_presentation.py                # deck (+ PDF via PowerPoint on Windows)
python video/build_video.py                # narrated walkthrough video from the deck and VIDEO_SCRIPT_20MIN.md
```

---

## 7. Regulatory & Ethical Demarcation

- **Regulatory Classification:** Class II Software as a Medical Device (SaMD) under FDA / CDSCO criteria; Section 520(o)(1)(E) Clinical Decision Support (CDS).
- **Strict Clinical Boundary:** Pancreas Twin provides trajectory forecasting and behavioral lifestyle coaching. It explicitly **DOES NOT** automate insulin pump delivery, calculate bolus doses, or alter pharmaceutical regimens.
- **Privacy Compliance:** Operates with sub-millisecond local inference on personal edge hardware (Intel Core Ultra 5 / Arc GPU) with zero external cloud API spend, supporting compliance with India DPDPA 2023 and US HIPAA.

---

## Demo Video

**Unlisted YouTube link:** VIDEO_LINK_PLACEHOLDER

A narrated walkthrough of the 15-slide deck plus a screen-recorded demo of the dashboard, 21 minutes 19 seconds (the brief asks for at least 20 minutes). The narration is in [`VIDEO_SCRIPT_20MIN.md`](VIDEO_SCRIPT_20MIN.md); the video is rebuilt with `python video/build_video.py`.

## Public Access

Everything this README links to is inside this public repository: code, trained weights, results, figures, deck (PDF and PPTX), architecture diagram (PDF), executive report (PDF) and the bundled processed dataset. The video is an unlisted YouTube video, viewable by anyone with the link, with no sign-in or permission needed. The raw source datasets are public and open access (no data use agreement); `scripts/download_data.py` fetches them from their original hosts (see `DATA_SOURCES.md`).

## Licence

- **Code:** MIT Licence, Copyright (c) 2026 Akhilesh K S. See [`LICENSE`](LICENSE).
- **Data:** not covered by the MIT licence. Raw datasets are not redistributed; each keeps its own licence (see `DATA_SOURCES.md`). The processed file `data/processed/harmonized_5min.csv.gz` is bundled so the dashboard runs out of the box. PhysioNet CGMacros is CC BY-NC-SA 4.0, so derived files that contain CGMacros rows (the harmonized files, the trained weights and the prediction files) are shared for non-commercial research use under the same terms, with attribution to all four source datasets.
