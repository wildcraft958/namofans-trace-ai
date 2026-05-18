"""Module G -- NL Investigation Copilot (LLM-powered).

Translates plain-English queries into NetworkX graph operations using
Gemini 2.5 Flash as a semantic parser. Gemini maps free-form text to one
of 10 structured intents; the graph executor then runs the right traversal
with extracted parameters.

Fallback: if Gemini is unreachable, a lightweight regex heuristic picks the
closest intent so the demo never returns empty.
"""

from __future__ import annotations

import json
import math
import os
import re
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import networkx as nx

# ──────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────

_STRUCTURING_THRESHOLD = 1_000_000  # Rs 10 lakh in paise-free units
_LAYERING_FORWARD_RATIO = 0.70       # 70% forwarded within 48h
_LAYERING_WINDOW_H = 48
_MULE_MIN_IN_DEGREE = 5
_MULE_MIN_OUT_DEGREE = 5

_ACCOUNT_RE = re.compile(r"(ACC-[A-Z0-9\-]+|RING-[A-Z0-9\-]+)", re.I)
_AMOUNT_RE = re.compile(r"[₹rs\s]*([0-9][0-9,]*(?:\.[0-9]+)?)\s*(?:l|lakh|cr|crore)?", re.I)
_DAYS_RE = re.compile(r"(\d+)\s*day", re.I)

# ──────────────────────────────────────────────
# System prompt for Gemini intent parser
# ──────────────────────────────────────────────

_PARSER_SYSTEM = """\
You are an AML (Anti-Money Laundering) query parser for TRACE.ai, a banking fraud-detection system.
Your job is to convert a natural-language investigation query into a structured JSON intent object.

Available intents and when to choose them:

1. circular_flow      — money moving in loops (A→B→C→A), round-tripping, ping-pong transfers
2. dormant_burst      — accounts inactive for N days that suddenly have outgoing activity
3. fund_trail         — trace all hops from a specific account (requires account_id)
4. high_kyc           — accounts flagged as HIGH KYC risk that sent large transfers
5. top_centrality     — most connected / highest PageRank / hub accounts
6. velocity_spike     — sudden increase in transaction rate (X times the normal rate)
7. layering           — accounts that forward ≥70% of received funds within 48h (obscuring origin)
8. structuring        — accounts with multiple transactions just below the Rs 10 lakh reporting threshold in 24h
9. mule               — high-degree aggregator accounts (many senders in, many recipients out in short window)
10. custom_subgraph   — anything that doesn't fit the above (complex or composite queries)

Output ONLY valid JSON with these fields (null if not applicable):
{
  "intent": "<one of the 10 intent strings above>",
  "account_id": "<ACC-XXXXX or null>",
  "amount_min": <number or null>,
  "amount_max": <number or null>,
  "days_dormant": <integer or null>,
  "n_top": <integer or null>,
  "velocity_multiplier": <float or null>,
  "time_window_days": <integer or null>,
  "explanation": "<one sentence on why this intent was chosen>"
}

Rules:
- Amounts must be in raw rupees (convert "5 lakh" → 500000, "2 crore" → 20000000).
- If the query mentions a specific account ID like ACC-00123, set account_id.
- For vague/multi-part queries, choose custom_subgraph.
- Never output anything outside the JSON block.

Examples:
Query: "which accounts are doing circular transfers above 5 lakh?"
→ {"intent":"circular_flow","account_id":null,"amount_min":500000,"amount_max":null,"days_dormant":null,"n_top":null,"velocity_multiplier":null,"time_window_days":null,"explanation":"User asked for circular/round-trip transfers with a minimum amount."}

Query: "show accounts that forwarded funds quickly to hide origin"
→ {"intent":"layering","account_id":null,"amount_min":null,"amount_max":null,"days_dormant":null,"n_top":null,"velocity_multiplier":null,"time_window_days":null,"explanation":"Rapid forwarding to hide origin is the layering pattern."}

Query: "which accounts received money from the structuring cluster?"
→ {"intent":"structuring","account_id":null,"amount_min":null,"amount_max":null,"days_dormant":null,"n_top":null,"velocity_multiplier":null,"time_window_days":null,"explanation":"Structuring involves transactions just below the reporting threshold."}

Query: "show me accounts with unusual transaction patterns this week"
→ {"intent":"velocity_spike","account_id":null,"amount_min":null,"amount_max":null,"days_dormant":null,"n_top":null,"velocity_multiplier":null,"time_window_days":7,"explanation":"Unusual patterns this week maps to velocity spike in the recent window."}
"""


