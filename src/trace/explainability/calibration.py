"""Calibration curve -- predicted vs. actual fraud probability.

Produces the calibration plot saved to docs/figures/calibration_curve.png.
Run once after training via scripts/run_demo.py.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.calibration import calibration_curve


def plot_calibration(
    y_true,
    y_prob,
    save_path: str | Path = "docs/figures/calibration_curve.png",
    n_bins: int = 10,
) -> Path:
    """Plot reliability diagram and save to save_path. Returns the saved path."""
    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)

    fraction_pos, mean_pred = calibration_curve(y_true, y_prob, n_bins=n_bins)

    fig, ax = plt.subplots(figsize=(6, 5))
    ax.plot([0, 1], [0, 1], "k--", label="Perfect calibration")
    ax.plot(mean_pred, fraction_pos, "s-", color="#1a73e8", label="XGBoost (graph features)")
    ax.set_xlabel("Mean predicted probability")
    ax.set_ylabel("Fraction of positives")
    ax.set_title("TRACE.ai -- Model Calibration Curve")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(save_path, dpi=150)
    plt.close(fig)
    return save_path


def calibration_stats(y_true, y_prob, n_bins: int = 10) -> dict:
    """Return ECE (Expected Calibration Error) and max calibration error."""
    fraction_pos, mean_pred = calibration_curve(y_true, y_prob, n_bins=n_bins)
    errors = np.abs(fraction_pos - mean_pred)
    return {
        "ece": float(errors.mean()),
        "max_calibration_error": float(errors.max()),
        "n_bins": n_bins,
    }
