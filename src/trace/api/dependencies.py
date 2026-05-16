"""Shared FastAPI dependencies -- graph singleton, model loader, alerts cache."""

from __future__ import annotations

import json
import threading
from pathlib import Path

import networkx as nx

_GRAPH_PATH = Path("data/processed/graph.pkl")
_ALERTS_PATH = Path("data/processed/alerts.json")

_lock = threading.RLock()
_graph: nx.MultiDiGraph | None = None
_alerts: list[dict] = []
_model = None
_scaler = None


def get_graph() -> nx.MultiDiGraph:
    global _graph
    with _lock:
        if _graph is None:
            _graph = _load_graph()
    return _graph


def reload_graph() -> nx.MultiDiGraph:
    global _graph
    with _lock:
        _graph = _load_graph()
    return _graph


def _load_graph() -> nx.MultiDiGraph:
    if _GRAPH_PATH.exists():
        from trace.graph.builder import load_graph
        return load_graph(_GRAPH_PATH)
    # Generate a fresh demo graph if nothing is on disk
    from trace.graph.builder import build_from_generator
    g, _, _ = build_from_generator(num_accounts=500, num_transactions=5_000)
    return g


def get_alerts() -> list[dict]:
    global _alerts
    with _lock:
        if not _alerts:
            _alerts = _load_alerts()
    return _alerts


def reload_alerts() -> list[dict]:
    global _alerts
    with _lock:
        _alerts = _load_alerts()
    return _alerts


def _load_alerts() -> list[dict]:
    if _ALERTS_PATH.exists():
        try:
            return json.loads(_ALERTS_PATH.read_text()) or []
        except Exception:
            pass
    return []


def get_model_and_scaler():
    global _model, _scaler
    with _lock:
        if _model is None:
            from trace.detection import gnn_classifier
            if gnn_classifier.model_exists():
                _model, _scaler = gnn_classifier.load()
    return _model, _scaler


def inject_graph_node(account_data: dict, transactions: list[dict]) -> None:
    """Add synthetic accounts/transactions to the in-memory graph (demo endpoint)."""
    g = get_graph()
    with _lock:
        aid = account_data["account_id"]
        g.add_node(aid, **account_data)
        for txn in transactions:
            g.add_edge(
                txn["sender_id"],
                txn["receiver_id"],
                amount=txn["amount"],
                timestamp=txn.get("timestamp"),
                channel=txn.get("channel", "NEFT"),
                fraud_label=txn.get("fraud_label", False),
            )