# ──────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────

def run(nl_query: str, graph: nx.MultiDiGraph) -> dict:
    """Parse nl_query with Gemini, execute graph traversal, return results.

    Returns:
        {
            result_nodes: list[str],
            result_edges: list[dict],
            summary: str,
            latency_ms: float,
            parsed_intent: dict,   # what Gemini understood
        }
    """
    t0 = time.monotonic()
    parsed = _parse_intent(nl_query)
    result = _execute(parsed, nl_query, graph)
    result["latency_ms"] = round((time.monotonic() - t0) * 1000, 1)
    result["parsed_intent"] = parsed
    return result


# ──────────────────────────────────────────────
# Intent parser (Gemini)
# ──────────────────────────────────────────────

def _parse_intent(nl_query: str) -> dict:
    """Call Gemini to get a structured intent dict. Falls back to regex on failure."""
    prompt = f'Query: "{nl_query}"\n'
    raw = _call_gemini(system=_PARSER_SYSTEM, user=prompt)
    if raw:
        parsed = _extract_json(raw)
        if parsed and parsed.get("intent"):
            return parsed
    # Gemini unavailable or returned bad JSON — use regex heuristic
    return _regex_fallback_intent(nl_query)


def _extract_json(text: str) -> dict | None:
    """Extract the first JSON object from text."""
    try:
        # Strip markdown code fences if present
        clean = re.sub(r"```(?:json)?|```", "", text).strip()
        # Find first { ... }
        start = clean.find("{")
        end = clean.rfind("}") + 1
        if start == -1 or end == 0:
            return None
        return json.loads(clean[start:end])
    except Exception:
        return None


def _regex_fallback_intent(q: str) -> dict:
    """Best-guess intent from keywords when Gemini is unavailable."""
    q_lower = q.lower()
    account_match = _ACCOUNT_RE.search(q)
    account_id = account_match.group(1) if account_match else None

    base: dict[str, Any] = {
        "account_id": account_id,
        "amount_min": None,
        "amount_max": None,
        "days_dormant": None,
        "n_top": None,
        "velocity_multiplier": None,
        "time_window_days": None,
        "explanation": "Regex fallback (Gemini unavailable)",
    }

    if any(w in q_lower for w in ("circular", "round", "loop", "ping")):
        return {**base, "intent": "circular_flow", "amount_min": _parse_amount(q_lower)}
    if any(w in q_lower for w in ("dormant", "inactive", "sleeping")):
        days_m = _DAYS_RE.search(q_lower)
        return {**base, "intent": "dormant_burst", "days_dormant": int(days_m.group(1)) if days_m else 90}
    if account_id and any(w in q_lower for w in ("trail", "flow", "trace", "fund", "path")):
        return {**base, "intent": "fund_trail"}
    if any(w in q_lower for w in ("kyc", "high risk")):
        return {**base, "intent": "high_kyc", "amount_min": _parse_amount(q_lower)}
    if any(w in q_lower for w in ("top", "central", "pagerank", "hub", "most connected")):
        n_m = re.search(r"top[\s-]*(\d+)", q_lower)
        return {**base, "intent": "top_centrality", "n_top": int(n_m.group(1)) if n_m else 10}
    if any(w in q_lower for w in ("velocity", "spike", "sudden", "burst", "unusual", "rapid")):
        mult_m = re.search(r"(\d+)\s*x", q_lower)
        return {**base, "intent": "velocity_spike",
                "velocity_multiplier": float(mult_m.group(1)) if mult_m else 3.0}
    if any(w in q_lower for w in ("layer", "forward", "forwarded", "obscur")):
        return {**base, "intent": "layering"}
    if any(w in q_lower for w in ("structur", "smurfing", "threshold", "below")):
        return {**base, "intent": "structuring"}
    if any(w in q_lower for w in ("mule", "aggregat", "collector")):
        return {**base, "intent": "mule"}
    if account_id:
        return {**base, "intent": "fund_trail"}
    return {**base, "intent": "custom_subgraph"}


