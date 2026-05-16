"""TDD tests for feature_engineering.py -- written before implementation."""

from __future__ import annotations

import pytest
import pandas as pd

from trace.data.generator import generate
from trace.graph.builder import build_graph
from trace.data.feature_engineering import extract_features, build_feature_matrix, FEATURE_COLS


@pytest.fixture(scope="module")
def graph_and_accounts():
    accounts, transactions = generate(num_accounts=200, num_transactions=2_000, seed=42)
    g = build_graph(accounts, transactions)
    return g, accounts


class TestExtractFeatures:
    def test_returns_all_feature_keys(self, graph_and_accounts):
        g, accounts = graph_and_accounts
        acc_id = accounts[0].account_id
        feats = extract_features(g, acc_id)
        assert set(feats.keys()) == set(FEATURE_COLS)

    def test_all_values_are_floats(self, graph_and_accounts):
        g, accounts = graph_and_accounts
        feats = extract_features(g, accounts[0].account_id)
        for k, v in feats.items():
            assert isinstance(v, float), f"{k} is not float: {type(v)}"

    def test_missing_account_returns_zeros(self, graph_and_accounts):
        g, _ = graph_and_accounts
        feats = extract_features(g, "NONEXISTENT-ACCOUNT")
        assert all(v == 0.0 for v in feats.values())

    def test_degree_in_non_negative(self, graph_and_accounts):
        g, accounts = graph_and_accounts
        for acc in accounts[:10]:
            feats = extract_features(g, acc.account_id)
            assert feats["degree_in"] >= 0.0
            assert feats["degree_out"] >= 0.0

    def test_kyc_risk_high_account_has_score_one(self, graph_and_accounts):
        g, accounts = graph_and_accounts
        high_risk = [a for a in accounts if a.kyc_risk == "HIGH"]
        if high_risk:
            feats = extract_features(g, high_risk[0].account_id)
            assert feats["kyc_risk_score"] == 1.0

    def test_fraud_ring_has_elevated_features(self, graph_and_accounts):
        g, _ = graph_and_accounts
        # RING-MU-00 is the mule aggregator — should have high degree
        if "RING-MU-00" in g:
            feats = extract_features(g, "RING-MU-00")
            assert feats["degree_in"] >= 6  # 12 senders → scaled down for 200-acc graph


class TestBuildFeatureMatrix:
    def test_returns_dataframe_with_correct_shape(self, graph_and_accounts):
        g, accounts = graph_and_accounts
        df = build_feature_matrix(g, accounts)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == len(accounts)
        assert list(df.columns) == FEATURE_COLS

    def test_index_is_account_ids(self, graph_and_accounts):
        g, accounts = graph_and_accounts
        df = build_feature_matrix(g, accounts)
        assert df.index.name == "account_id"
        assert accounts[0].account_id in df.index

    def test_no_nan_values(self, graph_and_accounts):
        g, accounts = graph_and_accounts
        df = build_feature_matrix(g, accounts)
        assert not df.isnull().any().any(), "Feature matrix contains NaN values"

    def test_values_are_numeric(self, graph_and_accounts):
        g, accounts = graph_and_accounts
        df = build_feature_matrix(g, accounts)
        for col in FEATURE_COLS:
            assert pd.api.types.is_numeric_dtype(df[col]), f"{col} is not numeric"
