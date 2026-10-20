"""Figure for the fresh 5-fold benchmark: RMSE by model and horizon, with fold std error bars."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path("fresh")
r = json.loads((HERE / "results.json").read_text())
models = [("persistence", "Persistence"), ("ridge", "Ridge"), ("lgb_cgm", "LGBM: CGM"),
          ("lgb_cgm_carb", "LGBM: + carbs"), ("lgb_full", "LGBM: + carbs + EHR")]
colors = ["#9aa0a6", "#7aa6c2", "#2f6f8f", "#1f9e89", "#0b4f6c"]
fig, axes = plt.subplots(1, 3, figsize=(13, 4.2), sharey=False)
for ax, H in zip(axes, ("30", "60", "120")):
    h = r["horizons"][H]
    vals = [h[k]["fold_rmse_mean"] for k, _ in models]
    errs = [h[k]["fold_rmse_std"] for k, _ in models]
    ax.bar(range(len(models)), vals, yerr=errs, color=colors, capsize=4)
    ax.set_xticks(range(len(models)))
    ax.set_xticklabels([n for _, n in models], rotation=30, ha="right", fontsize=8)
    ax.set_title(f"{H}-min horizon (5-fold, {r['n_patients']} patients)", fontsize=10)
    ax.set_ylabel("RMSE mg/dL")
    for i, v in enumerate(vals):
        ax.text(i, v + errs[i] + 0.4, f"{v:.1f}", ha="center", fontsize=8)
fig.suptitle("Fresh benchmark: real sensor readings only, patient-disjoint 5-fold CV", fontsize=11)
fig.tight_layout()
fig.savefig(HERE / "fresh_benchmark.png", dpi=200)
print("saved", HERE / "fresh_benchmark.png")