# ──────────────────────────────────────────────
# Graph executor — dispatches on parsed intent
# ──────────────────────────────────────────────

def _execute(parsed: dict, raw_query: str, g: nx.MultiDiGraph) -> dict:
    intent = parsed.get("intent", "custom_subgraph")

    handlers = {
        "circular_flow": _h_circular_flow,
        "dormant_burst": _h_dormant_burst,
        "fund_trail": _h_fund_trail,
        "high_kyc": _h_high_kyc,
        "top_centrality": _h_top_centrality,
        "velocity_spike": _h_velocity_spike,
        "layering": _h_layering,
        "structuring": _h_structuring,
        "mule": _h_mule,
        "custom_subgraph": _h_custom_subgraph,
    }

    handler = handlers.get(intent, _h_custom_subgraph)
    try:
        return handler(parsed, raw_query, g)
    except Exception as exc:
        # Safety net: never crash the API
        return {
            "result_nodes": [],
            "result_edges": [],
            "summary": f"Handler for '{intent}' raised an error: {exc}. Try rephrasing your query.",
        }


# ──────────────────────────────────────────────
# Intent handlers
# ──────────────────────────────────────────────

def _h_circular_flow(p: dict, _raw: str, g: nx.MultiDiGraph) -> dict:
    threshold = p.get("amount_min") or 100_000
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
                    if d.get("amount", 0) >= threshold
                )
                if total >= threshold:
                    flagged_nodes.extend([node, dst])
                    for _, target, data in g.out_edges(node, data=True):
                        flagged_edges.append({
                            "source": node,
                            "target": target,
                            "amount": data.get("amount", 0),
                            "channel": data.get("channel", ""),
                        })

    flagged_nodes = list(dict.fromkeys(flagged_nodes))[:50]
    return {
        "result_nodes": flagged_nodes,
        "result_edges": flagged_edges[:100],
        "summary": (
            f"Found {len(flagged_nodes)} accounts in circular flow patterns "
            f"with transactions >= Rs {threshold:,.0f}."
        ),
    }


def _h_dormant_burst(p: dict, _raw: str, g: nx.MultiDiGraph) -> dict:
    threshold_days = p.get("days_dormant") or 90
    time_window = p.get("time_window_days") or 30
    now = datetime.now(timezone.utc)
    flagged: list[str] = []

    for node, data in g.nodes(data=True):
        dormant = data.get("dormant_days", 0)
        if dormant < threshold_days:
            continue
        recent_out = [
            d for _, _, d in g.out_edges(node, data=True)
            if d.get("timestamp") and
            (now - _to_utc(d["timestamp"])).days <= time_window
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
            f"Found {len(flagged)} accounts dormant >= {threshold_days} days "
            f"with activity in the last {time_window} days (dormant burst pattern)."
        ),
    }


def _h_fund_trail(p: dict, _raw: str, g: nx.MultiDiGraph) -> dict:
    account_id = p.get("account_id")
    if not account_id:
        return {
            "result_nodes": [],
            "result_edges": [],
            "summary": "Fund trail requires a specific account ID (e.g. ACC-00123). None found in query.",
        }
    if account_id not in g:
        return {
            "result_nodes": [],
            "result_edges": [],
            "summary": f"Account {account_id} not found in the transaction graph.",
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


def _h_high_kyc(p: dict, _raw: str, g: nx.MultiDiGraph) -> dict:
    threshold = p.get("amount_min") or 500_000
    flagged: list[str] = []
    edges: list[dict] = []

    for node, data in g.nodes(data=True):
        if str(data.get("kyc_risk", "LOW")).upper() != "HIGH":
            continue
        for _, dst, d in g.out_edges(node, data=True):
            if d.get("amount", 0) >= threshold:
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
            f">= Rs {threshold:,.0f}."
        ),
    }


