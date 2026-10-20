"""
Clarke Error Grid Analysis (EGA) for Clinical CGM Evaluation.
Standard implementation based on Clarke et al. (1987) for blood glucose estimation.
Vectorized implementation across Zones A, B, C, D, and E.
"""

import numpy as np
import pandas as pd

def clarke_error_grid(ref_values, pred_values):
    """
    Computes Clarke Error Grid breakdown for reference (ground truth) and predicted glucose values in mg/dL.
    Returns dictionary with counts and percentages for Zones A, B, C, D, E.
    """
    ref = np.asarray(ref_values, dtype=float)
    pred = np.asarray(pred_values, dtype=float)

    # Filter out NaNs or non-positive values
    mask = (~np.isnan(ref)) & (~np.isnan(pred)) & (ref > 0) & (pred > 0)
    ref = ref[mask]
    pred = pred[mask]

    n_total = len(ref)
    if n_total == 0:
        return {"total": 0, "A": 0.0, "B": 0.0, "C": 0.0, "D": 0.0, "E": 0.0, "A_plus_B": 0.0}

    # Zone counters
    zone_a = 0
    zone_b = 0
    zone_c = 0
    zone_d = 0
    zone_e = 0

    for r, p in zip(ref, pred):
        # Zone A: within 20% or both <= 70
        if (p <= 70.0 and r <= 70.0) or (abs(p - r) <= 0.20 * r):
            zone_a += 1
        # Zone E: opposite extremes (fatal clinical errors)
        elif (p >= 180.0 and r <= 70.0) or (p <= 70.0 and r >= 180.0):
            zone_e += 1
        # Zone C: overcorrection
        elif (r >= 70.0 and r <= 290.0) and (p >= r + 110.0):
            zone_c += 1
        elif (r >= 130.0 and r <= 180.0) and (p <= (7.0 / 5.0) * r - 182.0):
            zone_c += 1
        # Zone D: failure to detect hypo or hyper
        elif (r <= 70.0 and p >= 70.0 and p <= 180.0):
            zone_d += 1
        elif (r >= 240.0 and p >= 70.0 and p <= 180.0):
            zone_d += 1
        # Zone B: benign errors (everything else)
        else:
            zone_b += 1

    pct_a = (zone_a / n_total) * 100.0
    pct_b = (zone_b / n_total) * 100.0
    pct_c = (zone_c / n_total) * 100.0
    pct_d = (zone_d / n_total) * 100.0
    pct_e = (zone_e / n_total) * 100.0
    pct_ab = pct_a + pct_b

    return {
        "total_points": n_total,
        "zone_a_count": zone_a,
        "zone_b_count": zone_b,
        "zone_c_count": zone_c,
        "zone_d_count": zone_d,
        "zone_e_count": zone_e,
        "zone_a_pct": round(pct_a, 2),
        "zone_b_pct": round(pct_b, 2),
        "zone_c_pct": round(pct_c, 2),
        "zone_d_pct": round(pct_d, 2),
        "zone_e_pct": round(pct_e, 2),
        "zone_a_plus_b_pct": round(pct_ab, 2)
    }

if __name__ == "__main__":
    # Self-test with synthetic data
    ref = np.array([100, 150, 60, 220, 80, 50])
    pred = np.array([105, 140, 58, 210, 85, 48])
    res = clarke_error_grid(ref, pred)
    print("Clarke Error Grid Self-Test Result:")
    for k, v in res.items():
        print(f"  {k}: {v}")
    assert res["zone_a_pct"] == 100.0, "Self-test failed"
    print("Self-test passed!")
