"""V1.3 Report engine tests."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.report.report_generator import ReportGenerator, _populate_from_pipeline


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


def test_life_profile_template_structure():
    fake = SimpleNamespace(
        decision_analysis={
            "current_state": "思维灵活",
            "strengths": ["学习力强"],
            "challenges": ["节奏需稳"],
            "action_suggestions": ["每周复盘"],
            "traditional_view": {"career": "官禄有主星"},
            "scenario": "自我成长",
        },
        life_timeline={"current_stage": "探索期", "growth_advice": "循序渐进"},
        traditional_analysis=["紫微在命"],
        suggestions=["保持好奇", "建立习惯"],
        advisor_analysis={"strengths": ["韧性"], "growth_direction": ["深耕一项技能"]},
        reflection_questions=["我最想验证的能力是什么？"],
        safety_notice="仅供自我认知参考",
    )
    sections = _populate_from_pipeline(fake, {"ming_gong": "子", "five_element": "水二局"})
    assert "identity" in sections
    assert sections["personality"]["strengths"]
    assert "注定" not in str(sections)
    assert "灾难" not in str(sections)


def test_report_create_api(client, auth_headers):
    chart_payload = {
        "name": "报告测试",
        "chart_data": {"ming_gong": "子", "five_element": "水二局", "palaces": []},
        "birth_info": {"solar": "1990-01-01"},
    }
    save = client.post("/api/user/charts", json=chart_payload, headers=auth_headers)
    assert save.status_code == 200
    chart_id = save.json()["id"]

    mock_payload = {
        "engine_version": "5.6",
        "summary": "测试摘要",
        "report_sections": {
            "identity": {"chart_summary": "测试", "traditional_basis": "", "modern_interpretation": ""},
            "personality": {"strengths": ["A"], "challenges": [], "growth_direction": []},
            "career": {"traditional_view": "", "advantages": [], "development_advice": []},
            "wealth": {"resource_pattern": "", "risk_awareness": "", "growth_advice": ""},
            "relationship": {"interaction_style": "", "growth_advice": ""},
            "life_cycle": {"current_stage": "", "focus": "", "advice": ""},
            "advisor_message": "继续探索",
        },
        "knowledge_trace": {"sources": []},
        "safety_notice": "仅供参考",
    }

    with patch.object(ReportGenerator, "generate", return_value=mock_payload):
        r = client.post(
            "/api/v1/report/create",
            json={"chart_id": chart_id, "report_type": "life_profile"},
            headers=auth_headers,
        )
    assert r.status_code == 200
    data = r.json()
    assert data["report_id"]
    assert data["summary"]
    assert "identity" in data["report_sections"] or "personality" in data["report_sections"]

    listing = client.get("/api/v1/report/list", headers=auth_headers)
    assert listing.status_code == 200
    assert any(item["id"] == data["report_id"] for item in listing.json())