def _h_top_centrality(p: dict, _raw: str, g: nx.MultiDiGraph) -> dict:
    n_top = p.get("n_top") or 10
    try:
        pr = nx.pagerank(g, max_iter=100, tol=1e-4)
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
        "summary": f"Top {len(node_ids)} accounts by PageRank centrality in the transaction graph.",
    }


def _h_velocity_spike(p: dict, _raw: str, g: nx.MultiDiGraph) -> dict:
    multiplier = p.get("velocity_multiplier") or 3.0
    time_window_days = p.get("time_window_days") or 7
    now = datetime.now(timezone.utc)
    window_recent = timedelta(days=time_window_days)
    window_baseline = timedelta(days=max(time_window_days * 4, 30))

    velocity: dict[str, tuple[float, float]] = {}
    for node in g.nodes():
        edges_all = [d for _, _, d in g.out_edges(node, data=True) if d.get("timestamp")]
        if not edges_all:
            continue
        recent = sum(
            1 for d in edges_all
            if (now - _to_utc(d["timestamp"])) <= window_recent
        )
        baseline_total = sum(
            1 for d in edges_all
            if (now - _to_utc(d["timestamp"])) <= window_baseline
        )
        periods = window_baseline / window_recent
        baseline_per_period = baseline_total / periods if periods > 0 else 0
        if baseline_per_period > 0 and recent >= multiplier * baseline_per_period:
            velocity[node] = (recent, baseline_per_period)

    flagged = list(velocity.keys())[:50]
    edges = []
    for node in flagged:
        for _, dst, d in g.out_edges(node, data=True):
            edges.append({"source": node, "target": dst, "amount": d.get("amount", 0)})
    return {
        "result_nodes": flagged,
        "result_edges": edges[:100],
        "summary": (
            f"Found {len(flagged)} accounts with transaction velocity >= {multiplier}x "
            f"baseline rate in the last {time_window_days} days."
        ),
    }


def _h_layering(p: dict, _raw: str, g: nx.MultiDiGraph) -> dict:
    """Accounts that forwarded >= 70% of received funds within 48h."""
    window_h = _LAYERING_WINDOW_H
    forward_ratio = _LAYERING_FORWARD_RATIO
    flagged: list[str] = []
    flagged_edges: list[dict] = []

    for node in g.nodes():
        # Total received
        in_edges = list(g.in_edges(node, data=True))
        if not in_edges:
            continue
        total_received = sum(d.get("amount", 0) for _, _, d in in_edges)
        if total_received == 0:
            continue

        # Outgoing within 48h of any incoming
        in_times = [
            _to_utc(d["timestamp"])
            for _, _, d in in_edges
            if d.get("timestamp")
        ]
        if not in_times:
            continue
        earliest_in = min(in_times)
        cutoff = earliest_in + timedelta(hours=window_h)

        forwarded = sum(
            d.get("amount", 0)
            for _, _, d in g.out_edges(node, data=True)
            if d.get("timestamp") and _to_utc(d["timestamp"]) <= cutoff
        )

        if forwarded / total_received >= forward_ratio:
            flagged.append(node)
            for src, _, d in in_edges:
                flagged_edges.append({"source": src, "target": node, "amount": d.get("amount", 0)})
            for _, dst, d in g.out_edges(node, data=True):
                flagged_edges.append({"source": node, "target": dst, "amount": d.get("amount", 0)})

    flagged = flagged[:50]
    return {
        "result_nodes": flagged,
        "result_edges": flagged_edges[:150],
        "summary": (
            f"Found {len(flagged)} accounts that forwarded >= {int(forward_ratio*100)}% "
            f"of received funds within {window_h}h (layering pattern)."
        ),
    }


