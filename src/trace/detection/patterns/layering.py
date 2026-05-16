"""Layering -- multi-hop chains, >=4 hops, funds forwarded >70%, within 48-hour window."""

from __future__ import annotations

from datetime import timedelta

import networkx as nx


def detect(g: nx.MultiDiGraph, account_id: str) -> bool:
    if account_id not in g:
        return False

    account_times = [
        data["timestamp"]
        for src, _dst, data in g.edges(data=True)
        if src == account_id and data.get("timestamp") is not None
    ]
    if not account_times:
        return False

    window_start = min(account_times)
    window_end = window_start + timedelta(hours=48)

    dg = nx.DiGraph()
    for src, dst, data in g.edges(data=True):
        ts = data.get("timestamp")
        if ts is None or not (window_start <= ts <= window_end):
            continue
        amt = data.get("amount", 0.0)
        if dg.has_edge(src, dst):
            dg[src][dst]["amount"] = max(dg[src][dst]["amount"], amt)
        else:
            dg.add_edge(src, dst, amount=amt)

    if account_id not in dg:
        return False

    def _dfs(node: str, path: list[str], in_amount: float) -> bool:
        if len(path) >= 5:  # 5 nodes = 4 hops
            return True
        for succ in dg.successors(node):
            if succ in path:
                continue
            out_amount = dg[node][succ].get("amount", 0.0)
            if in_amount > 0 and (out_amount / in_amount) < 0.70:
                continue
            if _dfs(succ, [*path, succ], out_amount):
                return True
        return False

    for succ in dg.successors(account_id):
        out_amount = dg[account_id][succ].get("amount", 0.0)
        if _dfs(succ, [account_id, succ], out_amount):
            return True

    return False
