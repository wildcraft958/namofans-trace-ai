"""Export NetworkX graph to PyG TemporalData, JSON for visualization."""

from __future__ import annotations

from datetime import datetime, timezone

import networkx as nx
import torch
from torch_geometric.data import TemporalData

# Channel one-hot encoding order (matches generator._CHANNELS)
_CHANNELS = ["UPI", "NEFT", "IMPS", "RTGS", "ATM"]
_CHANNEL_IDX = {c: i for i, c in enumerate(_CHANNELS)}

# Max amount used for normalisation (₹1 Crore cap)
_MAX_AMOUNT = 10_000_000.0


def _ts_to_unix(ts) -> float:
    """Convert datetime (or already-float) to Unix seconds."""
    if isinstance(ts, (int, float)):
        return float(ts)
    if isinstance(ts, datetime):
        if ts.tzinfo is None:
            # treat as UTC
            return ts.replace(tzinfo=timezone.utc).timestamp()
        return ts.timestamp()
    raise TypeError(f"Cannot convert {type(ts)} to unix timestamp")


def _channel_onehot(channel: str) -> list[float]:
    idx = _CHANNEL_IDX.get(channel, 0)
    oh = [0.0] * len(_CHANNELS)
    oh[idx] = 1.0
    return oh


def _build_edge_features(amount: float, channel: str, ts_unix: float) -> list[float]:
    """
    9-dimensional edge feature vector:
      [0]      normalised amount  (clipped to [0,1])
      [1..5]   channel one-hot    (UPI, NEFT, IMPS, RTGS, ATM)
      [6]      hour_of_day / 24
      [7]      day_of_week / 7
    Total: 1 + 5 + 1 + 1 = 8 dims  → padded to 9 with a bias constant 1.0
    """
    norm_amount = min(amount / _MAX_AMOUNT, 1.0)
    ch_oh = _channel_onehot(channel)

    dt = datetime.utcfromtimestamp(ts_unix)
    hour_norm = dt.hour / 24.0
    dow_norm = dt.weekday() / 7.0

    return [norm_amount, *ch_oh, hour_norm, dow_norm, 1.0]  # 9 dims


def to_pyg(g: nx.MultiDiGraph) -> tuple[TemporalData, dict[str, int]]:
    """Convert a NetworkX MultiDiGraph to PyG TemporalData.

    Returns
    -------
    data : TemporalData
        Fields: src, dst, t (float unix seconds), msg (float32 [E, 9])
    node_map : dict[str, int]
        Maps account_id -> integer node index used in src/dst tensors.
    """
    # Build a stable node index (sorted for reproducibility).
    nodes = sorted(g.nodes())
    node_map: dict[str, int] = {n: i for i, n in enumerate(nodes)}

    # Collect all edges sorted by timestamp.
    edge_records: list[tuple[float, int, int, list[float]]] = []
    for u, v, data in g.edges(data=True):
        ts_unix = _ts_to_unix(data["timestamp"])
        amount = float(data.get("amount", 0.0))
        channel = str(data.get("channel", "UPI"))
        feats = _build_edge_features(amount, channel, ts_unix)
        edge_records.append((ts_unix, node_map[u], node_map[v], feats))

    # Sort chronologically — TGN requires temporal ordering.
    edge_records.sort(key=lambda r: r[0])

    if not edge_records:
        # Return empty TemporalData with correct shapes.
        data = TemporalData(
            src=torch.zeros(0, dtype=torch.long),
            dst=torch.zeros(0, dtype=torch.long),
            t=torch.zeros(0, dtype=torch.float),
            msg=torch.zeros((0, 9), dtype=torch.float),
        )
        return data, node_map

    ts_list = [r[0] for r in edge_records]
    src_list = [r[1] for r in edge_records]
    dst_list = [r[2] for r in edge_records]
    msg_list = [r[3] for r in edge_records]

    data = TemporalData(
        src=torch.tensor(src_list, dtype=torch.long),
        dst=torch.tensor(dst_list, dtype=torch.long),
        t=torch.tensor(ts_list, dtype=torch.float),
        msg=torch.tensor(msg_list, dtype=torch.float),
    )
    return data, node_map


def to_viz_json(g: nx.MultiDiGraph, risk_map: dict[str, str] | None = None, limit: int = 1000) -> dict:
    """NetworkX → {nodes: [...], links: [...]} for react-force-graph-3d."""
    from trace.graph.builder import graph_to_viz
    return graph_to_viz(g, risk_map=risk_map, limit=limit)
