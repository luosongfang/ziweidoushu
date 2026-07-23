"""V1.2 — 主星亮度测试。"""

from __future__ import annotations

import pytest

from app.ziwei.core.chart_normalizer import ChartNormalizer
from app.ziwei.core.chart_schema_v2 import BRIGHTNESS_LEVELS, MAIN_STAR_NAMES
from app.ziwei.engines.brightness_engine import BrightnessEngine
from app.ziwei.rules.cache import clear_rules_cache
from app.ziwei_engine.chart_builder import ChartBuilder


@pytest.fixture(autouse=True)
def fresh_rules_cache():
    clear_rules_cache()
    yield
    clear_rules_cache()


class TestStarBrightness:
    def test_all_main_stars_have_brightness(self):
        chart = ChartNormalizer.normalize(ChartBuilder.build(
            name="基准男盘",
            gender="male",
            solar_date="1990-05-15",
            time="14:30",
            location="深圳",
            reference_year=2026,
        ))
        for name in MAIN_STAR_NAMES:
            star = next(s for s in chart.stars.main if s.name == name)
            assert star.brightness in BRIGHTNESS_LEVELS
            assert chart.brightness[name] == star.brightness

    def test_brightness_engine_uses_rules(self):
        value = BrightnessEngine.get_brightness("紫微", "巳")
        assert value in BRIGHTNESS_LEVELS

    def test_brightness_map_complete(self):
        chart = ChartNormalizer.normalize(ChartBuilder.build(
            name="基准男盘",
            gender="male",
            solar_date="1990-05-15",
            time="14:30",
            location="深圳",
            reference_year=2026,
        ))
        assert len(chart.brightness) == 14
