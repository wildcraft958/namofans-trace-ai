"""Temporal windowing utilities — slice graph by time intervals."""

from __future__ import annotations

from datetime import datetime, timedelta

import networkx as nx


def window(g: nx.MultiDiGraph, end: datetime, span: timedelta) -> nx.MultiDiGraph:
    """Return subgraph of edges with timestamp in (end - span, end].

    Parameters
    ----------
    g:    source MultiDiGraph with edge attribute ``timestamp`` (datetime)
    end:  upper bound (inclusive)
    span: window width; lower bound is (end - span), exclusive

    Returns
    -------
    A new MultiDiGraph containing only edges whose timestamp falls in
    (end - span, end].  All nodes from the original graph are preserved
    so that node attributes (account metadata) remain accessible even for
    nodes with no edges in the window.
    """
    start = end - span

    # Collect (u, v, key) for edges inside the time window.
    keep_edges: list[tuple] = [
        (u, v, k)
        for u, v, k, d in g.edges(data=True, keys=True)
        if start < d["timestamp"] <= end
    ]

    sub = nx.MultiDiGraph()
    # Copy all node attributes so downstream code can access account metadata.
    for node, data in g.nodes(data=True):
        sub.add_node(node, **data)

    for u, v, k in keep_edges:
        edge_data = g.edges[u, v, k]
        sub.add_edge(u, v, key=k, **edge_data)

    return sub
