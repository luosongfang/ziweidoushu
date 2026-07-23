"""Knowledge Core V1.1 — Reasoning Engine tests (no LLM)."""

from __future__ import annotations

import pytest

from app.ai.reasoning_engine import ReasoningEngine
from app.ai.safety_filter import SafetyFilter
from app.config import settings
from app.database.database import is_database_ready
from app.knowledge.knowledge_loader import KnowledgeLoader
from app.knowledge.reasoning.question_classifier import QuestionClassifier


@pytest.fixture(scope="module")
def require_postgres():
    if not settings.is_postgres:
        pytest.skip("Reasoning tests require PostgreSQL / Supabase DATABASE_URL")
    if not is_database_ready():
        pytest.skip("database not ready")


CHART_ZIFU = {
    "命宫": {"stars": ["紫微", "天府"]},
    "官禄宫": {"stars": ["武曲", "左辅"]},
    "财帛宫": {"stars": ["天府"]},
    "迁移宫": {"stars": ["天马"]},
    "福德宫": {"stars": ["天同"]},
}

CHART_SHAPOLANG = {
    "命宫": {"stars": ["七杀"]},
    "官禄宫": {"stars": ["破军"]},
    "财帛宫": {"stars": ["贪狼"]},
    "迁移宫": {"stars": ["七杀", "破军"]},
    "福德宫": {"stars": ["贪狼"]},
}


def test_stars_expanded_v1_1(require_postgres):
    stars = KnowledgeLoader.list_stars()
    names = {s["star_name"] for s in stars}
    required = [
        "紫微", "天机", "太阳", "武曲", "天同", "廉贞", "天府",
        "太阴", "贪狼", "巨门", "天相", "天梁", "七杀", "破军",
        "左辅", "右弼", "文昌", "文曲", "天魁", "天钺",
        "擎羊", "陀罗", "火星", "铃星", "地空", "地劫",
        "禄存", "天马", "红鸾", "天喜", "孤辰", "寡宿",
    ]
    assert len(stars) >= 32
    for name in required:
        assert name in names
        row = KnowledgeLoader.get_star(name)
        assert row is not None
        assert row.get("basic_meaning")
        assert row.get("growth_advice")
        assert row.get("ai_prompt")
        assert row.get("life_stage_expression")


def test_palaces_twelve(require_postgres):
    expected = [
        "命宫", "兄弟宫", "夫妻宫", "子女宫", "财帛宫", "疾厄宫",
        "迁移宫", "仆役宫", "官禄宫", "田宅宫", "福德宫", "父母宫",
    ]
    for pname in expected:
        p = KnowledgeLoader.get_palace(pname)
        assert p is not None, pname
        assert p.get("life_area")
        assert p.get("modern_interpretation")
        assert p.get("development_advice")


def test_ziwei_tianfu_career(require_postgres):
    result = ReasoningEngine.run(
        question="我的事业发展方向如何？",
        chart_data=CHART_ZIFU,
    )
    assert result.question_type == "career"
    assert result.reasoning
    assert result.traditional_analysis
    assert result.suggestions
    assert result.safety_notice
    assert "classify:career" in result.call_trace
    assert any("prompt_built_no_llm" in t for t in result.call_trace)
    # 紫府 / 命宫 / 官禄 应有调用记录
    joined = " ".join(result.call_trace)
    assert "命宫" in joined or any("命宫" in r.dimension or "命宫" in str(r.observations) for r in result.reasoning)
    sources = [s for r in result.reasoning for s in r.sources]
    assert any(s.get("name") == "紫微" for s in sources)
    assert any(s.get("name") == "天府" for s in sources)


def test_shapolang_change_pattern(require_postgres):
    result = ReasoningEngine.run(
        question="面对变化与事业突破，我该注意什么？",
        chart_data=CHART_SHAPOLANG,
    )
    assert result.reasoning
    patterns = [s for r in result.reasoning for s in r.sources if s.get("type") == "pattern"]
    assert any(p.get("name") == "杀破狼" for p in patterns) or any(
        "杀破狼" in o for r in result.reasoning for o in r.observations
    )
    assert result.suggestions
    # 变革型建议应存在，且无绝对断言
    blob = " ".join(result.suggestions + result.traditional_analysis)
    assert "一定会" not in blob
    assert "注定" not in blob


def test_entrepreneurship_analysis(require_postgres):
    assert QuestionClassifier.classify("我想创业做老板") == "entrepreneurship"
    result = ReasoningEngine.run(
        question="我想创业，如何评估？",
        chart_data=CHART_ZIFU,
        user_context={"goal": "创业"},
    )
    assert result.question_type == "entrepreneurship"
    dims = [r.dimension for r in result.reasoning]
    assert any("entrepreneurship" in d for d in dims)
    suggestions_blob = "\n".join(result.suggestions)
    # 结论区不得出现二元判决句式
    assert "你适合创业" not in suggestions_blob
    assert "你不适合创业" not in suggestions_blob
    assert "适合/不适合" not in suggestions_blob
    assert result.suggestions
    assert any("创业" in s or "止损" in s or "验证" in s for s in result.suggestions)
    model = KnowledgeLoader.get_question_model("entrepreneurship")
    assert model is not None
    for p in ("命宫", "官禄宫", "财帛宫", "迁移宫", "福德宫"):
        assert p in (model.get("required_palaces") or [])


def test_safety_expression_in_pipeline(require_postgres):
    SafetyFilter.refresh_cache()
    # inject unsafe phrases via a fake chart path still goes through filter on outputs;
    # also verify filter itself
    text = SafetyFilter.apply("你一定会发财，今年有灾，注定成功")
    assert "一定会发财" not in text
    assert "今年有灾" not in text
    assert "注定" not in text

    result = ReasoningEngine.run(
        question="未来财富一定会怎样？",
        chart_data=CHART_ZIFU,
    )
    blob = " ".join(
        result.traditional_analysis
        + result.suggestions
        + [result.safety_notice]
        + [x for r in result.reasoning for x in r.suggestions]
    )
    assert "一定会发财" not in blob
    assert result.safety_notice
