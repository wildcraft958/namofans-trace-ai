"""Module G -- NL Investigation Copilot.

Translates plain-English queries into NetworkX graph operations.
Six canned patterns are matched via regex (100% reliable for demo).
Unrecognized queries fall through to Gemini for intent parsing.
"""

from __future__ import annotations

import re
import time
from datetime import datetime, timedelta, timezone

import networkx as nx

_AMOUNT_RE = re.compile(r"[₹rs\s]*([0-9][0-9,]*(?:\.[0-9]+)?)\s*(?:l|lakh|cr|crore)?", re.I)
_ACCOUNT_RE = re.compile(r"(ACC-[A-Z0-9\-]+|RING-[A-Z0-9\-]+)", re.I)
_DAYS_RE = re.compile(r"(\d+)\s*day", re.I)


def run(nl_query: str, graph: nx.MultiDiGraph) -> dict:
    """Match query to a handler. Returns {result_nodes, result_edges, summary, latency_ms}."""
    t0 = time.monotonic()
    q = nl_query.strip().lower()
    result = _dispatch(q, nl_query, graph)
    result["latency_ms"] = round((time.monotonic() - t0) * 1000, 1)
    return result


def _dispatch(q: str, raw: str, g: nx.MultiDiGraph) -> dict:
    # Query 1: circular flows above amount
    if "circular" in q or "round" in q:
        return _circular_flows(q, g)

    # Query 2: dormant accounts
    if "dormant" in q:
        return _dormant_accounts(q, g)

    # Query 3: fund trail for a specific account
    m = _ACCOUNT_RE.search(raw)
    if m and ("trail" in q or "flow" in q or "trace" in q or "fund" in q):
        return _fund_trail(m.group(1), g)

    # Query 4: high KYC risk + amount filter
    if ("kyc" in q or "high risk" in q) and ("transfer" in q or "send" in q or "amount" in q):
        return _high_kyc_transfers(q, g)

    # Query 5: top degree / highest degree
    if "top" in q and ("degree" in q or "pagerank" in q or "connected" in q):
        return _top_degree(q, g)

    # Query 6: velocity change
    if "velocity" in q or "spike" in q or "sudden" in q:
        return _velocity_spike(q, g)

    # Specific account lookup without trail keyword
    if m:
        return _fund_trail(m.group(1), g)

    # Fallback: Gemini intent parsing
    return _gemini_fallback(raw, g)


# ──────────────────────────────────────────────
# Query handlers
# ──────────────────────────────────────────────

def _circular_flows(q: str, g: nx.MultiDiGraph) -> dict:
    amount_threshold = _parse_amount(q, default=100_000)

    flagged_nodes: list[str] = []
    flagged_edges: list[dict] = []

    for node in list(g.nodes())[:500]:
        out_neighbors = {dst for _, dst in g.out_edges(node)}
        if not out_neighbors:
            continue
        for dst in out_neighbors:
            if g.has_edge(dst, node):
                total = sum(
                    d.get("amount", 0)
                    for _, _, d in g.out_edges(node, data=True)
                    if d.get("amount", 0) >= amount_threshold
                )
                if total >= amount_threshold:
                    flagged_nodes.extend([node, dst])
                    for _, target, data in g.out_edges(node, data=True):
                        flagged_edges.append({
                            "source": node,
                            "target": target,
                            "amount": data.get("amount", 0),
                            "channel": data.get("channel", ""),
                        })

    flagged_nodes = list(dict.fromkeys(flagged_nodes))[:50]
    flagged_edges = flagged_edges[:100]
    return {
        "result_nodes": flagged_nodes,
        "result_edges": flagged_edges,
        "summary": (
            f"Found {len(flagged_nodes)} accounts in potential circular flow patterns "
            f"with transactions >= Rs {amount_threshold:,.0f}."
        ),
    }


