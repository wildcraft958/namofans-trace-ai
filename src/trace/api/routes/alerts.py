"""Alert endpoints."""

from __future__ import annotations

import json
from pathlib import Path
from trace.api.dependencies import get_alerts, reload_alerts

from fastapi import APIRouter, HTTPException

router = APIRouter()

_ALERTS_PATH = Path("data/processed/alerts.json")


@router.get("")
def list_alerts(level: str | None = None) -> list[dict]:
    alerts = get_alerts()
    if level:
        alerts = [a for a in alerts if a.get("risk_level", "").upper() == level.upper()]
    return alerts


@router.post("/{alert_id}/acknowledge")
def acknowledge(alert_id: str) -> dict:
    alerts = get_alerts()
    for alert in alerts:
        if alert.get("alert_id") == alert_id:
            alert["status"] = "acknowledged"
            _persist_alerts(alerts)
            return {"alert_id": alert_id, "status": "acknowledged"}
    raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")


@router.get("/drift-events")
def drift_events(since: str | None = None) -> list[dict]:
    from trace.intelligence.drift_dashboard import get_drift_events
    return get_drift_events(since=since)


@router.get("/{alert_id}/explain")
def explain(alert_id: str) -> dict:
    """Return pattern matches, risk breakdown, and SHAP feature importances."""
    alerts = get_alerts()
    alert = next((a for a in alerts if a.get("alert_id") == alert_id), None)
    if alert is None:
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")

    explanation_path = Path(f"data/processed/explanations/{alert_id}.txt")
    llm_explanation = ""
    if explanation_path.exists():
        llm_explanation = explanation_path.read_text()

    return {
        "alert_id": alert_id,
        "account_id": alert.get("account_id"),
        "risk_level": alert.get("risk_level"),
        "composite_score": alert.get("composite_score"),
        "pattern_matches": alert.get("pattern_matches", {}),
        "risk_contributions": alert.get("risk_contributions", {}),
        "shap_features": alert.get("shap_features", []),
        "llm_explanation": llm_explanation,
        "compliance_rules": alert.get("compliance_rules", []),
    }


def _persist_alerts(alerts: list[dict]) -> None:
    _ALERTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    _ALERTS_PATH.write_text(json.dumps(alerts, indent=2, default=str))
    reload_alerts()
