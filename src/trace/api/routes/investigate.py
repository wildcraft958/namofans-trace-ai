"""NL copilot endpoint."""

from __future__ import annotations

from trace.api.dependencies import get_graph
from trace.intelligence.copilot import run

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class InvestigateRequest(BaseModel):
    nl_query: str


@router.post("")
def investigate(req: InvestigateRequest) -> dict:
    g = get_graph()
    return run(req.nl_query, g)
