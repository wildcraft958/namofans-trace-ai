"""Smoke test — API health endpoint responds."""

from fastapi.testclient import TestClient

from trace.api.main import app


def test_health():
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