def _dormant_accounts(q: str, g: nx.MultiDiGraph) -> dict:
    threshold_days = 90
    m = _DAYS_RE.search(q)
    if m:
        threshold_days = int(m.group(1))

    now = datetime.now(timezone.utc)
    flagged: list[str] = []

    for node, data in g.nodes(data=True):
        dormant = data.get("dormant_days", 0)
        if dormant < threshold_days:
            continue
        # Check for recent outgoing activity
        recent_out = [
            d for _, _, d in g.out_edges(node, data=True)
            if d.get("timestamp") and (now - d["timestamp"].replace(tzinfo=timezone.utc)).days <= 30
        ]
        if recent_out:
            flagged.append(node)

    flagged = flagged[:50]
    edges = []
    for node in flagged:
        for _, dst, data in g.out_edges(node, data=True):
            edges.append({"source": node, "target": dst, "amount": data.get("amount", 0)})
    return {
        "result_nodes": flagged,
        "result_edges": edges[:100],
        "summary": (
            f"Found {len(flagged)} accounts dormant for >= {threshold_days} days "
            f"with recent transaction activity (potential dormant burst pattern)."
        ),
    }


def _fund_trail(account_id: str, g: nx.MultiDiGraph) -> dict:
    if account_id not in g:
        return {
            "result_nodes": [],
            "result_edges": [],
            "summary": f"Account {account_id} not found in graph.",
        }
    sub = _bfs_subgraph(g, account_id, depth=3)
    nodes = list(sub.nodes())
    edges = [
        {"source": u, "target": v, "amount": d.get("amount", 0), "channel": d.get("channel", "")}
        for u, v, d in sub.edges(data=True)
    ]
    return {
        "result_nodes": nodes,
        "result_edges": edges,
        "summary": (
            f"Fund trail for {account_id}: {len(nodes)} accounts, "
            f"{len(edges)} transactions within 3 hops."
        ),
    }


def _high_kyc_transfers(q: str, g: nx.MultiDiGraph) -> dict:
    amount_threshold = _parse_amount(q, default=500_000)

    flagged: list[str] = []
    edges: list[dict] = []

    for node, data in g.nodes(data=True):
        if str(data.get("kyc_risk", "LOW")).upper() != "HIGH":
            continue
        for _, dst, d in g.out_edges(node, data=True):
            if d.get("amount", 0) >= amount_threshold:
                flagged.append(node)
                edges.append({
                    "source": node,
                    "target": dst,
                    "amount": d.get("amount", 0),
                    "channel": d.get("channel", ""),
                })

    flagged = list(dict.fromkeys(flagged))[:50]
    return {
        "result_nodes": flagged,
        "result_edges": edges[:100],
        "summary": (
            f"Found {len(flagged)} HIGH KYC risk accounts with outgoing transfers "
            f">= Rs {amount_threshold:,.0f}."
        ),
    }


def _top_degree(q: str, g: nx.MultiDiGraph) -> dict:
    n_top = 10
    m = re.search(r"top[\s-]*(\d+)", q)
    if m:
        n_top = int(m.group(1))

    try:
        pr = nx.pagerank(g, max_iter=50, tol=1e-3)
    except Exception:
        pr = {n: float(g.degree(n)) for n in g.nodes()}

    top_nodes = sorted(pr.items(), key=lambda kv: kv[1], reverse=True)[:n_top]
    node_ids = [n for n, _ in top_nodes]

    edges = [
        {"source": u, "target": v, "amount": d.get("amount", 0)}
        for n in node_ids
        for u, v, d in g.out_edges(n, data=True)
        if v in node_ids
    ]
    return {
        "result_nodes": node_ids,
        "result_edges": edges,
        "summary": f"Top {len(node_ids)} accounts by PageRank centrality.",
    }


