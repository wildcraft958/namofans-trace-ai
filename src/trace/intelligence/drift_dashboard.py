"""Drift dashboard — timeline of ADWIN drift events for the live retraining demo."""

from __future__ import annotations


def get_drift_events(scorer, since=None) -> list[dict]:
    """Return list of {account_id, timestamp, score_before, score_after} drift events."""
    raise NotImplementedError
