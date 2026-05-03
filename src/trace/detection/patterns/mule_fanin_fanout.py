"""Mule account detector — high in-degree from disparate communities + immediate high out-degree."""

from __future__ import annotations


def detect(g, account_id: str) -> bool:
    raise NotImplementedError("In/out degree centrality + Louvain community detection.")
