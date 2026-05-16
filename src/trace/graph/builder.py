"""Build NetworkX MultiDiGraph from transactions."""

from __future__ import annotations

import pickle
from pathlib import Path
from trace.data.generator import Account, Transaction

import networkx as nx


def build_graph(accounts: list[Account], transactions: list[Transaction]) -> nx.MultiDiGraph:
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
            fraud_label=txn.fraud_label,
            fraud_type=txn.fraud_type,
        )
    return g


def build_from_generator(
    num_accounts: int = 5_000,
    num_transactions: int = 100_000,
    seed: int = 42,
    output_dir: Path | None = None,
) -> nx.MultiDiGraph:
    from trace.data.generator import generate
    accounts, transactions = generate(
        num_accounts=num_accounts,
        num_transactions=num_transactions,
        seed=seed,
        output_dir=output_dir,
    )
    return build_graph(accounts, transactions)


def save_graph(g: nx.MultiDiGraph, path: Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump(g, f, protocol=pickle.HIGHEST_PROTOCOL)


def load_graph(path: Path) -> nx.MultiDiGraph:
    with open(path, "rb") as f:
        return pickle.load(f)


def graph_to_viz(g: nx.MultiDiGraph, risk_map: dict[str, str] | None = None, limit: int = 1000) -> dict:
    """Convert graph to {nodes, links} format for frontend force-graph."""
    risk_map = risk_map or {}
    nodes = []
    seen_nodes = set()
    for node_id, data in list(g.nodes(data=True))[:limit]:
        nodes.append({
            "id": node_id,
            "account_type": data.get("account_type", "SAVINGS"),
            "kyc_risk": data.get("kyc_risk", "LOW"),
            "dormant_days": data.get("dormant_days", 0),
            "risk_level": risk_map.get(node_id, "LOW"),
            "name": data.get("name", ""),
        })
        seen_nodes.add(node_id)

    links = []
    for src, dst, data in g.edges(data=True):
        if src in seen_nodes and dst in seen_nodes:
            links.append({
                "source": src,
                "target": dst,
                "amount": data.get("amount", 0),
                "channel": data.get("channel", ""),
                "fraud_type": data.get("fraud_type", ""),
            })
            if len(links) >= limit * 3:
                break

    flagged_count = sum(1 for v in risk_map.values() if v != "LOW")
    return {
        "nodes": nodes,
        "links": links,
        "summary": {
            "total_nodes": g.number_of_nodes(),
            "total_edges": g.number_of_edges(),
            "flagged_nodes": flagged_count,
        },
    }


def get_subgraph(g: nx.MultiDiGraph, account_id: str, depth: int = 2) -> nx.MultiDiGraph:
    """BFS subgraph around account_id up to given depth."""
    reachable = {account_id}
    frontier = {account_id}
    for _ in range(depth):
        next_frontier = set()
        for node in frontier:
            next_frontier.update(g.successors(node))
            next_frontier.update(g.predecessors(node))
        next_frontier -= reachable
        reachable.update(next_frontier)
        frontier = next_frontier
    return g.subgraph(reachable).copy()  # type: ignore[return-value]
