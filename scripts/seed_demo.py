"""Seed a small 500-account deterministic demo graph for frontend development.

Produces data/processed/demo_graph.pkl and data/processed/alerts.json
with pre-scored alerts ready to serve from the API.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from trace.data.generator import generate
from trace.graph.builder import build_graph, save_graph
from trace.detection.pattern_matcher import score_account
from trace.detection.risk_fusion import fuse


def main() -> None:
    print("Seeding demo graph (500 accounts, 5000 transactions)...")
    accounts, transactions = generate(
        num_accounts=500,
        num_transactions=5_000,
        seed=42,
        output_dir=Path("data/sample"),
    )
    g = build_graph(accounts, transactions)
    save_graph(g, Path("data/processed/demo_graph.pkl"))
    print(f"Demo graph: {g.number_of_nodes()} nodes, {g.number_of_edges()} edges")

    # Score all accounts and collect top alerts
    alerts = []
    for acc in accounts:
        result = score_account(g, acc.account_id)
        if result["score"] > 0:
            risk = fuse(
                pattern=result["score"],
                gnn=result["score"] * 0.9,
                anomaly=min(result["score"] * 1.1, 1.0),
                compliance=0.3 if acc.kyc_risk == "HIGH" else 0.1,
            )
            if risk.level in ("HIGH", "CRITICAL"):
                matched = [k for k, v in result["matches"].items() if v]
                alerts.append({
                    "alert_id": f"ALT-{acc.account_id}",
                    "account_id": acc.account_id,
                    "account_type": acc.account_type,
                    "ifsc": acc.ifsc,
                    "kyc_risk": acc.kyc_risk,
                    "name": acc.name,
                    "risk_level": risk.level,
                    "composite_score": round(risk.composite, 4),
                    "contributions": {k: round(v, 4) for k, v in risk.contributions.items()},
                    "matched_patterns": matched,
                    "acknowledged": False,
                    "shap_features": {},
                })

    alerts.sort(key=lambda a: a["composite_score"], reverse=True)
    print(f"Generated {len(alerts)} HIGH/CRITICAL alerts")

    alerts_path = Path("data/processed/alerts.json")
    alerts_path.parent.mkdir(parents=True, exist_ok=True)
    with open(alerts_path, "w") as f:
        json.dump(alerts, f, indent=2)
    print(f"Alerts written to {alerts_path}")


if __name__ == "__main__":
    main()
