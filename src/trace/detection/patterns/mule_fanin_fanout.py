"""Mule account detector -- high in-degree from disparate sources + immediate high out-degree."""

from __future__ import annotations

from datetime import timedelta

import networkx as nx

_MIN_IN = 6
_MIN_OUT = 4
_WINDOW_HOURS = 24


def detect(g: nx.MultiDiGraph, account_id: str) -> bool:
    if account_id not in g:
        return False

    in_edges = sorted(
        [
            (data["timestamp"], src, data.get("amount", 0.0))
            for src, _dst, data in g.in_edges(account_id, data=True)
            if data.get("timestamp") is not None
        ],
        key=lambda x: x[0],
    )
    out_edges = [
        (data["timestamp"], dst, data.get("amount", 0.0))
        for _src, dst, data in g.out_edges(account_id, data=True)
        if data.get("timestamp") is not None
    ]

    if not in_edges or not out_edges:
        return False

    for i in range(len(in_edges)):
        t_start = in_edges[i][0]
        t_end = t_start + timedelta(hours=_WINDOW_HOURS)
        w_in = [(t, s, a) for t, s, a in in_edges if t_start <= t <= t_end]
        w_out = [(t, d, a) for t, d, a in out_edges if t_start <= t <= t_end]

        if len(w_in) >= _MIN_IN and len(w_out) >= _MIN_OUT:
            unique_senders = len({s for _, s, _ in w_in})
            if unique_senders >= max(3, _MIN_IN // 2):
                return True

    return False
