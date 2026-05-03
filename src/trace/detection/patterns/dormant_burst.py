"""Dormant account burst — inactive >90 days then >3 high-value txns within 48 hours."""

from __future__ import annotations


def detect(g, account_id: str) -> bool:
    raise NotImplementedError
