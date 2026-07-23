"""V1.3 Growth center API tests."""

from __future__ import annotations

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(autouse=True)
def _init_database():
    from app.database.database import init_db

    init_db()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_headers():
    uid = str(uuid4())
    return {"Authorization": f"Bearer {uid}", "X-Dev-User-Id": uid}


def test_growth_profile_requires_auth(client):
    r = client.get("/api/v1/growth/profile")
    assert r.status_code == 401


def test_growth_profile_returns_structure(client, auth_headers):
    r = client.get("/api/v1/growth/profile", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert "history" in data
    assert "goals" in data
    assert "focus_topics" in data
    assert "advisor_suggestions" in data
