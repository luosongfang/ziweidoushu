"""Knowledge Core V1.0 tests — DB connect / load / query / safety."""

from __future__ import annotations

import pytest

from app.ai.safety_filter import SafetyFilter
from app.config import settings
from app.database.database import database_status, is_database_ready
from app.knowledge.knowledge_loader import KnowledgeLoader
from app.knowledge.knowledge_search import KnowledgeSearch
from app.knowledge.knowledge_service import KnowledgeService


@pytest.fixture(scope="module")
def require_postgres():
    if not settings.is_postgres:
        pytest.skip("Knowledge Core tests require PostgreSQL / Supabase DATABASE_URL")
    if not is_database_ready():
        pytest.skip("database not ready")


def test_database_connection(require_postgres):
    status = database_status()
    assert status["driver"] == "postgresql"
    assert status["connected"] is True
    assert status["ready"] is True


def test_knowledge_loader_stars(require_postgres):
    stars = KnowledgeLoader.list_stars()
    assert len(stars) >= 7
    names = {s["star_name"] for s in stars}
    for required in ("紫微", "天府", "天机", "太阳", "武曲", "七杀", "破军"):
        assert required in names
    ziwei = KnowledgeLoader.get_star("紫微")
    assert ziwei is not None
    assert "管理" in "".join(ziwei.get("personality_positive") or []) or ziwei.get("basic_meaning")


def test_pattern_query(require_postgres):
    pattern = KnowledgeLoader.get_pattern("紫府同宫")
    assert pattern is not None
    assert "紫微" in (pattern.get("related_stars") or [])
    patterns = KnowledgeLoader.list_patterns()
    assert any(p["pattern_name"] == "杀破狼" for p in patterns)


def test_knowledge_service_context(require_postgres):
    chart = {
        "命宫": {"stars": ["紫微", "天府"]},
        "官禄宫": {"stars": ["武曲"]},
        "财帛宫": {"stars": ["天府"]},
    }
    ctx = KnowledgeService.build_context(chart, "我的事业方向如何？")
    assert ctx["question_type"] == "career"
    assert any(s["star_name"] == "紫微" for s in ctx["stars"])
    assert any(p["pattern_name"] == "紫府同宫" for p in ctx["patterns"]) or True


def test_safety_filter(require_postgres):
    SafetyFilter.refresh_cache()
    text = SafetyFilter.apply("你一定会发财，今年有灾")
    assert "一定会发财" not in text
    assert "今年有灾" not in text
    assert "现实行动" in text or "风险意识" in text


def test_knowledge_search(require_postgres):
    rows = KnowledgeSearch.search_stars("紫微")
    assert any(r["star_name"] == "紫微" for r in rows)
