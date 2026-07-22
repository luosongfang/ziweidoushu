"""验证系统测试。"""

from datetime import datetime

import pytest

from app.models.birth import ChartGenerateRequest
from app.ziwei.chart_generator import ChartGenerator
from app.ziwei.rules.cache import clear_rules_cache
from app.ziwei.verification.diff_detector import detect_diff
from app.ziwei.verification.manager import VerificationManager
from app.ziwei.verification.reference_runner import (
    load_reference_charts,
    verify_all_reference_charts,
    verify_reference_chart,
)


@pytest.fixture(autouse=True)
def fresh_rules_cache():
    clear_rules_cache()
    yield
    clear_rules_cache()


def test_load_reference_charts():
    data = load_reference_charts()
    assert "charts" in data
    assert len(data["charts"]) >= 6


def test_diff_detector_no_diff():
    expected = {"mingGong": "戌", "wuxingJu": "土五局"}
    actual = {"mingGong": "戌", "wuxingJu": "土五局"}
    assert detect_diff(expected, actual) == []


def test_diff_detector_with_diff():
    expected = {"mingGong": "戌"}
    actual = {"mingGong": "午"}
    assert len(detect_diff(expected, actual)) == 1


class TestReferenceVerification:
    def test_ref01_passes(self):
        data = load_reference_charts()
        spec = next(c for c in data["charts"] if c["id"] == "REF-01")
        assert verify_reference_chart(spec) == []

    @pytest.mark.parametrize("ref_id", ["REF-01", "REF-04", "REF-05"])
    def test_palace_bureau_refs(self, ref_id):
        data = load_reference_charts()
        spec = next(c for c in data["charts"] if c["id"] == ref_id)
        diffs = verify_reference_chart(spec)
        assert diffs == [], f"{ref_id} failed: {diffs}"

    def test_all_reference_charts(self):
        failures = verify_all_reference_charts()
        assert failures == {}, f"Reference failures: {failures}"


class TestVerificationManager:
    def test_run_reference_suite(self):
        report = VerificationManager.run_reference_suite()
        assert report.passed
        assert report.total_charts >= 6


def test_chart_trace_includes_all_engines():
    chart = ChartGenerator.generate(ChartGenerateRequest(
        birth_datetime=datetime(1990, 5, 15, 14, 30),
        gender="male",
    ))
    engines = [s["engine"] for s in chart.trace.steps]
    for name in ("calendar", "palace", "bureau", "star_placement", "four_transform", "fortune", "combination"):
        assert name in engines
