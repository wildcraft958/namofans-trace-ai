"""Circular flow / round-tripping detector.

Detects cycles >= 3 nodes where the cycle edges span <= 72 hours,
and cumulative transferred amount > Rs 1L.
"""

from __future__ import annotations

from datetime import timedelta

import networkx as nx

_WINDOW_HOURS = 72
_MIN_CYCLE_AMOUNT = 100_000  # Rs 1L


def detect(g: nx.MultiDiGraph, account_id: str) -> bool:
    if account_id not in g:
        return False

    # Collect all edges in the 2-hop neighborhood around account_id (BFS depth 2)
    # so we don't miss ring edges that start before account_id's own timestamps.
    neighborhood: set[str] = {account_id}
    for _ in range(5):  # up to 5 hops — enough to find a 5-node ring
        next_layer: set[str] = set()
        for node in neighborhood:
            next_layer.update(g.successors(node))
            next_layer.update(g.predecessors(node))
        neighborhood.update(next_layer)

    # Collect all timestamps from neighborhood edges
    all_neighbor_times = [
        data["timestamp"]
        for src, dst, data in g.edges(data=True)
        if (src in neighborhood or dst in neighborhood) and data.get("timestamp") is not None
    ]
    if not all_neighbor_times:
        return False

    global_min = min(all_neighbor_times)

    # Build directed graph within the 72-hour window from the global min in neighborhood
    window_end = global_min + timedelta(hours=_WINDOW_HOURS)
    dg = nx.DiGraph()
    for src, dst, data in g.edges(data=True):
        if src not in neighborhood and dst not in neighborhood:
            continue
        ts = data.get("timestamp")
        if ts is None or ts > window_end:
            continue
        amt = data.get("amount", 0.0)
        if dg.has_edge(src, dst):
            dg[src][dst]["amount"] += amt
        else:
            dg.add_edge(src, dst, amount=amt)

    if account_id not in dg:
        return False

    try:
        for cycle in nx.simple_cycles(dg):
            if len(cycle) >= 3 and account_id in cycle:
                # Check only edges that are actually in the cycle
                cycle_amount = sum(
                    dg[cycle[i]][cycle[(i + 1) % len(cycle)]].get("amount", 0)
                    for i in range(len(cycle))
                    if dg.has_edge(cycle[i], cycle[(i + 1) % len(cycle)])
                )
                if cycle_amount > _MIN_CYCLE_AMOUNT:
                    return True
    except Exception:
        pass

    return False
