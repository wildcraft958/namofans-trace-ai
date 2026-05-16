"""Seed a 500-account deterministic demo graph for frontend + API.

Produces:
  data/processed/graph.pkl   -- full graph (also used by API at startup)
  data/processed/alerts.json -- HIGH/CRITICAL alerts with XGBoost + SHAP scores
  data/processed/explanations/{alert_id}.txt -- Gemini LLM explanations (if key present)

Run this before starting the API server.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from trace.data.feature_engineering import build_feature_matrix
from trace.data.generator import generate
from trace.detection import gnn_classifier
from trace.detection.anomaly_scorer import OnlineScorer
from trace.detection.compliance_engine import ComplianceEngine
from trace.detection.pattern_matcher import score_account
from trace.detection.risk_fusion import fuse
from trace.explainability.shap_wrapper import batch_explain
from trace.graph.builder import build_graph, save_graph

import pandas as pd

_RULES_PATH = Path("compliance_rules.yaml")
_GRAPH_OUT = Path("data/processed/graph.pkl")
_ALERTS_OUT = Path("data/processed/alerts.json")


def main() -> None:
    print("=" * 60)
    print("TRACE.ai seed_demo.py -- full pipeline")
    print("=" * 60)

    # ── 1. Generate synthetic data ──────────────────────────────
    print("\n[1/7] Generating synthetic data (500 accounts, 5000 txns)...")
    accounts, transactions = generate(
        num_accounts=500,
        num_transactions=5_000,
        seed=42,
        output_dir=Path("data/sample"),
    )

    # ── 2. Build graph ──────────────────────────────────────────
    print("[2/7] Building NetworkX MultiDiGraph...")
    g = build_graph(accounts, transactions)
    _GRAPH_OUT.parent.mkdir(parents=True, exist_ok=True)
    save_graph(g, _GRAPH_OUT)
    print(f"      Graph: {g.number_of_nodes()} nodes, {g.number_of_edges()} edges")

    # ── 3. Feature engineering ──────────────────────────────────
    print("[3/7] Extracting graph features (11 features per account)...")
    feature_df = build_feature_matrix(g, accounts)

    # ── 4. Train / load XGBoost classifier ─────────────────────
    if gnn_classifier.model_exists():
        print("[4/7] Loading existing XGBoost model...")
        model, scaler = gnn_classifier.load()
    else:
        print("[4/7] Training XGBoost classifier...")
        labels = pd.Series(
            {a.account_id: 1 if a.account_id.startswith("RING-") else 0 for a in accounts},
            name="fraud_label",
        )
        labels = labels.reindex(feature_df.index).fillna(0).astype(int)
        model, scaler, auc = gnn_classifier.train(feature_df, labels, save=True)
        print(f"      AUC: {auc:.4f}")

    # ── 5. Score all accounts ───────────────────────────────────
    print("[5/7] Scoring accounts (XGBoost + SHAP + patterns + compliance)...")
    gnn_scores = gnn_classifier.score(model, scaler, feature_df)
    shap_values = batch_explain(model, scaler, feature_df)

    compliance_engine = ComplianceEngine(_RULES_PATH, start_watcher=False)
    online_scorer = OnlineScorer()

    alerts = []
    for acc in accounts:
        aid = acc.account_id
        feature_row = feature_df.loc[aid].to_dict() if aid in feature_df.index else {}

        # Pattern score
        pattern_result = score_account(g, aid)
        pattern_score = pattern_result["score"]

        # GNN / XGBoost score
        gnn_score = gnn_scores.get(aid, 0.0)

        # Online anomaly score -- warm up with 10 updates so HST builds a baseline
        anomaly_score = 0.0
        if feature_row:
            for _ in range(10):
                anomaly_score = online_scorer.update(aid, feature_row)
            anomaly_score = min(1.0, max(0.0, anomaly_score))

        # Compliance score based on per-transaction evaluation
        # Use account-level attributes as transaction proxy for compliance
        txn_proxy = {
            "amount": max(
                (d.get("amount", 0) for _, _, d in g.out_edges(aid, data=True)),
                default=0,
            ),
            "kyc_risk": str(acc.kyc_risk),
            "dormant_days": float(g.nodes[aid].get("dormant_days", 0)),
            "channel": "NEFT",
        }
        compliance_rules_triggered = compliance_engine.evaluate(txn_proxy)
        compliance_score = compliance_engine.compliance_score(txn_proxy)

        # Fuse all scores
        risk = fuse(
            pattern=pattern_score,
            gnn=gnn_score,
            anomaly=anomaly_score,
            compliance=compliance_score,
        )

        if risk.level == "LOW":
            continue

        shap_for_acc = shap_values.get(aid, {})
        top_shap = sorted(shap_for_acc.items(), key=lambda kv: abs(kv[1]), reverse=True)[:5]

        alert = {
            "alert_id": f"ALT-{aid}",
            "account_id": aid,
            "account_type": acc.account_type,
            "ifsc": acc.ifsc,
            "kyc_risk": acc.kyc_risk,
            "name": getattr(acc, "name", aid),
            "risk_level": risk.level,
            "composite_score": round(risk.composite, 4),
            "risk_contributions": {k: round(v, 4) for k, v in risk.contributions.items()},
            "pattern_matches": pattern_result["matches"],
            "compliance_rules": [
                {"rule_id": r["rule_id"], "action": r["action"], "severity": r["severity"]}
                for r in compliance_rules_triggered
            ],
            "shap_features": [
                {"feature": k, "shap_value": round(v, 4)} for k, v in top_shap
            ],
            "status": "open",
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "transactions": _get_top_transactions(g, aid),
        }
        alerts.append(alert)

    alerts.sort(key=lambda a: a["composite_score"], reverse=True)
    print(f"      Generated {len(alerts)} HIGH/CRITICAL alerts")

    # ── 6. Write alerts ─────────────────────────────────────────
    print("[6/7] Writing alerts.json...")
    _ALERTS_OUT.parent.mkdir(parents=True, exist_ok=True)
    _ALERTS_OUT.write_text(json.dumps(alerts, indent=2, default=str))
    print(f"      Written to {_ALERTS_OUT}")

    # ── 7. Pre-cache Gemini explanations ────────────────────────
    print("[7/7] Pre-caching LLM explanations...")
    try:
        from trace.intelligence.explainer import precache_all
        cached = precache_all(alerts[:20])
        print(f"      Cached {cached} explanations")
    except Exception as e:
        print(f"      Skipped (Gemini unavailable): {e}")

    print("\nDone! Run: uvicorn trace.api.main:app --reload")
    print(f"  Alerts: {len(alerts)} | Graph: {g.number_of_nodes()} nodes")


def _get_top_transactions(g, account_id: str, n: int = 5) -> list[dict]:
    txns = []
    for _, dst, data in g.out_edges(account_id, data=True):
        txns.append({
            "counterparty": dst,
            "amount": data.get("amount", 0),
            "channel": data.get("channel", "NEFT"),
            "timestamp": str(data.get("timestamp", ""))[:10],
        })
    txns.sort(key=lambda t: t["amount"], reverse=True)
    return txns[:n]


if __name__ == "__main__":
    main()
