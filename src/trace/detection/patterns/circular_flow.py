"""Circular flow / round-tripping detector.

Cycles ≥ 3 nodes, within a 72-hour window, cumulative amount > ₹1L.
"""

from __future__ import annotations


def detect(g, account_id: str) -> bool:
    raise NotImplementedError("Use nx.simple_cycles on a temporally-windowed subgraph.")
