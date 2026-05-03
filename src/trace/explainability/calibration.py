"""Calibration curve generator — predicted vs. actual fraud probability.

Produces the calibration plot referenced in the README + MODEL_CARD.
"""

from __future__ import annotations


def plot_calibration(y_true, y_prob, save_path):
    raise NotImplementedError("sklearn.calibration.calibration_curve + matplotlib")
