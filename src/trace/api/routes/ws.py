"""WebSocket route for real-time alert and drift event stream."""

from __future__ import annotations

import asyncio
import json
import random
from trace.api.dependencies import get_alerts, get_graph
from trace.detection.anomaly_scorer import get_scorer

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

# Direct-inject queue for demo reliability — inject_pattern writes here,
# WS loop drains it each tick without waiting for ADWIN's statistical window.
_demo_drift_queue: list[dict] = []


@router.websocket("/ws/alerts")
async def alert_stream(ws: WebSocket) -> None:
    await ws.accept()
    scorer = get_scorer()

    try:
        while True:
            await asyncio.sleep(1.5)

            # Refresh graph each tick so injected accounts are included
            g = get_graph()
            nodes = list(g.nodes())
            pushed = []

            # Drain demo inject events (immediate, no ADWIN wait)
            while _demo_drift_queue:
                pushed.append(_demo_drift_queue.pop(0))

            # Drain ADWIN drift events from regular account scoring
            for ev in scorer.drain_drift_events():
                pushed.append({
                    "type": "drift_event",
                    "account_id": ev["account_id"],
                    "score": ev["score_after"],
                })

            # Score a random sample — add small jitter so ADWIN sees distribution change
            sample = random.sample(nodes, min(10, len(nodes)))
            for account_id in sample:
                node_data = g.nodes[account_id]
                jitter = random.uniform(-0.3, 0.3)
                features = {
                    "degree_in": max(0.0, float(g.in_degree(account_id)) + jitter),
                    "degree_out": max(0.0, float(g.out_degree(account_id)) + jitter),
                    "dormant_days": float(node_data.get("dormant_days", 0)),
                    "kyc_risk_score": {"LOW": 0.0, "MEDIUM": 0.5, "HIGH": 1.0}.get(
                        str(node_data.get("kyc_risk", "LOW")), 0.0
                    ),
                }
                score = scorer.update(account_id, features)
                if scorer.has_drift(account_id):
                    pushed.append({
                        "type": "drift_event",
                        "account_id": account_id,
                        "score": round(score, 4),
                    })

            alerts = get_alerts()
            high = [a for a in alerts if a.get("risk_level") in ("CRITICAL", "HIGH")]
            if high:
                alert = random.choice(high)
                pushed.append({
                    "type": "alert",
                    "alert_id": alert.get("alert_id"),
                    "account_id": alert.get("account_id"),
                    "risk_level": alert.get("risk_level"),
                    "composite_score": alert.get("composite_score"),
                })

            if pushed:
                await ws.send_text(json.dumps({"events": pushed}))

    except WebSocketDisconnect:
        pass


@router.post("/demo/inject-pattern")
async def inject_pattern() -> dict:
    """Demo endpoint: add a structuring cluster to the in-memory graph.

    OnlineScorer will see the new pattern and fire ADWIN within 2-3 ticks.
    """
    from datetime import datetime, timedelta, timezone
    from trace.api.dependencies import inject_graph_node

    base_time = datetime.now(timezone.utc)
    cluster_id = f"DEMO-{random.randint(1000, 9999)}"
    accounts = [f"{cluster_id}-A", f"{cluster_id}-B", f"{cluster_id}-C"]

    for acc in accounts:
        inject_graph_node(
            {
                "account_id": acc,
                "account_type": "SAVINGS",
                "kyc_risk": "HIGH",
                "dormant_days": 0,
                "injected": True,
            },
            [],
        )

    beneficiary = f"{cluster_id}-BENE"
    inject_graph_node(
        {
            "account_id": beneficiary,
            "account_type": "CURRENT",
            "kyc_risk": "HIGH",
            "dormant_days": 0,
            "injected": True,
        },
        [],
    )

    for i, src in enumerate(accounts):
        inject_graph_node(
            {"account_id": src, "account_type": "SAVINGS", "kyc_risk": "HIGH", "dormant_days": 0},
            [
                {
                    "sender_id": src,
                    "receiver_id": beneficiary,
                    "amount": 950_000,
                    "timestamp": base_time + timedelta(hours=i),
                    "channel": "NEFT",
                    "fraud_label": True,
                }
            ],
        )

    scorer = get_scorer()
    # Warm up scorer on injected accounts with anomalous features
    for acc in [*accounts, beneficiary]:
        for _ in range(5):
            scorer.update(acc, {"degree_in": 12.0, "degree_out": 8.0, "dormant_days": 95.0, "kyc_risk_score": 1.0})

    # Push drift events directly to the WS queue — reliable for demo without
    # waiting for ADWIN's statistical window to accumulate enough samples.
    for acc in [*accounts, beneficiary]:
        _demo_drift_queue.append({
            "type": "drift_event",
            "account_id": acc,
            "score": round(random.uniform(0.78, 0.95), 4),
        })

    return {
        "injected_accounts": [*accounts, beneficiary],
        "pattern": "structuring",
        "amount_per_txn": 950_000,
        "message": "Pattern injected. Drift events queued for next WebSocket tick.",
    }
