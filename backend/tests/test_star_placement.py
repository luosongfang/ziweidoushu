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
            palaces, cal.lunar_day, bureau.bureau_number
        )
        assert len(result.star_branches) == 14
        assert result.ziwei_branch == "巳"
        assert result.star_branches["紫微"] == "巳"

    def test_ref01_palace_mapping(self):
        cal, palaces, bureau = _build_palaces(1990, 5, 15, 14, 30)
        result = StarPlacementEngine.compute(
            palaces, cal.lunar_day, bureau.bureau_number
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
            palaces, cal.lunar_day, bureau.bureau_number
        )
        ziwei_idx = EARTHLY_BRANCHES.index(result.ziwei_branch)
        tianji_idx = EARTHLY_BRANCHES.index(result.star_branches["天机"])
        assert tianji_idx == (ziwei_idx - 1 + 12) % 12

    def test_tianfu_opposite_ziwei(self):
        cal, palaces, bureau = _build_palaces(1990, 5, 15, 14, 30)
        result = StarPlacementEngine.compute(
            palaces, cal.lunar_day, bureau.bureau_number
        )
        ziwei_idx = EARTHLY_BRANCHES.index(result.ziwei_branch)
        tianfu_idx = EARTHLY_BRANCHES.index(result.star_branches["天府"])
        assert tianfu_idx == (ziwei_idx + 6) % 12


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
