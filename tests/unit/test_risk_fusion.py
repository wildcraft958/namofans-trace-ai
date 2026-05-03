"""Unit tests for risk fusion."""

from trace.detection.risk_fusion import fuse


def test_fuse_low():
    s = fuse(0.1, 0.1, 0.1, 0.1)
    assert s.composite < 0.5
    assert s.level == "LOW"


def test_fuse_critical():
    s = fuse(1.0, 1.0, 1.0, 1.0)
    assert s.composite == 1.0
    assert s.level == "CRITICAL"


def test_contributions_sum_to_composite():
    s = fuse(0.5, 0.6, 0.7, 0.8)
    assert abs(sum(s.contributions.values()) - s.composite) < 1e-9
