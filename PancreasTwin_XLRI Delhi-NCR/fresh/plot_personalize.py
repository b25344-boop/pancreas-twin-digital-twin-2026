"""Figure for the closed-loop personalisation result (fresh/personalize_results.json)."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path("fresh")
R = json.loads((HERE / "personalize_results.json").read_text())
NAMES = {"big_ideas": "BIG IDEAs\n(prediabetes)", "cgmacros": "CGMacros\n(mixed)", "hupa_ucm": "HUPA-UCM\n(T1D)",
         "shanghai_t2dm": "Shanghai\n(T2DM)", "all": "All 184\npatients"}
NAVY, TEAL = "#0F2043", "#00A8CC"

fig, axes = plt.subplots(1, 2, figsize=(12, 4.6), dpi=200)
for ax, H in zip(axes, ("60", "120")):
    h = R["horizons"][H]
    keys = list(h["by_cohort"]) + ["all"]
    pop = [h["by_cohort"][k]["population"] for k in keys[:-1]] + [h["population"]["rmse"]]
    per = [h["by_cohort"][k]["personalised"] for k in keys[:-1]] + [h["personalised"]["rmse"]]
    x = np.arange(len(keys))
    ax.bar(x - 0.2, pop, 0.4, color="#B8C4D6", label="Population model")
    ax.bar(x + 0.2, per, 0.4, color=TEAL, label="Personalised twin (learns from own CGM)")
    for xi, a, b in zip(x, pop, per):
        ax.text(xi + 0.2, b + 0.4, f"-{a - b:.1f}", ha="center", fontsize=8.5, color=NAVY, fontweight="bold")
    pp = h["per_patient"]
    ax.set_title(f"{H}-minute horizon: {pp['improved']} of {pp['n']} patients improve "
                 f"(Wilcoxon p = {pp['wilcoxon_p']:.0e})", fontsize=10.5, color=NAVY)
    ax.set_xticks(x)
    ax.set_xticklabels([NAMES[k] for k in keys], fontsize=8.5)
    ax.set_ylabel("RMSE (mg/dL), lower is better", fontsize=9)
    ax.set_ylim(0, max(pop) * 1.18)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=0.25)
axes[0].legend(fontsize=8.5, loc="upper left", frameon=False)
fig.suptitle("Closing the loop: the twin updates itself from each patient's own readings (5-fold CV, 184 patients)",
             fontsize=11.5, color=NAVY, fontweight="bold")
fig.tight_layout()
fig.savefig(HERE / "personalize.png", bbox_inches="tight")
print("saved", HERE / "personalize.png")
