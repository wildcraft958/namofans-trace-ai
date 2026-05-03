"""Alert endpoints."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("")
def list_alerts(level: str | None = None) -> list[dict]:
    raise NotImplementedError


@router.post("/{alert_id}/acknowledge")
def acknowledge(alert_id: str) -> dict:
    raise NotImplementedError


@router.get("/{alert_id}/explain")
def explain(alert_id: str) -> dict:
    """Returns GNNExplainer subgraph + SHAP feature importances."""
    raise NotImplementedError
