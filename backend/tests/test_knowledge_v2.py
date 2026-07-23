"""Knowledge Core V2.0 tests — theory / matrix / life advisor / safety."""

from __future__ import annotations

import pytest

from app.ai.reasoning_engine_v2 import ReasoningEngineV2
from app.ai.safety_filter import SafetyFilter
from app.config import settings
from app.database.database import is_database_ready
from app.knowledge.knowledge_models import (
    FourTransformMatrix,
    LifeScenarioModel,
    PalaceDimensionMatrix,
    StarCombinationMatrix,
    ZiweiTheoryRule,
)
from app.knowledge.reasoning.life_advisor_engine import LifeAdvisorEngine
from app.knowledge.reasoning.matrix_engine import MatrixEngine
from app.knowledge.reasoning.theory_engine import TheoryEngine
from sqlalchemy import func, select

from app.database.database import SessionLocal


@pytest.fixture(scope="module")
def require_postgres():
    if not settings.is_postgres:
        pytest.skip("Knowledge V2 tests require PostgreSQL / Supabase DATABASE_URL")
    if not is_database_ready():
        pytest.skip("database not ready")
    db = SessionLocal()
    try:
        n = db.scalar(select(func.count()).select_from(ZiweiTheoryRule))
        if not n:
            pytest.skip("V2 tables not seeded — run scripts/seed_knowledge_v2.py")
    finally:
        db.close()


CHART_ZIFU = {
    "命宫": {"stars": ["紫微", "天府"]},
    "官禄宫": {"stars": ["武曲", "左辅"]},
    "财帛宫": {"stars": ["天府"]},
    "迁移宫": {"stars": ["天马"]},
    "福德宫": {"stars": ["天同"]},
    "year_stem": "甲",
}

CHART_SHAPOLANG = {
    "命宫": {"stars": ["七杀", "破军", "贪狼"]},
    "官禄宫": {"stars": ["破军"]},
    "财帛宫": {"stars": ["贪狼"]},
    "迁移宫": {"stars": ["七杀"]},
    "福德宫": {"stars": ["贪狼"]},
}


def test_v2_table_counts(require_postgres):
    db = SessionLocal()
    try:
        assert db.scalar(select(func.count()).select_from(ZiweiTheoryRule)) >= 8
        assert db.scalar(select(func.count()).select_from(StarCombinationMatrix)) >= 6
        assert db.scalar(select(func.count()).select_from(PalaceDimensionMatrix)) >= 60
        assert db.scalar(select(func.count()).select_from(FourTransformMatrix)) >= 40
        assert db.scalar(select(func.count()).select_from(LifeScenarioModel)) >= 8
    finally:
        db.close()


def test_ziwei_tianfu_career_v2(require_postgres):
    result = ReasoningEngineV2.run(
        question="我的事业发展方向如何？",
        chart_data=CHART_ZIFU,
    )
    assert result.engine_version in {"2.0", "2.1", "3.2", "3.3", "4.0", "4.1", "5.0", "5.1"}
    assert result.question_type == "career"
    assert result.scenario_name == "career_choice"
    assert result.life_advisor
    assert result.matrix_summary
    assert "紫微天府" in (result.matrix_summary.get("matched_combinations") or []) or any(
        "紫微" in str(s) for r in result.reasoning for s in r.sources
    )
    assert result.traditional_analysis
    assert result.suggestions
    assert any(t.startswith("engine:v") for t in result.call_trace)
    assert any("theory_engine" in t for t in result.call_trace)
    assert any(t.startswith("matrix:") for t in result.call_trace)
    # no absolute fortune claims in output
    blob = " ".join(result.suggestions + result.traditional_analysis)
    assert "一定会发财" not in blob


