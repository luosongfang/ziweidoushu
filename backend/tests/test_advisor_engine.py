"""Advisor Engine V2.1 tests."""

from __future__ import annotations

import pytest

from app.ai.reasoning_engine_v2 import ReasoningEngineV2
from app.config import settings
from app.database.database import SessionLocal, is_database_ready
from app.knowledge.advisor.advisor_engine import AdvisorEngine
from app.knowledge.advisor.advisor_safety import AdvisorSafety
from app.knowledge.advisor.advisor_context_builder import AdvisorContextBuilder
from app.knowledge.knowledge_models import AdvisorActionModel, AdvisorDimensionRule
from sqlalchemy import func, select


@pytest.fixture(scope="module")
def require_postgres():
    if not settings.is_postgres:
        pytest.skip("Advisor tests require PostgreSQL / Supabase")
    if not is_database_ready():
        pytest.skip("database not ready")
    db = SessionLocal()
    try:
        n = db.scalar(select(func.count()).select_from(AdvisorDimensionRule))
        if not n:
            pytest.skip("V2.1 not seeded — run scripts/seed_knowledge_v2_1.py")
    finally:
        db.close()


CHART_ZIFU = {
    "命宫": {"stars": ["紫微", "天府"]},
    "官禄宫": {"stars": ["武曲", "左辅"]},
    "财帛宫": {"stars": ["天府"]},
    "迁移宫": {"stars": ["天马"]},
    "福德宫": {"stars": ["天同"]},
}

CHART_SHAPOLANG = {
    "命宫": {"stars": ["七杀", "破军", "贪狼"]},
    "官禄宫": {"stars": ["破军"]},
    "财帛宫": {"stars": ["贪狼"]},
    "迁移宫": {"stars": ["七杀"]},
    "福德宫": {"stars": ["贪狼"]},
}


def _blob(result) -> str:
    aa = result.advisor_analysis or {}
    parts = [
        *(result.suggestions or []),
        *(aa.get("strengths") or []),
        *(aa.get("challenges") or []),
        *(aa.get("growth_direction") or []),
        *(aa.get("action_plan") or []),
        result.safety_notice or "",
        " ".join(result.traditional_analysis or []),
    ]
    return "\n".join(str(x) for x in parts)


def test_zifu_career_leadership(require_postgres):
    result = ReasoningEngineV2.run(
        question="我的事业发展方向如何？如何发挥领导能力？",
        chart_data=CHART_ZIFU,
    )
    assert result.engine_version in {"2.1", "3.2", "3.3", "4.0", "4.1", "5.0", "5.1"}
    assert result.advisor_analysis
    blob = _blob(result)
    assert "领导" in blob or "组织" in blob or "资源整合" in blob
    assert "必然成功" not in blob
    assert any(t.startswith("engine:v") for t in result.call_trace)
    assert any("advisor_engine" in t for t in result.call_trace)


def test_shapolang_entrepreneurship(require_postgres):
    result = ReasoningEngineV2.run(
        question="我想创业，如何评估变化能力与风险？",
        chart_data=CHART_SHAPOLANG,
    )
    assert result.question_type == "entrepreneurship"
    blob = _blob(result)
    assert "变化" in blob or "适应" in blob
    assert "风险" in blob or "试错" in blob or "止损" in blob
    assert "一定发财" not in blob
    assert "你适合创业" not in blob


def test_relationship_communication_growth(require_postgres):
    result = ReasoningEngineV2.run(
        question="我和伴侣感情关系如何改善沟通与成长？",
        chart_data=CHART_ZIFU,
    )
    assert result.question_type == "relationship"
    blob = _blob(result)
    assert "沟通" in blob
    assert "成长" in blob or "经营" in blob or "边界" in blob
    assert "离婚预测" not in blob
    assert "必然离婚" not in blob
    assert "婚姻必失败" not in blob


def test_advisor_context_rewrite(require_postgres):
    text = AdvisorContextBuilder.rewrite_text("七杀入命，杀气重。")
    assert "杀气重" not in text
    assert "行动力" in text or "突破" in text
    assert "节奏" in text or "规划" in text


def test_advisor_safety_rules(require_postgres):
    assert "破财" not in AdvisorSafety.apply("你今年一定破财") or "风险" in AdvisorSafety.apply(
        "你今年一定破财"
    )
    out1 = AdvisorSafety.apply("你今年一定破财")
    assert "风险管理" in out1
    out2 = AdvisorSafety.apply("你的婚姻必失败")
    assert "沟通" in out2
    out3 = AdvisorSafety.apply("会发生灾难")
    assert "确定事件" in out3 or "反思" in out3


def test_advisor_tables_seeded(require_postgres):
    db = SessionLocal()
    try:
        assert db.scalar(select(func.count()).select_from(AdvisorDimensionRule)) >= 8
        assert db.scalar(select(func.count()).select_from(AdvisorActionModel)) >= 6
    finally:
        db.close()


def test_advisor_engine_direct(require_postgres):
    result = AdvisorEngine.analyze(
        chart_data=CHART_ZIFU,
        question="事业怎么规划？",
        question_type="career",
        matrix_summary={"matched_combinations": ["紫微天府"]},
    )
    assert result.strengths
    assert result.action_plan or result.suggestions
    assert result.reflection_questions
    assert result.as_advisor_analysis()["life_dimension"]
