"""Sprint 7 — AI 分析接口测试。"""

from __future__ import annotations

from datetime import datetime

import pytest

from app.ai.analysis_service import AnalysisService
from app.ai.context_builder import ContextBuilder
from app.ai.rag_retriever import RagRetriever
from app.models.analysis import AnalysisGenerateRequest
from app.models.birth import BirthInput, ChartGenerateRequest
from app.ziwei.chart_generator import ChartGenerator
from app.ziwei.rules.cache import clear_rules_cache


@pytest.fixture(autouse=True)
def fresh_rules_cache():
    clear_rules_cache()
    yield
    clear_rules_cache()


def _ref01_chart(reference: datetime | None = None):
    request = ChartGenerateRequest(
        birth_datetime=datetime(1990, 5, 15, 14, 30),
        gender="male",
        name="基准男盘",
        location={"country": "China", "city": "深圳", "longitude": 114.0579},
    )
    return ChartGenerator.generate(request, reference_date=reference or datetime(2026, 7, 22))


class TestContextBuilder:
    def test_build_overall_context(self):
        chart = _ref01_chart()
        ctx = ContextBuilder.build(chart, "overall")
        assert ctx["meta"]["mingGong"] == "戌"
        assert ctx["meta"]["wuxingJu"] == "土五局"
        assert len(ctx["combinations"]) >= 5
        assert ctx["four_transform"]["yearStem"] == "庚"
        assert any(p["isMingGong"] for p in ctx["palaces"])

    def test_build_palace_context(self):
        chart = _ref01_chart()
        ctx = ContextBuilder.build(chart, "palace", "官禄")
        focused = [p for p in ctx["palaces"] if p["focused"]]
        assert len(focused) == 1
        assert focused[0]["name"] == "官禄"
        assert "太阳" in focused[0]["mainStars"]


class TestRagRetriever:
    def test_retrieve_by_combination(self):
        chunks = RagRetriever.retrieve(["杀破狼", "四化"])
        assert len(chunks) > 0
        assert any("杀破狼" in (c.title or "") or "杀破狼" in c.content for c in chunks)

    def test_retrieve_empty_queries(self):
        assert RagRetriever.retrieve([]) == []


class TestAnalysisServiceRules:
    @pytest.mark.asyncio
    async def test_overall_analysis_ref01(self):
        chart = _ref01_chart()
        request = AnalysisGenerateRequest(chart=chart, mode="rules")
        result = await AnalysisService.generate(request)

        assert result.mode == "rules"
        assert result.analysis_type == "overall"
        assert len(result.sections) >= 4
        assert "命盘概览" in result.result_text
        assert "格局分析" in result.result_text
        assert "四化分析" in result.result_text
        assert result.chart_summary["mingGong"] == "戌"
        assert result.chart_summary["combinationCount"] >= 5

    @pytest.mark.asyncio
    async def test_palace_analysis(self):
        chart = _ref01_chart()
        request = AnalysisGenerateRequest(
            chart=chart,
            analysis_type="palace",
            palace_name="官禄",
            mode="rules",
        )
        result = await AnalysisService.generate(request)
        assert "官禄" in result.result_text
        assert "太阳" in result.result_text

    @pytest.mark.asyncio
    async def test_daxian_analysis(self):
        chart = _ref01_chart()
        request = AnalysisGenerateRequest(chart=chart, analysis_type="daxian", mode="rules")
        result = await AnalysisService.generate(request)
        assert "大限" in result.result_text

    @pytest.mark.asyncio
    async def test_liunian_analysis(self):
        chart = _ref01_chart()
        request = AnalysisGenerateRequest(chart=chart, analysis_type="liunian", mode="rules")
        result = await AnalysisService.generate(request)
        assert "流年" in result.result_text

    @pytest.mark.asyncio
    async def test_from_birth_input(self):
        birth = BirthInput(
            name="基准男盘",
            gender="male",
            date="1990-05-15",
            time="14:30",
            location={"country": "China", "city": "深圳", "longitude": 114.0579},
        )
        request = AnalysisGenerateRequest(
            birth=birth,
            reference_date="2026-07-22",
            mode="rules",
        )
        result = await AnalysisService.generate(request)
        assert result.mode == "rules"
        assert "庚午" in result.result_text or "庚" in result.result_text

    @pytest.mark.asyncio
    async def test_rag_chunks_included(self):
        chart = _ref01_chart()
        request = AnalysisGenerateRequest(chart=chart, mode="rules")
        result = await AnalysisService.generate(request)
        assert len(result.rag_chunks) > 0

    def test_palace_requires_name(self):
        chart = _ref01_chart()
        with pytest.raises(ValueError, match="palace_name"):
            AnalysisGenerateRequest(chart=chart, analysis_type="palace")

    def test_requires_chart_or_birth(self):
        with pytest.raises(ValueError, match="chart 或 birth"):
            AnalysisGenerateRequest(analysis_type="overall")
