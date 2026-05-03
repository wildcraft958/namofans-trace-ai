"""Module B — Graph Neural Network classifier.

Phase 2 ships GraphSAGE + temporal features (not full TGN).
TGN deferred to v2; see DECISIONS.md ADR-0002.

Trains on AMLSim. Inference is CPU-only.
"""

from __future__ import annotations

import torch
from torch_geometric.nn import SAGEConv


class GraphSAGEClassifier(torch.nn.Module):
    def __init__(self, in_channels: int, hidden: int = 64, num_classes: int = 2):
        super().__init__()
        self.conv1 = SAGEConv(in_channels, hidden)
        self.conv2 = SAGEConv(hidden, hidden)
        self.head = torch.nn.Linear(hidden, num_classes)

    def forward(self, x, edge_index):
        h = self.conv1(x, edge_index).relu()
        h = self.conv2(h, edge_index).relu()
        return self.head(h)


def train(data, epochs: int = 50):
    """Train on AMLSim PyG Data with focal loss. Use GraphSMOTE for imbalance."""
    raise NotImplementedError


def score(model, data) -> dict[str, float]:
    """Return per-account suspicious probability."""
    raise NotImplementedError
