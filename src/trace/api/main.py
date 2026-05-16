"""FastAPI app entrypoint."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .routes import alerts, graph, investigate, reports, ws

app = FastAPI(title="TRACE.ai API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# All API routes are prefixed with /api so they coexist with static frontend files.
app.include_router(graph.router, prefix="/api/graph", tags=["graph"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["alerts"])
app.include_router(investigate.router, prefix="/api/investigate", tags=["investigate"])
app.include_router(reports.router, prefix="/api/reports", tags=["reports"])
app.include_router(ws.router, tags=["websocket"])


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "service": "trace-ai"}


# Serve React SPA from /app/frontend/dist when the build exists.
_DIST = Path(__file__).parent.parent.parent.parent / "frontend" / "dist"
if _DIST.is_dir():
    app.mount("/assets", StaticFiles(directory=str(_DIST / "assets")), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def spa_fallback(full_path: str) -> FileResponse:
        return FileResponse(str(_DIST / "index.html"))
