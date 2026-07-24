"""Sprint 4 — Star Placement Engine 测试。"""

from __future__ import annotations

from datetime import datetime

import pytest

from app.models.birth import ChartGenerateRequest
from app.models.star import StarOutput
from app.ziwei.chart_generator import ChartGenerator
from app.ziwei.constants import EARTHLY_BRANCHES
from app.ziwei.engines.bureau_engine import BureauEngine
from app.ziwei.engines.calendar_engine import CalendarEngine
from app.ziwei.engines.palace_engine import PalaceEngine
from app.ziwei.engines.star_placement_engine import StarPlacementEngine
from app.ziwei.rules.loader import RulesLoader


def _build_palaces(year: int, month: int, day: int, hour: int, minute: int):
    cal = CalendarEngine.convert(datetime(year, month, day, hour, minute))
    ming, _, palaces = PalaceEngine.compute(
        cal.lunar_month, cal.shichen_index, year_stem=cal.year_stem
    )
    bureau = BureauEngine.compute(cal.year_stem, ming)
    return cal, palaces, bureau


class TestZiweiPosition:
    def test_day21_bureau5_si(self):
        branch = RulesLoader.get_ziwei_position(5, 21)
        assert branch == "巳"


class TestMainStarPlacement:
    def test_ref01_all_fourteen_stars(self):
        cal, palaces, bureau = _build_palaces(1990, 5, 15, 14, 30)
        result = StarPlacementEngine.compute(
            palaces,
            cal.lunar_day,
            bureau.bureau_number,
            cal.year_stem,
            cal.year_branch,
            cal.shichen_index,
            cal.lunar_month,
        )
        main14 = {
            "紫微", "天机", "太阳", "武曲", "天同", "廉贞",
            "天府", "太阴", "贪狼", "巨门", "天相", "天梁", "七杀", "破军",
        }
        assert main14.issubset(result.star_branches.keys())
        assert result.ziwei_branch == "巳"
        assert result.star_branches["紫微"] == "巳"

    def test_ref01_palace_mapping(self):
        cal, palaces, bureau = _build_palaces(1990, 5, 15, 14, 30)
        result = StarPlacementEngine.compute(
            palaces,
            cal.lunar_day,
            bureau.bureau_number,
            cal.year_stem,
            cal.year_branch,
            cal.shichen_index,
            cal.lunar_month,
        )
        assert result.main_star_names("疾厄") == ["紫微", "七杀"]
        assert result.main_star_names("兄弟") == ["廉贞", "破军"]
        assert result.main_star_names("官禄") == ["太阳", "巨门"]
        assert result.main_star_names("田宅") == ["武曲", "贪狼"]
        assert result.main_star_names("交友") == ["天相"]
        assert result.main_star_names("迁移") == ["天机", "天梁"]
        assert result.main_star_names("福德") == ["天同", "太阴"]
        assert result.main_star_names("父母") == ["天府"]
        assert result.main_star_names("命宫") == []
        assert result.main_star_names("夫妻") == []
        assert result.main_star_names("子女") == []
        assert result.main_star_names("财帛") == []

    def test_tianji_backward_from_ziwei(self):
        cal, palaces, bureau = _build_palaces(1990, 5, 15, 14, 30)
        result = StarPlacementEngine.compute(
            palaces,
            cal.lunar_day,
            bureau.bureau_number,
            cal.year_stem,
            cal.year_branch,
            cal.shichen_index,
            cal.lunar_month,
        )
        ziwei_idx = EARTHLY_BRANCHES.index(result.ziwei_branch)
        tianji_idx = EARTHLY_BRANCHES.index(result.star_branches["天机"])
        assert tianji_idx == (ziwei_idx - 1 + 12) % 12

    def test_tianfu_yin_shen_mirror(self):
        """天府为寅申轴镜像，非对宫（紫微巳时碰巧与对宫同为亥）。"""
        cal, palaces, bureau = _build_palaces(1990, 5, 15, 14, 30)
        result = StarPlacementEngine.compute(
            palaces,
            cal.lunar_day,
            bureau.bureau_number,
            cal.year_stem,
            cal.year_branch,
            cal.shichen_index,
            cal.lunar_month,
        )
        ziwei_idx = EARTHLY_BRANCHES.index(result.ziwei_branch)
        tianfu_idx = EARTHLY_BRANCHES.index(result.star_branches["天府"])
        assert tianfu_idx == (4 - ziwei_idx) % 12

    def test_1982_wei_hour_matches_classical(self):
        """1982-02-22 未时：水二局，紫微卯，天府丑，命宫廉贞七杀。"""
        cal, palaces, bureau = _build_palaces(1982, 2, 22, 14, 0)
        result = StarPlacementEngine.compute(
            palaces,
            cal.lunar_day,
            bureau.bureau_number,
            cal.year_stem,
            cal.year_branch,
            cal.shichen_index,
            cal.lunar_month,
        )
        assert cal.lunar_month == 1 and cal.lunar_day == 29
        assert bureau.bureau_name == "水二局"
        assert result.ziwei_branch == "卯"
        assert result.star_branches["天府"] == "丑"
        assert result.main_star_names("命宫") == ["廉贞", "七杀"]
        main14 = {
            "紫微", "天机", "太阳", "武曲", "天同", "廉贞",
            "天府", "太阴", "贪狼", "巨门", "天相", "天梁", "七杀", "破军",
        }
        assert main14.issubset(result.star_branches.keys())
        assert result.star_branches["破军"] == "亥"
        assert result.star_branches["贪狼"] == "卯"


class TestChartIntegration:
    @pytest.fixture
    def chart(self):
        return ChartGenerator.generate(ChartGenerateRequest(
            birth_datetime=datetime(1990, 5, 15, 14, 30),
            gender="male",
        ))

    def test_main_stars_in_palaces(self, chart):
        jie = next(p for p in chart.palaces if p.name == "疾厄")
        assert [s.name for s in jie.mainStars] == ["紫微", "七杀"]
        assert all(isinstance(s, StarOutput) for s in jie.mainStars)
        assert all(s.isMain for s in jie.mainStars)

    def test_empty_palace_no_main_stars(self, chart):
        ming = chart.palaces[0]
        assert ming.mainStars == []

    def test_trace_includes_star_placement(self, chart):
        step = next(s for s in chart.trace.steps if s["engine"] == "star_placement")
        assert step["output"]["ziweiBranch"] == "巳"
        assert step["output"]["mainStarCount"] == 14

    @pytest.mark.parametrize(
        "palace,stars",
        [
            ("疾厄", ["紫微", "七杀"]),
            ("兄弟", ["廉贞", "破军"]),
            ("官禄", ["太阳", "巨门"]),
            ("福德", ["天同", "太阴"]),
            ("父母", ["天府"]),
        ],
    )
    def test_ref01_key_palaces(self, chart, palace, stars):
        p = next(x for x in chart.palaces if x.name == palace)
        assert [s.name for s in p.mainStars] == stars
