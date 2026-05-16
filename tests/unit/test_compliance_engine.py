"""TDD tests for compliance_engine.py."""

from __future__ import annotations

import time
from trace.detection.compliance_engine import ComplianceEngine

import pytest


@pytest.fixture
def engine(tmp_path):
    rules_file = tmp_path / "test_rules.yaml"
    rules_file.write_text("""
rules:
  - id: HIGH_VALUE_OUTGOING
    description: "Single transaction > Rs 5L"
    field: amount
    op: gt
    value: 500000
    action: FLAG
    severity: HIGH

  - id: HIGH_KYC_RISK
    description: "Account has HIGH KYC risk"
    field: kyc_risk
    op: eq
    value: HIGH
    action: ALERT
    severity: MEDIUM
""")
    return ComplianceEngine(rules_file)


class TestComplianceEngine:
    def test_evaluate_flags_high_value(self, engine):
        txn = {"amount": 600_000, "kyc_risk": "LOW", "channel": "NEFT"}
        results = engine.evaluate(txn)
        assert any(r["rule_id"] == "HIGH_VALUE_OUTGOING" for r in results)

    def test_evaluate_no_match_for_clean_txn(self, engine):
        txn = {"amount": 1_000, "kyc_risk": "LOW", "channel": "UPI"}
        results = engine.evaluate(txn)
        assert len(results) == 0

    def test_evaluate_kyc_risk_rule(self, engine):
        txn = {"amount": 1_000, "kyc_risk": "HIGH", "channel": "UPI"}
        results = engine.evaluate(txn)
        assert any(r["rule_id"] == "HIGH_KYC_RISK" for r in results)

    def test_result_has_required_fields(self, engine):
        txn = {"amount": 600_000, "kyc_risk": "LOW"}
        results = engine.evaluate(txn)
        if results:
            r = results[0]
            assert "rule_id" in r
            assert "action" in r
            assert "severity" in r

    def test_compliance_score_0_for_clean(self, engine):
        txn = {"amount": 1_000, "kyc_risk": "LOW"}
        score = engine.compliance_score(txn)
        assert score == 0.0

    def test_compliance_score_positive_for_flagged(self, engine):
        txn = {"amount": 700_000, "kyc_risk": "HIGH"}
        score = engine.compliance_score(txn)
        assert score > 0.0

    def test_hot_reload_updates_rules(self, engine, tmp_path):
        rules_file = engine.rules_path
        txn = {"amount": 200_000, "kyc_risk": "LOW"}
        assert len(engine.evaluate(txn)) == 0

        # Rewrite rules with a lower threshold
        rules_file.write_text("""
rules:
  - id: MEDIUM_VALUE
    description: "Transaction > Rs 1L"
    field: amount
    op: gt
    value: 100000
    action: FLAG
    severity: LOW
""")
        time.sleep(1.5)  # allow watchdog to reload
        results = engine.evaluate(txn)
        assert any(r["rule_id"] == "MEDIUM_VALUE" for r in results)
