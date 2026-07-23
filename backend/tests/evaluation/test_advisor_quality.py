"""Evaluation runner for advisor_quality_cases.json (Knowledge Core V2.1)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.ai.reasoning_engine_v2 import ReasoningEngineV2
from app.config import settings
from app.database.database import SessionLocal, is_database_ready
from app.knowledge.knowledge_models import AdvisorDimensionRule
from sqlalchemy import func, select

CASES_PATH = Path(__file__).with_name("advisor_quality_cases.json")


@pytest.fixture(scope="module")
def require_postgres():
    if not settings.is_postgres:
        pytest.skip("evaluation requires PostgreSQL")
    if not is_database_ready():
        pytest.skip("database not ready")
    db = SessionLocal()
    try:
        if not db.scalar(select(func.count()).select_from(AdvisorDimensionRule)):
            pytest.skip("V2.1 advisor not seeded")
    finally:
        db.close()


def _load_cases() -> list[dict]:
    data = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    cases = data["cases"]
    assert len(cases) >= 20
    return cases


def _output_blob(result) -> str:
    aa = result.advisor_analysis or {}
    chunks = [
        *(result.suggestions or []),
        *(result.reflection_questions or []),
        *(aa.get("strengths") or []),
        *(aa.get("challenges") or []),
        *(aa.get("growth_direction") or []),
        *(aa.get("action_plan") or []),
        aa.get("life_dimension") or "",
        aa.get("safety_notice") or "",
        result.safety_notice or "",
        " ".join(result.traditional_analysis or []),
    ]
    return "\n".join(str(c) for c in chunks)


@pytest.mark.parametrize("case", _load_cases(), ids=lambda c: c["id"])
def test_advisor_quality_case(require_postgres, case: dict):
    result = ReasoningEngineV2.run(
        question=case["question"],
        chart_data=case["chart"],
    )
    blob = _output_blob(result)
    expect_any = case.get("expect_any") or []
    assert any(k in blob for k in expect_any), (
        f"{case['id']} missing expected keywords {expect_any}; got snippet={blob[:400]}"
    )
    for bad in case.get("forbid") or []:
        assert bad not in blob, f"{case['id']} contains forbidden `{bad}`"


def test_quality_case_categories_cover(require_postgres):
    cats = {c["category"] for c in _load_cases()}
    for required in ("事业", "创业", "财富", "感情", "学习", "人生迷茫"):
        assert required in cats
