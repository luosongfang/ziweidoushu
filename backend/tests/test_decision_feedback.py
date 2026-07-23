"""Knowledge Core V5.1 — decision feedback / paths / knowledge_trace tests."""

from __future__ import annotations

import uuid

import pytest

from app.ai.reasoning_engine_v2 import ReasoningEngineV2
from app.config import settings
from app.database.database import is_database_ready
from app.knowledge.decision import DecisionEngine
from app.knowledge.decision_feedback import (
    DecisionProfile,
    FeedbackService,
    PathSimulator,
    ReferenceMapper,
)


@pytest.fixture(scope="module")
def require_postgres():
    if not settings.is_postgres:
        pytest.skip("requires PostgreSQL")
    if not is_database_ready():
        pytest.skip("database not ready")


CHART = {
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


@pytest.fixture
def user_a(require_postgres):
    uid = str(uuid.uuid4())
    FeedbackService.delete_user_data(uid)
    yield uid
    FeedbackService.delete_user_data(uid)


@pytest.fixture
def user_b(require_postgres):
    uid = str(uuid.uuid4())
    FeedbackService.delete_user_data(uid)
    yield uid
    FeedbackService.delete_user_data(uid)


def test_feedback_save(user_a):
    bundle = DecisionEngine.analyze(
        question="我想创业，如何评估？",
        chart_data=CHART,
        question_type="entrepreneurship",
        persist_history=True,
        user_id=user_a,
    )
    hid = bundle.get("decision_history_id")
    saved = FeedbackService.save_feedback(
        user_id=user_a,
        feedback_type="helpful",
        feedback_content="建议很实用，已开始建安全垫",
        decision_history_id=hid,
        result_status="confirmed",
    )
    assert saved["saved"] is True
    assert saved["id"]
    assert saved["feedback_type"] == "helpful"
    rows = FeedbackService.list_feedback(user_a)
    assert len(rows) >= 1
    assert rows[0]["feedback_type"] == "helpful"


def test_feedback_updates_profile(user_a):
    FeedbackService.save_feedback(
        user_id=user_a,
        feedback_type="helpful",
        feedback_content="接受稳健建议",
        result_status="confirmed",
    )
    FeedbackService.save_feedback(
        user_id=user_a,
        feedback_type="partially_helpful",
        feedback_content="部分适用",
        result_status="pending",
    )
    profile = DecisionProfile.refresh_profile(user_a)
    assert profile["user_id"]
    assert profile["decision_style"]
    assert profile["risk_preference"]
    assert profile.get("analytics", {}).get("feedback_total", 0) >= 2
    assert float(profile["analytics"]["acceptance_rate"]) > 0
    again = DecisionProfile.get_profile(user_a)
    assert again["decision_style"] == profile["decision_style"]


def test_entrepreneurship_dual_paths(require_postgres):
    PathSimulator.refresh()
    da = {
        "scenario": "创业选择",
        "scenario_code": "entrepreneurship",
        "strengths": ["资源整合优势"],
        "challenges": ["需关注现金流风险"],
        "action_suggestions": ["小步验证"],
    }
    paths = PathSimulator.simulate(da)
    assert paths["scenario"] == "创业"
    assert len(paths["paths"]) == 2
    types = {p["type"] for p in paths["paths"]}
    assert "稳健路径" in types and "进取路径" in types
    stable = next(p for p in paths["paths"] if p["path_type"] == "stable")
    assert "现金流" in stable["focus"] or any("现金" in f for f in stable["focus"])
    aggressive = next(p for p in paths["paths"] if p["path_type"] == "aggressive")
    assert any("扩张" in f or "机会" in f for f in aggressive["focus"])
    assert "一定成功" not in paths["final"]
    assert "必然胜出" not in paths["final"] or "不预测" in paths["final"]
    assert "结合现实条件" in paths["final"]

    result = ReasoningEngineV2.run(
        question="我想创业开公司，如何选择节奏？",
        chart_data=CHART,
        user_context={"age": 36},
    )
    assert result.engine_version == "5.1"
    assert result.decision_paths
    assert len(result.decision_paths.get("paths") or []) == 2


def test_knowledge_trace_generation(require_postgres):
    result = ReasoningEngineV2.run(
        question="紫微天府命盘，创业方向如何规划？",
        chart_data=CHART,
    )
    trace = result.knowledge_trace or {}
    assert trace.get("theory")
    assert "三合" in trace["theory"] or "紫微" in trace["theory"]
    assert isinstance(trace.get("entities"), list)
    assert "紫微" in trace["entities"] or "天府" in trace["entities"]
    assert isinstance(trace.get("books"), list)
    assert isinstance(trace.get("reasoning_path"), list)
    assert len(trace["reasoning_path"]) >= 2

    unit = ReferenceMapper.build_trace(
        decision_analysis=result.decision_analysis,
        theory_analysis=result.theory_analysis,
        sources=result.sources,
        stars=["紫微", "天府"],
        theory_used=result.theory_used,
    )
    assert unit["entities"]
    assert unit["reasoning_path"]


def test_user_isolation(user_a, user_b):
    FeedbackService.save_feedback(
        user_id=user_a,
        feedback_type="helpful",
        feedback_content="A 用户反馈",
        result_status="confirmed",
    )
    FeedbackService.save_feedback(
        user_id=user_b,
        feedback_type="not_helpful",
        feedback_content="B 用户反馈",
        result_status="changed",
    )
    DecisionProfile.refresh_profile(user_a)
    DecisionProfile.refresh_profile(user_b)

    rows_a = FeedbackService.list_feedback(user_a)
    rows_b = FeedbackService.list_feedback(user_b)
    assert any(r["feedback_type"] == "helpful" for r in rows_a)
    assert any(r["feedback_type"] == "not_helpful" for r in rows_b)
    assert not any(r.get("feedback_content") == "A 用户反馈" for r in rows_b)

    pa = DecisionProfile.get_profile(user_a)
    pb = DecisionProfile.get_profile(user_b)
    assert pa["user_id"] != pb["user_id"]
    assert pa.get("analytics", {}).get("feedback_counts", {}).get("helpful", 0) >= 1
    assert pb.get("analytics", {}).get("feedback_counts", {}).get("not_helpful", 0) >= 1