def _h_structuring(p: dict, _raw: str, g: nx.MultiDiGraph) -> dict:
    """Accounts with multiple transactions just below Rs 10L threshold in 24h."""
    threshold = _STRUCTURING_THRESHOLD
    window_h = 24
    min_txns = 2  # at least 2 sub-threshold txns in the window
    flagged: list[str] = []
    flagged_edges: list[dict] = []

    for node in g.nodes():
        out_edges = [
            (dst, d) for _, dst, d in g.out_edges(node, data=True)
            if d.get("amount") and d.get("timestamp")
        ]
        if len(out_edges) < min_txns:
            continue

        # Sort by timestamp
        out_edges.sort(key=lambda x: _to_utc(x[1]["timestamp"]))

        # Sliding window: check any 24h window with >= min_txns sub-threshold txns
        for i, (_dst_i, d_i) in enumerate(out_edges):
            t_start = _to_utc(d_i["timestamp"])
            t_end = t_start + timedelta(hours=window_h)
            window_txns = [
                (dst_j, d_j) for dst_j, d_j in out_edges[i:]
                if _to_utc(d_j["timestamp"]) <= t_end
                and 0.8 * threshold <= d_j.get("amount", 0) < threshold
            ]
            if len(window_txns) >= min_txns:
                flagged.append(node)
                for dst_j, d_j in window_txns:
                    flagged_edges.append({
                        "source": node,
                        "target": dst_j,
                        "amount": d_j.get("amount", 0),
                    })
                break  # one match per node is enough

    flagged = list(dict.fromkeys(flagged))[:50]
    return {
        "result_nodes": flagged,
        "result_edges": flagged_edges[:150],
        "summary": (
            f"Found {len(flagged)} accounts with >= {min_txns} transactions between "
            f"Rs {0.8*threshold:,.0f} and Rs {threshold:,.0f} within {window_h}h "
            f"(structuring / smurfing pattern)."
        ),
    }


def _h_mule(p: dict, _raw: str, g: nx.MultiDiGraph) -> dict:
    """High-degree aggregator accounts: many unique senders in + many unique recipients out."""
    time_window_days = p.get("time_window_days") or 30
    min_in = _MULE_MIN_IN_DEGREE
    min_out = _MULE_MIN_OUT_DEGREE
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=time_window_days)
    flagged: list[str] = []
    flagged_edges: list[dict] = []

    for node in g.nodes():
        in_senders = set()
        out_receivers = set()
        for src, _, d in g.in_edges(node, data=True):
            ts = d.get("timestamp")
            if ts and _to_utc(ts) >= cutoff:
                in_senders.add(src)
        for _, dst, d in g.out_edges(node, data=True):
            ts = d.get("timestamp")
            if ts and _to_utc(ts) >= cutoff:
                out_receivers.add(dst)

        if len(in_senders) >= min_in and len(out_receivers) >= min_out:
            flagged.append(node)
            for src in in_senders:
                flagged_edges.append({"source": src, "target": node, "amount": 0})
            for dst in out_receivers:
                flagged_edges.append({"source": node, "target": dst, "amount": 0})

    flagged = flagged[:50]
    return {
        "result_nodes": list({n for e in flagged_edges for n in (e["source"], e["target"])} | set(flagged))[:100],
        "result_edges": flagged_edges[:150],
        "summary": (
            f"Found {len(flagged)} potential mule accounts with >= {min_in} senders in "
            f"and >= {min_out} recipients out within {time_window_days} days."
        ),
    }


def _h_custom_subgraph(p: dict, raw_query: str, g: nx.MultiDiGraph) -> dict:
    """Ask Gemini to generate NetworkX Python code for the query, then exec it safely."""
    code_prompt = f"""\
You are a NetworkX expert. Write Python code to answer this AML investigation query against a
NetworkX MultiDiGraph called `g`.

Query: "{raw_query}"

Rules:
- The graph nodes have attributes: account_id, kyc_risk (LOW/MEDIUM/HIGH), dormant_days, balance
- The graph edges have attributes: amount (float, INR), timestamp (datetime), channel (str)
- Store your answer as two Python lists assigned to variables named `result_nodes` (list of node IDs)
  and `result_edges` (list of dicts with keys source, target, amount).
- Write only executable Python. No explanation. No markdown. No import statements.
- You may use: nx, g, math, datetime, timedelta, timezone (all pre-imported).
- Do NOT use: os, sys, open, exec, eval, __import__, subprocess, or any file I/O.
- Keep it under 30 lines.

Python code:"""

    code = _call_gemini(system="You are a Python/NetworkX code generator.", user=code_prompt)

    if code:
        code = _strip_code_fences(code)
        result = _safe_exec_networkx(code, g)
        if result:
            return result

    # Gemini code gen failed — fall back to top centrality as a sensible default
    fallback = _h_top_centrality({"n_top": 15}, raw_query, g)
    fallback["summary"] = (
        f"Could not generate custom query code. Showing top 15 central accounts instead. "
        f"Original query: \"{raw_query}\""
    )
    return fallback


