"""Module E — Risk fusion. Weighted composite of pattern + GNN + anomaly + compliance."""

from __future__ import annotations

from dataclasses import dataclass

W_PATTERN = 0.30
W_GNN = 0.30
W_ANOMALY = 0.20
W_COMPLIANCE = 0.20


@dataclass
class RiskScore:
    composite: float
    level: str  # CRITICAL | HIGH | MEDIUM | LOW
    contributions: dict[str, float]


def fuse(pattern: float, gnn: float, anomaly: float, compliance: float) -> RiskScore:
    composite = (
        W_PATTERN * pattern
        + W_GNN * gnn
        + W_ANOMALY * anomaly
        + W_COMPLIANCE * compliance
    )
    level = (
        "CRITICAL" if composite >= 0.85
        else "HIGH" if composite >= 0.70
        else "MEDIUM" if composite >= 0.50
        else "LOW"
    )
    return RiskScore(
        composite=composite,
        level=level,
        contributions={
            "pattern": W_PATTERN * pattern,
            "gnn": W_GNN * gnn,
            "anomaly": W_ANOMALY * anomaly,
            "compliance": W_COMPLIANCE * compliance,
        },
    )
