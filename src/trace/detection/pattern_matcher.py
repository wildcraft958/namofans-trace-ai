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


def score_account(g, account_id: str) -> dict:
    """Run all 5 pattern detectors against an account. Return matched typologies + score."""
    matches = {}
    matches["circular_flow"] = circular_flow.detect(g, account_id)
    matches["layering"] = layering.detect(g, account_id)
    matches["structuring"] = structuring.detect(g, account_id)
    matches["mule"] = mule_fanin_fanout.detect(g, account_id)
    matches["dormant_burst"] = dormant_burst.detect(g, account_id)
    pattern_score = sum(1 for v in matches.values() if v) / len(matches)
    return {"score": pattern_score, "matches": matches}
