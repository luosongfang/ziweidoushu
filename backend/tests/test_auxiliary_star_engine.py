"""V1.2 — AuxiliaryStarEngine 测试。"""

from __future__ import annotations

from datetime import datetime

import pytest

from app.ziwei.core.chart_normalizer import ChartNormalizer
from app.ziwei.core.chart_schema_v2 import AUXILIARY_STAR_NAMES, MAIN_STAR_NAMES
from app.ziwei.engines.auxiliary_star_engine import AuxiliaryStarEngine
from app.ziwei.engines.calendar_engine import CalendarEngine
from app.ziwei.engines.palace_engine import PalaceEngine
from app.ziwei.rules.cache import clear_rules_cache
from app.ziwei_engine.chart_builder import ChartBuilder


@pytest.fixture(autouse=True)
def fresh_rules_cache():
    clear_rules_cache()
    yield
    clear_rules_cache()


def _palaces(year: int, month: int, day: int, hour: int, minute: int):
    cal = CalendarEngine.convert(datetime(year, month, day, hour, minute))
    _, _, palaces = PalaceEngine.compute(
        cal.lunar_month, cal.shichen_index, year_stem=cal.year_stem
    )
    return cal, palaces


class TestAuxiliaryStarEngine:
    def test_nine_auxiliary_stars(self):
        cal, palaces = _palaces(1990, 5, 15, 14, 30)
        stars = AuxiliaryStarEngine.compute(palaces, cal.lunar_month, cal.year_branch)
        assert len(stars) == 9
        assert {s.name for s in stars} == set(AUXILIARY_STAR_NAMES)

    def test_each_star_has_trace(self):
        cal, palaces = _palaces(1990, 5, 15, 14, 30)
        stars = AuxiliaryStarEngine.compute(palaces, cal.lunar_month, cal.year_branch)
        for star in stars:
            assert star.trace.get("engine") == "auxiliary_star"
            assert star.trace.get("source")
            assert star.palace
            assert star.branch

    def test_stable_for_same_birth(self):
        cal, palaces = _palaces(1990, 5, 15, 14, 30)
        first = AuxiliaryStarEngine.compute(palaces, cal.lunar_month, cal.year_branch)
        second = AuxiliaryStarEngine.compute(palaces, cal.lunar_month, cal.year_branch)
        assert [(s.name, s.palace) for s in first] == [(s.name, s.palace) for s in second]

    def test_different_birth_different_positions(self):
        cal_a, palaces_a = _palaces(1990, 5, 15, 14, 30)
        cal_b, palaces_b = _palaces(1985, 3, 8, 6, 0)
        stars_a = AuxiliaryStarEngine.compute(palaces_a, cal_a.lunar_month, cal_a.year_branch)
        stars_b = AuxiliaryStarEngine.compute(palaces_b, cal_b.lunar_month, cal_b.year_branch)
        map_a = {s.name: s.palace for s in stars_a}
        map_b = {s.name: s.palace for s in stars_b}
        assert map_a != map_b

    def test_does_not_affect_main_stars(self):
        raw = ChartBuilder.build(
            name="基准男盘",
            gender="male",
            solar_date="1990-05-15",
            time="14:30",
            location="深圳",
            reference_year=2026,
        )
        chart = ChartNormalizer.normalize(raw)
        main_names = {s.name for s in chart.stars.main}
        assert main_names == set(MAIN_STAR_NAMES)
        assert not main_names & {s.name for s in chart.stars.auxiliary}
