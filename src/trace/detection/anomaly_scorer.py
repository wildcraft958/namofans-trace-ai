"""Module C -- Online anomaly scorer with River HalfSpaceTrees + ADWIN drift.

Per-account streaming baseline. Updates per transaction. No batch retraining.
"""

from __future__ import annotations

from datetime import datetime, timezone

from river import anomaly, drift


class OnlineScorer:
    def __init__(self) -> None:
        self._models: dict[str, anomaly.HalfSpaceTrees] = {}
        self._drift: dict[str, drift.ADWIN] = {}
        self._prev_scores: dict[str, float] = {}
        self._drift_events: list[dict] = []

    def update(self, account_id: str, features: dict[str, float]) -> float:
        if account_id not in self._models:
            self._models[account_id] = anomaly.HalfSpaceTrees(seed=42)
            self._drift[account_id] = drift.ADWIN()

        model = self._models[account_id]
        drift_det = self._drift[account_id]

        score_before = self._prev_scores.get(account_id, 0.0)
        score = float(model.score_one(features))
        model.learn_one(features)
        drift_det.update(score)

        if drift_det.drift_detected:
            self._drift_events.append({
                "account_id": account_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "score_before": round(score_before, 4),
                "score_after": round(score, 4),
            })

        self._prev_scores[account_id] = score
        return score

    def has_drift(self, account_id: str) -> bool:
        d = self._drift.get(account_id)
        return bool(d.drift_detected) if d is not None else False

    def drain_drift_events(self) -> list[dict]:
        events, self._drift_events = self._drift_events, []
        return events


_global_scorer = OnlineScorer()


def get_scorer() -> OnlineScorer:
    return _global_scorer
