"""Dormant account burst -- inactive >90 days then >3 high-value txns within 48 hours."""

from __future__ import annotations

from datetime import timedelta

import networkx as nx

_DORMANT_THRESHOLD = 90
_BURST_TXNS = 3
_BURST_HOURS = 48
_HIGH_VALUE = 500_000  # Rs 5L per transaction


def detect(g: nx.MultiDiGraph, account_id: str) -> bool:
    if account_id not in g:
        return False

    dormant_days = g.nodes[account_id].get("dormant_days", 0)
    if dormant_days < _DORMANT_THRESHOLD:
        return False

    out_edges = sorted(
        [
            (data["timestamp"], data.get("amount", 0.0))
            for _, _, data in g.out_edges(account_id, data=True)
            if data.get("timestamp") is not None
        ],
        key=lambda x: x[0],
    )

    if len(out_edges) < _BURST_TXNS:
        return False

    for i in range(len(out_edges)):
        t_start = out_edges[i][0]
        t_end = t_start + timedelta(hours=_BURST_HOURS)
        burst = [a for t, a in out_edges if t_start <= t <= t_end and a >= _HIGH_VALUE]
        if len(burst) >= _BURST_TXNS:
            return True

    return False
