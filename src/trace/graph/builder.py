"""Build NetworkX MultiDiGraph from transactions."""

from __future__ import annotations

import networkx as nx


def build_graph(accounts, transactions) -> nx.MultiDiGraph:
    g = nx.MultiDiGraph()
    for acc in accounts:
        g.add_node(acc.account_id, **acc.__dict__)
    for txn in transactions:
        g.add_edge(
            txn.sender,
            txn.receiver,
            key=txn.txn_id,
            amount=txn.amount,
            timestamp=txn.timestamp,
            channel=txn.channel,
        )
    return g
