"""Graph feature classifier -- XGBoost on engineered graph features.

Replaces GraphSAGE for Phase 2 POC. Uses 11 features extracted from the
NetworkX graph (degree, PageRank, velocity, amounts, KYC risk, dormancy).

Per DECISIONS.md ADR-0002 and the hackathon organiser's sample D3:
"GNNs require significantly more compute than POC scope allows."
XGBoost on graph features achieves AUC > 0.90 on AMLSim synthetic data.

Routing: if a trained TGN model exists, score_account() delegates to it.
XGBoost remains the fallback when TGN has not been trained yet.
"""

from __future__ import annotations

import pickle
from pathlib import Path

import networkx as nx
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


# ---------------------------------------------------------------------------
# TGN-routing entry point (used by API / scoring pipelines)
# ---------------------------------------------------------------------------

def score_account(graph: nx.MultiDiGraph, account_id: str) -> float:
    """Return fraud probability for a single account.

    Routes to TGN if a trained model exists; falls back to XGBoost otherwise.
    Returns 0.0 if neither model is trained.
    """
    try:
        from trace.detection import tgn_classifier
        if tgn_classifier.model_exists():
            tgn_model, node_map = tgn_classifier.load()
            scores = tgn_classifier.score(tgn_model, graph, [account_id], node_map=node_map)
            return scores.get(account_id, 0.0)
    except Exception as e:
        print(f"[gnn_classifier] TGN scoring failed ({e}), falling back to XGBoost")

    if not model_exists():
        return 0.0

    # XGBoost fallback — needs feature_df; build minimal single-row frame
    try:
        xgb_model, xgb_scaler = load()
        features = _extract_single_account_features(graph, account_id)
        feat_df = pd.DataFrame([features], index=[account_id])
        scores_xgb = score(xgb_model, xgb_scaler, feat_df)
        return scores_xgb.get(account_id, 0.0)
    except Exception as e:
        print(f"[gnn_classifier] XGBoost fallback also failed ({e})")
        return 0.0


def _extract_single_account_features(graph: nx.MultiDiGraph, account_id: str) -> dict:
    """Build the 11 XGBoost features for a single account on-the-fly."""
    node_data = graph.nodes.get(account_id, {})
    kyc_map = {"LOW": 0.1, "MEDIUM": 0.5, "HIGH": 0.9}

    in_edges = list(graph.in_edges(account_id, data=True))
    out_edges = list(graph.out_edges(account_id, data=True))

    amounts_out = [d.get("amount", 0) for _, _, d in out_edges]
    counterparties = {v for _, v, _ in out_edges} | {u for u, _, _ in in_edges}

    pr_map = nx.pagerank(graph, alpha=0.85, max_iter=50)
    cc_graph = nx.Graph(graph)
    cc_map = nx.clustering(cc_graph)

    return {
        "degree_in": len(in_edges),
        "degree_out": len(out_edges),
        "pagerank": pr_map.get(account_id, 0.0),
        "clustering_coeff": cc_map.get(account_id, 0.0),
        "txn_velocity_7d": len(out_edges),  # simplified
        "avg_amount_out": float(sum(amounts_out) / max(len(amounts_out), 1)),
        "std_amount_out": float(
            (sum((a - sum(amounts_out) / max(len(amounts_out), 1)) ** 2
                 for a in amounts_out) / max(len(amounts_out), 1)) ** 0.5
        ) if amounts_out else 0.0,
        "max_amount_out": float(max(amounts_out)) if amounts_out else 0.0,
        "unique_counterparties": len(counterparties),
        "dormant_days": node_data.get("dormant_days", 0),
        "kyc_risk_score": kyc_map.get(node_data.get("kyc_risk", "LOW"), 0.1),
    }
