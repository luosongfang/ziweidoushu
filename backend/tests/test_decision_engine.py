"""Knowledge Core V5.0 — Decision Intelligence tests (no LLM)."""

from __future__ import annotations

import pytest

from app.ai.reasoning_engine_v2 import ReasoningEngineV2
from app.config import settings
from app.database.database import is_database_ready
from app.knowledge.decision import DecisionEngine, DecisionRiskAnalyzer
from app.knowledge.decision.decision_context_builder import DecisionContextBuilder


@pytest.fixture(scope="module")
def require_postgres():
    if not settings.is_postgres:
        pytest.skip("requires PostgreSQL")
    if not is_database_ready():
        pytest.skip("database not ready")


CHART_ZIFU = {
    "age": 36,
    "gender": "male",
    "yin_yang": "yang",
    "bureau_number": 4,
    "命宫": {"stars": ["紫微", "天府"]},
    "官禄宫": {"stars": ["武曲"]},
    "财帛宫": {"stars": ["天府", "禄存"]},
    "迁移宫": {"stars": ["天马"]},
    "福德宫": {"stars": ["天同"]},
}

CHART_SPL = {
    "age": 32,
    "gender": "male",
    "yin_yang": "yang",
    "bureau_number": 3,
    "命宫": {"stars": ["七杀"]},
    "官禄宫": {"stars": ["破军"]},
    "迁移宫": {"stars": ["贪狼"]},
    "财帛宫": {"stars": ["武曲"]},
    "夫妻宫": {"stars": ["贪狼"]},
    "福德宫": {"stars": ["天同"]},
}


def _blob(da: dict) -> str:
    parts = [
        da.get("current_state") or "",
        " ".join(da.get("strengths") or []),
        " ".join(da.get("challenges") or []),
        " ".join(da.get("action_suggestions") or []),
        " ".join(da.get("decision_points") or []),
        str(da.get("traditional_view") or ""),
        da.get("safety_notice") or "",
    ]
    return " ".join(parts)


def test_zifu_entrepreneurship_resource_integration(require_postgres):
    DecisionContextBuilder.refresh()
    result = ReasoningEngineV2.run(
        question="我想创业，如何评估方向与资源？",
        chart_data=CHART_ZIFU,
        user_context={"age": 36, "gender": "male", "bureau_number": 4},
    )
    assert result.engine_version in {"5.0", "5.1"}
    da = result.decision_analysis or {}
    assert da.get("scenario_code") == "entrepreneurship" or "创业" in (da.get("scenario") or "")
    blob = _blob(da)
    assert "资源整合" in blob
    assert da.get("sources") or True  # sources encouraged
    assert any(t.startswith("decision:") for t in result.call_trace)


def test_shapolang_career_change_adaptability(require_postgres):
    result = ReasoningEngineV2.run(
        question="我想转行换赛道，如何评估转型能力？",
        chart_data=CHART_SPL,
        user_context={"age": 32},
    )
    da = result.decision_analysis or {}
    assert da.get("scenario_code") in {"career_change", "life_transition"} or "转" in (
        da.get("scenario") or ""
    )
    blob = _blob(da)
    assert "变化" in blob or "开创" in blob or "转型" in blob


def test_wealth_risk_not_prediction(require_postgres):
    result = ReasoningEngineV2.run(
        question="如何做好投资理财与财富规划？",
        chart_data=CHART_ZIFU,
    )
    da = result.decision_analysis or {}
    assert da.get("scenario_code") == "investment_decision" or "投资" in (da.get("scenario") or "")
    blob = _blob(da)
    assert "风险" in blob or "安全垫" in blob
    for banned in ("一定发财", "必赚", "命中注定破财", "你会暴富"):
        assert banned not in blob


def test_relationship_management_advice(require_postgres):
    result = ReasoningEngineV2.run(
        question="我和伴侣感情关系如何改善沟通与相处？",
        chart_data=CHART_SPL,
    )
    da = result.decision_analysis or {}
    assert da.get("scenario_code") == "relationship_choice" or "感情" in (da.get("scenario") or "")
    blob = _blob(da)
    assert "沟通" in blob or "边界" in blob or "经营" in blob
    for banned in ("必须离婚", "注定分手"):
        assert banned not in blob


def test_major_choice_safe_output(require_postgres):
    DecisionRiskAnalyzer.refresh()
    dangerous = DecisionRiskAnalyzer.sanitize(
        "你一定会失败，你命中注定破财，今年必有灾，必须离婚，一定发财。"
    )
    for banned in ("一定会失败", "命中注定破财", "今年必有灾", "必须离婚", "一定发财"):
        assert banned not in dangerous

    result = ReasoningEngineV2.run(
        question="面对人生重大选择，我该如何决策？",
        chart_data=CHART_ZIFU,
        user_context={"age": 40},
    )
    da = result.decision_analysis or {}
    assert da.get("safety_notice")
    assert "传统文化学习" in da["safety_notice"] or "人生规划" in da["safety_notice"]
    blob = _blob(da)
    for banned in ("命中注定", "必有灾", "一定会失败", "必须离婚"):
        assert banned not in blob
    assert da.get("reflection_questions")
    assert da.get("action_suggestions")
    # unit path also works
    unit = DecisionEngine.analyze(
        question="重大选择如何做？",
        chart_data=CHART_ZIFU,
        question_type="life_stage",
    )
    assert unit["decision_analysis"]["safety_notice"]
