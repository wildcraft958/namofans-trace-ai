"""Unit tests for all 5 pattern detectors using seeded fraud rings from generator.py."""

from __future__ import annotations

from trace.data.generator import generate
from trace.detection.patterns import (
    circular_flow,
    dormant_burst,
    layering,
    mule_fanin_fanout,
    structuring,
)
from trace.graph.builder import build_graph

import pytest


@pytest.fixture(scope="module")
def graph():
    accounts, transactions = generate(num_accounts=500, num_transactions=5_000, seed=42)
    return build_graph(accounts, transactions)


class TestCircularFlow:
    def test_detects_seeded_ring(self, graph):
        # RING-CF-00..04 form a circular ring
        assert circular_flow.detect(graph, "RING-CF-00") is True

    def test_clean_account_not_flagged(self, graph):
        # ACC-00001 is a clean account with no seeded pattern
        assert circular_flow.detect(graph, "ACC-00001") is False

    def test_missing_account_returns_false(self, graph):
        assert circular_flow.detect(graph, "NONEXISTENT") is False


class TestLayering:
    def test_detects_seeded_chain(self, graph):
        # RING-LY-00 starts a 5-hop layering chain
        assert layering.detect(graph, "RING-LY-00") is True

    def test_clean_account_not_flagged(self, graph):
        assert layering.detect(graph, "ACC-00002") is False

    def test_missing_account_returns_false(self, graph):
        assert layering.detect(graph, "NONEXISTENT") is False


class TestStructuring:
    def test_detects_seeded_structuring(self, graph):
        # RING-ST-00 sends 4x Rs 9.5L same-day
        assert structuring.detect(graph, "RING-ST-00") is True

    def test_clean_account_not_flagged(self, graph):
        assert structuring.detect(graph, "ACC-00003") is False

    def test_missing_account_returns_false(self, graph):
        assert structuring.detect(graph, "NONEXISTENT") is False


class TestMuleFanInFanOut:
    def test_detects_mule_aggregator(self, graph):
        # RING-MU-00 receives from 12 senders and sends to 8 receivers
        assert mule_fanin_fanout.detect(graph, "RING-MU-00") is True

    def test_clean_account_not_flagged(self, graph):
        assert mule_fanin_fanout.detect(graph, "ACC-00004") is False

    def test_missing_account_returns_false(self, graph):
        assert mule_fanin_fanout.detect(graph, "NONEXISTENT") is False


class TestDormantBurst:
    def test_detects_dormant_burst(self, graph):
        # RING-DB-00 has dormant_days=95 and 5x Rs 8L burst
        assert dormant_burst.detect(graph, "RING-DB-00") is True

    def test_clean_account_not_flagged(self, graph):
        # ACC-00005 has dormant_days < 90 from generator
        assert dormant_burst.detect(graph, "ACC-00005") is False

    def test_missing_account_returns_false(self, graph):
        assert dormant_burst.detect(graph, "NONEXISTENT") is False
