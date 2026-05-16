"""TDD tests for gnn_classifier.py (XGBoost graph feature classifier)."""

from __future__ import annotations

from trace.data.feature_engineering import build_feature_matrix
from trace.data.generator import generate
from trace.detection.gnn_classifier import score, train
from trace.graph.builder import build_graph

import numpy as np
import pandas as pd
import pytest


@pytest.fixture(scope="module")
def trained_model():
    accounts, transactions = generate(num_accounts=300, num_transactions=3_000, seed=42)
    g = build_graph(accounts, transactions)
    df = build_feature_matrix(g, accounts)
    labels = pd.Series(
        {a.account_id: 1 if a.account_id.startswith("RING-") else 0 for a in accounts},
        name="fraud_label",
    )
    labels = labels.reindex(df.index).fillna(0).astype(int)
    model, scaler, auc = train(df, labels, save=False)
    return model, scaler, df, labels, auc


class TestTrain:
    def test_returns_model_scaler_auc(self, trained_model):
        model, scaler, _df, _labels, auc = trained_model
        assert model is not None
        assert scaler is not None
        assert 0.0 <= auc <= 1.0

    def test_auc_above_threshold(self, trained_model):
        _, _, _, _, auc = trained_model
        # XGBoost on seeded synthetic fraud rings should achieve high AUC
        assert auc >= 0.80, f"AUC {auc:.4f} below 0.80 threshold"

    def test_model_has_predict_proba(self, trained_model):
        model, _, _, _, _ = trained_model
        assert hasattr(model, "predict_proba")


class TestScore:
    def test_returns_dict_with_account_ids(self, trained_model):
        model, scaler, df, _, _ = trained_model
        scores = score(model, scaler, df)
        assert isinstance(scores, dict)
        assert len(scores) == len(df)

    def test_all_scores_in_unit_interval(self, trained_model):
        model, scaler, df, _, _ = trained_model
        scores = score(model, scaler, df)
        for acc_id, prob in scores.items():
            assert 0.0 <= prob <= 1.0, f"Score {prob} out of range for {acc_id}"

    def test_fraud_rings_score_higher_than_clean(self, trained_model):
        model, scaler, df, _, _ = trained_model
        scores = score(model, scaler, df)
        fraud_scores = [v for k, v in scores.items() if k.startswith("RING-")]
        clean_scores = [v for k, v in scores.items() if not k.startswith("RING-")]
        if fraud_scores and clean_scores:
            assert np.mean(fraud_scores) > np.mean(clean_scores), (
                f"Fraud mean={np.mean(fraud_scores):.3f} should be > clean mean={np.mean(clean_scores):.3f}"
            )
