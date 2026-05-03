"""Module F — LLM Alert Explainer.

Produces a natural-language explanation grounded in graph evidence.
LLM via LiteLLM (GPT-4o-mini / Claude Haiku). Template-constrained generation.
Compliance officer reviews before any STR is filed.
"""

from __future__ import annotations


PROMPT_TEMPLATE = """You are an AML compliance assistant. Given the following alert evidence, write a 4-sentence explanation in plain English. Cite specific accounts, amounts, and timestamps from the evidence. Do NOT invent facts.

EVIDENCE:
{evidence}

EXPLANATION:"""


def explain(alert: dict) -> str:
    raise NotImplementedError("litellm.completion with PROMPT_TEMPLATE.format(evidence=...).")
