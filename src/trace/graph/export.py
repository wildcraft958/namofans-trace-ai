"""Export NetworkX graph to PyG Data, Neo4j, JSON for visualization."""

from __future__ import annotations


def to_pyg(g):
    """NetworkX → torch_geometric.data.Data."""
    raise NotImplementedError


def to_viz_json(g) -> dict:
    """NetworkX → {nodes: [...], links: [...]} for react-force-graph-3d."""
    raise NotImplementedError
