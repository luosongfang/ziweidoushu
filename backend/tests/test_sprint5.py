"""Sprint 5 — 辅煞杂曜、四化、亮度测试。"""

from __future__ import annotations

from datetime import datetime

import pytest

from app.models.birth import ChartGenerateRequest
from app.ziwei.chart_generator import ChartGenerator
from app.ziwei.engines.brightness_engine import BrightnessEngine
from app.ziwei.engines.calendar_engine import CalendarEngine
from app.ziwei.engines.four_transform_engine import FourTransformEngine
from app.ziwei.engines.bureau_engine import BureauEngine
from app.ziwei.engines.palace_engine import PalaceEngine
from app.ziwei.engines.star_placement_engine import StarPlacementEngine
from app.ziwei.rules.cache import clear_rules_cache
from app.ziwei.rules.loader import RulesLoader
from app.ziwei.rules.seed_generator import build_all_rules


@pytest.fixture(autouse=True)
def fresh_rules_cache():
    clear_rules_cache()
    yield
    clear_rules_cache()


def _ref01_placement():
    cal = CalendarEngine.convert(datetime(1990, 5, 15, 14, 30))
    ming, _, palaces = PalaceEngine.compute(
        cal.lunar_month, cal.shichen_index, year_stem=cal.year_stem
    )
    bureau = BureauEngine.compute(cal.year_stem, ming)
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
    return cal, placement, branch_to_palace


class TestStarLookupRules:
    def test_lookup_rules_loaded(self):
        rules = build_all_rules()
        assert len(rules["star_lookup_rules"]) >= 5

    def test_tiankui_geng(self):
        lookup = RulesLoader.get_star_lookup("天魁")
        assert lookup["mapping"]["庚"] == "丑"


class TestAuxShaZaPlacement:
    def test_ref01_aux_stars(self):
        _, placement, _ = _ref01_placement()
        assert placement.aux_stars.get("子女")  # 左辅右弼天钺
        names = {s["name"] for stars in placement.aux_stars.values() for s in stars}
        assert {"左辅", "右弼", "天魁", "天钺", "禄存"} <= names

    def test_ref01_sha_stars(self):
        _, placement, _ = _ref01_placement()
        names = {s["name"] for stars in placement.sha_stars.values() for s in stars}
        assert names == {"擎羊", "陀罗", "火星", "铃星", "地空", "地劫"}

    def test_ref01_za_stars(self):
        _, placement, _ = _ref01_placement()
        assert placement.za_stars["夫妻"][0]["name"] == "天马"

    def test_ref01_zuofu_ziyou_same_palace(self):
        _, placement, _ = _ref01_placement()
        zi_nu = {s["name"] for s in placement.aux_stars.get("子女", [])}
        assert "左辅" in zi_nu and "右弼" in zi_nu


class TestBrightness:
    def test_ziwei_si_wang(self):
        assert BrightnessEngine.get_brightness("紫微", "巳") == "旺"

    def test_taiyang_yin_wang(self):
        assert BrightnessEngine.get_brightness("太阳", "寅") == "旺"


class TestFourTransform:
    def test_geng_year_transform(self):
        _, placement, branch_to_palace = _ref01_placement()
        star_to_palace = placement.star_to_palace(branch_to_palace)
        result = FourTransformEngine.compute("庚", star_to_palace)
        assert result.star_sihua["太阳"] == "禄"
        assert result.star_sihua["武曲"] == "权"
        assert result.star_sihua["太阴"] == "科"
        assert result.star_sihua["天同"] == "忌"
        assert result.summary.lu.palace == "官禄"
        assert result.summary.ji.palace == "福德"


class TestChartIntegration:
    @pytest.fixture
    def chart(self):
        return ChartGenerator.generate(ChartGenerateRequest(
            birth_datetime=datetime(1990, 5, 15, 14, 30),
            gender="male",
        ))

    def test_four_transform_summary(self, chart):
        assert chart.fourTransformSummary is not None
        assert chart.fourTransformSummary.yearStem == "庚"
        assert chart.fourTransformSummary.lu.star == "太阳"

    def test_main_star_brightness_and_sihua(self, chart):
        guanlu = next(p for p in chart.palaces if p.name == "官禄")
        taiyang = next(s for s in guanlu.mainStars if s.name == "太阳")
        assert taiyang.brightness == "旺"
        assert taiyang.sihua == "禄"

    def test_fude_double_sihua(self, chart):
        fude = next(p for p in chart.palaces if p.name == "福德")
        tian_tong = next(s for s in fude.mainStars if s.name == "天同")
        tai_yin = next(s for s in fude.mainStars if s.name == "太阴")
        assert tian_tong.sihua == "忌"
        assert tai_yin.sihua == "科"
        assert "天同忌" in fude.fourTransform.incoming
        assert "太阴科" in fude.fourTransform.incoming

    def test_aux_sha_in_output(self, chart):
        zi_nu = next(p for p in chart.palaces if p.name == "子女")
        aux_names = {s.name for s in zi_nu.auxStars}
        assert "左辅" in aux_names and "右弼" in aux_names
        fu_qi = next(p for p in chart.palaces if p.name == "夫妻")
        assert {s.name for s in fu_qi.shaStars} == {"火星"}
        ming = chart.palaces[0]
        assert [s.name for s in ming.shaStars] == ["铃星"]

    def test_trace_engines(self, chart):
        engines = [s["engine"] for s in chart.trace.steps]
        assert "four_transform" in engines
