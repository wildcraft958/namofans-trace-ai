"""GNNExplainer wrapper — extracts the subgraph + edge mask that explains a flag.

Used by the dashboard "Why?" button. Returns top-k contributing edges/nodes.
Reference: torch_geometric.explain.GNNExplainer
"""

from __future__ import annotations


def explain_account(model, data, account_idx: int, top_k: int = 5) -> dict:
    """Return {nodes: [...], edges: [...], masks: {...}} for the account."""
    raise NotImplementedError("Wire torch_geometric.explain.Explainer with GNNExplainer algo.")
