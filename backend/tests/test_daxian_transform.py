"""V1.2 — 大限四化测试。"""

from __future__ import annotations

from datetime import datetime

import pytest

from app.ziwei.core.chart_normalizer import ChartNormalizer
from app.ziwei.engines.calendar_engine import CalendarEngine
from app.ziwei.engines.fortune_engine import FortuneEngine
from app.ziwei.engines.palace_engine import PalaceEngine
from app.ziwei.engines.star_placement_engine import StarPlacementEngine
from app.ziwei.rules.cache import clear_rules_cache
from app.ziwei.transformation.daxian_hua import DaxianTransformCalculator
from app.ziwei_engine.chart_builder import ChartBuilder


@pytest.fixture(autouse=True)
def fresh_rules_cache():
    clear_rules_cache()
    yield
    clear_rules_cache()


def _build_context(year: int, month: int, day: int, hour: int, minute: int, gender: str):
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
    star_to_palace = placement.star_to_palace(branch_to_palace)
    daxian_map, _ = FortuneEngine.calc_daxian(
        palaces, bureau.bureau_number, cal.year_stem, gender
    )
    birth = datetime(year, month, day, hour, minute)
    ref = datetime(2026, month, day, hour, minute)
    virtual_age = FortuneEngine._calc_age(birth, ref)  # noqa: SLF001
    return cal, palaces, star_to_palace, daxian_map, virtual_age


class TestDaxianTransform:
    def test_four_transforms_present(self):
        _, palaces, star_to_palace, daxian_map, virtual_age = _build_context(
            1990, 5, 15, 14, 30, "male"
        )
        result = DaxianTransformCalculator.compute(
            palaces, daxian_map, star_to_palace, "male", "庚", virtual_age
        )
        assert result is not None
        assert result.stem
        assert result.period
        assert result.lu and result.lu.star and result.lu.palace
        assert result.quan and result.quan.star and result.quan.palace
        assert result.ke and result.ke.star and result.ke.palace
        assert result.ji and result.ji.star and result.ji.palace
        assert result.source == "four_transform_rules"
        assert result.trace.get("engine") == "daxian_transform"

    def test_in_normalized_chart(self):
        chart = ChartNormalizer.normalize(ChartBuilder.build(
            name="基准男盘",
            gender="male",
            solar_date="1990-05-15",
            time="14:30",
            location="深圳",
            reference_year=2026,
        ))
        dt = chart.daxian_transform
        assert dt is not None
        assert dt.lu.star and dt.lu.palace
        assert dt.quan.star and dt.quan.palace
        assert dt.ke.star and dt.ke.palace
        assert dt.ji.star and dt.ji.palace
