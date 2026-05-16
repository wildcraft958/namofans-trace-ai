"""Graph endpoints -- full graph + per-account subgraph."""

from __future__ import annotations

from trace.api.dependencies import get_graph
from trace.graph.builder import get_subgraph, graph_to_viz

from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.get("")
def get_full_graph(limit: int = 1000) -> dict:
    """Return the full graph in {nodes, links, summary} viz format."""
    g = get_graph()
    risk_map = _load_risk_map()
    return graph_to_viz(g, risk_map=risk_map, limit=limit)


@router.get("/{account_id}")
def get_account_subgraph(account_id: str, depth: int = 2) -> dict:
    g = get_graph()
    if account_id not in g:
        raise HTTPException(status_code=404, detail=f"Account {account_id} not found")
    sub = get_subgraph(g, account_id, depth=depth)
    risk_map = _load_risk_map()
    return graph_to_viz(sub, risk_map=risk_map, limit=10_000)


def _load_risk_map() -> dict[str, str]:
    """Return {account_id: risk_level} from alerts cache."""
    from trace.api.dependencies import get_alerts
    alerts = get_alerts()
    return {a["account_id"]: a.get("risk_level", "LOW") for a in alerts}
