"""Phase 2 命盘引擎测试 — Engine V1.0。"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.ziwei.constants import EARTHLY_BRANCHES
from app.ziwei.engines.calendar_engine import CalendarEngine
from app.ziwei.rules.cache import clear_rules_cache
from app.ziwei_engine.calendar.lunar_converter import LunarConverter
from app.ziwei_engine.chart_builder import ChartBuilder
from app.ziwei_engine.palace.ming_gong import MingGongCalculator
from app.ziwei_engine.palace.shen_gong import ShenGongCalculator
from app.ziwei_engine.stars.fourteen_stars import FourteenStarsCalculator
from app.ziwei_engine.transformation.four_hua import FourHuaCalculator


@pytest.fixture(autouse=True)
def fresh_rules():
    clear_rules_cache()
    yield
    clear_rules_cache()


class TestLunarConverter:
    def test_convert_1990_05_20(self):
        lunar, _ = LunarConverter.convert("1990-05-20", "14:30", "北京")
        assert lunar.lunar_year == 1990
        assert 1 <= lunar.lunar_month <= 12
        assert 1 <= lunar.lunar_day <= 30
        assert isinstance(lunar.is_leap, bool)


class TestMingShenGong:
    def test_ming_gong_algorithm(self):
        """农历四月未时 — 与 REF-01 同月同时。"""
        cal = CalendarEngine.convert(__import__("datetime").datetime(1990, 5, 20, 14, 30))
        ming = MingGongCalculator.calculate(cal.lunar_month, cal.shichen_index)
        shen = ShenGongCalculator.calculate(cal.lunar_month, cal.shichen_index)
        assert ming in EARTHLY_BRANCHES
        assert shen in EARTHLY_BRANCHES
        assert ming == "戌"
        assert shen == "子"

    def test_ming_shen_different(self):
        cal = CalendarEngine.convert(__import__("datetime").datetime(1990, 5, 20, 14, 30))
        ming_idx = MingGongCalculator.calculate_index(cal.lunar_month, cal.shichen_index)
        shen_idx = ShenGongCalculator.calculate_index(cal.lunar_month, cal.shichen_index)
        assert ming_idx != shen_idx


class TestFourHua:
    def test_ten_stems_rules(self):
        rules = FourHuaCalculator.all_rules()
        assert len(rules) == 10
        geng = FourHuaCalculator.get_rule("庚")
        assert geng.hua_lu == "太阳"


class TestChartBuilder:
    def test_case1_1990_05_20_male(self):
        result = ChartBuilder.build(
            name="测试用户",
            gender="male",
            solar_date="1990-05-20",
            time="14:30",
            location="北京",
            reference_year=2026,
        )
        assert result["birth"]["year_gan"] == "庚"
        assert result["birth"]["year_zhi"] == "午"
        assert result["birth"]["lunar_detail"]["lunar_year"] == 1990
        assert result["chart"]["ming_gong"] == "戌"
        assert result["chart"]["shen_gong"] == "子"
        assert result["chart"]["five_element"] == "土五局"
        assert result["chart"]["ziwei"]["star"] == "紫微"
        assert len(result["chart"]["main_stars"]) == 14
        assert len(result["chart"]["palaces"]) == 12
        assert result["chart"]["four_hua"]["year_gan"] == "庚"

    def test_fourteen_star_names(self):
        result = ChartBuilder.build(
            name="测试", gender="male",
            solar_date="1990-05-20", time="14:30", location="北京",
        )
        names = {s["name"] for s in result["chart"]["main_stars"]}
        assert names == set(FourteenStarsCalculator.MAIN_STAR_NAMES)


class TestChartApi:
    def test_post_create(self):
        client = TestClient(app)
        response = client.post(
            "/api/chart/create",
            json={
                "name": "测试用户",
                "gender": "male",
                "solar_date": "1990-05-20",
                "time": "14:30",
                "location": "北京",
                "persist": False,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["schema_version"] == "2.5"
        assert data["birth"]["year_gan"] == "庚"
        assert data["meta"]["mingGong"] == "戌"
        assert len(data["palaces"]) == 12
        assert len(data["stars"]["main"]) == 14
