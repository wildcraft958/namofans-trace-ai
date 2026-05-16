"""Structuring -- multiple transactions each just below the Rs 10L CTR threshold.

Targets PMLA / RBI: Cash Transaction Report mandatory for any single txn > Rs 10L.
Pattern: >= 3 outgoing transactions within 24h, each in Rs 9L-9.99L range.
"""

from __future__ import annotations

from datetime import timedelta

import networkx as nx

_CTR_THRESHOLD = 1_000_000  # Rs 10L reporting threshold
_LOWER_BOUND = 800_000      # Rs 8L — suspicious proximity to threshold
_MIN_TXNS = 3
_WINDOW_HOURS = 24


def detect(g: nx.MultiDiGraph, account_id: str) -> bool:
    if account_id not in g:
        return False

    # Collect outgoing edges sorted by time
    edges = sorted(
        [
            (data["timestamp"], dst, data.get("amount", 0.0))
            for _src, dst, data in g.out_edges(account_id, data=True)
            if data.get("timestamp") is not None
        ],
        key=lambda x: x[0],
    )
    if len(edges) < _MIN_TXNS:
        return False

    # Sliding 24-hour window
    for i in range(len(edges)):
        t_start = edges[i][0]
        t_end = t_start + timedelta(hours=_WINDOW_HOURS)
        window = [(t, r, a) for t, r, a in edges if t_start <= t <= t_end]

        # Transactions with amounts in the suspicious near-threshold range
        near_threshold = [(t, r, a) for t, r, a in window if _LOWER_BOUND <= a < _CTR_THRESHOLD]

        if len(near_threshold) >= _MIN_TXNS:
            return True

        # Also check: multiple transactions to SAME receiver summing to >threshold but each below
        by_recv: dict[str, list[tuple]] = {}
        for t, r, a in window:
            if a < _CTR_THRESHOLD:
                by_recv.setdefault(r, []).append((t, a))

        for _recv, txns in by_recv.items():
            if len(txns) >= _MIN_TXNS:
                total = sum(a for _, a in txns)
                if total >= _CTR_THRESHOLD and all(a < _CTR_THRESHOLD for _, a in txns):
                    return True

    return False
