"""V1.2 — 小限系统测试。"""

from __future__ import annotations

from datetime import datetime

import pytest

from app.ziwei.core.chart_normalizer import ChartNormalizer
from app.ziwei.engines.calendar_engine import CalendarEngine
from app.ziwei.engines.palace_engine import PalaceEngine
from app.ziwei.fortune.xiaoxian import XiaoxianCalculator
from app.ziwei.rules.cache import clear_rules_cache
from app.ziwei_engine.chart_builder import ChartBuilder


@pytest.fixture(autouse=True)
def fresh_rules_cache():
    clear_rules_cache()
    yield
    clear_rules_cache()


def _setup(year: int, month: int, day: int, hour: int, minute: int):
    cal = CalendarEngine.convert(datetime(year, month, day, hour, minute))
    _, _, palaces = PalaceEngine.compute(
        cal.lunar_month, cal.shichen_index, year_stem=cal.year_stem
    )
    birth = datetime(year, month, day, hour, minute)
    return cal, palaces, birth


class TestXiaoxianCalculator:
    def test_enabled_with_cycle(self):
        cal, palaces, birth = _setup(1990, 5, 15, 14, 30)
        result = XiaoxianCalculator.compute(
            palaces, "male", cal.year_stem, birth, reference=datetime(2026, 5, 15, 14, 30)
        )
        assert result.enabled
        assert result.current_age > 0
        assert result.current_palace
        assert len(result.yearly_cycle) == 120
        assert result.yearly_cycle[0].age == 1
        assert result.trace.get("engine") == "xiaoxian"

    def test_gender_direction(self):
        cal, palaces, birth = _setup(1985, 3, 8, 6, 0)
        male = XiaoxianCalculator.compute(
            palaces, "male", cal.year_stem, birth, reference=datetime(2026, 3, 8, 6, 0)
        )
        female = XiaoxianCalculator.compute(
            palaces, "female", cal.year_stem, birth, reference=datetime(2026, 3, 8, 6, 0)
        )
        if male.direction != female.direction:
            assert male.current_palace != female.current_palace

    def test_age_changes_palace(self):
        cal, palaces, birth = _setup(1990, 5, 15, 14, 30)
        age_30 = XiaoxianCalculator.compute(
            palaces, "male", cal.year_stem, birth, reference=datetime(2019, 5, 15, 14, 30)
        )
        age_40 = XiaoxianCalculator.compute(
            palaces, "male", cal.year_stem, birth, reference=datetime(2029, 5, 15, 14, 30)
        )
        assert age_30.current_age != age_40.current_age
        assert age_30.current_palace != age_40.current_palace

    def test_normalized_in_chart(self):
        chart = ChartNormalizer.normalize(ChartBuilder.build(
            name="基准男盘",
            gender="male",
            solar_date="1990-05-15",
            time="14:30",
            location="深圳",
            reference_year=2026,
        ))
        assert chart.xiaoxian.enabled
        assert chart.xiaoxian.ranges == chart.xiaoxian.yearly_cycle
