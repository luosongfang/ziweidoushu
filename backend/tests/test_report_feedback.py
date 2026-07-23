"""V1.3 Report feedback tests."""

from __future__ import annotations

from unittest.mock import patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.report.report_generator import ReportGenerator


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


def _mock_report():
    return {
        "engine_version": "5.6",
        "summary": "反馈测试",
        "report_sections": {
            "identity": {"chart_summary": "x", "traditional_basis": "", "modern_interpretation": ""},
            "personality": {"strengths": [], "challenges": [], "growth_direction": []},
            "career": {"traditional_view": "", "advantages": [], "development_advice": []},
            "wealth": {"resource_pattern": "", "risk_awareness": "", "growth_advice": ""},
            "relationship": {"interaction_style": "", "growth_advice": ""},
            "life_cycle": {"current_stage": "", "focus": "", "advice": ""},
            "advisor_message": "",
        },
        "knowledge_trace": {},
        "safety_notice": "参考",
    }


def test_report_feedback(client, auth_headers):
    save = client.post(
        "/api/user/charts",
        json={
            "name": "反馈命盘",
            "chart_data": {"ming_gong": "丑"},
            "birth_info": {},
        },
        headers=auth_headers,
    )
    chart_id = save.json()["id"]

    with patch.object(ReportGenerator, "generate", return_value=_mock_report()):
        created = client.post(
            "/api/v1/report/create",
            json={"chart_id": chart_id, "report_type": "life_profile"},
            headers=auth_headers,
        )
    report_id = created.json()["report_id"]

    fb = client.post(
        "/api/v1/report/feedback",
        json={"report_id": report_id, "helpful": True, "comment": "有帮助"},
        headers=auth_headers,
    )
    assert fb.status_code == 200
    assert fb.json()["success"] is True
