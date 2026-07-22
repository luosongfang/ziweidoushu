"""Sprint 6 — 大限、组合、验证系统测试。"""

from __future__ import annotations

from datetime import datetime

import pytest

from app.models.birth import ChartGenerateRequest
from app.ziwei.chart_generator import ChartGenerator
from app.ziwei.engines.bureau_engine import BureauEngine
from app.ziwei.engines.calendar_engine import CalendarEngine
from app.ziwei.engines.combination_engine import CombinationEngine
from app.ziwei.engines.fortune_engine import FortuneEngine
from app.ziwei.engines.four_transform_engine import FourTransformEngine
from app.ziwei.engines.palace_engine import PalaceEngine
from app.ziwei.engines.star_placement_engine import StarPlacementEngine
from app.ziwei.rules.cache import clear_rules_cache
from app.ziwei.verification.manager import VerificationManager


@pytest.fixture(autouse=True)
def fresh_rules_cache():
    clear_rules_cache()
    yield
    clear_rules_cache()


def _build_ref01(reference: datetime | None = None):
    cal = CalendarEngine.convert(datetime(1990, 5, 15, 14, 30))
    ming, _, palaces = PalaceEngine.compute(
        cal.lunar_month, cal.shichen_index, year_stem=cal.year_stem
    )
    bureau = BureauEngine.compute(cal.year_stem, ming)
    placement = StarPlacementEngine.compute(
        palaces,
        cal.lunar_day,
        bureau.bureau_number,
        cal.year_stem,
        cal.year_branch,
        cal.shichen_index,
        cal.lunar_month,
    )
    branch_to_palace = {p.branch: p.name for p in palaces}
    transform = FourTransformEngine.compute(
        cal.year_stem, placement.star_to_palace(branch_to_palace)
    )
    daxian_map, _ = FortuneEngine.calc_daxian(
        palaces, bureau.bureau_number, cal.year_stem, "male"
    )
    ref = reference or datetime(2026, 7, 22)
    fortune = FortuneEngine.build_snapshot(
        palaces, daxian_map, datetime(1990, 5, 15, 14, 30), "male", cal.year_stem, ref
    )
    combos = CombinationEngine.compute(palaces, placement, transform.star_sihua)
    return palaces, placement, transform, fortune, combos


class TestFortuneEngine:
    def test_ref01_daxian_forward(self):
        palaces, _, _, _, _ = _build_ref01()
        daxian_map, direction = FortuneEngine.calc_daxian(palaces, 5, "庚", "male")
        assert direction == "forward"
        assert daxian_map["命宫"].start_age == 5
        assert daxian_map["兄弟"].start_age == 15

    def test_current_daxian_2026(self):
        _, _, _, fortune, _ = _build_ref01(datetime(2026, 7, 22))
        assert fortune.current_daxian is not None
        assert fortune.current_daxian["palace"] == "子女"
        assert fortune.current_daxian["virtualAge"] == 36

    def test_annual_fortune_2026(self):
        _, _, _, fortune, _ = _build_ref01(datetime(2026, 7, 22))
        assert fortune.annual_fortune is not None
        assert fortune.annual_fortune["yearBranch"] == "午"
        assert fortune.annual_fortune["palace"] == "财帛"

    def test_monthly_fortune(self):
        _, _, _, fortune, _ = _build_ref01(datetime(2026, 7, 22))
        assert fortune.monthly_fortune is not None
        assert fortune.monthly_fortune["month"] == 7


class TestCombinationEngine:
    def test_ref01_patterns(self):
        _, _, _, _, combos = _build_ref01()
        names = sorted(p.name for p in combos.patterns)
        assert "禄马交驰" in names
        assert "天同太阴" in names
        assert "武曲贪狼" in names
        assert "杀破狼" in names
        assert "太阳化禄" in names
        assert "天同化忌" in names
        assert len(names) == 10

    def test_luma_same_palace(self):
        _, _, _, _, combos = _build_ref01()
        luma = next(p for p in combos.patterns if p.name == "禄马交驰")
        assert luma.palaces == ["夫妻"]


class TestVerificationManager:
    def test_reference_suite_passes(self):
        report = VerificationManager.run_reference_suite()
        assert report.total_charts >= 6
        assert report.passed, report.failed_charts


class TestChartIntegration:
    def test_chart_has_fortune_and_combinations(self):
        chart = ChartGenerator.generate(ChartGenerateRequest(
            birth_datetime=datetime(1990, 5, 15, 14, 30),
            gender="male",
        ))
        assert chart.fortune.daxianDirection == "forward"
        assert chart.fortune.currentDaxian is not None
        assert chart.fortune.annualFortune is not None
        assert len(chart.combinations.patterns) == 10
        engines = [s["engine"] for s in chart.trace.steps]
        assert "fortune" in engines
        assert "combination" in engines