def test_shapolang_change_personality(require_postgres):
    result = ReasoningEngineV2.run(
        question="我的性格与变化适应力怎样？",
        chart_data=CHART_SHAPOLANG,
    )
    # may classify as personality; matrix should still catch 杀破狼
    combos = (result.matrix_summary or {}).get("matched_combinations") or []
    assert "杀破狼" in combos
    advisor = result.life_advisor or {}
    assert advisor.get("growth_direction") or result.suggestions
    blob = " ".join(
        (advisor.get("challenges") or [])
        + (advisor.get("growth_direction") or [])
        + result.suggestions
    )
    assert "灾难" not in blob or "压力" in blob


def test_entrepreneurship_v2(require_postgres):
    result = ReasoningEngineV2.run(
        question="我想创业做老板，如何评估？",
        chart_data=CHART_ZIFU,
    )
    assert result.question_type == "entrepreneurship"
    assert result.scenario_name == "entrepreneurship"
    suggestions = "\n".join(result.suggestions)
    assert "你适合创业" not in suggestions
    assert "你不适合创业" not in suggestions
    assert result.life_advisor
    assert result.life_advisor.get("reflection_questions")


def test_wealth_v2(require_postgres):
    result = ReasoningEngineV2.run(
        question="如何做好财富规划与理财？",
        chart_data=CHART_ZIFU,
    )
    assert result.question_type == "wealth"
    assert result.scenario_name == "wealth_planning"
    assert result.suggestions or (result.life_advisor or {}).get("growth_direction")
    blob = " ".join(result.suggestions + [(result.life_advisor or {}).get("modern_view") or ""])
    assert "稳赚不赔" not in blob
    assert "一定会发财" not in blob


def test_relationship_v2(require_postgres):
    result = ReasoningEngineV2.run(
        question="我和伴侣的感情关系模式如何改善？",
        chart_data=CHART_ZIFU,
    )
    assert result.question_type == "relationship"
    assert result.scenario_name == "marriage_relationship"
    blob = " ".join(
        result.suggestions
        + [(result.life_advisor or {}).get("traditional_view") or ""]
        + [(result.life_advisor or {}).get("safety_notice") or ""]
    )
    assert "必然离婚" not in blob
    assert "一定会离婚" not in blob


def test_safety_expression_v2(require_postgres):
    SafetyFilter.refresh_cache()
    samples = {
        "你一定会失败": ["压力", "不确定", "验证", "备选"],
        "你一定会发财": ["财富管理", "现实行动", "风险"],
        "今年必有灾": ["风险意识", "规划", "准备"],
        "必然离婚": ["沟通", "关系", "经营"],
        "有劫难": ["压力", "挑战", "准备"],
        "破财": ["资源管理", "风险控制", "财务"],
        "婚姻不顺": ["沟通", "调整"],
    }
    for forbidden, hints in samples.items():
        out = SafetyFilter.apply(forbidden)
        assert forbidden not in out or out != forbidden
        assert any(h in out for h in hints), (forbidden, out)

    # lifespan / medical
    for bad in ("寿命", "死亡时间", "疾病诊断"):
        out = SafetyFilter.apply(f"关于{bad}的问题")
        assert "医疗" in out or "专业" in out

    result = ReasoningEngineV2.run(
        question="未来财富一定会怎样？今年有灾吗？",
        chart_data=CHART_ZIFU,
    )
    blob = " ".join(
        result.traditional_analysis
        + result.suggestions
        + [result.safety_notice]
        + list((result.life_advisor or {}).get("growth_direction") or [])
    )
    assert "一定会发财" not in blob
    assert "今年必有灾" not in blob


def test_theory_and_matrix_engines_direct(require_postgres):
    theory = TheoryEngine.match_for_question("career", pattern_names=["杀破狼"])
    assert theory.traditional_basis
    assert theory.sources

    matrix, summary = MatrixEngine.analyze(CHART_ZIFU, "career", ["命宫", "官禄宫", "财帛宫"])
    assert "紫微天府" in summary["matched_combinations"]
    assert matrix.strengths or matrix.suggestions

    scenario = LifeAdvisorEngine.resolve_scenario("wealth")
    assert scenario["scenario_name"] == "wealth_planning"
