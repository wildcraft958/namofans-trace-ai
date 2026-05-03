"""Layering — multi-hop chains, ≥4 hops, funds forwarded >70%, within 48-hour window."""

from __future__ import annotations


def detect(g, account_id: str) -> bool:
    raise NotImplementedError("DFS bounded by depth; compare hop amounts for forwarding ratio.")
