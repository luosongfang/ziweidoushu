"""V1.2 — 流年四化测试。"""

from __future__ import annotations

from datetime import datetime

import pytest

from app.ziwei.core.chart_normalizer import ChartNormalizer
from app.ziwei.engines.calendar_engine import CalendarEngine
from app.ziwei.engines.palace_engine import PalaceEngine
from app.ziwei.engines.star_placement_engine import StarPlacementEngine
from app.ziwei.rules.cache import clear_rules_cache
from app.ziwei.transformation.liunian_hua import LiunianTransformCalculator
from app.ziwei_engine.chart_builder import ChartBuilder


@pytest.fixture(autouse=True)
def fresh_rules_cache():
    clear_rules_cache()
    yield
    clear_rules_cache()


def _star_to_palace(year: int, month: int, day: int, hour: int, minute: int) -> dict[str, str]:
    cal = CalendarEngine.convert(datetime(year, month, day, hour, minute))
    ming_branch, _, palaces = PalaceEngine.compute(
        cal.lunar_month, cal.shichen_index, year_stem=cal.year_stem
    )
    from app.ziwei.engines.bureau_engine import BureauEngine

    bureau = BureauEngine.compute(cal.year_stem, ming_branch)
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
    return placement.star_to_palace(branch_to_palace)


class TestAnnualTransform:
    def test_2026_bingwu_year(self):
        star_to_palace = _star_to_palace(1990, 5, 15, 14, 30)
        result = LiunianTransformCalculator.compute(2026, star_to_palace)
        assert result.year == 2026
        assert result.stem == "丙"
        assert result.branch == "午"
        assert result.lu and result.lu.star
        assert result.quan and result.quan.star
        assert result.ke and result.ke.star
        assert result.ji and result.ji.star
        assert result.trace.get("engine") == "annual_transform"

    def test_in_liunian_schema(self):
        chart = ChartNormalizer.normalize(ChartBuilder.build(
            name="基准男盘",
            gender="male",
            solar_date="1990-05-15",
            time="14:30",
            location="深圳",
            reference_year=2026,
        ))
        annual = chart.liunian.annual_transform
        assert annual is not None
        assert annual.year == 2026
        assert annual.stem == "丙"
        assert annual.lu.star and annual.lu.palace
