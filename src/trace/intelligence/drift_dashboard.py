"""Drift dashboard -- ADWIN event log for the live retraining demo.

Records drift events from OnlineScorer and persists them so the
frontend DriftTimeline can poll /alerts/drift-events.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

_EVENTS_PATH = Path("data/processed/drift_events.json")


def record_drift_event(
    account_id: str,
    score_before: float,
    score_after: float,
    timestamp: str | None = None,
) -> None:
    _EVENTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    events = _load_events()
    events.append({
        "account_id": account_id,
        "timestamp": timestamp or datetime.now(timezone.utc).isoformat(),
        "score_before": round(score_before, 4),
        "score_after": round(score_after, 4),
    })
    _EVENTS_PATH.write_text(json.dumps(events, indent=2))


def get_drift_events(scorer=None, since: str | None = None) -> list[dict]:
    """Return drift events from scorer (in-memory) + persisted file.

    scorer: OnlineScorer instance -- drains its in-memory events first.
    since: ISO timestamp string -- filter events after this time.
    """
    events: list[dict] = []

    if scorer is not None:
        live = scorer.drain_drift_events()
        for ev in live:
            record_drift_event(
                ev["account_id"],
                ev["score_before"],
                ev["score_after"],
                ev["timestamp"],
            )
        events.extend(live)

    persisted = _load_events()
    # Merge without duplicating events already drained from scorer
    existing_ts = {e["timestamp"] for e in events}
    for ev in persisted:
        if ev["timestamp"] not in existing_ts:
            events.append(ev)

    if since:
        events = [e for e in events if e["timestamp"] >= since]

    events.sort(key=lambda e: e["timestamp"])
    return events


def _load_events() -> list[dict]:
    if not _EVENTS_PATH.exists():
        return []
    try:
        return json.loads(_EVENTS_PATH.read_text()) or []
    except Exception:
        return []
