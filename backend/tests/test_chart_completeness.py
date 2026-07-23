"""V1.2 — StandardChartSchema V2.5 完整度测试。"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.ziwei.core.chart_normalizer import ChartNormalizer
from app.ziwei.core.chart_schema_v2 import AUXILIARY_STAR_NAMES, MAIN_STAR_NAMES
from app.ziwei.core.chart_validator import ChartValidator
from app.ziwei.rules.cache import clear_rules_cache
from app.ziwei_engine.chart_builder import ChartBuilder

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "standard_charts"
GOLDEN_DIR = Path(__file__).parent / "golden"


@pytest.fixture(autouse=True)
def fresh_rules_cache():
    clear_rules_cache()
    yield
    clear_rules_cache()


def _build_from_fixture(fixture: dict) -> dict:
    inp = fixture["input"]
    return ChartBuilder.build(
        name=inp.get("name", "测试"),
        gender=inp.get("gender", "male"),
        solar_date=inp["date"],
        time=inp["time"],
        location=inp.get("location"),
        reference_year=2026,
    )


class TestChartCompleteness:
    def test_sc01_full_structure(self):
        chart = ChartNormalizer.normalize(_build_from_fixture(
            json.loads((FIXTURES_DIR / "SC-01.json").read_text(encoding="utf-8"))
        ))
        assert chart.schema_version == "2.5"
        assert len(chart.palaces) == 12
        assert len(chart.stars.main) == 14
        assert {s.name for s in chart.stars.main} == set(MAIN_STAR_NAMES)
        assert len(chart.stars.auxiliary) == len(AUXILIARY_STAR_NAMES)
        assert chart.xiaoxian.enabled
        assert chart.daxian_transform
        assert chart.liunian.annual_transform
        assert chart.trace.steps
        assert ChartValidator.validate(chart) == []

    @pytest.mark.parametrize("fixture_id", [f"SC-{i:02d}" for i in range(1, 11)])
    def test_all_standard_charts_build(self, fixture_id: str):
        path = FIXTURES_DIR / f"{fixture_id}.json"
        if not path.exists():
            pytest.skip(f"missing {fixture_id}")
        fixture = json.loads(path.read_text(encoding="utf-8"))
        chart = ChartNormalizer.normalize(_build_from_fixture(fixture))
        assert chart.schema_version == "2.5"
        assert len(chart.palaces) == 12
        assert len(chart.stars.main) == 14


class TestGoldenRegression:
    @pytest.mark.parametrize("fixture_id", [f"SC-{i:02d}" for i in range(1, 11)])
    def test_golden_match(self, fixture_id: str):
        golden_path = GOLDEN_DIR / f"{fixture_id}.json"
        fixture = json.loads((FIXTURES_DIR / f"{fixture_id}.json").read_text(encoding="utf-8"))
        chart = ChartNormalizer.normalize(_build_from_fixture(fixture))
        payload = json.loads(chart.model_dump_json())

        if not golden_path.exists():
            GOLDEN_DIR.mkdir(parents=True, exist_ok=True)
            golden_path.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            pytest.skip(f"generated golden {fixture_id}")

        golden = json.loads(golden_path.read_text(encoding="utf-8"))
        for key in ("schema_version", "engine_version", "stars", "xiaoxian", "daxian_transform"):
            assert payload[key] == golden[key], f"mismatch on {key}"
