"""NL copilot endpoint."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class InvestigateRequest(BaseModel):
    nl_query: str


@router.post("")
def investigate(req: InvestigateRequest) -> dict:
    raise NotImplementedError
