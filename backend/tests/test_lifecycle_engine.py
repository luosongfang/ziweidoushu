"""Knowledge Core V4.1 — Dynamic Life Cycle Engine tests (no LLM)."""

from __future__ import annotations

import pytest

from app.ai.reasoning_engine_v2 import ReasoningEngineV2
from app.config import settings
from app.database.database import is_database_ready
from app.knowledge.intelligence.interpretation_layer import InterpretationLayer
from app.knowledge.lifecycle import LifeCycleEngine
from app.knowledge.lifecycle.annual_engine import AnnualEngine
from app.knowledge.lifecycle.cycle_calculator import CycleCalculator
from app.knowledge.lifecycle.lifecycle_advisor import LifecycleAdvisor
from app.knowledge.lifecycle.stage_analyzer import StageAnalyzer


@pytest.fixture(scope="module")
def require_postgres():
    if not settings.is_postgres:
        pytest.skip("requires PostgreSQL")
    if not is_database_ready():
        pytest.skip("database not ready")


CHART = {
    "age": 38,
    "gender": "male",
    "yin_yang": "yang",
    "bureau_number": 4,
    "year_stem": "甲",
    "命宫": {"stars": ["紫微", "天府"]},
    "官禄宫": {"stars": ["武曲"]},
    "财帛宫": {"stars": ["天府", "禄存"]},
    "迁移宫": {"stars": ["天马"]},
    "夫妻宫": {"stars": ["贪狼"]},
    "福德宫": {"stars": ["天同"]},
}


def test_major_limit_calculation(require_postgres):
    CycleCalculator.refresh()
    # 金四局起运 4 岁；阳男顺行
    limits = CycleCalculator.major_limits(
        bureau_number=4, gender="male", yin_yang="yang"
    )
    assert limits
    assert limits[0]["age_start"] == 4
    assert limits[0]["age_end"] == 13
    assert limits[0]["palace"] == "命宫"
    assert limits[0]["direction"] == "shun"
    assert limits[1]["palace"] == "父母宫"

    # 阴男逆行
    ni = CycleCalculator.major_limits(bureau_number=3, gender="male", yin_yang="yin")
    assert ni[0]["age_start"] == 3
    assert ni[0]["direction"] == "ni"

    cur = CycleCalculator.current_major_limit(
        38, bureau_number=4, gender="male", yin_yang="yang"
    )
    assert cur is not None
    assert cur["age_start"] <= 38 <= cur["age_end"]
    assert cur.get("source")


def test_life_stage_matching(require_postgres):
    StageAnalyzer.refresh()
    assert StageAnalyzer.match(10)["stage_name"] == "childhood"
    assert StageAnalyzer.match(18)["stage_name"] == "education"
    assert StageAnalyzer.match(28)["stage_name"] == "career_build"
    stage = StageAnalyzer.match(38)
    assert stage["stage_name"] == "career_expand"
    assert stage["age_range"] == "35-44"
    assert "career" in stage["focus"]
    analyzed = StageAnalyzer.analyze(38, question_type="career")
    assert "不作绝对事件预测" in analyzed["traditional_view"]


def test_annual_interface(require_postgres):
    AnnualEngine.refresh()
    sb = AnnualEngine.year_stem_branch(1984)
    assert sb["stem"] == "甲" and sb["branch"] == "子"
    annual = AnnualEngine.analyze(year=2026, question_type="career", major_palace="官禄宫")
    assert annual["year"] == 2026
    assert annual["ganzhi"]
    assert annual["influences"]
    assert "不作绝对事件预测" in annual["summary"] or "不作年度判决" in str(annual)
    assert annual["sources"]


def test_cycle_advice_generation(require_postgres):
    LifecycleAdvisor.refresh()
    result = LifeCycleEngine.analyze(
        CHART,
        question_type="career",
        user_context={"age": 38, "gender": "male", "bureau_number": 4},
    )
    lt = result["life_timeline"]
    assert lt["current_stage"] == "career_expand"
    assert lt["age_range"] == "35-44"
    assert set(lt["focus"]) >= {"career"}
    assert lt["traditional_view"]
    assert lt["growth_advice"]
    assert result["major_limit"]
    assert result["annual"]

    pipeline = ReasoningEngineV2.run(
        question="我目前事业拓展阶段该如何规划？",
        chart_data=CHART,
        user_context={"age": 38, "gender": "male", "bureau_number": 4, "yin_yang": "yang"},
    )
    assert pipeline.engine_version in {"4.1", "5.0", "5.1"}
    assert pipeline.life_timeline
    assert pipeline.life_timeline.get("current_stage") == "career_expand"
    assert any(t.startswith("lifecycle:") for t in pipeline.call_trace)
    assert pipeline.theory_analysis  # V4.0 retained


def test_safe_expression(require_postgres):
    InterpretationLayer.refresh()
    advice = LifecycleAdvisor.advise(
        question_type="life_stage",
        stage=StageAnalyzer.match(38),
        major_limit=CycleCalculator.current_major_limit(38, bureau_number=4),
        annual=AnnualEngine.analyze(year=2026, question_type="life_stage"),
    )
    blob = (
        (advice["life_timeline"].get("traditional_view") or "")
        + (advice["life_timeline"].get("growth_advice") or "")
        + (advice.get("growth_advice") or "")
    )
    for banned in ("必有灾难", "注定", "必然发生", "一定会"):
        assert banned not in blob
    assert "规划" in blob or "复盘" in blob or "阶段" in blob or "参考" in blob
    assert "绝对" in blob or "不作" in blob or "参考" in blob
