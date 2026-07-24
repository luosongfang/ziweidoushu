"""Accuracy Center V1.4.1 — 黄金盘强校准检测（不改算法）。"""

from __future__ import annotations

import copy

import pytest

from app.ziwei.accuracy import (
    AccuracyManager,
    ChartDiffEngine,
    analyze_root_cause,
    build_coverage_report,
    compare_charts,
)
from app.ziwei.debug.chart_conflict_detector import detect_chart_conflict
from app.ziwei.debug.reference_manager import list_charts, load_chart
from app.ziwei.rules.cache import clear_rules_cache


@pytest.fixture(autouse=True)
def _rules():
    clear_rules_cache()
    yield
    clear_rules_cache()


class TestEmptyPalaceStrictCompare:
    def test_empty_main_stars_compared(self):
        eng = {
            "meta": {"minggong": "戌", "shengong": "子", "wuxingju": "土五局"},
            "palaces": [
                {"name": "命宫", "branch": "戌", "main_stars": ["紫微"]},
            ],
        }
        ref = {
            "meta": {"minggong": "戌", "shengong": "子", "wuxingju": "土五局"},
            "palaces": [
                {"name": "命宫", "branch": "戌", "main_stars": []},
            ],
        }
        result = compare_charts(eng, ref)
        fields = [d["field"] for d in result["critical_difference"]]
        assert "宫.命宫.主星" in fields
        assert result["accuracy_score"] < 100


class TestRootCauseDetection:
    def test_ming_gong_diff(self):
        diff = {
            "critical_difference": [
                {"field": "命宫", "engine": "子", "reference": "戌", "impact": "critical"}
            ],
            "major_difference": [],
            "minor_difference": [],
        }
        out = analyze_root_cause(diff)
        assert out["cause"] == "calendar_or_palace_engine"
        assert out["matched_rule"] == 1

    def test_star_diff_when_ming_ok(self):
        diff = {
            "critical_difference": [
                {"field": "星曜.紫微.地支", "engine": "午", "reference": "巳", "impact": "critical"}
            ],
            "major_difference": [],
            "minor_difference": [],
        }
        out = analyze_root_cause(diff)
        assert out["cause"] == "star_position_engine"
        assert out["matched_rule"] == 2

    def test_four_transform_diff(self):
        diff = {
            "critical_difference": [],
            "major_difference": [
                {"field": "四化.birth.禄", "engine": "武曲", "reference": "太阳", "impact": "major"}
            ],
            "minor_difference": [],
        }
        out = analyze_root_cause(diff)
        assert out["cause"] == "four_transform_engine"
        assert out["matched_rule"] == 3

    def test_minor_star_diff(self):
        diff = {
            "critical_difference": [],
            "major_difference": [
                {"field": "星曜.左辅.地支", "engine": "子", "reference": "丑", "impact": "major"}
            ],
            "minor_difference": [],
        }
        out = analyze_root_cause(diff)
        assert out["cause"] == "minor_star_engine"
        assert out["matched_rule"] == 4

    def test_fortune_diff(self):
        diff = {
            "critical_difference": [],
            "major_difference": [
                {"field": "运限.大限宫位", "engine": "寅", "reference": "卯", "impact": "major"}
            ],
            "minor_difference": [],
        }
        out = analyze_root_cause(diff)
        assert out["cause"] == "fortune_engine"
        assert out["matched_rule"] == 5


class TestGoldenDatasetLoading:
    def test_load_twenty_cases(self):
        charts = list_charts()
        assert len(charts) == 20
        ids = {c["id"] for c in charts}
        for i in range(1, 21):
            assert f"SC-C{i:02d}" in ids

    def test_c01_expected_schema(self):
        c = load_chart("SC-C01")
        assert c["verification_level"] == "verified_professional"
        assert c["birth"]["solar"] == "1990-05-15"
        assert c["meta"]["minggong"] == "戌"
        assert len(c["palaces"]) == 12
        assert c["four_transform"]["lu"]["star"] == "太阳"
        # V1.4.1 palace buckets
        p0 = c["palaces"][0]
        assert "lucky_stars" in p0 or "main_stars" in p0

    def test_only_professional_auto(self):
        auto = AccuracyManager().list_auto_test_charts()
        assert len(auto) == 1
        assert auto[0]["id"] == "SC-C01"


class TestCoverageReport:
    def test_coverage_shape(self):
        report = build_coverage_report()
        assert report["total_cases"] == 20
        assert report["verified_cases"] == 1
        cov = report["coverage"]
        for k in ("male_yang", "male_yin", "female_yang", "female_yin"):
            assert k in cov
            assert cov[k] in ("ok", "thin", "missing")
        fe = cov["five_element"]
        assert set(fe) == {"water", "wood", "metal", "fire", "earth"}
        assert isinstance(cov["hour_distribution"], dict)
        # diversity: not all five-element zero
        assert sum(fe.values()) >= 5


class TestChartConflictDetection:
    def test_same_birth_star_conflict(self):
        a = load_chart("SC-C01")
        b = copy.deepcopy(a)
        # mutate stars only
        for p in b.get("palaces") or []:
            if "紫微" in (p.get("main_stars") or []):
                p["main_stars"] = [s for s in p["main_stars"] if s != "紫微"]
        # put 紫微 elsewhere
        for p in b["palaces"]:
            if p["name"] == "命宫":
                p["main_stars"] = ["紫微"]
                break
        if b.get("fourteen_stars"):
            b["fourteen_stars"]["紫微"] = {"branch": "戌", "palace": "命宫"}
        b["meta"]["ziwei_position"] = "戌"

        out = detect_chart_conflict(a, b)
        assert out["same_birth"] is True
        assert "stars" in out["difference_type"]
        assert "algorithm_error" in out["possible_reason"]
        assert out["root_cause"]["cause"] in (
            "star_position_engine",
            "calendar_or_palace_engine",
        )

    def test_true_solar_reason(self):
        a = {
            "birth": {
                "solar_date": "1990-05-15",
                "time": "14:30",
                "gender": "male",
                "location": "深圳",
                "true_solar_time": True,
            },
            "meta": {"ming_gong": "戌", "shen_gong": "子", "wuxing_ju": "土五局"},
            "palaces": [],
        }
        b = {
            "birth": {
                "solar_date": "1990-05-15",
                "time": "14:30",
                "gender": "male",
                "location": None,
                "true_solar_time": False,
            },
            "meta": {"ming_gong": "亥", "shen_gong": "丑", "wuxing_ju": "木三局"},
            "palaces": [],
        }
        out = detect_chart_conflict(a, b)
        assert out["same_birth"] is True
        assert "true_solar_time" in out["possible_reason"]
        assert "palace" in out["difference_type"] or "calendar" in out["difference_type"] or out["diff_count"] >= 1


class TestProfessionalStillMatches:
    def test_sc_c01_engine_match(self):
        mgr = AccuracyManager()
        result = mgr.compare_with_engine("SC-C01")
        assert result.get("matched") is True
        assert result["accuracy_score"] == 100.0