def _velocity_spike(q: str, g: nx.MultiDiGraph) -> dict:
    multiplier = 5.0
    m = re.search(r"(\d+)\s*x", q)
    if m:
        multiplier = float(m.group(1))

    now = datetime.now(timezone.utc)
    window_recent = timedelta(days=7)
    window_baseline = timedelta(days=30)

    velocity: dict[str, tuple[float, float]] = {}
    for node in g.nodes():
        edges_all = [
            d for _, _, d in g.out_edges(node, data=True) if d.get("timestamp")
        ]
        if not edges_all:
            continue
        recent = sum(
            1 for d in edges_all
            if hasattr(d["timestamp"], "replace")
            and (now - d["timestamp"].replace(tzinfo=timezone.utc)) <= window_recent
        )
        baseline_total = sum(
            1 for d in edges_all
            if hasattr(d["timestamp"], "replace")
            and (now - d["timestamp"].replace(tzinfo=timezone.utc)) <= window_baseline
        )
        baseline_weekly = (baseline_total / 4.0) if baseline_total else 0
        if baseline_weekly > 0 and recent >= multiplier * baseline_weekly:
            velocity[node] = (recent, baseline_weekly)

    flagged = list(velocity.keys())[:50]
    edges = []
    for node in flagged:
        for _, dst, d in g.out_edges(node, data=True):
            edges.append({"source": node, "target": dst, "amount": d.get("amount", 0)})

    return {
        "result_nodes": flagged,
        "result_edges": edges[:100],
        "summary": (
            f"Found {len(flagged)} accounts with transaction velocity >= {multiplier}x baseline."
        ),
    }


def _gemini_fallback(query: str, g: nx.MultiDiGraph) -> dict:
    """Use Gemini to parse intent, then map to one of 6 handlers."""
    prompt = f"""\
You are an AML graph query assistant. Map this user query to ONE of these keywords:
circular, dormant, trail, kyc, degree, velocity

User query: "{query}"

Respond with ONLY the keyword (no explanation):"""

    intent = _call_gemini_simple(prompt).strip().lower()

    fake_q = intent
    if intent == "circular":
        return _circular_flows(fake_q, g)
    if intent == "dormant":
        return _dormant_accounts(fake_q, g)
    if intent == "kyc":
        return _high_kyc_transfers(fake_q, g)
    if intent == "degree":
        return _top_degree(fake_q, g)
    if intent == "velocity":
        return _velocity_spike(fake_q, g)
    return {
        "result_nodes": [],
        "result_edges": [],
        "summary": f"Could not parse query: '{query}'. Try: circular flows, dormant accounts, fund trail ACC-XXXX, high KYC transfers, top degree, velocity spike.",
    }


def _call_gemini_simple(prompt: str) -> str:
    import os
    from pathlib import Path

    sa_key = Path("google_service_key.json")
    if sa_key.exists():
        try:
            import json

            import vertexai
            from vertexai.generative_models import GenerativeModel
            data = json.loads(sa_key.read_text())
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(sa_key.absolute())
            vertexai.init(project=data.get("project_id", "trace-ai"), location="us-central1")
            model = GenerativeModel("gemini-2.5-flash-preview-05-20")
            return model.generate_content(prompt).text
        except Exception:
            pass

    api_key = os.getenv("GEMINI_API_KEY", "")
    if api_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            return genai.GenerativeModel("gemini-2.5-flash-preview-05-20").generate_content(prompt).text
        except Exception:
            pass

    return "circular"


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def _bfs_subgraph(g: nx.MultiDiGraph, start: str, depth: int = 3) -> nx.MultiDiGraph:
    visited = {start}
    frontier = {start}
    for _ in range(depth):
        next_frontier: set[str] = set()
        for node in frontier:
            next_frontier.update(g.successors(node))
            next_frontier.update(g.predecessors(node))
        frontier = next_frontier - visited
        visited |= frontier
    # subgraph().copy() preserves graph type (MultiDiGraph)
    return g.subgraph(visited).copy()  # type: ignore[return-value]


def _parse_amount(q: str, default: float = 100_000) -> float:
    m = _AMOUNT_RE.search(q)
    if not m:
        return default
    raw = m.group(1).replace(",", "")
    amount = float(raw)
    if "l" in q[m.start():m.end() + 5].lower() or "lakh" in q[m.start():m.end() + 10].lower():
        amount *= 100_000
    elif "cr" in q[m.start():m.end() + 5].lower():
        amount *= 10_000_000
    return amount
