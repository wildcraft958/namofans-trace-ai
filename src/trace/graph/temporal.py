"""Temporal windowing utilities — slice graph by time intervals."""

from __future__ import annotations

from datetime import datetime, timedelta

import networkx as nx


def window(g: nx.MultiDiGraph, end: datetime, span: timedelta) -> nx.MultiDiGraph:
    """Return subgraph of edges with timestamp in (end - span, end]."""
    raise NotImplementedError
