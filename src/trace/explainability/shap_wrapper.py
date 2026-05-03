"""SHAP wrapper — feature-level explanations for the anomaly scorer.

Used to rank features (txn velocity, amount variance, channel switch, etc.)
that pushed the composite risk score over the CRITICAL/HIGH threshold.
"""

from __future__ import annotations


def explain_features(model_predict_fn, features) -> dict:
    """Return {feature_name: shap_value} for a single sample."""
    raise NotImplementedError("Use shap.KernelExplainer over the fusion pipeline.")
