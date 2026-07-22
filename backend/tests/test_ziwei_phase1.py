"""Phase 1 / Sprint 0 排盘引擎测试。"""

from __future__ import annotations

from datetime import datetime

import pytest

from app.models.birth import ChartGenerateRequest
from app.ziwei.chart_generator import ChartGenerator
from app.ziwei.engines.calendar_engine import CalendarEngine, hour_to_shichen
from app.ziwei.engines.palace_engine import PalaceEngine
from app.ziwei.engines.bureau_engine import BureauEngine


class TestShichen:
    def test_wei_hour(self):
        idx, name, _ = hour_to_shichen(14, 30)
        assert idx == 7
        assert name == "未时"


class TestPalaceAlgorithm:
    def test_ming_gong_month4_hour_wei(self):
        assert PalaceEngine.calc_ming_gong_branch(4, 7) == 10

    def test_shen_gong_month4_hour_wei(self):
        assert PalaceEngine.calc_shen_gong_branch(4, 7) == 0

    def test_twelve_palaces_branch_order(self):
        palaces = PalaceEngine.build_twelve_palaces(10, 0)
        assert [p.branch for p in palaces] == [
            "戌", "酉", "申", "未", "午", "巳", "辰", "卯", "寅", "丑", "子", "亥"
        ]

    def test_opposite_palace(self):
        palaces = PalaceEngine.build_twelve_palaces(10, 0)
        ming = palaces[0]
        assert ming.opposite == "迁移"

    def test_sanhe_relation(self):
        palaces = PalaceEngine.build_twelve_palaces(10, 0)
        ming = palaces[0]
        assert len(ming.sanhe) == 2


class TestBureau:
    def test_bingxu_tu_wuju(self):
        result = BureauEngine.compute("庚", 10)
        assert result.ming_gong_ganzhi == "丙戌"
        assert result.bureau_name == "土五局"


class TestChart19900515Male:
    @pytest.fixture
    def chart(self):
        req = ChartGenerateRequest(
            birth_datetime=datetime(1990, 5, 15, 14, 30, 0),
            gender="male",
            name="测试命盘",
        )
        return ChartGenerator.generate(req)

    def test_version(self, chart):
        assert chart.version == "1.0-final"
        assert chart.school == "sanhe"

    def test_lunar_conversion(self, chart):
        assert "四月" in chart.birth.lunar
        assert chart.birth.ganzhi.year == "庚午"
        assert chart.birth.ganzhi.hour == "癸未"

    def test_ming_shen_gong(self, chart):
        assert chart.meta.mingGong == "戌"
        assert chart.meta.shenGong == "子"
        assert chart.meta.mingGongGanZhi == "丙戌"

    def test_wuxing_ju(self, chart):
        assert chart.meta.wuxingJu == "土五局"
        assert chart.meta.bureauNumber == 5

    def test_palace_structure(self, chart):
        assert len(chart.palaces) == 12
        ming = chart.palaces[0]
        assert ming.position == 1
        assert ming.opposite == "迁移"
        assert ming.isMingGong is True

    def test_daxian(self, chart):
        assert chart.fortune.daxianDirection == "forward"
        assert chart.palaces[0].daxian.startAge == 5

    def test_trace(self, chart):
        assert chart.trace is not None
        assert len(chart.trace.steps) >= 3


class TestChart19850308Female:
    @pytest.fixture
    def chart(self):
        return ChartGenerator.generate(ChartGenerateRequest(
            birth_datetime=datetime(1985, 3, 8, 6, 0, 0),
            gender="female",
        ))

    def test_daxian_forward(self, chart):
        assert chart.fortune.daxianDirection == "forward"


class TestChart19850308Male:
    @pytest.fixture
    def chart(self):
        return ChartGenerator.generate(ChartGenerateRequest(
            birth_datetime=datetime(1985, 3, 8, 6, 0, 0),
            gender="male",
        ))

    def test_daxian_reverse(self, chart):
        assert chart.fortune.daxianDirection == "backward"


class TestCalendar:
    def test_solar_to_lunar_1990(self):
        result = CalendarEngine.convert(datetime(1990, 5, 15, 14, 30))
        assert result.lunar_month == 4
        assert result.lunar_day == 21
        assert result.hour_branch == "未"
