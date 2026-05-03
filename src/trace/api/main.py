"""FastAPI app entrypoint."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import alerts, graph, investigate, reports, ws

app = FastAPI(title="TRACE.ai API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten for prod
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(graph.router, prefix="/graph", tags=["graph"])
app.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
app.include_router(investigate.router, prefix="/investigate", tags=["investigate"])
app.include_router(reports.router, prefix="/reports", tags=["reports"])
app.include_router(ws.router, tags=["websocket"])


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "trace-ai"}