def _safe_exec_networkx(code: str, g: nx.MultiDiGraph) -> dict | None:
    """Execute generated NetworkX code in a restricted namespace."""
    namespace: dict[str, Any] = {
        "nx": nx,
        "g": g,
        "math": math,
        "datetime": datetime,
        "timedelta": timedelta,
        "timezone": timezone,
        # Explicitly deny dangerous builtins
        "__builtins__": {
            "len": len,
            "list": list,
            "dict": dict,
            "set": set,
            "sum": sum,
            "min": min,
            "max": max,
            "sorted": sorted,
            "enumerate": enumerate,
            "zip": zip,
            "range": range,
            "int": int,
            "float": float,
            "str": str,
            "bool": bool,
            "abs": abs,
            "round": round,
            "isinstance": isinstance,
            "hasattr": hasattr,
            "getattr": getattr,
            "print": print,
        },
    }
    try:
        exec(code, namespace)
        result_nodes = list(namespace.get("result_nodes", []))[:100]
        result_edges = list(namespace.get("result_edges", []))[:150]
        if not isinstance(result_nodes, list) or not isinstance(result_edges, list):
            return None
        return {
            "result_nodes": result_nodes,
            "result_edges": result_edges,
            "summary": f"Custom query returned {len(result_nodes)} accounts and {len(result_edges)} edges.",
        }
    except Exception as exc:
        print(f"[copilot] custom_subgraph exec failed: {exc}")
        return None


# ──────────────────────────────────────────────
# Gemini caller (mirrors explainer.py pattern)
# ──────────────────────────────────────────────

def _call_gemini(system: str, user: str) -> str:
    """Call Gemini 2.5 Flash. Returns empty string on failure."""
    full_prompt = f"{system}\n\n{user}"

    sa_key = Path("google_service_key.json")
    if sa_key.exists():
        try:
            import json as _json

            import vertexai
            from vertexai.generative_models import GenerativeModel

            data = _json.loads(sa_key.read_text())
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(sa_key.absolute())
            vertexai.init(project=data.get("project_id", "trace-ai"), location="us-central1")
            model = GenerativeModel("gemini-2.5-flash-preview-05-20")
            return model.generate_content(full_prompt).text.strip()
        except Exception as e:
            print(f"[copilot] Vertex AI failed: {e}. Trying google-generativeai SDK.")

    api_key = os.getenv("GEMINI_API_KEY", "")
    if api_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-2.5-flash-preview-05-20")
            return model.generate_content(full_prompt).text.strip()
        except Exception as e:
            print(f"[copilot] google-generativeai failed: {e}.")

    return ""


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
    return g.subgraph(visited).copy()  # type: ignore[return-value]


def _to_utc(ts: Any) -> datetime:
    """Ensure a timestamp is timezone-aware UTC."""
    if isinstance(ts, datetime):
        if ts.tzinfo is None:
            return ts.replace(tzinfo=timezone.utc)
        return ts.astimezone(timezone.utc)
    return datetime.now(timezone.utc)


def _parse_amount(q: str, default: float = 100_000) -> float:
    m = _AMOUNT_RE.search(q)
    if not m:
        return default
    raw = m.group(1).replace(",", "")
    amount = float(raw)
    tail = q[m.start(): m.end() + 10].lower()
    if "lakh" in tail or tail.rstrip().endswith("l"):
        amount *= 100_000
    elif "crore" in tail or "cr" in tail:
        amount *= 10_000_000
    return amount


