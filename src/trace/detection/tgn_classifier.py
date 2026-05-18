"""Temporal Graph Network (TGN) AML classifier — PyG 2.7.0 compatible.

Architecture:
  TGNMemory (IdentityMessage + LastAggregator) → per-node memory vectors
  → TransformerConv GNN embedding layer → MLP fraud classifier

Public API matches gnn_classifier.py:
  train(feature_df, labels, graph, transactions, save=True) -> (model, train_auc, test_auc)
  load()  -> (model, node_map)
  score(model, graph, account_ids, node_map=None) -> dict[str, float]
  model_exists() -> bool
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import TYPE_CHECKING

import networkx as nx
import numpy as np
import torch
import torch.nn as nn
from sklearn.metrics import roc_auc_score
from torch_geometric.data import TemporalData
from torch_geometric.loader import TemporalDataLoader
from torch_geometric.nn import TransformerConv
from torch_geometric.nn.models import TGNMemory

if TYPE_CHECKING:
    pass

_MODEL_PATH = Path("models/tgn_classifier.pt")

_MEMORY_DIM = 64
_TIME_DIM = 32
_MSG_DIM = 9
_EMBED_DIM = 64
_HIDDEN_DIM = 32
_DROPOUT = 0.3
_BATCH_SIZE = 200
_EPOCHS = 15
_LR = 0.0005
_TRAIN_SPLIT = 0.80


# ---------------------------------------------------------------------------
# Required TGN helper modules (removed from PyG 2.7.0 core)
# ---------------------------------------------------------------------------

class _IdentityMessage(nn.Module):
    """Concatenates source memory, destination memory, raw message, time encoding."""

    def __init__(self, raw_msg_dim: int, memory_dim: int, time_dim: int) -> None:
        super().__init__()
        self.out_channels = raw_msg_dim + 2 * memory_dim + time_dim

    def forward(
        self,
        z_src: torch.Tensor,
        z_dst: torch.Tensor,
        raw_msg: torch.Tensor,
        t_enc: torch.Tensor,
    ) -> torch.Tensor:
        return torch.cat([z_src, z_dst, raw_msg, t_enc], dim=-1)


class _LastAggregator(nn.Module):
    """Keeps only the most recent message per destination node.

    Sorts messages by timestamp ascending so the last scatter write
    (highest timestamp) overwrites earlier ones — no scatter_argmax needed.
    """

    def forward(
        self,
        msg: torch.Tensor,
        index: torch.Tensor,
        t: torch.Tensor,
        dim_size: int,
    ) -> torch.Tensor:
        out = msg.new_zeros((dim_size, msg.size(-1)))
        if index.numel() == 0:
            return out
        # Sort ascending by time so later (higher-t) writes win
        perm = torch.argsort(t)
        sorted_idx = index[perm].unsqueeze(-1).expand(-1, msg.size(-1))
        out.scatter_(0, sorted_idx, msg[perm])
        return out


# ---------------------------------------------------------------------------
# Full model definition
# ---------------------------------------------------------------------------

class TGNClassifier(nn.Module):
    """TGNMemory + TransformerConv embedding + MLP fraud head."""

    def __init__(self, num_nodes: int) -> None:
        super().__init__()
        self.num_nodes = num_nodes

        msg_module = _IdentityMessage(_MSG_DIM, _MEMORY_DIM, _TIME_DIM)
        agg_module = _LastAggregator()

        self.memory = TGNMemory(
            num_nodes=num_nodes,
            raw_msg_dim=_MSG_DIM,
            memory_dim=_MEMORY_DIM,
            time_dim=_TIME_DIM,
            message_module=msg_module,
            aggregator_module=agg_module,
        )

        self.gnn = TransformerConv(
            in_channels=_MEMORY_DIM,
            out_channels=_EMBED_DIM // 2,
            heads=2,
            dropout=_DROPOUT,
            edge_dim=None,
        )

        self.mlp = nn.Sequential(
            nn.Linear(_EMBED_DIM, _HIDDEN_DIM),
            nn.ReLU(),
            nn.Dropout(_DROPOUT),
            nn.Linear(_HIDDEN_DIM, 1),
        )

    def reset_memory(self) -> None:
        self.memory.reset_state()

    def detach_memory(self) -> None:
        self.memory.detach()

    def forward(
        self,
        src: torch.Tensor,
        dst: torch.Tensor,
        t: torch.Tensor,
        msg: torch.Tensor,
        edge_index: torch.Tensor,
        query_nodes: torch.Tensor,
    ) -> torch.Tensor:
        """Update memory from batch edges, embed, return logits for query_nodes."""
        # update_state processes edges through message/aggregator → GRU → memory
        self.memory.update_state(src, dst, t.long(), msg)
        # forward(n_id) retrieves current memory vectors
        n_id = torch.arange(self.num_nodes, device=src.device)
        z, _ = self.memory(n_id)          # [num_nodes, memory_dim]
        z_emb = self.gnn(z, edge_index)   # [num_nodes, embed_dim]
        return self.mlp(z_emb[query_nodes]).squeeze(-1)

    def get_all_scores(
        self,
        src: torch.Tensor,
        dst: torch.Tensor,
        t: torch.Tensor,
        msg: torch.Tensor,
        edge_index: torch.Tensor,
    ) -> torch.Tensor:
        """Process all edges and return sigmoid fraud scores for ALL nodes."""
        self.memory.update_state(src, dst, t.long(), msg)
        n_id = torch.arange(self.num_nodes, device=src.device)
        z, _ = self.memory(n_id)
        z_emb = self.gnn(z, edge_index)
        return torch.sigmoid(self.mlp(z_emb).squeeze(-1))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_edge_index(src: torch.Tensor, dst: torch.Tensor, num_nodes: int) -> torch.Tensor:
    """Build a static edge_index from unique (src, dst) pairs in the batch."""
    pairs = torch.stack([src, dst], dim=0)
    unique_pairs = torch.unique(pairs, dim=1)
    return unique_pairs


def _make_node_labels(node_map: dict[str, int], fraud_ids: set[str]) -> torch.Tensor:
    labels = torch.zeros(len(node_map), dtype=torch.float)
    for acc_id, idx in node_map.items():
        if acc_id in fraud_ids:
            labels[idx] = 1.0
    return labels


def _auc(probs: np.ndarray, labels: np.ndarray, node_indices: list[int]) -> float:
    if not node_indices:
        return 0.5
    y_t = labels[node_indices]
    y_s = probs[node_indices]
    if y_t.sum() == 0 or y_t.sum() == len(y_t):
        return 0.5
    return float(roc_auc_score(y_t, y_s))


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def train(
    feature_df,
    labels,
    graph: nx.MultiDiGraph,
    transactions,
    save: bool = True,
) -> tuple:
    """Train TGN classifier. Returns (model, train_auc, test_auc)."""
    from trace.graph.export import to_pyg

    fraud_ids: set[str] = set()
    for acc_id in graph.nodes():
        if str(acc_id).startswith("RING-"):
            fraud_ids.add(str(acc_id))
    if labels is not None:
        for acc_id, lbl in labels.items():
            if lbl == 1:
                fraud_ids.add(str(acc_id))
    # AMLSim data: HIGH kyc_risk accounts are fraud-labeled
    for node, data in graph.nodes(data=True):
        if data.get("kyc_risk") == "HIGH" and data.get("fraud_label", False):
            fraud_ids.add(str(node))

    print(f"[TGN] Fraud nodes: {len(fraud_ids)}  |  Total: {graph.number_of_nodes()}")
    print(f"[TGN] Edges: {graph.number_of_edges()}")

    if graph.number_of_edges() < 20:
        raise ValueError("Fewer than 20 edges — not enough to train TGN.")

    data, node_map = to_pyg(graph)
    num_nodes = len(node_map)
    num_edges = int(data.src.shape[0])

    split_idx = int(num_edges * _TRAIN_SPLIT)
    train_data = TemporalData(
        src=data.src[:split_idx],
        dst=data.dst[:split_idx],
        t=data.t[:split_idx],
        msg=data.msg[:split_idx],
    )
    test_data = TemporalData(
        src=data.src[split_idx:],
        dst=data.dst[split_idx:],
        t=data.t[split_idx:],
        msg=data.msg[split_idx:],
    )
    print(f"[TGN] Train edges: {split_idx}  Test edges: {num_edges - split_idx}")

    node_labels = _make_node_labels(node_map, fraud_ids)
    # CPU only — CUDA driver incompatible with this PyTorch build
    device = torch.device("cpu")
    print(f"[TGN] Device: {device}")

    model = TGNClassifier(num_nodes=num_nodes).to(device)

    n_pos = int(node_labels.sum().item())
    n_neg = num_nodes - n_pos
    pos_weight = torch.tensor([n_neg / max(n_pos, 1)], dtype=torch.float)
    criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
    optimizer = torch.optim.Adam(model.parameters(), lr=_LR)

    train_loader = TemporalDataLoader(train_data, batch_size=_BATCH_SIZE)
    node_labels_dev = node_labels.to(device)

    t_start = time.time()
    for epoch in range(1, _EPOCHS + 1):
        model.train()
        model.reset_memory()
        total_loss = 0.0
        n_batches = 0

        for batch in train_loader:
            optimizer.zero_grad()

            src = batch.src.to(device)
            dst = batch.dst.to(device)
            t_b = batch.t.to(device)
            msg = batch.msg.to(device)

            involved = torch.unique(torch.cat([src, dst]))
            edge_index = _build_edge_index(src, dst, num_nodes)

            logits = model(src, dst, t_b, msg, edge_index, involved)
            batch_labels = node_labels_dev[involved]

            loss = criterion(logits, batch_labels)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            model.detach_memory()

            total_loss += loss.item()
            n_batches += 1

        elapsed = time.time() - t_start
        print(f"  Epoch {epoch:02d}/{_EPOCHS}  loss={total_loss/max(n_batches,1):.4f}  {elapsed:.0f}s")

    # ── Evaluate train split ─────────────────────────────────────────────────
    model.eval()
    model.reset_memory()
    with torch.no_grad():
        src_tr = train_data.src.to(device)
        dst_tr = train_data.dst.to(device)
        t_tr = train_data.t.to(device)
        msg_tr = train_data.msg.to(device)
        ei_tr = _build_edge_index(src_tr, dst_tr, num_nodes)
        probs_tr = model.get_all_scores(src_tr, dst_tr, t_tr, msg_tr, ei_tr).cpu().numpy()

    labels_np = node_labels.numpy()
    touched_tr = list(set(train_data.src.tolist()) | set(train_data.dst.tolist()))
    train_auc = _auc(probs_tr, labels_np, touched_tr)

    # ── Evaluate test split (warm-up with train first) ───────────────────────
    model.reset_memory()
    with torch.no_grad():
        for batch in TemporalDataLoader(train_data, batch_size=_BATCH_SIZE):
            model.memory.update_state(
                batch.src.to(device), batch.dst.to(device),
                batch.t.long().to(device), batch.msg.to(device),
            )

        src_te = test_data.src.to(device)
        dst_te = test_data.dst.to(device)
        t_te = test_data.t.to(device)
        msg_te = test_data.msg.to(device)
        ei_te = _build_edge_index(src_te, dst_te, num_nodes)
        probs_te = model.get_all_scores(src_te, dst_te, t_te, msg_te, ei_te).cpu().numpy()

    touched_te = list(set(test_data.src.tolist()) | set(test_data.dst.tolist()))
    test_auc = _auc(probs_te, labels_np, touched_te)

    print(f"\n[TGN] Train AUC: {train_auc:.4f}  |  Test AUC: {test_auc:.4f}")
    print(f"[TGN] Fraud: {n_pos}/{num_nodes}  pos_weight: {n_neg/max(n_pos,1):.1f}x")

    if save:
        _MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
        torch.save({
            "model_state": model.state_dict(),
            "num_nodes": num_nodes,
            "node_map": node_map,
            "train_auc": train_auc,
            "test_auc": test_auc,
        }, _MODEL_PATH)
        print(f"[TGN] Saved → {_MODEL_PATH}")

    return model, train_auc, test_auc


def load() -> tuple:
    """Load saved TGN. Returns (model, node_map)."""
    if not _MODEL_PATH.exists():
        raise FileNotFoundError(f"No TGN model at {_MODEL_PATH}. Run train_tgn.py first.")
    ckpt = torch.load(_MODEL_PATH, map_location="cpu", weights_only=False)
    model = TGNClassifier(num_nodes=ckpt["num_nodes"])
    model.load_state_dict(ckpt["model_state"])
    model.eval()
    return model, ckpt["node_map"]


def score(
    model: TGNClassifier,
    graph: nx.MultiDiGraph,
    account_ids: list[str],
    node_map: dict[str, int] | None = None,
) -> dict[str, float]:
    """Score accounts. Returns {account_id: risk_probability}."""
    from trace.graph.export import to_pyg

    model.eval()
    model.reset_memory()

    if node_map is None:
        _, node_map = to_pyg(graph)

    data, _ = to_pyg(graph)
    if data.src.shape[0] == 0:
        return {acc_id: 0.0 for acc_id in account_ids}

    src = data.src
    dst = data.dst
    t = data.t
    msg = data.msg
    edge_index = _build_edge_index(src, dst, len(node_map))

    with torch.no_grad():
        all_probs = model.get_all_scores(src, dst, t, msg, edge_index).cpu().numpy()

    return {
        acc_id: float(all_probs[node_map[acc_id]])
        if acc_id in node_map and node_map[acc_id] < len(all_probs)
        else 0.0
        for acc_id in account_ids
    }


def model_exists() -> bool:
    return _MODEL_PATH.exists()
