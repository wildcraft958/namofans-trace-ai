"""GNNExplainer wrapper — extracts the subgraph + edge mask that explains a flag.

Used by the dashboard "Why?" button. Returns top-k contributing edges/nodes.

Implementation: gradient-based edge saliency for TGNMemory models.
For each edge, we compute |d(fraud_logit) / d(msg_features)| to rank edges by
their contribution to the fraud score for the queried account node.
This is compatible with TGN's stateful memory (pure GNNExplainer permutation
masking is not, because memory state is non-differentiable across restarts).
"""

from __future__ import annotations

import torch
import torch.nn as nn


def explain_account(
    model: nn.Module,
    src: torch.Tensor,
    dst: torch.Tensor,
    t: torch.Tensor,
    msg: torch.Tensor,
    edge_index: torch.Tensor,
    account_idx: int,
    top_k: int = 5,
) -> dict:
    """Return the top-k edges most responsible for the fraud score of account_idx.

    Args:
        model: TGNClassifier (must be in eval mode)
        src, dst, t, msg: edge tensors (same format as training)
        edge_index: static edge_index tensor [2, E]
        account_idx: integer node index to explain
        top_k: number of top edges to return

    Returns:
        {
            "account_idx": int,
            "fraud_score": float,
            "top_edges": [{"src": int, "dst": int, "saliency": float}, ...],
            "top_nodes": [int, ...],
        }
    """
    model.eval()
    model.reset_memory()

    msg_grad = msg.float().detach().requires_grad_(True)

    # Forward pass with gradient tracking on msg
    model.memory.update_state(src, dst, t.long(), msg_grad)
    n_id = torch.arange(model.num_nodes, device=src.device)
    z, _ = model.memory(n_id)
    z_emb = model.gnn(z, edge_index)
    logit = model.mlp(z_emb[account_idx]).squeeze(-1)
    fraud_score = torch.sigmoid(logit).item()

    # Backward to get per-edge-message gradient
    logit.backward()

    if msg_grad.grad is not None:
        # Saliency: L1 norm of gradient across message feature dimension
        saliency = msg_grad.grad.abs().sum(dim=-1).detach().cpu().numpy()
    else:
        saliency = [0.0] * len(src)

    src_np = src.cpu().numpy()
    dst_np = dst.cpu().numpy()

    # Rank edges by saliency
    import numpy as np
    order = np.argsort(saliency)[::-1]
    top_edges = [
        {
            "src": int(src_np[i]),
            "dst": int(dst_np[i]),
            "saliency": float(saliency[i]),
        }
        for i in order[:top_k]
    ]
    top_nodes = list({int(src_np[i]) for i in order[:top_k]} |
                     {int(dst_np[i]) for i in order[:top_k]})

    model.reset_memory()
    return {
        "account_idx": account_idx,
        "fraud_score": fraud_score,
        "top_edges": top_edges,
        "top_nodes": top_nodes,
    }
