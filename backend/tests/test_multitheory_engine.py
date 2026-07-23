"""Knowledge Core V4.0 Phase1 — Multi-Theory Decision Engine tests (no LLM)."""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy import text

from app.ai.reasoning_engine_v2 import ReasoningEngineV2
from app.config import settings
from app.database.database import SessionLocal, is_database_ready
from app.knowledge.multitheory.synthesis_engine import SynthesisEngine
from app.knowledge.multitheory.theory_analyzer import TheoryAnalyzer
from app.knowledge.multitheory.theory_conflict_checker import TheoryConflictChecker
from app.knowledge.multitheory.theory_dispatcher import TheoryDispatcher
from app.knowledge.multitheory.theory_registry import TheoryRegistry


@pytest.fixture(scope="module")
def require_postgres():
    if not settings.is_postgres:
        pytest.skip("requires PostgreSQL")
    if not is_database_ready():
        pytest.skip("database not ready")


CHART = {
    "命宫": {"stars": ["紫微", "天府"]},
    "官禄宫": {"stars": ["武曲"]},
    "财帛宫": {"stars": ["天府", "禄存"]},
    "迁移宫": {"stars": ["天马"]},
    "夫妻宫": {"stars": ["贪狼"]},
    "福德宫": {"stars": ["天同"]},
    "田宅宫": {"stars": ["武曲"]},
}


def test_entrepreneurship_uses_sanhe_and_sihua(require_postgres):
    TheoryRegistry.refresh()
    TheoryDispatcher.refresh()
    types = TheoryDispatcher.theory_types("entrepreneurship")
    assert "sanhe" in types
    assert "sihua" in types

    result = ReasoningEngineV2.run(
        question="我准备创业，想评估事业路径与风险管理。",
        chart_data=CHART,
        persist_theory_results=False,
    )
    assert result.engine_version in {"4.0", "4.1", "5.0", "5.1"}
    assert result.question_type == "entrepreneurship"
    assert any(x in (result.theory_used or []) for x in ("三合派", "四化"))
    ta = result.theory_analysis or {}
    assert "sanhe" in ta
    assert "four_transform" in ta
    assert ta["sanhe"].get("summary")
    assert ta["four_transform"].get("sources")
    assert "theory_dispatcher" in " ".join(result.call_trace)


def test_wealth_uses_caibo_related_theories(require_postgres):
    dispatch = TheoryDispatcher.dispatch("wealth")
    palaces = TheoryDispatcher.union_palaces("wealth")
    assert "财帛宫" in palaces
    assert any(d["theory_type"] in {"sanhe", "sihua"} for d in dispatch)

    result = ReasoningEngineV2.run(
        question="如何做好财富规划与理财配置？",
        chart_data=CHART,
    )
    assert result.question_type == "wealth"
    assert "财帛宫" in palaces
    ta = result.theory_analysis or {}
    # wealth theories should mention 财帛 in sanhe required palaces / summary
    sanhe = ta.get("sanhe") or {}
    blob = (sanhe.get("summary") or "") + str(result.theory_route)
    assert "财帛" in blob or "财帛宫" in str(result.theory_route.get("dispatch") or dispatch)


def test_theory_results_persisted(require_postgres):
    analysis_id = str(uuid.uuid4())
    dispatch = TheoryDispatcher.dispatch("career")
    results = TheoryAnalyzer.analyze_all(
        chart=CHART,
        question_type="career",
        dispatch=dispatch,
        analysis_id=analysis_id,
        persist=True,
    )
    assert len(results) >= 2
    for r in results.values():
        assert r.get("sources"), "every theory result must have sources"

    db = SessionLocal()
    try:
        n = db.execute(
            text(
                "SELECT COUNT(*) FROM public.theory_analysis_results WHERE analysis_id = CAST(:aid AS uuid)"
            ),
            {"aid": analysis_id},
        ).scalar()
        assert int(n or 0) == len(results)
    finally:
        db.close()
        # cleanup
        db2 = SessionLocal()
        try:
            db2.execute(
                text(
                    "DELETE FROM public.theory_analysis_results WHERE analysis_id = CAST(:aid AS uuid)"
                ),
                {"aid": analysis_id},
            )
            db2.commit()
        finally:
            db2.close()


def test_conflict_detection(require_postgres):
    fake = {
        "sanhe": {
            "summary": "三合强调稳定资源与结构优势",
            "strengths": ["资源整合优势明显", "结构稳健"],
            "challenges": [],
            "suggestions": ["稳步推进"],
            "required_palaces": ["命宫", "官禄宫"],
        },
        "sihua": {
            "summary": "四化提示阶段性风险与波动需谨慎",
            "strengths": [],
            "challenges": ["资源波动风险", "节奏压力"],
            "suggestions": ["加强风险管理"],
            "required_palaces": ["财帛宫", "官禄宫"],
        },
    }
    conflicts = TheoryConflictChecker.check(fake)
    assert conflicts
    assert any(c.get("level") in {"conflict", "difference"} for c in conflicts)


def test_synthesis_advice_generated(require_postgres):
    SynthesisEngine.refresh()
    dispatch = TheoryDispatcher.dispatch("entrepreneurship")
    results = TheoryAnalyzer.analyze_all(
        chart=CHART,
        question_type="entrepreneurship",
        dispatch=dispatch,
        persist=False,
    )
    conflicts = TheoryConflictChecker.check(results)
    synthesis = SynthesisEngine.synthesize(
        results,
        question_type="entrepreneurship",
        conflicts=conflicts,
    )
    assert synthesis.get("common") or synthesis.get("common_points")
    assert synthesis.get("difference") or synthesis.get("different_views")
    assert synthesis.get("advice") or synthesis.get("decision_advice")
    assert "绝对预测" not in (synthesis.get("advice") or "") or "不作绝对预测" in (
        synthesis.get("advice") or ""
    )
    # API-shaped payload
    payload = TheoryAnalyzer.to_api_payload(results, synthesis=synthesis, conflicts=conflicts)
    assert payload["synthesis"]["advice"]
    assert "sanhe" in payload and "four_transform" in payload
