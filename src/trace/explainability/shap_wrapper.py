"""SHAP TreeExplainer wrapper for XGBoost graph feature classifier.

Returns per-feature SHAP values for a single account row.
Used by the explainability card and /alerts/{id}/explain endpoint.
"""

from __future__ import annotations

from trace.detection.gnn_classifier import FEATURE_COLS

import numpy as np
import shap


def explain_account(
    model,
    scaler,
    feature_row: dict[str, float],
) -> dict[str, float]:
    """Return {feature_name: shap_value} for a single account.

    Positive values push toward fraud classification.
    """
    x = np.array([[feature_row.get(col, 0.0) for col in FEATURE_COLS]])
    x_scaled = scaler.transform(x)

    explainer = shap.TreeExplainer(model)
    sv = explainer.shap_values(x_scaled)

    # XGBoost binary outputs shape (n_samples, n_features) directly
    if isinstance(sv, list):
        values = sv[1][0]
    else:
        values = sv[0]

    return {col: float(val) for col, val in zip(FEATURE_COLS, values, strict=False)}


def top_features(
    model,
    scaler,
    feature_row: dict[str, float],
    n: int = 5,
) -> list[dict]:
    """Return top-n features ranked by absolute SHAP magnitude."""
    shap_vals = explain_account(model, scaler, feature_row)
    ranked = sorted(shap_vals.items(), key=lambda kv: abs(kv[1]), reverse=True)
    return [{"feature": k, "shap_value": round(v, 4)} for k, v in ranked[:n]]


def batch_explain(model, scaler, feature_df) -> dict[str, dict[str, float]]:
    """Compute SHAP values for every row in a feature DataFrame.

    Returns {account_id: {feature: shap_value}}.
    """
    x = feature_df[FEATURE_COLS].fillna(0.0).values
    x_scaled = scaler.transform(x)

    explainer = shap.TreeExplainer(model)
    sv = explainer.shap_values(x_scaled)
    if isinstance(sv, list):
        values = sv[1]
    else:
        values = sv

    result = {}
    for idx, account_id in enumerate(feature_df.index):
        result[str(account_id)] = {
            col: float(values[idx, j]) for j, col in enumerate(FEATURE_COLS)
        }
    return result
