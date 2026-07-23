"""Knowledge Core V5.5 — evaluation engine tests (no LLM)."""

from __future__ import annotations

import uuid

import pytest

from app.config import settings
from app.database.database import is_database_ready
from app.knowledge.evaluation import (
    CaseLibrary,
    EvaluationEngine,
    ExpertReview,
    QualityMetrics,
    TheoryStatistics,
)


@pytest.fixture(scope="module")
def require_postgres():
    if not settings.is_postgres:
        pytest.skip("requires PostgreSQL")
    if not is_database_ready():
        pytest.skip("database not ready")


def test_case_save(require_postgres):
    before = CaseLibrary.count()
    assert before >= 20  # seeded library
    saved = CaseLibrary.save_case(
        {
            "case_name": f"测试案例-{uuid.uuid4().hex[:8]}",
            "birth_info_summary": "匿名教学案例·单元测试",
            "chart_features": {"命宫": ["紫微"], "官禄宫": ["武曲"]},
            "main_patterns": ["紫府同宫"],
            "life_stage": "career_build",
            "question_type": "career",
            "analysis_reference": {
                "question": "事业如何规划？",
                "traditional_reference": ["官禄宫看事业表达"],
                "analysis_dimension": ["career"],
            },
            "case_source": "unit_test",
            "verification_level": "classic",
        }
    )
    assert saved["saved"] is True
    assert saved["id"]
    got = CaseLibrary.get_case(saved["id"])
    assert got is not None
    assert got["case_name"] == saved["case_name"]
    assert "chart_features" in got
    assert got["analysis_reference"].get("question")


def test_expert_review(require_postgres):
    cases = CaseLibrary.list_cases(limit=1)
    assert cases
    case_id = cases[0]["id"]
    review = ExpertReview.submit(
        case_id=case_id,
        reviewer_type="internal",
        review_score=88,
        logic_score=85,
        safety_score=95,
        value_score=80,
        comments="理论引用清晰，表达安全，具成长价值。",
    )
    assert review["saved"] is True
    assert review["review_score"] == 88
    assert review["safety_score"] == 95
    rows = ExpertReview.list_for_case(case_id)
    assert any(r["id"] == review["id"] for r in rows)


def test_quality_calculation(require_postgres):
    analysis = {
        "scenario": "创业选择",
        "scenario_code": "entrepreneurship",
        "question_type": "entrepreneurship",
        "theory_used": ["三合派", "四化"],
        "traditional_view": {
            "sanhe": "三合视角观察命官财迁结构。",
            "four_transform": "四化提示节奏管理。",
            "cycle": "大限阶段主题仅供规划参考。",
        },
        "strengths": ["资源整合优势"],
        "challenges": ["需关注现金流风险"],
        "action_suggestions": ["小步验证", "建立安全垫", "季度复盘"],
        "reflection_questions": ["安全垫能支撑多久？"],
        "safety_notice": "本分析定位为传统文化学习与人生规划辅助，不作绝对预测。",
        "sources": [{"book": "紫微教学案例", "page": "1"}],
    }
    trace = {
        "theory": "三合紫微",
        "entities": ["紫微", "天府"],
        "books": [{"name": "紫微教学案例", "page": "1"}],
        "reasoning_path": ["识别场景", "三合观察", "四化辅助", "输出成长建议"],
    }
    scores = QualityMetrics.score(
        analysis_result=analysis,
        knowledge_trace=trace,
        feedback={"feedback_type": "helpful"},
        persist=True,
        analysis_id=str(uuid.uuid4()),
    )
    assert scores["theory_accuracy"] >= 60
    assert scores["logic_score"] >= 50
    assert scores["safety_score"] >= 80
    assert scores["growth_value"] >= 50
    assert scores["overall_score"] >= 50
    assert scores["scoring_target"] == "analysis_process"

    bundled = EvaluationEngine.evaluate_analysis(
        analysis_result=analysis,
        knowledge_trace=trace,
        feedback={"feedback_type": "helpful"},
        theory_used=["三合派", "四化"],
        scenario="entrepreneurship",
        persist=True,
    )
    qs = bundled["quality_score"]
    assert "overall_score" in qs
    assert qs["safety_score"] >= 80


def test_theory_statistics(require_postgres):
    TheoryStatistics.seed_baseline()
    TheoryStatistics.record_usage(
        theory_system="三合派",
        scenario="entrepreneurship",
        feedback_type="helpful",
    )
    TheoryStatistics.record_usage(
        theory_system="四化",
        scenario="wealth",
        feedback_type="partially_helpful",
    )
    stats = TheoryStatistics.list_stats(scenario="entrepreneurship")
    assert stats
    assert any(r["theory_system"] == "sanhe" for r in stats)
    ranking = TheoryStatistics.ranking_summary()
    assert "entrepreneurship" in ranking
    roles = {r["theory_system"]: r.get("role") for r in ranking["entrepreneurship"]}
    # sanhe should appear with a role
    assert "sanhe" in roles

    api = EvaluationEngine.theory_stats()
    assert api["stats"]
    assert api["ranking"]


def test_safety_scoring(require_postgres):
    dangerous = {
        "suggestions": ["你一定会失败", "今年必有灾", "一定发财"],
        "safety_notice": "命中注定破财",
    }
    safe = {
        "suggestions": ["建议结合现实条件小步验证", "可以提前关注风险管理"],
        "safety_notice": "传统文化学习 + 人生规划辅助，不作绝对预测。",
        "action_suggestions": ["建立安全垫", "季度复盘"],
        "sources": [{"book": "教学", "page": "2"}],
    }
    bad = QualityMetrics.score(analysis_result=dangerous)
    good = QualityMetrics.score(
        analysis_result=safe,
        knowledge_trace={
            "theory": "三合紫微",
            "entities": ["武曲"],
            "books": [{"name": "教学", "page": "2"}],
            "reasoning_path": ["安全表达检查"],
        },
    )
    assert bad["safety_score"] < good["safety_score"]
    assert bad["safety_score"] <= 50
    assert good["safety_score"] >= 80
    # ensure we never claim destiny accuracy
    assert "人生结果" in (bad.get("notice") or good.get("notice") or "") or (
        bad.get("scoring_target") == "analysis_process"
    )
