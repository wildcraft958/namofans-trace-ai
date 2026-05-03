"""Graph endpoints — full graph + per-account subgraph."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("")
def get_graph(limit: int = 1000) -> dict:
    """Return the full graph in {nodes, links} viz format."""
    raise NotImplementedError


@router.get("/{account_id}")
def get_account_subgraph(account_id: str, depth: int = 2) -> dict:
    raise NotImplementedError
