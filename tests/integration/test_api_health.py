"""Smoke test — API health endpoint responds."""

from trace.api.main import app

from fastapi.testclient import TestClient


def test_health():
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
