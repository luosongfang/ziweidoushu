"""StandardChartSchema V2 — 生产 API 与 ChartOutput 对齐测试。"""

from __future__ import annotations

from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.birth import ChartGenerateRequest
from app.ziwei.chart_generator import ChartGenerator
from app.ziwei.core.chart_normalizer import ChartNormalizer
from app.ziwei.core.chart_schema_v2 import MAIN_STAR_NAMES
from app.ziwei.core.chart_validator import ChartValidator
from app.ziwei.rules.cache import clear_rules_cache
from app.ziwei_engine.chart_builder import ChartBuilder


@pytest.fixture(autouse=True)
def fresh_rules_cache():
    clear_rules_cache()
    yield
    clear_rules_cache()


def _ref01_builder_raw() -> dict:
    return ChartBuilder.build(
        name="基准男盘",
        gender="male",
        solar_date="1990-05-15",
        time="14:30",
        location="深圳",
        reference_year=2026,
    )


def _ref01_generator_output():
    return ChartGenerator.generate(ChartGenerateRequest(
        birth_datetime=datetime(1990, 5, 15, 14, 30),
        gender="male",
        name="基准男盘",
    ))


class TestChartNormalizer:
    def test_schema_version(self):
        chart = ChartNormalizer.normalize(_ref01_builder_raw())
        assert chart.schema_version == "2.5"

    def test_fourteen_main_stars_structured(self):
        chart = ChartNormalizer.normalize(_ref01_builder_raw())
        assert len(chart.stars.main) == 14
        assert {s.name for s in chart.stars.main} == set(MAIN_STAR_NAMES)

    def test_lucky_sha_za_structured(self):
        chart = ChartNormalizer.normalize(_ref01_builder_raw())
        assert len(chart.stars.lucky) == 6
        assert len(chart.stars.sha) == 6
        assert len(chart.stars.lu_cun) == 1
        assert len(chart.stars.za) == 1
        assert chart.stars.za[0].name == "天马"

    def test_palace_opposite_and_sanhe(self):
        chart = ChartNormalizer.normalize(_ref01_builder_raw())
        ming = next(p for p in chart.palaces if p.is_ming_gong)
        assert ming.opposite == "迁移"
        assert ming.sanhe == ["财帛", "官禄"]
        assert chart.sanhe["命宫"] == ["财帛", "官禄"]
        assert chart.opposite["命宫"] == "迁移"

    def test_star_category_and_brightness(self):
        chart = ChartNormalizer.normalize(_ref01_builder_raw())
        ziwei = next(s for s in chart.stars.main if s.name == "紫微")
        assert ziwei.category == "main"
        assert ziwei.type == "main"
        assert ziwei.brightness
        assert chart.brightness["紫微"]

    def test_validator_no_warnings_for_ref01(self):
        chart = ChartNormalizer.normalize(_ref01_builder_raw())
        assert ChartValidator.validate(chart) == []

    def test_v25_auxiliary_stars(self):
        chart = ChartNormalizer.normalize(_ref01_builder_raw())
        assert len(chart.stars.auxiliary) == 9
        assert {s.name for s in chart.stars.auxiliary} == {
            "天刑", "天姚", "红鸾", "天喜", "孤辰", "寡宿", "华盖", "天哭", "天虚",
        }
        assert all(s.trace for s in chart.stars.auxiliary)
        main_names = {s.name for s in chart.stars.main}
        assert not main_names & {s.name for s in chart.stars.auxiliary}

    def test_v25_xiaoxian(self):
        chart = ChartNormalizer.normalize(_ref01_builder_raw())
        assert chart.xiaoxian.enabled
        assert chart.xiaoxian.current_palace
        assert len(chart.xiaoxian.yearly_cycle) == 120

    def test_v25_period_transforms(self):
        chart = ChartNormalizer.normalize(_ref01_builder_raw())
        assert chart.daxian_transform is not None
        assert chart.daxian_transform.stem
        assert chart.liunian.annual_transform is not None
        assert chart.liunian.annual_transform.year == 2026


class TestProductionApiSchemaV2:
    def test_post_create_returns_v2(self):
        client = TestClient(app)
        response = client.post(
            "/api/chart/create",
            json={
                "name": "基准男盘",
                "gender": "male",
                "solar_date": "1990-05-15",
                "time": "14:30",
                "location": "深圳",
                "persist": False,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["schema_version"] == "2.5"
        assert data["meta"]["mingGong"] == "戌"
        assert len(data["palaces"]) == 12
        assert len(data["stars"]["main"]) == 14
        assert data["warnings"] == []


class TestSchemaV2MatchesChartOutputCore:
    def test_meta_alignment(self):
        v2 = ChartNormalizer.normalize(_ref01_builder_raw())
        full = _ref01_generator_output()
        assert v2.meta.mingGong == full.meta.mingGong
        assert v2.meta.shenGong == full.meta.shenGong
        assert v2.meta.wuxingJu == full.meta.wuxingJu
        assert v2.meta.mingGongGanZhi == full.meta.mingGongGanZhi

    def test_palace_branches_alignment(self):
        v2 = ChartNormalizer.normalize(_ref01_builder_raw())
        full = _ref01_generator_output()
        assert [p.branch for p in v2.palaces] == [p.branch for p in full.palaces]

    def test_main_star_positions_alignment(self):
        v2 = ChartNormalizer.normalize(_ref01_builder_raw())
        full = _ref01_generator_output()
        v2_map = {s.name: s.palace for s in v2.stars.main}
        full_map = {
            star.name: palace.name
            for palace in full.palaces
            for star in palace.mainStars
        }
        assert v2_map == full_map

    def test_four_transform_alignment(self):
        v2 = ChartNormalizer.normalize(_ref01_builder_raw())
        full = _ref01_generator_output()
        assert v2.four_transform.yearStem == full.fourTransformSummary.yearStem
        assert v2.four_transform.lu.star == full.fourTransformSummary.lu.star
        assert v2.four_transform.lu.palace == full.fourTransformSummary.lu.palace
        assert v2.four_transform.ji.star == full.fourTransformSummary.ji.star
        assert v2.four_transform.ji.palace == full.fourTransformSummary.ji.palace

    def test_sanhe_order_stable(self):
        v2 = ChartNormalizer.normalize(_ref01_builder_raw())
        ming = next(p for p in v2.palaces if p.is_ming_gong)
        assert ming.sanhe == ["财帛", "官禄"]

    def test_daxian_direction_alignment(self):
        v2 = ChartNormalizer.normalize(_ref01_builder_raw())
        full = _ref01_generator_output()
        assert v2.daxian.direction == full.fortune.daxianDirection
