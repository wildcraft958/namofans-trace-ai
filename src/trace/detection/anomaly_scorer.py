"""Module C — Online anomaly scorer with River HalfSpaceTrees + ADWIN drift.

Per-account streaming baseline. Updates per transaction. No batch retraining.
"""

from __future__ import annotations

from river import anomaly, drift


class OnlineScorer:
    def __init__(self) -> None:
        self.models: dict[str, anomaly.HalfSpaceTrees] = {}
        self.drift: dict[str, drift.ADWIN] = {}

    def update(self, account_id: str, features: dict[str, float]) -> float:
        if account_id not in self.models:
            self.models[account_id] = anomaly.HalfSpaceTrees(seed=42)
            self.drift[account_id] = drift.ADWIN()
        score = self.models[account_id].score_one(features)
        self.models[account_id].learn_one(features)
        self.drift[account_id].update(score)
        return score

    def has_drift(self, account_id: str) -> bool:
        return self.drift.get(account_id, drift.ADWIN()).drift_detected
