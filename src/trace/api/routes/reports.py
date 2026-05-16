"""STR report endpoints."""

from __future__ import annotations

from pathlib import Path
from trace.api.dependencies import get_alerts

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter()


@router.post("/str/{alert_id}")
def generate_str(alert_id: str) -> FileResponse:
    """Generate STR PDF on demand and stream as a file download."""
    alerts = get_alerts()
    alert = next((a for a in alerts if a.get("alert_id") == alert_id), None)
    if alert is None:
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")

    from trace.intelligence.str_generator import generate

    out_dir = Path("data/processed/str_reports")
    out_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = out_dir / f"STR_{alert_id}.pdf"

    generate(alert, pdf_path)

    return FileResponse(
        path=str(pdf_path),
        media_type="application/pdf",
        filename=f"STR_{alert_id}.pdf",
    )


@router.get("/str/{alert_id}/download")
def download_str(alert_id: str) -> FileResponse:
    """Return pre-generated STR PDF if it exists."""
    pdf_path = Path(f"data/processed/str_reports/STR_{alert_id}.pdf")
    if not pdf_path.exists():
        return generate_str(alert_id)
    return FileResponse(
        path=str(pdf_path),
        media_type="application/pdf",
        filename=f"STR_{alert_id}.pdf",
    )
