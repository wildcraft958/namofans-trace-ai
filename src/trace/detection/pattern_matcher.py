"""Module A — Graph pattern matcher.

Detects 5 AML typologies via NetworkX algorithms:
  1. Circular flow / round-tripping  (simple_cycles)
  2. Layering chains                 (temporal path analysis, ≥4 hops)
  3. Structuring                     (sub-threshold clustering)
  4. Mule fan-in / fan-out           (degree centrality + community)
  5. Dormant account burst           (temporal burst analysis)
"""

from __future__ import annotations

from .patterns import (
    circular_flow,
    dormant_burst,
    layering,
    mule_fanin_fanout,
    structuring,
)

_PATTERN_SEVERITY = {
    "circular_flow": 0.90,  # round-tripping is a clear fraud indicator
    "mule": 0.90,           # fan-in/fan-out is an explicit mule signal
    "layering": 0.85,       # multi-hop layering is the hallmark of ML
    "structuring": 0.80,    # sub-threshold splitting is CTR avoidance
    "dormant_burst": 0.75,  # dormant burst has some legitimate explanations
}


def score_account(g, account_id: str) -> dict:
    """Run all 5 pattern detectors against an account. Return matched typologies + score."""
    matches = {
        "circular_flow": circular_flow.detect(g, account_id),
        "layering": layering.detect(g, account_id),
        "structuring": structuring.detect(g, account_id),
        "mule": mule_fanin_fanout.detect(g, account_id),
        "dormant_burst": dormant_burst.detect(g, account_id),
    }
    fired = [k for k, v in matches.items() if v]
    if not fired:
        pattern_score = 0.0
    else:
        # Driven by the highest-severity pattern detected;
        # each additional confirmed pattern adds a 0.05 confirmation boost.
        base = max(_PATTERN_SEVERITY[p] for p in fired)
        boost = 0.05 * (len(fired) - 1)
        pattern_score = min(1.0, base + boost)
    return {"score": pattern_score, "matches": matches}