def _strip_code_fences(text: str) -> str:
    return re.sub(r"```(?:python)?|```", "", text).strip()


# ──────────────────────────────────────────────
# Self-test (guarded)
# ──────────────────────────────────────────────

if __name__ == "__main__":
    import random
    from datetime import datetime, timedelta, timezone

    random.seed(42)
    now = datetime.now(timezone.utc)

    # Build a small mock graph: 20 accounts, 50 directed edges
    G = nx.MultiDiGraph()
    accounts = [f"ACC-{i:05d}" for i in range(20)]
    kyc_risks = ["LOW", "LOW", "LOW", "MEDIUM", "HIGH"]

    for acc in accounts:
        G.add_node(
            acc,
            kyc_risk=random.choice(kyc_risks),
            dormant_days=random.choice([0, 0, 0, 120, 200]),
            balance=random.uniform(10_000, 5_000_000),
        )

    # Add 50 random edges with timestamps and amounts
    for _ in range(50):
        src, dst = random.sample(accounts, 2)
        days_ago = random.randint(0, 45)
        amount = random.choice([
            random.uniform(50_000, 900_000),   # sub-threshold
            random.uniform(950_000, 990_000),   # structuring range
            random.uniform(1_000_000, 5_000_000),
        ])
        G.add_edge(
            src, dst,
            amount=amount,
            timestamp=now - timedelta(days=days_ago, hours=random.randint(0, 23)),
            channel=random.choice(["NEFT", "IMPS", "UPI", "RTGS"]),
        )

    # Add circular flow: A → B → A
    G.add_edge("ACC-00001", "ACC-00002", amount=600_000,
               timestamp=now - timedelta(days=2), channel="NEFT")
    G.add_edge("ACC-00002", "ACC-00001", amount=580_000,
               timestamp=now - timedelta(days=1), channel="RTGS")

    # Add a dormant burst: ACC-00003 was dormant, recently active
    G.nodes["ACC-00003"]["dormant_days"] = 150
    G.add_edge("ACC-00003", "ACC-00004", amount=200_000,
               timestamp=now - timedelta(days=5), channel="UPI")

    # Add structuring on ACC-00005: 3 txns just below 10L in 24h
    for i in range(3):
        G.add_edge("ACC-00005", accounts[i + 10], amount=970_000,
                   timestamp=now - timedelta(hours=i * 6), channel="NEFT")

    # Add mule on ACC-00006: many senders in, many recipients out
    for sender in accounts[7:13]:
        G.add_edge(sender, "ACC-00006", amount=100_000,
                   timestamp=now - timedelta(days=random.randint(1, 10)), channel="UPI")
    for recv in accounts[13:19]:
        G.add_edge("ACC-00006", recv, amount=95_000,
                   timestamp=now - timedelta(days=random.randint(1, 5)), channel="IMPS")

    test_queries = [
        "which accounts are doing circular transfers above 5 lakh?",
        "show me accounts with unusual transaction patterns this week",
        "find dormant accounts that suddenly became active",
        "which accounts received money from the structuring cluster?",
        "show me accounts that forwarded most of their received funds quickly to hide their origin",
    ]

    print("=" * 70)
    print("TRACE.ai NL Investigation Copilot — Self Test")
    print("=" * 70)
    for q in test_queries:
        print(f"\nQuery: {q!r}")
        result = run(q, G)
        pi = result.get("parsed_intent", {})
        print(f"  Intent   : {pi.get('intent')} (via {'Gemini' if pi.get('explanation') != 'Regex fallback (Gemini unavailable)' else 'regex fallback'})")
        print(f"  Explain  : {pi.get('explanation', '')}")
        print(f"  Nodes    : {len(result['result_nodes'])} — {result['result_nodes'][:5]}")
        print(f"  Edges    : {len(result['result_edges'])}")
        print(f"  Summary  : {result['summary']}")
        print(f"  Latency  : {result['latency_ms']} ms")
