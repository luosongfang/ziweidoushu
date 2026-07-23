"""Knowledge Core V3.2 — intelligence routing tests (no LLM)."""

from __future__ import annotations

import pytest

from app.ai.reasoning_engine_v2 import ReasoningEngineV2
from app.config import settings
from app.database.database import is_database_ready
from app.knowledge.intelligence.citation_engine import CitationEngine
from app.knowledge.intelligence.interpretation_layer import InterpretationLayer
from app.knowledge.intelligence.theory_router import TheoryRouter


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


def test_career_theory_route(require_postgres):
    route = TheoryRouter.route("career")
    assert "命宫" in route["required_palaces"]
    assert "官禄宫" in route["required_palaces"]
    assert "财帛宫" in route["required_palaces"]
    assert "三合派" in route["required_theories"]
    assert "四化" in route["required_theories"] or "大限" in route["required_theories"]

    result = ReasoningEngineV2.run(
        question="我的事业发展方向如何？",
        chart_data=CHART,
    )
    assert result.engine_version in {"3.2", "3.3", "4.0", "4.1", "5.0", "5.1"}
    assert result.question_type == "career"
    assert "命宫" in (result.theory_route or {}).get("required_palaces", [])
    assert "官禄宫" in (result.theory_route or {}).get("required_palaces", [])
    assert any(t in (result.theory_used or []) for t in ("三合派", "四化", "大限"))


def test_wealth_uses_caibo(require_postgres):
    route = TheoryRouter.route("wealth")
    assert "财帛宫" in route["required_palaces"]
    result = ReasoningEngineV2.run(
        question="如何做好财富规划与理财？",
        chart_data=CHART,
    )
    assert result.question_type == "wealth"
    assert "财帛宫" in (result.theory_route or {}).get("required_palaces", [])


def test_relationship_uses_fuqi(require_postgres):
    route = TheoryRouter.route("relationship")
    assert "夫妻宫" in route["required_palaces"]
    result = ReasoningEngineV2.run(
        question="我和伴侣感情关系如何改善沟通？",
        chart_data=CHART,
    )
    assert result.question_type == "relationship"
    assert "夫妻宫" in (result.theory_route or {}).get("required_palaces", [])


def test_dangerous_expression_safe(require_postgres):
    InterpretationLayer.refresh()
    out = InterpretationLayer.apply("传统说法是必有灾难，还会破财。")
    assert "必有灾难" not in out
    assert "风险管理" in out or "风险" in out
    assert "破财" not in out or "资源管理" in out

    result = ReasoningEngineV2.run(
        question="今年必有灾吗？会不会破财？",
        chart_data=CHART,
    )
    blob = " ".join(result.traditional_analysis + result.suggestions + [result.safety_notice])
    assert "必有灾难" not in blob
    assert "今年必有灾" not in blob


def test_citations_generated(require_postgres):
    result = ReasoningEngineV2.run(
        question="我的事业长期规划要注意什么？",
        chart_data=CHART,
    )
    # sources may be empty if no tagged chunks matched — evidence/citation lines still expected
    assert result.evidence is not None
    assert len(result.evidence) >= 1
    for e in result.evidence:
        assert e.get("claim")
        assert "analysis_id" in e
    # citation engine formatting
    lines = CitationEngine.render_lines(
        [{"book": "紫微斗数全书", "page": 35, "chapter": "紫微星"}]
    )
    assert any("紫微斗数全书" in x and "35" in x for x in lines)
    if result.sources:
        assert all("book" in s or "page" in s for s in result.sources)
