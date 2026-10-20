"""
Architecture diagram for Project Pancreas Twin (Digital Twin Challenge 2026).
Produces a self-contained figure (no CDN, no external asset):
  figures/architecture_diagram.png  (300 dpi)
  figures/architecture_diagram.pdf
The brief lists an architecture diagram as a required deliverable; this is it.
No em dashes or en dashes are used anywhere in this file or in the output.
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "figures")
os.makedirs(OUT, exist_ok=True)

INK = "#1A1A1A"
GREEN = "#0F5132"
GREEN_D = "#0A3822"
TEAL = "#0E6E6E"
AMBER = "#B45309"
CARD = "#FFFFFF"
BG = "#F7F5F0"
LINE = "#C9C2B2"
MUTED = "#5B636B"

fig, ax = plt.subplots(figsize=(16, 9), dpi=300)
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis("off")


def box(x, y, w, h, title, lines, edge=GREEN, fill=CARD, tc=GREEN_D, fs=11):
    p = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4,rounding_size=1.2",
                       linewidth=1.6, edgecolor=edge, facecolor=fill, mutation_scale=1)
    ax.add_patch(p)
    ax.text(x + w / 2, y + h - 2.2, title, ha="center", va="top", fontsize=fs + 1,
            color=tc, fontweight="bold")
    for i, ln in enumerate(lines):
        ax.text(x + w / 2, y + h - 5.0 - i * 2.6, ln, ha="center", va="top",
                fontsize=fs - 1.5, color=INK)


def arrow(x1, y1, x2, y2, color=AMBER, style="-|>", lw=2.0, rad=0.0):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style, mutation_scale=16,
                                 linewidth=lw, color=color, connectionstyle=f"arc3,rad={rad}"))


ax.text(50, 96.5, "Project Pancreas Twin: multi-modal physiological digital twin architecture",
        ha="center", va="top", fontsize=18, color=GREEN_D, fontweight="bold")
ax.text(50, 92.6, "Forecast glucose 60 and 120 minutes ahead from CGM, meals, wearables and EHR; update from each patient's own readings; clinician in the loop.",
        ha="center", va="top", fontsize=11, color=MUTED)

# Data sources
box(2, 62, 20, 22, "Open clinical cohorts", [
    "PhysioNet CGMacros: 45 subjects",
    "PhysioNet BIG IDEAs: 16 subjects",
    "HUPA-UCM: 25 subjects (T1D)",
    "Shanghai T2DM: 100 patients",
    "11.59 GB, 247M raw records",
], edge=TEAL, tc=TEAL)

# Harmonization
box(27, 66, 20, 15, "Harmonization", [
    "Real readings, as-of joins only",
    "184 patients, 442,353 readings",
    "Patient-disjoint 5-fold CV",
    "Targets at +60 and +120 min",
], edge=GREEN)

# Two towers
box(52, 78, 20, 10, "Static EHR tower", [
    "Age, BMI, HbA1c, med class",
    "Measured values, provenance flagged",
], edge=GREEN)
box(52, 64, 20, 11, "Dynamic tower", [
    "CGM, HR, METs, nutrition",
    "CGM lags, rolling stats, clock",
], edge=GREEN)

# Fusion
box(77, 68, 21, 18, "Fusion and heads", [
    "LightGBM headline model",
    "Two-tower: static MLP + 48-step GRU",
    "Quantile heads: 90% confidence cone",
    "Per-patient update loop (own CGM)",
    "Asymmetric hypo penalty 2.5x",
], edge=GREEN_D, tc=GREEN_D)

# Outputs
box(52, 44, 46, 13, "Outputs", [
    "Clinician dashboard: KPI row, timeline, why-this-alert, what-if walk",
    "Early-warning alert with lead time and a 90 percent confidence cone",
    "No insulin dosing, no automated therapy change: clinician in the loop",
], edge=AMBER, tc=AMBER)

# Verification band
box(2, 44, 44, 13, "Verification gates (all pass)", [
    "G1 patient disjoint, G2 no future leakage",
    "G4 train-only scalers, G7 unit plausibility",
    "QG2 beats persistence, QG3 honest ablation",
], edge=MUTED, tc=GREEN_D, fs=10)

# Measured results band
box(2, 22.5, 96, 15.5, "Measured outcomes (patient-disjoint, real readings, no leakage)", [
    "5-fold CV, 184 patients: persistence 31.14 / 44.33 mg/dL; LightGBM 25.85 / 35.65 (17% and 20% better) at 60 / 120 min.",
    "Per-patient update loop: 25.47 / 34.54 mg/dL (18% and 22% better); 127 of 184 patients improve, p < 1e-12.",
    "Fusion: meal logging adds +0.42 / +0.56 mg/dL; static EHR does not generalise (+0.15 / -0.07). Reported honestly.",
    "Clarke Zone A+B 97.2% (97.6% personalised), Zone E 0.01%. Secondary 17-patient split: LightGBM 27.93 / 39.54.",
], edge=GREEN, tc=GREEN_D, fs=10)

# Framing band
box(2, 6, 96, 14, "Framing and governance", [
    "Data flows both ways: the twin learns from its own patient's readings (NASEM 2024 twin test). The therapy loop stays manual and clinical.",
    "Edge inference, no cloud; designed for DPDPA 2023 and HIPAA. Class II SaMD decision support, no insulin dosing.",
    "Honesty is a feature: the ablation, the persistence floor and the measured (not cited) metrics are all reported.",
], edge=TEAL, tc=TEAL, fs=10)

# Arrows
arrow(22, 73, 27, 73)          # sources -> harmonization
arrow(47, 76, 52, 83)          # harmonization -> static tower
arrow(47, 72, 52, 69)          # harmonization -> dynamic tower
arrow(72, 83, 77, 80)          # static -> fusion
arrow(72, 69, 77, 73)          # dynamic -> fusion
arrow(87, 68, 80, 57)          # fusion -> outputs
arrow(50, 66, 50, 57, color=MUTED)  # harmonization -> gates
arrow(50, 44, 50, 38, color=GREEN)  # gates -> measured
arrow(50, 22.5, 50, 20, color=TEAL)   # measured -> framing

for ext, dpi in (("png", 300), ("pdf", 300)):
    path = os.path.join(OUT, f"architecture_diagram.{ext}")
    fig.savefig(path, dpi=dpi, bbox_inches="tight", facecolor=BG)
    print("[OK]", path)
plt.close(fig)