"""Ziwei Core Engine V1.3 — 专业命盘完整化测试。"""

from __future__ import annotations

import pytest

from app.ziwei.core.chart_quality_validator import ChartQualityValidator
from app.ziwei.core.professional_chart_schema import MAIN_STAR_NAMES_V3, OTHER_STAR_NAMES
from app.ziwei.core.professional_normalizer import ProfessionalNormalizer
from app.ziwei.engines.minor_star_placement_engine import MinorStarPlacementEngine
from app.ziwei.rules.cache import clear_rules_cache
from app.ziwei.transformation.four_transform_engine_v2 import FourTransformEngineV2
from app.ziwei_engine.chart_builder import ChartBuilder
from tests.fixtures.professional_charts.cases import PROFESSIONAL_CASES

REQUIRED_MINOR = {
    "红鸾", "天喜", "天姚", "咸池", "孤辰", "寡宿", "华盖", "天刑",
    "天哭", "天虚", "天官", "天福", "天寿", "天才", "天月",
}


@pytest.fixture(autouse=True)
def _clear_rules():
    clear_rules_cache()
    yield
    clear_rules_cache()


def _build_v3(case: dict):
    raw = ChartBuilder.build(
        name=case["name"],
        gender=case["gender"],
        solar_date=case["solar_date"],
        time=case["time"],
        location=case.get("location"),
    )
    return raw, ProfessionalNormalizer.normalize(raw, include_legacy_v2=False)


class TestMinorStarsV13:
    def test_all_required_minor_stars_present(self):
        raw, _ = _build_v3(PROFESSIONAL_CASES[0])
        names = {s["star"] for s in raw["chart"]["minor_stars"]}
        missing = REQUIRED_MINOR - names
        assert not missing, f"缺失杂曜：{missing}"

    def test_minor_star_has_trace_and_rule_source(self):
        raw, _ = _build_v3(PROFESSIONAL_CASES[0])
        for s in raw["chart"]["minor_stars"]:
            assert s["palace"]
            assert s["rule_source"]
            assert s["trace"]


class TestFourTransformV2:
    def test_birth_daxian_liunian_self(self):
        raw, v3 = _build_v3(PROFESSIONAL_CASES[0])
        ft = raw["chart"]["four_transform_v2"]
        assert all(ft["year"].get(k) for k in ("lu", "quan", "ke", "ji"))
        assert isinstance(ft["self"], list) and len(ft["self"]) >= 12
        assert v3.four_transform.birth_transform.lu
        assert v3.feixing["enabled"] is True


class TestXiaoxianV13:
    def test_xiaoxian_cycle(self):
        _, v3 = _build_v3(PROFESSIONAL_CASES[1])
        items = v3.fortune.xiaoxian.items
        assert len(items) >= 12
        assert items[0]["age"] == 1
        assert items[0]["palace"]


class TestCombinationsWired:
    def test_combinations_on_builder(self):
        raw, v3 = _build_v3(PROFESSIONAL_CASES[1])
        assert "combinations" in raw["chart"]
        assert isinstance(v3.star_combination, list)


class TestProfessionalQualityGate:
    @pytest.mark.parametrize("case", PROFESSIONAL_CASES, ids=[c["id"] for c in PROFESSIONAL_CASES])
    def test_each_professional_case(self, case):
        raw, v3 = _build_v3(case)
        assert raw["engine_version"] == "1.3"
        assert len(v3.palaces) == 12
        main_names = {s.name for s in v3.stars.main_stars}
        assert set(MAIN_STAR_NAMES_V3) <= main_names
        assert v3.bazi.year and v3.meta.ming_gong and v3.meta.wuxing_ju
        assert v3.four_transform.birth_transform.lu
        assert v3.fortune.xiaoxian.enabled
        minor_names = {s.name for s in v3.stars.others if s.name in REQUIRED_MINOR}
        # others 可能去重；用 raw minor_stars 严检
        raw_minor = {s["star"] for s in raw["chart"]["minor_stars"]}
        assert REQUIRED_MINOR <= raw_minor
        ChartQualityValidator.assert_valid(v3)


class TestNoFakeFortune:
    def test_liuyue_liuri_liushi_disabled(self):
        _, v3 = _build_v3(PROFESSIONAL_CASES[0])
        assert v3.fortune.liuyue.enabled is False
        assert v3.fortune.liuri.enabled is False
        assert v3.fortune.liushi.enabled is False
        assert v3.fortune.liuyue.items == []
