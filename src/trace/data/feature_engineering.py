"""Feature engineering for graph-based fraud classifier.

Extracts 11 features per account from the NetworkX graph.
"""

from __future__ import annotations

from datetime import timedelta

import networkx as nx
import numpy as np
import pandas as pd

_KYC_SCORE = {"LOW": 0.0, "MEDIUM": 0.5, "HIGH": 1.0}

FEATURE_COLS = [
    "degree_in", "degree_out", "pagerank", "clustering_coeff",
    "txn_velocity_7d", "avg_amount_out", "std_amount_out", "max_amount_out",
    "unique_counterparties", "dormant_days", "kyc_risk_score",
]


def extract_features(g: nx.MultiDiGraph, account_id: str) -> dict[str, float]:
    """Return 11-feature dict for a single account. All values are floats."""
    if account_id not in g:
        return {col: 0.0 for col in FEATURE_COLS}

    node_data = g.nodes[account_id]

    degree_in = float(g.in_degree(account_id))
    degree_out = float(g.out_degree(account_id))

    try:
        pr = nx.pagerank(g, max_iter=50, tol=1e-4).get(account_id, 0.0)
    except Exception:
        pr = 0.0

    try:
        ug = g.to_undirected(as_view=True)
        cc = float(nx.clustering(ug, account_id))
    except Exception:
        cc = 0.0

    out_edges = [
        (data.get("timestamp"), data.get("amount", 0.0), dst)
        for _, dst, data in g.out_edges(account_id, data=True)
    ]
    amounts = [a for _, a, _ in out_edges if a > 0]
    avg_amt = float(np.mean(amounts)) if amounts else 0.0
    std_amt = float(np.std(amounts)) if len(amounts) > 1 else 0.0
    max_amt = float(max(amounts)) if amounts else 0.0
    unique_cp = float(len({dst for _, _, dst in out_edges}))

    all_times = [t for t, _, _ in out_edges if t is not None]
    if all_times:
        max_time = max(all_times)
        window_7d = max_time - timedelta(days=7)
        count_7d = sum(1 for t, _, _ in out_edges if t is not None and t >= window_7d)
        velocity = count_7d / 7.0
    else:
        velocity = 0.0

    dormant_days = float(node_data.get("dormant_days", 0))
    kyc_risk_score = _KYC_SCORE.get(str(node_data.get("kyc_risk", "LOW")), 0.0)

    return {
        "degree_in": degree_in,
        "degree_out": degree_out,
        "pagerank": pr,
        "clustering_coeff": cc,
        "txn_velocity_7d": velocity,
        "avg_amount_out": avg_amt,
        "std_amount_out": std_amt,
        "max_amount_out": max_amt,
        "unique_counterparties": unique_cp,
        "dormant_days": dormant_days,
        "kyc_risk_score": kyc_risk_score,
    }


def build_feature_matrix(
    g: nx.MultiDiGraph,
    accounts: list,
    pagerank_cache: dict[str, float] | None = None,
) -> pd.DataFrame:
    """Build feature matrix for all accounts. Returns DataFrame indexed by account_id."""
    if pagerank_cache is None:
        try:
            pagerank_cache = nx.pagerank(g, max_iter=100, tol=1e-4)
        except Exception:
            n = g.number_of_nodes()
            pagerank_cache = {node: 1.0 / n for node in g.nodes()}

    try:
        ug = g.to_undirected(as_view=True)
        clustering_cache = nx.clustering(ug)
    except Exception:
        clustering_cache = {}

    rows = []
    for acc in accounts:
        aid = acc.account_id
        if aid not in g:
            rows.append({"account_id": aid, **{col: 0.0 for col in FEATURE_COLS}})
            continue

        node_data = g.nodes[aid]
        degree_in = float(g.in_degree(aid))
        degree_out = float(g.out_degree(aid))
        pr = float(pagerank_cache.get(aid, 0.0))
        cc = float(clustering_cache.get(aid, 0.0))

        out_edges = [
            (data.get("timestamp"), data.get("amount", 0.0), dst)
            for _, dst, data in g.out_edges(aid, data=True)
        ]
        amounts = [a for _, a, _ in out_edges if a > 0]
        avg_amt = float(np.mean(amounts)) if amounts else 0.0
        std_amt = float(np.std(amounts)) if len(amounts) > 1 else 0.0
        max_amt = float(max(amounts)) if amounts else 0.0
        unique_cp = float(len({dst for _, _, dst in out_edges}))

        all_times = [t for t, _, _ in out_edges if t is not None]
        if all_times:
            max_time = max(all_times)
            window_7d = max_time - timedelta(days=7)
            count_7d = sum(1 for t, _, _ in out_edges if t is not None and t >= window_7d)
            velocity = count_7d / 7.0
        else:
            velocity = 0.0

        rows.append({
            "account_id": aid,
            "degree_in": degree_in,
            "degree_out": degree_out,
            "pagerank": pr,
            "clustering_coeff": cc,
            "txn_velocity_7d": velocity,
            "avg_amount_out": avg_amt,
            "std_amount_out": std_amt,
            "max_amount_out": max_amt,
            "unique_counterparties": unique_cp,
            "dormant_days": float(node_data.get("dormant_days", 0)),
            "kyc_risk_score": _KYC_SCORE.get(str(node_data.get("kyc_risk", "LOW")), 0.0),
        })

    df = pd.DataFrame(rows)
    df = df.set_index("account_id")
    df.index.name = "account_id"
    return df[FEATURE_COLS].fillna(0.0)
