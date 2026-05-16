"""Graph feature classifier -- XGBoost on engineered graph features.

Replaces GraphSAGE for Phase 2 POC. Uses 11 features extracted from the
NetworkX graph (degree, PageRank, velocity, amounts, KYC risk, dormancy).

Per DECISIONS.md ADR-0002 and the hackathon organiser's sample D3:
"GNNs require significantly more compute than POC scope allows."
XGBoost on graph features achieves AUC > 0.90 on AMLSim synthetic data.

TGN / GraphSAGE deferred to v2 when real bank data is available.
"""

from __future__ import annotations

import pickle
from pathlib import Path

import pandas as pd
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

_MODEL_PATH = Path("models/classifier.pkl")
_SCALER_PATH = Path("models/scaler.pkl")

FEATURE_COLS = [
    "degree_in", "degree_out", "pagerank", "clustering_coeff",
    "txn_velocity_7d", "avg_amount_out", "std_amount_out", "max_amount_out",
    "unique_counterparties", "dormant_days", "kyc_risk_score",
]


def train(
    feature_df: pd.DataFrame,
    labels: pd.Series,
    save: bool = True,
) -> tuple:
    """Train XGBoost classifier. Returns (model, scaler, auc)."""
    x_arr = feature_df[FEATURE_COLS].fillna(0.0).values
    y = labels.reindex(feature_df.index).fillna(0).astype(int).values

    scaler = StandardScaler()
    x_scaled = scaler.fit_transform(x_arr)

    n_pos = int(y.sum())
    n_neg = int((y == 0).sum())
    pos_weight = n_neg / max(n_pos, 1)

    model = XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.05,
        scale_pos_weight=pos_weight,
        subsample=0.8,
        colsample_bytree=0.8,
        eval_metric="auc",
        random_state=42,
        verbosity=0,
    )
    model.fit(x_scaled, y)

    probs = model.predict_proba(x_scaled)[:, 1]
    auc = float(roc_auc_score(y, probs)) if n_pos > 0 else 0.0
    print(f"Classifier AUC (train): {auc:.4f}  |  fraud={n_pos}/{len(y)}")

    if save:
        _MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(_MODEL_PATH, "wb") as f:
            pickle.dump(model, f)
        with open(_SCALER_PATH, "wb") as f:
            pickle.dump(scaler, f)

    return model, scaler, auc


def load() -> tuple:
    """Load saved model + scaler. Raises FileNotFoundError if not trained yet."""
    with open(_MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    with open(_SCALER_PATH, "rb") as f:
        scaler = pickle.load(f)
    return model, scaler


def score(model, scaler, feature_df: pd.DataFrame) -> dict[str, float]:
    """Return per-account suspicious probability. Keys are account_id strings."""
    x_arr = feature_df[FEATURE_COLS].fillna(0.0).values
    x_scaled = scaler.transform(x_arr)
    probs = model.predict_proba(x_scaled)[:, 1]
    return dict(zip(feature_df.index.astype(str), probs.tolist(), strict=False))


def model_exists() -> bool:
    return _MODEL_PATH.exists() and _SCALER_PATH.exists()
