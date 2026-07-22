"""Sprint 3 — Palace Engine 测试。"""

from __future__ import annotations

from datetime import datetime

import pytest

from app.models.birth import ChartGenerateRequest
from app.ziwei.chart_generator import ChartGenerator
from app.ziwei.engines.palace_engine import PalaceEngine
from app.ziwei.rules.loader import RulesLoader


class TestMingShenGong:
    def test_ming_gong_month4_hour_wei(self):
        assert PalaceEngine.calc_ming_gong_branch(4, 7) == 10  # 戌

    def test_shen_gong_month4_hour_wei(self):
        assert PalaceEngine.calc_shen_gong_branch(4, 7) == 0  # 子

    def test_ming_gong_month1_hour_mao(self):
        """1985-03-08 06:00 → 正月卯时 → 亥。"""
        assert PalaceEngine.calc_ming_gong_branch(1, 5) == 11  # 亥

    def test_shen_gong_month1_hour_mao(self):
        assert PalaceEngine.calc_shen_gong_branch(1, 5) == 5  # 巳


class TestTwelvePalaces:
    def test_branch_order_ref01(self):
        palaces = PalaceEngine.build_twelve_palaces(10, 0)
        assert [p.branch for p in palaces] == list("戌酉申未午巳辰卯寅丑子亥")

    def test_branch_order_ref04(self):
        palaces = PalaceEngine.build_twelve_palaces(11, 5)
        assert [p.branch for p in palaces] == list("亥戌酉申未午巳辰卯寅丑子")

    def test_opposite_palace(self):
        palaces = PalaceEngine.build_twelve_palaces(10, 0)
        ming = palaces[0]
        assert ming.opposite == "迁移"
        qianyi = next(p for p in palaces if p.name == "迁移")
        assert qianyi.opposite == "命宫"

    def test_sanhe_from_ming_xu(self):
        palaces = PalaceEngine.build_twelve_palaces(10, 0)
        ming = palaces[0]
        assert set(ming.sanhe) == {"财帛", "官禄"}

    def test_shen_gong_flag(self):
        palaces = PalaceEngine.build_twelve_palaces(10, 0)
        shen = [p for p in palaces if p.is_shen_gong]
        assert len(shen) == 1
        assert shen[0].branch == "子"
        assert shen[0].name == "福德"


class TestPalaceGanzhi:
    def test_all_palaces_have_ganzhi(self):
        _, _, palaces = PalaceEngine.compute(4, 7, year_stem="庚")
        assert len(palaces) == 12
        assert all(p.ganzhi for p in palaces)
        assert palaces[0].ganzhi == "丙戌"

    def test_ref04_ming_ganzhi(self):
        _, _, palaces = PalaceEngine.compute(1, 5, year_stem="乙")
        assert palaces[0].branch == "亥"
        assert palaces[0].ganzhi == "丁亥"


class TestPalaceMeanings:
    def test_all_palaces_have_meaning(self):
        _, _, palaces = PalaceEngine.compute(4, 7, year_stem="庚")
        for p in palaces:
            assert p.keyword
            assert p.meaning
            rule = RulesLoader.get_palace_meaning(p.name)
            assert rule is not None
            assert p.keyword == rule["keyword"]

    def test_ming_gong_keyword(self):
        _, _, palaces = PalaceEngine.compute(4, 7, year_stem="庚")
        assert palaces[0].keyword == "自我"


class TestChartIntegration:
    @pytest.fixture
    def chart(self):
        return ChartGenerator.generate(ChartGenerateRequest(
            birth_datetime=datetime(1990, 5, 15, 14, 30),
            gender="male",
        ))

    def test_palace_ganzhi_in_output(self, chart):
        ming = chart.palaces[0]
        assert ming.ganzhi == "丙戌"
        assert all(p.ganzhi for p in chart.palaces)

    def test_palace_analysis_tags(self, chart):
        ming = chart.palaces[0]
        assert ming.analysis_tags.tags[0] == "自我"
        assert "人生格局" in ming.analysis_tags.tags[1]

    def test_twelve_palace_names(self, chart):
        names = [p.name for p in chart.palaces]
        assert names[0] == "命宫"
        assert names[-1] == "父母"
