"""STR report endpoints."""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter()


@router.get("/str/{alert_id}")
def download_str(alert_id: str) -> FileResponse:
    raise NotImplementedError("Generate STR PDF on demand and stream the file.")
