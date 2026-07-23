"""V1.2 用户身份 API 冒烟测试。"""

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


def test_user_profile_requires_auth(client):
    r = client.get("/api/user/profile")
    assert r.status_code == 401


def test_user_profile_dev_mode(client, auth_headers):
    r = client.get("/api/user/profile", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert "nickname" in data
    assert data["auth_user_id"]


def test_save_and_list_charts(client, auth_headers):
    payload = {
        "name": "测试命盘",
        "chart_data": {"ming_gong": "子", "five_element": "水二局", "palaces": []},
        "birth_info": {"solar": "1990-01-01", "gender": "male"},
        "birth_date": "1990-01-01",
        "gender": "male",
    }
    save = client.post("/api/user/charts", json=payload, headers=auth_headers)
    assert save.status_code == 200
    chart_id = save.json()["id"]

    listing = client.get("/api/user/charts", headers=auth_headers)
    assert listing.status_code == 200
    assert any(c["id"] == chart_id for c in listing.json())


def test_save_analysis_history(client, auth_headers):
    payload = {
        "question": "自我认知概览",
        "analysis_type": "personality",
        "summary": "思维灵活，适合循序渐进探索。",
    }
    r = client.post("/api/user/history", json=payload, headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["summary"]

    history = client.get("/api/user/history", headers=auth_headers)
    assert history.status_code == 200
    assert len(history.json()) >= 1


def test_memory_context(client, auth_headers):
    r = client.get("/api/v1/memory/context", headers=auth_headers)
    assert r.status_code == 200
    assert "continuity_message" in r.json()
