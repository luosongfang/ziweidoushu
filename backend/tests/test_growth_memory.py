"""Knowledge Core V3.3 — user growth memory tests (no LLM)."""

from __future__ import annotations

import uuid

import pytest

from app.ai.reasoning_engine_v2 import ReasoningEngineV2
from app.config import settings
from app.database.database import is_database_ready
from app.knowledge.memory.growth_context_builder import GrowthContextBuilder
from app.knowledge.memory.interest_analyzer import InterestAnalyzer
from app.knowledge.memory.memory_service import MemoryService


@pytest.fixture(scope="module")
def require_postgres():
    if not settings.is_postgres:
        pytest.skip("requires PostgreSQL")
    if not is_database_ready():
        pytest.skip("database not ready")


CHART = {
    "命宫": {"stars": ["紫微", "天府"]},
    "官禄宫": {"stars": ["武曲"]},
    "财帛宫": {"stars": ["天府"]},
    "迁移宫": {"stars": ["天马"]},
    "夫妻宫": {"stars": ["贪狼"]},
    "福德宫": {"stars": ["天同"]},
}


@pytest.fixture
def user_a(require_postgres):
    uid = str(uuid.uuid4())
    MemoryService.delete_user_data(uid)
    yield uid
    MemoryService.delete_user_data(uid)


@pytest.fixture
def user_b(require_postgres):
    uid = str(uuid.uuid4())
    MemoryService.delete_user_data(uid)
    yield uid
    MemoryService.delete_user_data(uid)


def test_first_consultation_creates_record(user_a):
    result = ReasoningEngineV2.run(
        question="我准备创业，想了解事业发展方向。",
        chart_data=CHART,
        user_id=user_a,
        persist_growth_memory=True,
    )
    assert result.engine_version in {"3.3", "4.0", "4.1", "5.0", "5.1"}
    assert "growth_memory:saved" in result.call_trace
    assert result.user_context is not None
    assert "continuity_message" in result.user_context

    ctx = MemoryService.get_user_context(user_a, question_type="career")
    assert ctx["interest_scores"]["career"] > 0
    # entrepreneurship / career should have raised career interest
    assert any(
        t in (ctx.get("previous_topics") or [])
        for t in ("创业", "事业", "career")
    ) or ctx["main_interests"]


def test_second_consultation_reads_history(user_a):
    ReasoningEngineV2.run(
        question="我想做好财富规划与理财。",
        chart_data=CHART,
        user_id=user_a,
        persist_growth_memory=True,
    )
    result2 = ReasoningEngineV2.run(
        question="事业上如何稳步推进？",
        chart_data=CHART,
        user_id=user_a,
        persist_growth_memory=True,
    )
    assert "growth_memory:loaded" in result2.call_trace
    uc = result2.user_context or {}
    assert uc.get("previous_topics")
    assert uc.get("continuity_message")
    assert "之前" in uc["continuity_message"] or "关注" in uc["continuity_message"]


def test_interest_weights_update(user_a):
    profile0 = {
        "career_interest": 0.0,
        "wealth_interest": 0.0,
        "relationship_interest": 0.0,
        "family_interest": 0.0,
        "learning_interest": 0.0,
        "growth_interest": 0.0,
        "keywords": [],
    }
    p1 = InterestAnalyzer.apply_deltas(profile0, "career", "事业发展方向")
    assert p1["career_interest"] == pytest.approx(0.1)
    p2 = InterestAnalyzer.apply_deltas(p1, "entrepreneurship", "准备创业")
    assert p2["career_interest"] > p1["career_interest"]
    assert p2["wealth_interest"] > 0
    p3 = InterestAnalyzer.apply_deltas(p2, "wealth", "收入与理财")
    assert p3["wealth_interest"] > p2["wealth_interest"]

    MemoryService.update_profile(user_a, "career", "事业")
    MemoryService.update_profile(user_a, "wealth", "收入")
    ctx = MemoryService.get_user_context(user_a)
    assert ctx["interest_scores"]["career"] > 0
    assert ctx["interest_scores"]["wealth"] > 0
    assert "career" in ctx["main_interests"] or "wealth" in ctx["main_interests"]


def test_advisor_context_generated(user_a):
    MemoryService.save_memory(
        user_id=user_a,
        question="准备创业，关注风险管理。",
        question_type="entrepreneurship",
        theory_used=["三合派", "四化"],
        analysis_result={"question_type": "entrepreneurship", "suggestions": ["小步验证"]},
    )
    ctx = MemoryService.get_user_context(user_a, question_type="career")
    advisor_ctx = GrowthContextBuilder.advisor_context(ctx, "career")
    assert advisor_ctx["continuity_message"]
    assert advisor_ctx["main_interests"] or advisor_ctx["previous_topics"]
    assert any(
        "创业" in (m or "")
        for m in (ctx.get("growth_goals") or [])
    ) or "创业" in " ".join(ctx.get("previous_topics") or [])


def test_user_data_isolation(user_a, user_b):
    MemoryService.save_memory(
        user_id=user_a,
        question="我关注事业与创业。",
        question_type="career",
        theory_used=["三合派"],
    )
    MemoryService.save_memory(
        user_id=user_b,
        question="我想改善感情沟通。",
        question_type="relationship",
        theory_used=["三合派"],
    )
    ctx_a = MemoryService.get_user_context(user_a)
    ctx_b = MemoryService.get_user_context(user_b)

    assert ctx_a["interest_scores"]["career"] > 0
    assert ctx_b["interest_scores"]["relationship"] > 0
    # isolation: B should not inherit A's career weight from A's saves
    assert ctx_b["interest_scores"]["career"] == 0 or ctx_b["interest_scores"]["career"] < ctx_a[
        "interest_scores"
    ]["career"]
    topics_a = set(ctx_a.get("previous_topics") or [])
    topics_b = set(ctx_b.get("previous_topics") or [])
    # relationship topic must not appear as A's primary from B's question
    assert "感情" not in topics_a or "事业" in topics_a or "创业" in topics_a
    assert "感情" in topics_b or "relationship" in ctx_b["main_interests"]
    assert ctx_a["summary"] != ctx_b["summary"] or topics_a != topics_b
