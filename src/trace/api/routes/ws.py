"""WebSocket route for real-time alert stream."""

from __future__ import annotations

from fastapi import APIRouter, WebSocket

router = APIRouter()


@router.websocket("/ws/alerts")
async def alert_stream(ws: WebSocket) -> None:
    await ws.accept()
    raise NotImplementedError("Push new alerts as they are produced by the detection engine.")
