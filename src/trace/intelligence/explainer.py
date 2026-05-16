"""Module F -- LLM Alert Explainer via Gemini (Vertex AI).

Produces a natural-language explanation grounded in graph evidence.
Responses are disk-cached so the live demo never depends on LLM latency.
Compliance officer reviews before any STR is filed.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

_CACHE_DIR = Path("data/processed/explanations")

PROMPT_TEMPLATE = """\
You are an AML (Anti-Money Laundering) compliance expert at an Indian bank.
Given the following alert evidence from the TRACE.ai system, write a concise
4-sentence explanation in plain English for a compliance officer.

Rules:
- Cite specific account IDs (masked as ****XXXX), amounts in INR, and pattern names.
- Do NOT invent facts. Use only the evidence provided.
- Be direct and professional. No markdown, no bullet points.
- End with the regulatory implication (PMLA Section 12 / FIU-IND STR obligation).

EVIDENCE:
{evidence}

EXPLANATION:"""


def explain(alert: dict) -> str:
    """Return LLM explanation for an alert. Disk-cached after first call."""
    alert_id = alert.get("alert_id", "unknown")
    cache_path = _CACHE_DIR / f"{alert_id}.txt"

    if cache_path.exists():
        return cache_path.read_text().strip()

    evidence = _build_evidence(alert)
    explanation = _call_gemini(evidence)

    _CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(explanation)
    return explanation


def precache_all(alerts: list[dict]) -> int:
    """Pre-cache Gemini explanations for all alerts. Returns count cached."""
    cached = 0
    for alert in alerts:
        alert_id = alert.get("alert_id", "")
        if not alert_id:
            continue
        cache_path = _CACHE_DIR / f"{alert_id}.txt"
        if cache_path.exists():
            continue
        try:
            explain(alert)
            cached += 1
        except Exception as e:
            print(f"[explainer] Failed to cache {alert_id}: {e}")
    return cached


def _build_evidence(alert: dict) -> str:
    acc = alert.get("account_id", "UNKNOWN")
    masked = f"****{acc[-4:]}" if len(acc) >= 4 else acc
    risk = alert.get("risk_level", "HIGH")
    score = alert.get("composite_score", 0.0)

    matches = alert.get("pattern_matches", {})
    triggered = [p.replace("_", " ").title() for p, v in matches.items() if v]
    contributions = alert.get("risk_contributions", {})

    top_shap = alert.get("shap_features", [])[:3]
    shap_text = ", ".join(
        f"{f['feature']} (SHAP={f['shap_value']:+.3f})" for f in top_shap
    )

    txns = alert.get("transactions", [])
    txn_summary = ""
    if txns:
        total = sum(t.get("amount", 0) for t in txns[:5])
        txn_summary = f"Top transactions total: Rs {total:,.0f} across {len(txns)} transactions."

    parts = [
        f"Subject account: {masked}",
        f"Risk level: {risk} (composite score: {score:.2f})",
        f"Triggered patterns: {', '.join(triggered) if triggered else 'None'}",
        f"Risk contributions: pattern={contributions.get('pattern', 0):.3f}, "
        f"ml={contributions.get('gnn', 0):.3f}, "
        f"anomaly={contributions.get('anomaly', 0):.3f}, "
        f"compliance={contributions.get('compliance', 0):.3f}",
    ]
    if shap_text:
        parts.append(f"Top SHAP features: {shap_text}")
    if txn_summary:
        parts.append(txn_summary)

    return "\n".join(parts)


def _call_gemini(evidence: str) -> str:
    prompt = PROMPT_TEMPLATE.format(evidence=evidence)

    # Try Vertex AI with service account first
    sa_key = Path("google_service_key.json")
    if sa_key.exists():
        try:
            import vertexai
            from vertexai.generative_models import GenerativeModel

            project_id = _read_project_id(sa_key)
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(sa_key.absolute())
            vertexai.init(project=project_id, location="us-central1")

            model = GenerativeModel("gemini-2.5-flash-preview-05-20")
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"[explainer] Vertex AI failed: {e}. Trying google-generativeai SDK.")

    # Fallback to google-generativeai with GEMINI_API_KEY
    api_key = os.getenv("GEMINI_API_KEY", "")
    if api_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-2.5-flash-preview-05-20")
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"[explainer] google-generativeai failed: {e}. Using template fallback.")

    return _template_fallback(evidence)


def _template_fallback(evidence: str) -> str:
    lines = evidence.splitlines()
    acc_line = next((ln for ln in lines if "Subject account:" in ln), "Subject account: ****XXXX")
    pattern_line = next((ln for ln in lines if "Triggered patterns:" in ln), "")
    risk_line = next((ln for ln in lines if "Risk level:" in ln), "")
    return (
        f"TRACE.ai has identified a suspicious transaction pattern for {acc_line.split(':', 1)[-1].strip()}. "
        f"{risk_line.split(':', 1)[-1].strip() if risk_line else ''} "
        f"{pattern_line.split(':', 1)[-1].strip() if pattern_line else ''}. "
        "This activity is consistent with known money laundering typologies under PMLA Schedule A. "
        "The compliance officer should review this alert and file an STR with FIU-IND within 7 working days if warranted."
    )


def _read_project_id(sa_key: Path) -> str:
    try:
        data = json.loads(sa_key.read_text())
        return data.get("project_id", "trace-ai")
    except Exception:
        return "trace-ai"
