# Data Sources, Licences and Access Terms

Raw data is **not redistributed** in this repository. Fetch it with `python scripts/download_data.py` (see `--list`), which writes into `data/raw/`. The MIT licence in `LICENSE` covers code only; every dataset below keeps its own licence. Licence and access details for the four modelling cohorts were re-checked on the landing pages on 2026-10-01. The rest come from the acquisition manifest (`data/MANIFEST.json`, 2026-09-28).

## A. Datasets used for modelling (the 184-patient benchmark and the 106-subject harmonized set)

| Dataset | Subjects used | Landing page / DOI | Licence | Access and DUA | How to fetch |
|---|---|---|---|---|---|
| **PhysioNet CGMacros v1.0.0** | 45 | https://physionet.org/content/cgmacros/1.0.0/ , doi:10.13026/3z8q-x658 | **CC BY-NC-SA 4.0** | Open access. No credentialing, no signed DUA; use must follow the licence (non-commercial, share-alike, attribution). | Automatic: `CGMacros_dateshifted365.zip` |
| **PhysioNet BIG IDEAs Lab Glycemic Variability and Wearable Device Data v1.1.2** | 16 | https://physionet.org/content/big-ideas-glycemic-wearable/1.1.2/ , doi:10.13026/zthx-5212 | Open Data Commons Attribution v1.0 (ODC-By) | Open access. No credentialing, no signed DUA; attribution required. | Automatic: per-subject Dexcom, food log and HR files |
| **HUPA-UCM Diabetes Dataset v1** | 25 (23 usable in the fresh rebuild) | https://data.mendeley.com/datasets/3hbcscwz44/1 , doi:10.17632/3hbcscwz44.1 | CC BY 4.0 | Open access, no DUA; attribution required. | Manual: download the zip from Mendeley Data, save as `data/raw/hupa_ucm/hupa_ucm.zip`; the script extracts it |
| **Shanghai T2DM (Chinese diabetes datasets, Zhao et al.)** | 100 (fresh rebuild; the harmonized set used 20) | https://doi.org/10.6084/m9.figshare.21600933 (collection doi:10.6084/m9.figshare.c.6310860) | CC BY 4.0 | Open access, no DUA; attribution required. | Automatic: figshare API, `diabetes_datasets.zip` |

**Citations**
- Gutierrez-Osuna R, Kerr D, Mortazavi B, Das A. CGMacros: a scientific dataset for personalized nutrition and diet monitoring (version 1.0.0). PhysioNet, 2025. https://doi.org/10.13026/3z8q-x658
- Cho P, Kim J, Bent B, Dunn J. BIG IDEAs Lab Glycemic Variability and Wearable Device Data (version 1.1.2). PhysioNet, 2023. https://doi.org/10.13026/zthx-5212. Original paper: Bent B, Cho PJ, Henriquez M, et al. Engineering digital biomarkers of interstitial glucose from noninvasive smartwatches. npj Digit. Med. 4, 89 (2021).
- HUPA-UCM Diabetes Dataset, Mendeley Data, V1. https://doi.org/10.17632/3hbcscwz44.1
- Zhao Q, Zhu J, Wang C, Rao W. diabetes_datasets.zip. figshare, 2022. https://doi.org/10.6084/m9.figshare.21600933.v5 (Scientific Data 2023, "Chinese diabetes datasets for data-driven machine learning").
- Standard PhysioNet citation: Goldberger A, et al. PhysioBank, PhysioToolkit, and PhysioNet. Circulation 101(23):e215-e220 (2000).

## B. What the licences mean for this repository

- **CGMacros is non-commercial and share-alike.** Any derived file containing CGMacros rows (the harmonized file and its 126 KB sample in `data/processed/`, the trained model weights in `models/`, and the prediction files) is shared for **non-commercial research use under CC BY-NC-SA 4.0**. A commercial product would need CGMacros removed and the models retrained, or a separate licence from the dataset authors.
- **The full harmonized file (27 MB) is bundled** at `data/processed/harmonized_5min.csv.gz` so the dashboard runs without downloading anything. It is pushed with git (GitHub's limit is 100 MB per file; only the browser upload is capped at 25 MB). It can be regenerated with `harmonize_5min.py` after downloading.
- The other three cohorts (CC BY 4.0, ODC-By) need attribution only, which this file and the report provide.
- None of the four needs a signed data use agreement. They were tagged "credentialed" in early planning, and that turned out to be wrong: both PhysioNet sets are open access (`strawberry/CREDENTIALED_DATA_EVALUATION.md` in the workspace has the audit).

## C. Other datasets acquired but not used in the reported models

These were downloaded during the data survey (11.59 GB, 17 sources) and listed for completeness. None of them feeds the headline or secondary results.

| Slug | Dataset | Landing page / DOI | Licence | Note |
|---|---|---|---|---|
| azt1d | AZT1D Real-World Type 1 Diabetes Dataset | https://data.mendeley.com/datasets/gk9m674wcx/1 | CC BY 4.0 | |
| bris_t1d_open | Bris-T1D Open Dataset | https://data.bris.ac.uk/data/dataset/33z5jc8fa6tob21ptrugzqog08 | CC BY 4.0 | |
| colas_2019 | Colas 2019 PLOS ONE T2D Dataset | https://doi.org/10.1371/journal.pone.0226841 | CC BY 4.0 | |
| d1namo | D1NAMO Multimodal Diabetes Dataset | https://zenodo.org/records/5651217 | CC BY-SA 4.0 | Share-alike |
| extra_park_cgm | Stanford Park CGMdb | https://web.stanford.edu/group/genetics/cgmdb/data/data_cgm.csv | CC BY 4.0 (per manifest) | |
| extra_uchtt1dm | UC-HT-T1DM Dataset | https://github.com/fisiologiacuantitativauc/UC_HT_T1DM | MIT | |
| glucofm_bench | GlucoFM-Bench | https://huggingface.co/datasets/glucofmbench/GlucoFM-Bench | CC BY-NC-SA 4.0 | Non-commercial |
| glucose_ml_auto | Glucose-ML Harmonized CGM Pipeline | https://github.com/Augmented-Health-Lab/Glucose-ML-Project | MIT | |
| hall_2018 | Hall 2018 PLOS Biology Glucotypes | https://doi.org/10.1371/journal.pbio.2005143 | CC BY 4.0 | |
| hrv_sleep_diary | HRV & Sleep Diary Multimodal Cohort | https://doi.org/10.6084/m9.figshare.28509740 | CC BY 4.0 | |
| shanghai_t1dm | Shanghai T1DM Dataset | https://doi.org/10.6084/m9.figshare.c.6310860 | CC BY 4.0 | Same archive as Shanghai T2DM |
| synthea_t2d | Synthea Type-2-Diabetes Synthetic Cohort | https://github.com/synthetichealth/synthea | Apache-2.0 | Synthetic EHR, explored only |
| t1d_uom | T1D-UOM Manchester Diabetes Study | https://zenodo.org/records/15806142 | CC BY 4.0 | |
| tooling_awesome_cgm | Awesome-CGM Repository Index | https://github.com/IrinaStatsLab/Awesome-CGM | MIT | Reference index |
| tooling_glucose_ml | Glucose-ML Project Tooling | https://github.com/Augmented-Health-Lab/Glucose-ML-Project | MIT | Reference code |

Datasets assessed and not used because access needs credentialing or a signed DUA: Synapse DiaTrend (syn38187184, Synapse certified user plus intended-use statement), OhioT1DM (institutional DUA, server offline), MIMIC-IV (credentialed, ICU scope).
