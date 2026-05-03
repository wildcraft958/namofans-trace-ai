"""Feature engineering for online anomaly + GraphSAGE."""

from __future__ import annotations


def build_account_features():
    """Per-account features: degree, txn velocity, amount variance, etc."""
    raise NotImplementedError
