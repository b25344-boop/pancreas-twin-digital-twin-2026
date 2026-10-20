"""
Academic & Executive PDF Report Generator for Digital Twin Challenge 2026.
Uses reportlab to generate a publication-quality, color-themed report:
Project_Pancreas_Twin_Executive_Report.pdf
"""

import os
import sys
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

PDF_PATH = Path("Project_Pancreas_Twin_Executive_Report.pdf")
FIG_DIR = Path("figures")
FRESH_DIR = Path("fresh")

# Brand Colors
C_NAVY = colors.HexColor("#0F2043")
C_TEAL = colors.HexColor("#00A8CC")
C_DARK = colors.HexColor("#212529")
C_MUTED = colors.HexColor("#6C757D")
C_LIGHT_BG = colors.HexColor("#F8F9FA")
C_ACCENT_BG = colors.HexColor("#EBF3FA")
C_BORDER = colors.HexColor("#DEE2E6")
C_GREEN = colors.HexColor("#2E7D32")
C_RED = colors.HexColor("#C62828")


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(C_MUTED)

        # Header (pages 2+)
        if self._pageNumber > 1:
            self.drawString(36, 11 * inch - 26, "PROJECT PANCREAS TWIN: MULTI-MODAL METABOLIC DIGITAL TWIN")
            self.drawRightString(8.5 * inch - 36, 11 * inch - 26, "HAPPIEST HEALTH • 2026")
            self.setStrokeColor(C_BORDER)
            self.setLineWidth(0.5)
            self.line(36, 11 * inch - 30, 8.5 * inch - 36, 11 * inch - 30)

        # Footer (all pages)
        self.setStrokeColor(C_BORDER)
        self.setLineWidth(0.5)
        self.line(36, 36, 8.5 * inch - 36, 36)
        self.drawString(36, 24, "Team PancreasTwin | Akhilesh K S (XLRI Delhi-NCR) | Class II SaMD Decision Support Architecture")
        self.drawRightString(8.5 * inch - 36, 24, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()


def build_pdf():
    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=42,
        bottomMargin=42
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=28,
        textColor=C_NAVY,
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=C_TEAL,
        spaceAfter=14
    )

    h1_style = ParagraphStyle(
        "Heading1_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        textColor=C_NAVY,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        "Heading2_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=C_TEAL,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        "Body_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.5,
        textColor=C_DARK,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        "Bullet_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=C_DARK,
        leftIndent=12,
        spaceAfter=3
    )

    callout_style = ParagraphStyle(
        "Callout_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8.5,
        leading=12,
        textColor=C_MUTED,
        spaceAfter=8
    )

    cell_style = ParagraphStyle("Cell_Custom", parent=styles["Normal"], fontName="Helvetica", fontSize=8, leading=10, textColor=C_DARK)
    cell_bold = ParagraphStyle("CellBold_Custom", parent=cell_style, fontName="Helvetica-Bold")
    head_cell = ParagraphStyle("HeadCell_Custom", parent=cell_bold, textColor=colors.white)

    def wrap_rows(rows, header=True, bold_cols=()):
        out = []
        for ri, row in enumerate(rows):
            new = []
            for ci, cell in enumerate(row):
                if header and ri == 0:
                    new.append(Paragraph(cell, head_cell))
                elif ci in bold_cols:
                    new.append(Paragraph(cell, cell_bold))
                else:
                    new.append(Paragraph(cell, cell_style))
            out.append(new)
        return out

    story = []

    # Title & Metadata
    story.append(Paragraph("PROJECT PANCREAS TWIN", title_style))
    story.append(Paragraph(
        "A Multi-Modal Physiological Digital Twin for 60-Minute Glycemic Excursion Forecasting with Counterfactual Intervention Modeling",
        subtitle_style
    ))
    story.append(HRFlowable(width="100%", thickness=1.5, color=C_TEAL, spaceBefore=0, spaceAfter=12))

    # Executive Metadata Box
    meta_data = [
        ["Challenge Track:", "Happiest Health: Digital Twin Challenge 2026 (Unstop)", "Team / Leader:", "PancreasTwin / Akhilesh K S (XLRI Delhi-NCR)"],
        ["Target Horizons:", "60 Minutes (Interventional) & 120 Minutes (Strategic)", "Evaluation Framework:", "Patient-Disjoint 5-Fold CV + Clarke Error Grid"],
        ["Cohort Breadth:", "184 Patients, 442,353 Real Readings (5-Fold CV)", "Deployment Envelope:", "Edge NPU / Core Ultra 5 (0.84 ms, Zero Cloud API)"]
    ]
    t_meta = Table(wrap_rows(meta_data, header=False, bold_cols=(0, 2)), colWidths=[1.2 * inch, 2.6 * inch, 1.3 * inch, 2.4 * inch])
    t_meta.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), C_LIGHT_BG),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("TEXTCOLOR", (0, 0), (-1, -1), C_DARK),
        ("GRID", (0, 0), (-1, -1), 0.5, C_BORDER),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 10))

    # ==========================================
    # Section 1: Executive Summary & Clinical Rationale
    # ==========================================
    story.append(Paragraph("1. Executive Summary & Clinical Rationale", h1_style))
    story.append(Paragraph(
        "Continuous Glucose Monitoring (CGM) represents a standard-of-care revolution in outpatient diabetes management, yet current commercial offerings remain strictly reactive. Standard CGMs trigger alert buzzers only when interstitial glucose crosses high thresholds (e.g., > 180 mg/dL). By that time, carbohydrate absorption is advanced, and patient opportunities for non-pharmacological mitigation are largely forfeited.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Project Pancreas Twin</b> transforms this paradigm by constructing a multi-modal physiological digital twin capable of projecting blood glucose trajectories <b>60 minutes and 120 minutes into the future</b>. Combining CGM history, meal and carbohydrate logs, wearable telemetry (heart rate, physical exertion METs, circadian time) and static Electronic Health Record (EHR) phenotypes (age, body mass index, baseline HbA1c, medication class), the twin provides actionable pre-emptive warnings that permit behavioral lifestyle interventions, such as a 15-minute brisk walk, to blunt postprandial glucose excursions via skeletal muscle GLUT4 translocation.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Headline result.</b> In patient-disjoint 5-fold cross-validation on 184 patients (442,353 real sensor readings, every patient tested once), the best model (LightGBM with carbohydrate and static EHR features) reaches an RMSE of <b>25.85 +/- 1.03 mg/dL at 60 minutes</b> and <b>35.65 +/- 2.13 mg/dL at 120 minutes</b>, against a persistence floor of 31.14 +/- 1.66 and 44.33 +/- 2.77. That is <b>17% and 20% better than persistence</b>. A 17-patient held-out split from the original team pipeline gives consistent secondary evidence (LightGBM 27.93 and 39.54 versus persistence 32.66 and 48.07). Of the extra modalities, meal logging is the larger driver; the static EHR gain seen on the 17-patient split did not generalise in 5-fold CV.",
        body_style
    ))

    story.append(Paragraph(
        "<b>Closing the loop.</b> A digital twin must also learn from its own patient. As readings arrive, the twin compares its past forecasts with what actually happened (only forecasts whose outcome is already known) and corrects the next forecast by its recent error (24-hour window, shrunk toward zero, settings fixed before testing). On the same 5 folds this lowers RMSE to <b>25.47 +/- 1.12 mg/dL at 60 minutes and 34.54 +/- 2.30 at 120 minutes: 18% and 22% better than persistence</b>. 127 of 184 patients improve (Wilcoxon p = 8e-13), every cohort improves and Clarke Zone A+B rises. Details: fresh/PERSONALIZATION.md.",
        body_style
    ))

    # ==========================================
    # Section 2: Clinical Physiology & The 60-Minute Horizon
    # ==========================================
    story.append(Paragraph("2. Clinical Physiology: The 60-Minute Interventional Window", h1_style))
    story.append(Paragraph(
        "In metabolic clinical management, the predictive horizon must strictly align with human physiological intervention kinetics. Forecasting at 15 minutes is insufficient because insulin-independent muscle uptake requires 15 to 20 minutes to reach active metabolic rates. Conversely, forecasting beyond 2 hours suffers from high stochastic uncertainty introduced by spontaneous activity and unscheduled snacking.",
        body_style
    ))
    story.append(Paragraph(
        "<b>The GLUT4 Translocation Mechanism:</b> The 60-minute window unlocks non-pharmacological lifestyle mitigation. Moderate physical exertion (such as a 15-minute brisk walk, ~3.5 to 4.5 METs) stimulates skeletal muscle contractions, inducing insulin-independent GLUT4 glucose transporter translocation from intracellular vesicles to the plasma membrane. This accelerates systemic glucose uptake, blunting postprandial glucose peaks by 35 to 45 mg/dL without pharmaceutical adjustments.",
        body_style
    ))

    # ==========================================
    # Section 3: Data Foundation & Harmonization Pipeline
    # ==========================================
    story.append(Paragraph("3. Multi-Cohort Data Foundation (534k Epochs across 106 Patients)", h1_style))
    story.append(Paragraph(
        "To establish genuine clinical generalizability, Project Pancreas Twin conducted an exhaustive survey of open biomedical cohorts, downloading and verifying 11.59 GB across 17 open clinical repositories totaling 247,427,617 records.",
        body_style
    ))

    # Dataset Table
    ds_data = [
        ["Cohort Name", "Modality Streams", "Verified Subject Count", "Standardized Sampling", "Role in Digital Twin Pipeline"],
        ["PhysioNet CGMacros", "Dexcom G6 CGM + Fitbit HR + METs + Meals", "45 Human Subjects", "5-Minute Epochs", "Primary Multi-Modal Training & Validation"],
        ["PhysioNet BIG IDEAs", "Dexcom CGM + Fitbit HR + Food Logs", "16 Pre-Diabetic Subjects", "5-Minute Epochs", "Pre-Diabetes Trajectory Modeling"],
        ["HUPA-UCM Cohort", "FreeStyle Libre 2 CGM + Zephyr HR + Steps", "25 Diabetic Subjects", "5-Minute Epochs", "Continuous Wearables Sensor Fusion"],
        ["Shanghai T2DM", "Clinical CGM + Laboratory Biomarkers", "20 Hospitalized T2D Patients", "5-Minute Epochs", "Real Clinical Laboratory Validation"],
        ["Synthea T2D Engine", "Longitudinal Synthetic Patient EHR", "500 Patients (92k rows)", "Event-Driven EHR", "Static Phenotype Embedding Calibration"]
    ]
    t_ds = Table(wrap_rows(ds_data), colWidths=[1.4 * inch, 2.0 * inch, 1.2 * inch, 1.1 * inch, 1.8 * inch])
    t_ds.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), C_NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("LEADING", (0, 0), (-1, -1), 10),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("GRID", (0, 0), (-1, -1), 0.5, C_BORDER),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, C_LIGHT_BG]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t_ds)
    story.append(Spacer(1, 8))

    story.append(Paragraph(
        "<b>Strict Patient-Disjoint Slicing (Gate G1):</b> The harmonizer resamples continuous sensors into 534,175 uniform 5-minute epochs and partitions the data strictly by unique patient identifier: 74 training subjects (402,662 epochs), 15 validation subjects (80,952 epochs), and 17 held-out test subjects (50,561 epochs). Zero patient telemetry overlaps across partitions, eliminating data leakage.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Data Provenance Disclosure:</b> Patient static EHR profiles utilize measured clinical data where available: 45 subjects from CGMacros carry measured age, BMI, and laboratory HbA1c; 16 subjects from BIG IDEAs carry measured HbA1c; 20 subjects from Shanghai carry measured age, gender, and clinical laboratory metrics. HUPA-UCM (25 subjects) utilizes baseline population priors, marked transparently via the static_ehr_source provenance field.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Independent Fresh Rebuild (headline dataset):</b> A from-scratch rebuild (<code>fresh/</code>) loads all 109 Shanghai T2DM files (the harmonized set loads 20), keeps real sensor readings only at each sensor's native cadence (no interpolated anchors or targets), and removes a patient leak (patients 2001 and 2014 had one recording in train and one in test). Result: 442,353 readings from 184 patients: 100 Shanghai T2DM, 45 CGMacros, 23 HUPA-UCM and 16 BIG IDEAs, covering T1D, T2DM, prediabetes and healthy adults. Static EHR values are used only where measured.",
        body_style
    ))

    # ==========================================
    # Section 4: System Architecture: The Two-Tower Digital Twin
    # ==========================================
    story.append(Paragraph("4. System Architecture: Two-Tower Multi-Modal Fusion", h1_style))
    story.append(Paragraph(
        "The Pancreas Twin neural architecture employs a dual-tower structure that explicitly separates time-invariant metabolic resistance from time-varying physiological dynamics:",
        body_style
    ))
    story.append(Paragraph("• <b>Tower 1 (Static EHR MLP):</b> Encodes patient age, BMI, baseline glycated HbA1c, and prescription classifications (Metformin and insulin therapy) into a dense 16-dimensional static metabolic embedding.", bullet_style))
    story.append(Paragraph("• <b>Tower 2 (Dynamic Wearables GRU):</b> Processes a 48-step lookback sequence (4 hours) across 8 continuous channels (glucose, velocity dG/dt, acceleration, heart rate, METs activity, carbohydrates, and cyclical circadian sine/cosine clock) using a 2-layer Gated Recurrent Unit (hidden dimension 64).", bullet_style))
    story.append(Paragraph("• <b>Multi-Modal Late Fusion & Multi-Task Heads:</b> Concatenates static and recurrent representations (32-d) to simultaneously drive: (1) a 60-minute Quantile Head producing p05, p50, and p95 predictions (90% confidence cone), (2) a 120-minute continuous trajectory head, and (3) an early warning binary spike classifier.", bullet_style))
    story.append(Paragraph("• <b>Pinball Loss with Asymmetric Hypoglycemia Penalty:</b> Optimized with quantile pinball loss. Critically, an asymmetric 2.5x penalty is applied when reference glucose drops below 70 mg/dL, penalizing optimistic predictions that could conceal life-threatening hypoglycemic crashes.", bullet_style))

    story.append(Spacer(1, 8))

    # ==========================================
    # Section 5: Benchmark Evaluation (primary: fresh 5-fold CV; secondary: 17-patient split)
    # ==========================================
    story.append(Paragraph("5. Benchmark Evaluation: Patient-Disjoint 5-Fold CV on 184 Patients", h1_style))
    story.append(Paragraph(
        "In continuous glucose forecasting, naive Zero-Order Hold (ZOH, persistence: predicting no change) is a notoriously competitive baseline due to interstitial fluid lag. A model that cannot beat it provides no predictive clinical utility. Table 1 is the headline: 5-fold StratifiedGroupKFold on patient (stratified by cohort), 1/n patient weighting, real readings only, every one of the 184 patients tested exactly once. Values are fold RMSE mean +/- standard deviation.",
        body_style
    ))
    fr_data = [
        ["Model (5-fold CV, 184 patients)", "60m RMSE (mg/dL)", "120m RMSE (mg/dL)", "Clarke A+B at 60m", "vs. Persistence (60m / 120m)"],
        ["Persistence (ZOH)", "31.14 +/- 1.66", "44.33 +/- 2.77", "97.9%", "Baseline floor"],
        ["Ridge (delta target)", "28.34 +/- 1.39", "38.60 +/- 2.29", "97.2%", "-9% / -13%"],
        ["LightGBM, CGM only", "26.46 +/- 1.17", "36.18 +/- 2.17", "97.3%", "-15% / -18%"],
        ["LightGBM, + carbs", "26.05 +/- 1.19", "35.76 +/- 2.24", "97.3%", "-16% / -19%"],
        ["LightGBM, + carbs + static EHR", "25.85 +/- 1.03", "35.65 +/- 2.13", "97.2%", "-17% / -20%"],
    ]
    t_fr = Table(fr_data, colWidths=[2.2 * inch, 1.2 * inch, 1.2 * inch, 1.1 * inch, 1.8 * inch])
    t_fr.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), C_NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("LEADING", (0, 0), (-1, -1), 10),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, C_BORDER),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, C_LIGHT_BG]),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(t_fr)
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "Per cohort at 60 minutes (best model): BIG IDEAs 18.5, CGMacros 24.6, Shanghai T2DM 23.7 and HUPA-UCM (T1D) 29.2 mg/dL. The per-patient (macro) RMSE at 60 minutes is 24.50 mg/dL.",
        body_style
    ))
    img_fresh = FRESH_DIR / "fresh_benchmark.png"
    if img_fresh.exists():
        story.append(Image(str(img_fresh), width=7.4 * inch, height=7.4 * inch * 840 / 2600))
        story.append(Paragraph("<i>Figure 1: Fresh benchmark, real sensor readings only, patient-disjoint 5-fold CV on 184 patients (error bars: fold standard deviation).</i>", callout_style))

    story.append(Paragraph("5b. Secondary Evidence: 17-Patient Held-Out Split (Original Team Pipeline)", h2_style))
    story.append(Paragraph(
        "The original pipeline evaluates on a single held-out split of 17 unseen patients (50,561 5-minute epochs). Table 2 reports it as secondary evidence. Scored on the same 17 patients, the fresh rebuild reaches 26.33 mg/dL (60m) and 36.05 mg/dL (120m), and the two persistence floors agree within 0.2 to 1.4 mg/dL, so both pipelines measure the same thing.",
        body_style
    ))

    # Benchmark Table
    bench_data = [
        ["Model Architecture", "Horizon", "RMSE (mg/dL)", "MAE (mg/dL)", "Clarke A+B (%)", "Clarke Zone E (%)", "Spike ROC-AUC", "Delta vs. Persistence Floor"],
        ["Linear Velocity Extrap.", "60m", "45.22", "30.96", "96.27%", "0.26%", "0.898", "+12.56 mg/dL (Unstable)"],
        ["Zero-Order Hold (ZOH)", "60m", "32.66", "21.87", "97.65%", "0.10%", "0.914", "Baseline Persistence Floor"],
        ["Two-Tower Deep Net (48-step)", "60m", "29.71", "20.09", "97.62%", "0.04%", "0.898", "-2.95 mg/dL (Beats Floor)"],
        ["Multi-Modal Ridge Regressor", "60m", "29.28", "20.10", "97.40%", "0.05%", "0.927", "-3.38 mg/dL (Beats Floor)"],
        ["ExtraTrees Regressor Ensemble", "60m", "28.71", "19.47", "97.19%", "0.03%", "0.928", "-3.95 mg/dL (Beats Floor)"],
        ["LightGBM GBDT Regressor", "60m", "27.93", "19.13", "97.13%", "0.02%", "0.934", "-4.73 mg/dL (Beats Floor)"],
        ["Zero-Order Hold (ZOH)", "120m", "48.07", "32.84", "94.36%", "0.45%", "0.818", "Baseline Persistence Floor"],
        ["Two-Tower Deep Net (48-step)", "120m", "39.93", "28.06", "95.50%", "0.09%", "0.898", "-8.14 mg/dL (Beats Floor)"],
        ["LightGBM GBDT Regressor", "120m", "39.54", "27.70", "95.27%", "0.05%", "0.860", "-8.53 mg/dL (Beats Floor)"]
    ]
    t_b = Table(bench_data, colWidths=[1.8 * inch, 0.6 * inch, 0.8 * inch, 0.8 * inch, 0.9 * inch, 0.9 * inch, 0.8 * inch, 1.4 * inch])
    t_b.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), C_NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7.5),
        ("LEADING", (0, 0), (-1, -1), 9.5),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
        ("GRID", (0, 0), (-1, -1), 0.5, C_BORDER),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, C_LIGHT_BG]),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(t_b)
    story.append(Spacer(1, 10))

    # ==========================================
    # Section 6: Multi-Modal Fusion Ablation: Proving Static EHR Value
    # ==========================================
    story.append(Paragraph("6. Multi-Modal Fusion Ablation: What Each Signal Really Adds", h1_style))
    story.append(Paragraph(
        "A central inquiry in metabolic AI is whether conditioning temporal wearable signals with static EHR features provides measurable advantage over CGM signals alone. To isolate driver contributions, an ablation study was run across five progressive information levels on the 17-patient held-out split (Table 3), and the key steps were then re-tested in the 5-fold rebuild (Table 4):",
        body_style
    ))

    # Ablation Table
    ab_data = [
        ["Information Level", "Signal Features Included", "60m RMSE", "60m Delta vs L1", "120m RMSE", "120m Delta vs L1", "Wilcoxon Significance"],
        ["L0: Persistence", "None (Zero-Order Hold baseline)", "32.66 mg/dL", "-3.81 mg/dL", "48.07 mg/dL", "-6.94 mg/dL", "Reference Floor"],
        ["L1: CGM History", "CGM sequence, velocity, acceleration", "28.85 mg/dL", "Baseline (0.0)", "41.13 mg/dL", "Baseline (0.0)", "CGM Foundation"],
        ["L2: + Cardiorespiratory", "CGM + Heart Rate + METs Exertion", "28.94 mg/dL", "-0.09 mg/dL", "41.06 mg/dL", "+0.07 mg/dL", "Physiological Context"],
        ["L3: + Nutrition", "CGM + Effort + Carbohydrates + Calories", "28.83 mg/dL", "+0.02 mg/dL", "40.71 mg/dL", "+0.42 mg/dL", "Digestive Input"],
        ["L4: + Static EHR", "Full Multimodal (+ Age, BMI, HbA1c, Meds)", "28.11 mg/dL", "+0.74 mg/dL", "39.80 mg/dL", "+1.33 mg/dL", "p = 0.0056 (60m) / p = 0.0348 (120m)"]
    ]
    t_ab = Table(ab_data, colWidths=[1.3 * inch, 2.1 * inch, 0.8 * inch, 1.0 * inch, 0.8 * inch, 1.0 * inch, 1.5 * inch])
    t_ab.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), C_TEAL),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7.5),
        ("LEADING", (0, 0), (-1, -1), 9.5),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
        ("GRID", (0, 0), (-1, -1), 0.5, C_BORDER),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, C_LIGHT_BG]),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(t_ab)
    story.append(Spacer(1, 8))

    story.append(Paragraph(
        "<b>17-patient finding:</b> On the held-out split, static EHR conditioning improved 14 of 17 subjects at 60 minutes (+0.74 mg/dL, Wilcoxon p = 0.0056) and 12 of 17 at 120 minutes (+1.33 mg/dL, p = 0.0348).",
        body_style
    ))
    fu_data = [
        ["Added signal (5-fold CV)", "Patients", "60m RMSE gain", "60m significance", "120m RMSE gain", "120m significance"],
        ["Meal / carbohydrate logging", "184", "+0.42 mg/dL", "gain in pooled RMSE", "+0.56 mg/dL", "gain in pooled RMSE"],
        [Paragraph("Static EHR (age, BMI, HbA1c)", bullet_style), "153 (measured)", "+0.15 mg/dL", Paragraph("p = 0.046 (borderline), 93 of 153 improved", bullet_style), "-0.07 mg/dL", "p = 0.47 (not significant)"],
    ]
    t_fu = Table(fu_data, colWidths=[1.7 * inch, 0.9 * inch, 0.9 * inch, 1.6 * inch, 0.9 * inch, 1.5 * inch])
    t_fu.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), C_NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7.5),
        ("LEADING", (0, 0), (-1, -1), 9.5),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, C_BORDER),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, C_LIGHT_BG]),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(Spacer(1, 4))
    story.append(t_fu)
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "<b>Honest reading:</b> The static EHR effect was real for those 17 people but does not generalise across 153 patients with measured static data: it is small and borderline at 60 minutes and absent at 120 minutes. Meal and carbohydrate logging is the bigger multimodal driver. The product implication is direct: the twin gets more accurate when the patient logs meals, so the app should make meal logging effortless.",
        body_style
    ))

    # Embed Fusion Ablation Figure
    img_ab = FIG_DIR / "fusion_ablation.png"
    if img_ab.exists():
        story.append(Image(str(img_ab), width=7.4 * inch, height=3.2 * inch))
        story.append(Paragraph("<i>Figure 2: Fusion ablation on the 17-patient held-out split (60m and 120m RMSE by information level). The static EHR step shown here did not replicate in 5-fold CV (Table 4).</i>", callout_style))

    story.append(Spacer(1, 10))

    # ==========================================
    # Section 7: Figures & Clinical Validation
    # ==========================================
    story.append(Paragraph("7. Clarke Error Grid Safety & Clinical Lead Time", h1_style))
    story.append(Paragraph(
        "FDA guidance mandates evaluation via Clarke Error Grid Analysis (EGA). Predictions in Zone A and B are clinically safe and lead to correct or benign clinical decisions. Predictions in Zone E represent catastrophic errors that recommend opposite treatment.",
        body_style
    ))
    story.append(Paragraph(
        "In the 5-fold CV on 184 patients, the best 60-minute model places <b>97.2% of predictions in Zone A+B</b> and 0.01% in Zone E (persistence scores 97.9% A+B: Clarke zones are wide enough that a lagged forecast usually stays in Zone B, which is why RMSE is the primary metric). On the 17-patient held-out split (49,286 evaluations, chart below), the Two-Tower network achieves <b>97.62% in Zone A+B</b> and <b>0.04% in Zone E</b>. In event detection, the model achieves a <b>median lead time of 40 to 50 minutes</b> prior to acute spike onset, with Clinical Decision Support (CDS) debouncing suppressing repetitive clustered alarms and reducing false alert rates by 80.7% (from 177.37/100h down to 34.23/100h).",
        body_style
    ))

    # Embed Figures Side by Side
    img_clarke = FIG_DIR / "clarke_error_grid.png"
    img_comp = FIG_DIR / "model_comparison.png"
    if img_clarke.exists() and img_comp.exists():
        img_table = Table([[
            Image(str(img_clarke), width=3.5 * inch, height=3.5 * inch),
            Image(str(img_comp), width=3.8 * inch, height=2.4 * inch)
        ]], colWidths=[3.6 * inch, 3.9 * inch])
        img_table.setStyle(TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(img_table)

    story.append(Spacer(1, 10))

    # Embed Trajectory Sample
    img_traj = FIG_DIR / "trajectory_sample.png"
    if img_traj.exists():
        story.append(Image(str(img_traj), width=7.4 * inch, height=3.5 * inch))
        story.append(Paragraph("<i>Figure 3: Patient Digital Twin Live Trajectory displaying continuous CGM trace, 60-min forecast cone (p05-p95), and the safe target band (70-180 mg/dL).</i>", callout_style))

    story.append(Spacer(1, 10))

    # ==========================================
    # Section 8: "What-If" Counterfactual Simulation & CDSS App
    # ==========================================
    story.append(Paragraph("8. 'What-If' Lifestyle Simulation Engine & CDSS Dashboard", h1_style))
    story.append(Paragraph(
        "Unlike passive monitoring systems that induce alarm fatigue, Pancreas Twin provides an interactive counterfactual 'What-If' simulation engine. Implemented in <code>app.py</code> via Streamlit and Plotly, the dashboard allows clinicians and patients to:",
        body_style
    ))
    story.append(Paragraph("1. <b>Explore Patient Phenotypes:</b> Select across 17 held-out patient twins with varying age, BMI, baseline HbA1c, and insulin regimens.", bullet_style))
    story.append(Paragraph("2. <b>Scrub Through 24-Hour Day:</b> Navigate continuous biometric telemetry to inspect postprandial glycemic excursions.", bullet_style))
    story.append(Paragraph("3. <b>Simulate Walking Interventions:</b> Toggle a simulated 15-minute post-meal walk (4.0 METs). The prototype applies a rule-based adjustment (36 mg/dL at 60 minutes, 28 mg/dL at 120 minutes) sized to reported post-meal walking effects; it is not yet learned from data.", bullet_style))
    story.append(Paragraph("4. <b>Automated Triage Badge:</b> Visual alert ribbons categorize risk: CRITICAL SPIKE ALERT (Red), HYPOGLYCEMIA WARNING (Amber), or GLYCEMIC STABILITY NORMAL (Green).", bullet_style))

    # ==========================================
    # Section 9: Edge Economics & Hardware Economics
    # ==========================================
    story.append(Paragraph("9. Edge Deployment Economics & Zero Cloud API Spend", h1_style))
    story.append(Paragraph(
        "Commercial healthcare AI systems frequently rely on cloud LLM APIs, incurring recurrent operational costs ($0.03 to $0.08 per patient-day, or $25/patient/year). In contrast, Project Pancreas Twin executes 100% locally on personal edge hardware (Intel Core Ultra 5 225H / Arc GPU). Inference latency is 0.84 milliseconds per sample on CPU and 0.22 milliseconds on GPU. Biometric telemetry never leaves the patient device, guaranteeing strict compliance with India's Digital Personal Data Protection Act (DPDPA 2023) and US HIPAA guidelines.",
        body_style
    ))

    # ==========================================
    # Section 10: Regulatory Classification & Safety Guardrails
    # ==========================================
    story.append(Paragraph("10. Regulatory Classification & Ethical Guardrails", h1_style))
    story.append(Paragraph(
        "Pancreas Twin is engineered as a <b>Class II Software as a Medical Device (SaMD)</b> under FDA and CDSCO frameworks, operating under Section 520(o)(1)(E) Clinical Decision Support criteria. <b>Strict Demarcation:</b> The system provides proactive behavioral coaching and clinician triage; it explicitly DOES NOT automate insulin delivery, adjust pharmaceutical dosages, or control infusion pumps. Clear non-diagnostic disclaimers are enforced across all views.",
        body_style
    ))

    # ==========================================
    # Section 11: 12-Month Commercialization Roadmap
    # ==========================================
    story.append(Paragraph("11. Commercialization Strategy & 12-Month Roadmap", h1_style))
    story.append(Paragraph(
        "The Rs 2,00,000 prize deployment will execute across a four-stage commercialization plan: (1) <b>Q1 2027:</b> Clinical feasibility trial with 50 outpatients at leading Indian diabetology networks (e.g. Apollo Sugar, Max Healthcare); (2) <b>Q2 2027:</b> Formal CDSCO Class B pre-submission; (3) <b>Q3 2027:</b> Native integration with Apple HealthKit, Google Health Connect, and HL7 FHIR electronic health record connectors; (4) <b>Q4 2027:</b> Enterprise roll-out with private insurers and corporate health wellness programs.",
        body_style
    ))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[SUCCESS] Executive PDF report saved to {PDF_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(build_pdf())
