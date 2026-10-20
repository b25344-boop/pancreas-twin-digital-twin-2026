"""
Generate Consulting-Grade 16:9 Presentation for Digital Twin Challenge 2026.
Output: Project_Pancreas_Twin_Deck.pptx
"""

import os
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

OUTPUT_FILE = Path("Project_Pancreas_Twin_Deck.pptx")
FIG_DIR = Path("figures")
FRESH_DIR = Path("fresh")

# Brand Palettes
C_NAVY = RGBColor(15, 32, 67)       # #0F2043
C_TEAL = RGBColor(0, 168, 204)      # #00A8CC
C_WHITE = RGBColor(255, 255, 255)
C_DARK = RGBColor(33, 37, 41)       # #212529
C_MUTED = RGBColor(108, 117, 125)   # #6C757D
C_BG_LIGHT = RGBColor(246, 248, 251)
C_BORDER = RGBColor(222, 226, 230)
C_GREEN = RGBColor(46, 125, 50)     # #2E7D32
C_RED = RGBColor(198, 40, 40)       # #C62828

def create_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    def add_header(slide, title_text, category="HAPPIEST HEALTH DIGITAL TWIN CHALLENGE 2026"):
        # Header banner
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.3))
        tf_cat = cat_box.text_frame
        tf_cat.word_wrap = True
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category.upper()
        p_cat.font.size = Pt(10)
        p_cat.font.bold = True
        p_cat.font.color.rgb = C_TEAL

        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.65), Inches(11.7), Inches(0.6))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.size = Pt(22)
        p_title.font.bold = True
        p_title.font.color.rgb = C_NAVY

    def add_card(slide, left, top, width, height, bg_color=C_BG_LIGHT, border_color=C_BORDER):
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        shape.fill.solid()
        shape.fill.fore_color.rgb = bg_color
        shape.line.color.rgb = border_color
        shape.line.width = Pt(1)
        return shape

    # ==========================================
    # SLIDE 1: Title Slide (Dark Navy Theme)
    # ==========================================
    s1 = prs.slides.add_slide(blank_layout)
    bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = C_NAVY
    bg1.line.fill.background()

    t_box = s1.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(11.3), Inches(3.5))
    tf1 = t_box.text_frame
    tf1.word_wrap = True
    
    p0 = tf1.paragraphs[0]
    p0.text = "HAPPIEST HEALTH • DIGITAL TWIN CHALLENGE 2026"
    p0.font.size = Pt(13)
    p0.font.bold = True
    p0.font.color.rgb = C_TEAL
    p0.space_after = Pt(14)

    p1 = tf1.add_paragraph()
    p1.text = "Project Pancreas Twin"
    p1.font.size = Pt(40)
    p1.font.bold = True
    p1.font.color.rgb = C_WHITE
    p1.space_after = Pt(8)

    p2 = tf1.add_paragraph()
    p2.text = "Multi-Modal Physiological Digital Twin for 60-Minute Glycemic Excursion Forecasting"
    p2.font.size = Pt(20)
    p2.font.color.rgb = RGBColor(200, 225, 245)
    p2.space_after = Pt(24)

    p3 = tf1.add_paragraph()
    p3.text = "Fusing CGM History, Meal Logs, Wearable Telemetry and EHR Phenotypes to Pre-empt Acute Diabetic Crises"
    p3.font.size = Pt(14)
    p3.font.color.rgb = RGBColor(170, 190, 210)

    auth_box = s1.shapes.add_textbox(Inches(1.0), Inches(5.8), Inches(11.3), Inches(1.0))
    tf_a = auth_box.text_frame
    pa = tf_a.paragraphs[0]
    pa.text = "Team PancreasTwin | Team leader: Akhilesh K S | XLRI - Xavier School of Management, Delhi-NCR | Category: Healthcare AI & Metabolic Digital Twins"
    pa.font.size = Pt(12)
    pa.font.color.rgb = RGBColor(150, 175, 200)

    # ==========================================
    # SLIDE 2: Clinical Burden
    # ==========================================
    s2 = prs.slides.add_slide(blank_layout)
    add_header(s2, "The Clinical Burden: The Hidden Hazard of Acute Glycemic Excursions")
    
    metrics = [
        ("101M", "Adults with Diabetes in India", "ICMR-INDIAB (Lancet Diabetes Endocrinol, 2023). A 90-day HbA1c average hides the daily spikes linked to microvascular damage."),
        ("136M", "Adults with Prediabetes", "Same ICMR-INDIAB survey. Lows below 70 mg/dL cause confusion, falls and emergency visits; highs build silent damage."),
        ("Reactive", "Current CGM Failure Mode", "Existing CGMs sound alarms after glucose has already spiked (>180 mg/dL), when pharmaceutical or lifestyle intervention is too late.")
    ]
    for i, (num, title, desc) in enumerate(metrics):
        left = Inches(0.8 + i * 4.0)
        add_card(s2, left, Inches(1.5), Inches(3.7), Inches(5.2))
        
        tb = s2.shapes.add_textbox(left + Inches(0.2), Inches(1.8), Inches(3.3), Inches(4.5))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = num
        p.font.size = Pt(36)
        p.font.bold = True
        p.font.color.rgb = C_NAVY
        p.space_after = Pt(8)

        p = tf.add_paragraph()
        p.text = title
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = C_TEAL
        p.space_after = Pt(14)

        p = tf.add_paragraph()
        p.text = desc
        p.font.size = Pt(13)
        p.font.color.rgb = C_DARK

    # ==========================================
    # SLIDE 3: The 60-Minute Horizon
    # ==========================================
    s3 = prs.slides.add_slide(blank_layout)
    add_header(s3, "Clinical Timing: Why the 60-Minute Horizon Unlocks Action")

    cards_h = [
        ("15 to 30 Min (Too Short)", C_RED, "• Rapid-acting insulin takes 15-20 min to begin onset.\n• Digestion is already in full swing.\n• Muscle contraction cannot blunt an existing peak.\n• Result: Patient can only panic and watch the spike."),
        ("60 Min: The Actionable Window", C_GREEN, "• Non-pharmacological window: A 15-min post-meal walk stimulates GLUT4 translocation, blunting spikes by roughly 35-40 mg/dL.\n• Hypoglycemia rescue: 15g carbs absorbs in time to prevent crash.\n• Maximum predictive signal before stochastic behavioral drift."),
        ("120+ Min (High Stochasticity)", C_NAVY, "• Behavioral uncertainty multiplies over 2 hours.\n• Unannounced snacks, spontaneous movement, and stress spikes introduce variance.\n• Multi-horizon head tracks 2-hour trajectory for strategic planning.")
    ]
    for i, (title, color, text) in enumerate(cards_h):
        left = Inches(0.8 + i * 4.0)
        add_card(s3, left, Inches(1.5), Inches(3.7), Inches(5.2))
        
        tb = s3.shapes.add_textbox(left + Inches(0.2), Inches(1.7), Inches(3.3), Inches(4.7))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = color
        p.space_after = Pt(14)

        p = tf.add_paragraph()
        p.text = text
        p.font.size = Pt(13)
        p.font.color.rgb = C_DARK

    # ==========================================
    # SLIDE 4: Data Pipeline
    # ==========================================
    s4 = prs.slides.add_slide(blank_layout)
    add_header(s4, "Data Ingestion & Harmonization: 247M Records Curated Across 17 Cohorts")

    # Left card: Dataset summary
    add_card(s4, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.2))
    tb_data = s4.shapes.add_textbox(Inches(1.0), Inches(1.7), Inches(5.2), Inches(4.8))
    tf_d = tb_data.text_frame
    tf_d.word_wrap = True
    
    pd0 = tf_d.paragraphs[0]
    pd0.text = "Exhaustive Multi-Cohort Ingestion"
    pd0.font.size = Pt(18)
    pd0.font.bold = True
    pd0.font.color.rgb = C_NAVY
    pd0.space_after = Pt(10)

    bullets = [
        "Total Ingested: 11.59 GB across 17 open clinical cohorts (247,427,617 records).",
        "HUPA-UCM: 26.1M records (Libre 2 CGM, steps, heart rate, sleep).",
        "D1NAMO: 206.2M records (Zephyr ECG, accelerometer, meals).",
        "Synthea T2D: 92k longitudinal synthetic EHR records across 500 patients.",
        "Tier-2 PhysioNet Open Access: CGMacros (45 subjects) & BIG IDEAs (16 subjects) downloaded and parsed with 0 DUA friction.",
        "Data Provenance: 65 subjects carry full measured clinical labs (CGMacros bio.csv + Shanghai); 16 subjects carry measured HbA1c; 25 subjects utilize baseline priors (marked via static_ehr_source).",
        "Independent rebuild: all 109 Shanghai files, real sensor readings only: 442,353 readings from 184 patients (T1D, T2DM, prediabetes, healthy)."
    ]
    for b in bullets:
        p = tf_d.add_paragraph()
        p.text = "• " + b
        p.font.size = Pt(11)
        p.font.color.rgb = C_DARK
        p.space_after = Pt(5)

    # Right card: Harmonization Specs
    add_card(s4, Inches(6.8), Inches(1.5), Inches(5.7), Inches(5.2))
    tb_h = s4.shapes.add_textbox(Inches(7.0), Inches(1.7), Inches(5.3), Inches(4.8))
    tf_h = tb_h.text_frame
    tf_h.word_wrap = True

    ph0 = tf_h.paragraphs[0]
    ph0.text = "Harmonization Pipeline (harmonize_5min.py)"
    ph0.font.size = Pt(18)
    ph0.font.bold = True
    ph0.font.color.rgb = C_TEAL
    ph0.space_after = Pt(10)

    h_bullets = [
        "Standardized Epoch: Uniform 5-minute sampling grid matching Libre/Dexcom hardware.",
        "Total Harmonized Cohort: 534,175 synchronized epochs across 106 human subjects.",
        "Strict Patient-Disjoint Partitioning (Gate G1): Zero patient overlap across splits.",
        "  - Train Split: 402,662 epochs (74 subjects)",
        "  - Validation Split: 80,952 epochs (15 subjects)",
        "  - Held-Out Test Split: 50,561 epochs (17 subjects)",
        "Engineered Features: Dynamic velocity (dG/dt), acceleration, rolling 30m mean, rolling 60m std, circadian time, heart rate, METs, and static EHR vectors.",
        "Multi-Horizon Targets: Dual-task evaluation at 60 mins and 120 mins (2 hours).",
        "Headline evaluation: patient-disjoint 5-fold CV on 184 patients (every patient tested once)."
    ]
    for b in h_bullets:
        p = tf_h.add_paragraph()
        p.text = ("• " if not b.startswith("  -") else "") + b
        p.font.size = Pt(11)
        p.font.color.rgb = C_DARK
        p.space_after = Pt(5)

    # ==========================================
    # SLIDE 5: Architecture
    # ==========================================
    s5 = prs.slides.add_slide(blank_layout)
    add_header(s5, "Multi-Modal Architecture: Two-Tower Digital Twin")

    # Tower 1
    add_card(s5, Inches(0.8), Inches(1.5), Inches(3.7), Inches(5.2))
    tb_t1 = s5.shapes.add_textbox(Inches(1.0), Inches(1.7), Inches(3.3), Inches(4.7))
    tf_t1 = tb_t1.text_frame
    tf_t1.word_wrap = True
    p = tf_t1.paragraphs[0]
    p.text = "Tower 1: Static EHR MLP"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_NAVY
    p.space_after = Pt(10)
    for b in ["Encodes baseline physiology:", "• Patient Age & BMI", "• Baseline Glycated HbA1c", "• Metformin Prescription Status", "• Insulin Regimen Classification", "\nEmbeds static metabolic clearance and insulin resistance profiles."]:
        p = tf_t1.add_paragraph()
        p.text = b
        p.font.size = Pt(12)
        p.font.color.rgb = C_DARK

    # Tower 2
    add_card(s5, Inches(4.8), Inches(1.5), Inches(3.7), Inches(5.2))
    tb_t2 = s5.shapes.add_textbox(Inches(5.0), Inches(1.7), Inches(3.3), Inches(4.7))
    tf_t2 = tb_t2.text_frame
    tf_t2.word_wrap = True
    p = tf_t2.paragraphs[0]
    p.text = "Tower 2: Dynamic GRU"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_TEAL
    p.space_after = Pt(10)
    for b in ["Consumes real-time wearable streams:", "• 48 historical 5-min steps (4-hr lookback)", "• Continuous glucose, velocity & acceleration", "• Continuous heart rate (Zephyr/Fitbit)", "• Physical exertion (METs activity)", "• Diurnal circadian sine/cosine clock", "\n2-Layer Recurrent GRU captures trajectory momentum and digestion lags."]:
        p = tf_t2.add_paragraph()
        p.text = b
        p.font.size = Pt(12)
        p.font.color.rgb = C_DARK

    # Fusion Head
    add_card(s5, Inches(8.8), Inches(1.5), Inches(3.7), Inches(5.2))
    tb_f = s5.shapes.add_textbox(Inches(9.0), Inches(1.7), Inches(3.3), Inches(4.7))
    tf_f = tb_f.text_frame
    tf_f.word_wrap = True
    p = tf_f.paragraphs[0]
    p.text = "Late Fusion & Multi-Task"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_GREEN
    p.space_after = Pt(10)
    for b in ["Feature Concatenation & Multi-Heads:", "• Fused Multi-Modal Embedding (32-d)", "• 60m Quantile Head: p05, p50, p95 (90% cone)", "• 120m Horizon Head: 2-hour trajectory", "• Early Warning Head: Acute spike probability", "\nPinball loss + Asymmetric Hypo penalty prevents dangerous crashes."]:
        p = tf_f.add_paragraph()
        p.text = b
        p.font.size = Pt(12)
        p.font.color.rgb = C_DARK

    # ==========================================
    # SLIDE 6: Headline Benchmark (fresh 5-fold patient-disjoint CV)
    # ==========================================
    s6 = prs.slides.add_slide(blank_layout)
    add_header(s6, "Headline Result: 17% Better at 60 Min and 20% Better at 120 Min than Persistence")

    fresh_fig = FRESH_DIR / "fresh_benchmark.png"
    if fresh_fig.exists():
        s6.shapes.add_picture(str(fresh_fig), Inches(0.8), Inches(1.4), width=Inches(11.7))

    head_cards = [
        ("60-Minute Horizon", C_NAVY, [
            "LightGBM + carbs + EHR: 25.85 +/- 1.03 mg/dL",
            "Persistence floor: 31.14 +/- 1.66 mg/dL",
            "17% lower RMSE | Clarke A+B 97.2%, Zone E 0.01%"]),
        ("120-Minute Horizon", C_TEAL, [
            "LightGBM + carbs + EHR: 35.65 +/- 2.13 mg/dL",
            "Persistence floor: 44.33 +/- 2.77 mg/dL",
            "20% lower RMSE at the 2-hour horizon"]),
        ("How It Was Measured", C_GREEN, [
            "184 patients, 442,353 real readings, no interpolated targets",
            "Patient-disjoint 5-fold CV: every patient tested once",
            "Mean +/- std across the 5 folds"]),
    ]
    for i, (title, color, lines) in enumerate(head_cards):
        left = Inches(0.8 + i * 3.95)
        add_card(s6, left, Inches(5.25), Inches(3.75), Inches(1.75))
        tb = s6.shapes.add_textbox(left + Inches(0.15), Inches(5.3), Inches(3.45), Inches(1.65))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = color
        p.space_after = Pt(4)
        for line in lines:
            p = tf.add_paragraph()
            p.text = "• " + line
            p.font.size = Pt(10.5)
            p.font.color.rgb = C_DARK
            p.space_after = Pt(2)

    # ==========================================
    # SLIDE 7: Secondary Evidence (17-patient held-out team split)
    # ==========================================
    s7 = prs.slides.add_slide(blank_layout)
    add_header(s7, "Secondary Evidence: The Same Result Holds on a 17-Patient Held-Out Split")

    comp_fig = FIG_DIR / "model_comparison.png"
    if comp_fig.exists():
        s7.shapes.add_picture(str(comp_fig), Inches(0.8), Inches(1.5), width=Inches(6.8))

    add_card(s7, Inches(7.8), Inches(1.5), Inches(4.7), Inches(5.2))
    tb_res = s7.shapes.add_textbox(Inches(8.0), Inches(1.7), Inches(4.3), Inches(4.8))
    tf_res = tb_res.text_frame
    tf_res.word_wrap = True

    p = tf_res.paragraphs[0]
    p.text = "Held-Out Test Split (n=17 patients, 50k rows)"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = C_NAVY
    p.space_after = Pt(8)

    rows_txt = [
        "60-Min Horizon (original team pipeline):",
        "  • Persistence floor: 32.66 mg/dL",
        "  • Two-Tower GRU: 29.71 | Ridge: 29.28",
        "  • LightGBM: 27.93 mg/dL (MAE 19.13, Clarke A+B 97.13%)",
        "120-Min Horizon (original team pipeline):",
        "  • Persistence floor: 48.07 mg/dL",
        "  • Two-Tower GRU: 39.93 | LightGBM: 39.54 mg/dL",
        "Fresh rebuild scored on the same 17 patients:",
        "  • 26.33 mg/dL at 60 min and 36.05 mg/dL at 120 min",
        "  • Persistence floors agree within 0.2 to 1.4 mg/dL, so both pipelines measure the same thing",
        "Why secondary: one 17-patient split is a small sample. The 5-fold result on 184 patients is the primary claim."
    ]
    for r in rows_txt:
        p = tf_res.add_paragraph()
        p.text = r
        p.font.size = Pt(10.5)
        p.font.color.rgb = C_DARK
        p.space_after = Pt(2)

    # ==========================================
    # SLIDE 8: Multi-Modal Fusion (honest)
    # ==========================================
    s8f = prs.slides.add_slide(blank_layout)
    add_header(s8f, "Multi-Modal Fusion: Meal Logging Matters More than Static EHR")

    ab_fig = FIG_DIR / "fusion_ablation.png"
    if ab_fig.exists():
        s8f.shapes.add_picture(str(ab_fig), Inches(0.8), Inches(1.5), width=Inches(6.8))

    add_card(s8f, Inches(7.8), Inches(1.5), Inches(4.7), Inches(5.2))
    tb_ab = s8f.shapes.add_textbox(Inches(8.0), Inches(1.7), Inches(4.3), Inches(4.8))
    tf_ab = tb_ab.text_frame
    tf_ab.word_wrap = True

    p = tf_ab.paragraphs[0]
    p.text = "What Each Signal Adds (RMSE gain, mg/dL)"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = C_NAVY
    p.space_after = Pt(8)

    ab_rows = [
        "On the 17-patient split (chart, left):",
        "  • Static EHR: +0.74 at 60 min (p = 0.0056) and +1.33 at 120 min (p = 0.0348)",
        "Across 153 patients in 5-fold CV:",
        "  • Static EHR: +0.15 at 60 min (p = 0.046, borderline) and -0.07 at 120 min (not significant)",
        "  • Meal and carb logging: +0.42 at 60 min and +0.56 at 120 min",
        "Honest reading:",
        "  • The static EHR gain was real for those 17 people but does not generalise.",
        "  • Meal logging is the bigger multimodal driver.",
        "Product message: the twin gets more accurate when the patient logs meals, so the app should make meal logging effortless."
    ]
    for r in ab_rows:
        p = tf_ab.add_paragraph()
        p.text = r
        p.font.size = Pt(10.5)
        p.font.color.rgb = C_DARK
        p.space_after = Pt(3)

    # ==========================================
    # SLIDE 9: Closing the Loop (per-patient twin update, fresh/personalize.py)
    # ==========================================
    s_pz = prs.slides.add_slide(blank_layout)
    add_header(s_pz, "Closing the Loop: The Twin Learns Each Patient from Their Own Readings")

    pz_fig = FRESH_DIR / "personalize.png"
    if pz_fig.exists():
        s_pz.shapes.add_picture(str(pz_fig), Inches(1.57), Inches(1.35), width=Inches(10.2))

    pz_cards = [
        ("What Changes", C_NAVY, [
            "Twin compares its past forecasts with readings that later arrived",
            "Recent error (24 h, shrunk) corrects the next forecast",
            "No future data used; runs on the phone, no retraining"]),
        ("Result (5-fold CV, 184 patients)", C_TEAL, [
            "60 min: 25.85 to 25.47 mg/dL (18% better than persistence)",
            "120 min: 35.62 to 34.54 mg/dL (22% better than persistence)",
            "~70% of patients improve, p < 1e-12; Clarke A+B up at both horizons"]),
        ("Why It Matters", C_GREEN, [
            "Shadow to twin: data flows back from the patient (NASEM definition)",
            "Gain grows with memory: 72 h beats 24 h beats 6 h",
            "Settings fixed before testing; full grid in PERSONALIZATION.md"]),
    ]
    for i, (title, color, lines) in enumerate(pz_cards):
        left = Inches(0.8 + i * 3.95)
        add_card(s_pz, left, Inches(5.45), Inches(3.75), Inches(1.75))
        tb = s_pz.shapes.add_textbox(left + Inches(0.15), Inches(5.5), Inches(3.45), Inches(1.65))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = color
        p.space_after = Pt(4)
        for line in lines:
            p = tf.add_paragraph()
            p.text = "• " + line
            p.font.size = Pt(10)
            p.font.color.rgb = C_DARK
            p.space_after = Pt(2)

    # ==========================================
    # SLIDE 10: Clarke Error Grid Analysis
    # ==========================================
    s8 = prs.slides.add_slide(blank_layout)
    add_header(s8, "Clinical Safety: 97.2% Clarke Zone A+B in 5-Fold CV (97.6% on Held-Out Split)")

    # Embed Figure clarke_error_grid.png
    clarke_fig = FIG_DIR / "clarke_error_grid.png"
    if clarke_fig.exists():
        s8.shapes.add_picture(str(clarke_fig), Inches(0.8), Inches(1.5), width=Inches(5.5))

    # Right side: Clinical safety discussion
    add_card(s8, Inches(6.6), Inches(1.5), Inches(5.9), Inches(5.2))
    tb_c = s8.shapes.add_textbox(Inches(6.8), Inches(1.7), Inches(5.5), Inches(4.8))
    tf_c = tb_c.text_frame
    tf_c.word_wrap = True

    p = tf_c.paragraphs[0]
    p.text = "Clarke Error Grid Safety Validation"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_NAVY
    p.space_after = Pt(10)

    clarke_notes = [
        "Primary (5-fold CV, 184 patients, 60 min): Zone A+B 97.2%, Zone E 0.01% for LightGBM + carbs + EHR.",
        "Chart (17-patient held-out split, Two-Tower GRU, n=49,286): Zone A (Clinically Accurate): 76.5% of predictions fall within 20% of reference glucose or both <=70 mg/dL.",
        "Zone B (Benign / Acceptable): 21.1% of predictions deviate but lead to benign clinical decisions.",
        "Clinically Safe Total (Zone A + B): 97.62% on the held-out split.",
        "Near-Zero Catastrophic Errors (Zone E = 0.04%): Negligible occurrence of opposite treatment errors across 49,000+ test samples.",
        "90% Quantile Confidence Cone: 91.8% empirical test coverage achieved via Pinball Loss across quantiles tau in [0.05, 0.50, 0.95].",
        "Clinical Debouncing (CDS): Eliminates clustered alarms, reducing false alert rate by 80.7% (from 177.37/100h down to 34.23/100h) with 40-50 min median lead time."
    ]
    for n in clarke_notes:
        p = tf_c.add_paragraph()
        p.text = "• " + n
        p.font.size = Pt(10.5)
        p.font.color.rgb = C_DARK
        p.space_after = Pt(6)

    # ==========================================
    # SLIDE 10: Counterfactual Simulation & Trajectory
    # ==========================================
    s9 = prs.slides.add_slide(blank_layout)
    add_header(s9, "Counterfactual Simulation: Turning Prediction into Actionable Prescription")

    # Embed trajectory figure
    traj_fig = FIG_DIR / "trajectory_sample.png"
    if traj_fig.exists():
        s9.shapes.add_picture(str(traj_fig), Inches(0.8), Inches(1.5), width=Inches(6.8))

    # Right side: What-If Simulator Explanation
    add_card(s9, Inches(7.8), Inches(1.5), Inches(4.7), Inches(5.2))
    tb_w = s9.shapes.add_textbox(Inches(8.0), Inches(1.7), Inches(4.3), Inches(4.8))
    tf_w = tb_w.text_frame
    tf_w.word_wrap = True

    p = tf_w.paragraphs[0]
    p.text = "Physiological 'What-If' Engine"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_TEAL
    p.space_after = Pt(10)

    w_notes = [
        "Beyond Passive Alarms: Traditional monitors warn of failure. Pancreas Twin models intervention pathways.",
        "GLUT4 Muscle Translocation: Skeletal muscle contractions stimulate insulin-independent glucose transport.",
        "Simulation: When a spike to 215 mg/dL is predicted, the user simulates a 15-minute post-meal walk (4.0 METs).",
        "Quantified Impact (rule-based prototype): lowers the 60-min forecast by 36 mg/dL, in line with reported post-meal walking effects; learning this effect from data is on the roadmap.",
        "Patient Psychology: Shifting diabetes management from anxiety and guilt to empowered, predictive control."
    ]
    for n in w_notes:
        p = tf_w.add_paragraph()
        p.text = "• " + n
        p.font.size = Pt(12)
        p.font.color.rgb = C_DARK
        p.space_after = Pt(6)

    # ==========================================
    # SLIDE 11: Edge Deployment & Economics
    # ==========================================
    s10 = prs.slides.add_slide(blank_layout)
    add_header(s10, "Edge Hardware & Deployment: Zero Cloud Cost, Complete Privacy")

    edge_cards = [
        ("Sub-Millisecond Inference", C_NAVY, "• 0.84 ms CPU latency on Intel Core Ultra 5.\n• 0.22 ms with Intel Arc GPU acceleration.\n• Model checkpoint is only 199 KB.\n• Easily runs on smartphone or smart watch edge NPU without internet."),
        ("Zero Ongoing Cloud Spend", C_TEAL, "• Competitor architectures route continuous sensor streams to cloud LLMs ($0.05/pt/day = $18/pt/year).\n• Pancreas Twin executes 100% on edge hardware.\n• Zero cloud inference bills; zero recurring API risk."),
        ("Privacy & DPDPA Compliance", C_GREEN, "• Continuous biometric telemetry never leaves the patient device.\n• Designed to support India DPDPA 2023 and US HIPAA compliance (data minimisation, on-device processing).\n• No cloud data breach exposure.")
    ]
    for i, (title, color, text) in enumerate(edge_cards):
        left = Inches(0.8 + i * 4.0)
        add_card(s10, left, Inches(1.5), Inches(3.7), Inches(5.2))
        
        tb = s10.shapes.add_textbox(left + Inches(0.2), Inches(1.7), Inches(3.3), Inches(4.7))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = color
        p.space_after = Pt(14)

        p = tf.add_paragraph()
        p.text = text
        p.font.size = Pt(13)
        p.font.color.rgb = C_DARK

    # ==========================================
    # SLIDE 12: CDSS Streamlit Application
    # ==========================================
    s11 = prs.slides.add_slide(blank_layout)
    add_header(s11, "Clinical Decision Support System: Interactive Web Application")

    add_card(s11, Inches(0.8), Inches(1.5), Inches(11.7), Inches(5.2))
    tb_app = s11.shapes.add_textbox(Inches(1.0), Inches(1.7), Inches(11.3), Inches(4.8))
    tf_app = tb_app.text_frame
    tf_app.word_wrap = True

    p = tf_app.paragraphs[0]
    p.text = "Built & Verified in app.py (Streamlit + Plotly, runs locally)"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_NAVY
    p.space_after = Pt(12)

    features = [
        "1. Dynamic Patient Persona Switcher: Select across held-out patient twins with real clinical phenotypes (Age 42-78, BMI 22-38, Baseline HbA1c 6.5%-10.8%, Insulin & Metformin statuses).",
        "2. Continuous Day Scrubber: Interactive slider to navigate through 24-hour physiological telemetry and inspect postprandial glycemic excursions.",
        "3. Dual-Axis Plotly Biometric Visualizer: High-definition rendering of 4-hour historical lookback, 60-min and 120-min forecast cones, target band (70-180 mg/dL), and METs activity.",
        "4. Automated Triage Badge: Immediate color-coded status banner: CRITICAL SPIKE ALERT (Red), HYPOGLYCEMIA WARNING (Amber), or GLYCEMIC STABILITY NORMAL (Green).",
        "5. Interactive 'What-If' Intervention Toggle: Real-time re-calculation demonstrating how a 15-minute walk suppresses upcoming spikes."
    ]
    for feat in features:
        p = tf_app.add_paragraph()
        p.text = feat
        p.font.size = Pt(13)
        p.font.color.rgb = C_DARK
        p.space_after = Pt(8)

    # ==========================================
    # SLIDE 13: Regulatory & Ethical Guardrails
    # ==========================================
    s12 = prs.slides.add_slide(blank_layout)
    add_header(s12, "Regulatory Strategy & Ethical Boundaries: Safe by Design")

    cards_reg = [
        ("SaMD Classification", C_NAVY, "• Classified as Software as a Medical Device (SaMD) Class II under FDA / CDSCO frameworks.\n• Falls under Section 520(o)(1)(E) Clinical Decision Support (CDS).\n• Intended for physician and patient informational coaching."),
        ("Strict Demarcation", C_RED, "• STRICTLY NO AUTONOMOUS DOSING: Never controls insulin pumps or delivers closed-loop boluses.\n• Exclusively non-pharmacological lifestyle coaching and early warning triage.\n• Clear patient-facing disclaimers on every view."),
        ("Evidence & Auditability", C_GREEN, "• 100% transparent feature importance.\n• No black-box generative hallucinations.\n• Deterministic fallbacks to robust Ridge and ExtraTrees models if telemetry drops.")
    ]
    for i, (title, color, text) in enumerate(cards_reg):
        left = Inches(0.8 + i * 4.0)
        add_card(s12, left, Inches(1.5), Inches(3.7), Inches(5.2))
        
        tb = s12.shapes.add_textbox(left + Inches(0.2), Inches(1.7), Inches(3.3), Inches(4.7))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = color
        p.space_after = Pt(14)

        p = tf.add_paragraph()
        p.text = text
        p.font.size = Pt(13)
        p.font.color.rgb = C_DARK

    # ==========================================
    # SLIDE 14: Business Model & 12-Month Roadmap
    # ==========================================
    s13 = prs.slides.add_slide(blank_layout)
    add_header(s13, "Commercialization & Roadmap: Deploying the Rs 2,00,000 Challenge Vision")

    add_card(s13, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.2))
    tb_b = s13.shapes.add_textbox(Inches(1.0), Inches(1.7), Inches(5.2), Inches(4.8))
    tf_b = tb_b.text_frame
    tf_b.word_wrap = True
    p = tf_b.paragraphs[0]
    p.text = "Commercialization Model (B2B2C)"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_NAVY
    p.space_after = Pt(10)

    biz_pts = [
        "Hospital & Clinic Networks: White-label CDSS integrated into outpatient clinics (Apollo Sugar, Max Healthcare, Fortis).",
        "Corporate Wellness & Insurers: Value-based outcomes contract reducing emergency room admissions for severe hypoglycemia.",
        "HL7 FHIR Interoperability: Native FHIR Observation and DiagnosticReport connectors.",
        "Patient Subscription: Premium freemium tier with custom what-if meal simulation."
    ]
    for b in biz_pts:
        p = tf_b.add_paragraph()
        p.text = "• " + b
        p.font.size = Pt(12)
        p.font.color.rgb = C_DARK
        p.space_after = Pt(6)

    add_card(s13, Inches(6.8), Inches(1.5), Inches(5.7), Inches(5.2))
    tb_r = s13.shapes.add_textbox(Inches(7.0), Inches(1.7), Inches(5.3), Inches(4.8))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True
    p = tf_r.paragraphs[0]
    p.text = "12-Month Implementation Roadmap"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_TEAL
    p.space_after = Pt(10)

    roadmap_pts = [
        "Phase 1 (October 2026): PoC complete: 17% (60 min) and 20% (120 min) better than persistence in 5-fold CV on 184 patients, 18% and 22% with per-patient updating; Streamlit CDSS MVP live.",
        "Phase 2 (Q1 2027): Prospective 50-patient clinical observational trial with continuous Dexcom G7 and Apple Watch feeds.",
        "Phase 3 (Q2 2027): CDSCO Class B medical device pre-submission in India; multi-horizon 120-minute ensemble expansion.",
        "Phase 4 (Q3-Q4 2027): Enterprise pilot launch with Indian Diabetology chains; Apple HealthKit / Google Health Connect native integration."
    ]
    for r in roadmap_pts:
        p = tf_r.add_paragraph()
        p.text = "• " + r
        p.font.size = Pt(12)
        p.font.color.rgb = C_DARK
        p.space_after = Pt(6)

    prs.save(str(OUTPUT_FILE))
    print(f"[SUCCESS] Pitch deck saved to {OUTPUT_FILE}")


def export_pdf():
    """Export the deck to PDF through Microsoft PowerPoint COM (Windows), the same route as the original PDF.
    Skips quietly when PowerPoint or pywin32 is unavailable."""
    try:
        import win32com.client
    except ImportError:
        print("[SKIP] pywin32 not installed; export the PDF from PowerPoint manually.")
        return
    pdf_path = OUTPUT_FILE.with_suffix(".pdf").resolve()
    app = win32com.client.DispatchEx("PowerPoint.Application")
    try:
        pres = app.Presentations.Open(str(OUTPUT_FILE.resolve()), True, False, False)
        pres.SaveAs(str(pdf_path), 32)  # 32 = ppSaveAsPDF
        pres.Close()
        print(f"[SUCCESS] PDF export saved to {pdf_path}")
    finally:
        app.Quit()


if __name__ == "__main__":
    create_deck()
    export_pdf()
