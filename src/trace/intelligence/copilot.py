"""Module G — NL Investigation Copilot. Translates English → graph queries.

Six canned queries are pre-cached for demo reliability:
  1. "Show all circular flows above ₹X in the last N days"
  2. "Which accounts sent funds to dormant accounts yesterday?"
  3. "Give me the full fund trail for ACC-####"
  4. "Flag all high KYC risk accounts that transferred >₹X to the same beneficiary"
  5. "Top 10 highest-degree accounts in the last 7 days"
  6. "Accounts with sudden velocity change > 5x baseline"
"""

from __future__ import annotations


def run(nl_query: str, graph) -> dict:
    """Returns {result_nodes, result_edges, summary, latency_ms}."""
    raise NotImplementedError("LLM → NetworkX call → JSON.")
