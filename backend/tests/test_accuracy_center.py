"""Professional Accuracy Center V1.4 — 检测能力测试（不改算法）。"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.ziwei.accuracy import (
    AccuracyManager,
    AccuracyReportBuilder,
    AccuracyValidationGate,
    ChartDiffEngine,
    compare_charts,
    write_accuracy_report,
)
from app.ziwei.accuracy.chart_diff_engine import MAIN_14, normalize_chart
from app.ziwei.rules.cache import clear_rules_cache

REPORT_PATH = (
    Path(__file__).resolve().parents[1]
    / "app"
    / "ziwei"
    / "accuracy"
    / "output"
    / "accuracy_report.json"
)


@pytest.fixture(autouse=True)
def _rules():
    clear_rules_cache()
    yield
    clear_rules_cache()


class TestAccuracyManager:
    def test_only_professional_auto(self):
        mgr = AccuracyManager()
        auto = mgr.list_auto_test_charts()
        assert all(c["verification_level"] == "verified_professional" for c in auto)
        assert any(c["id"] == "SC-C01" for c in auto)

    def test_pending_excluded(self):
        mgr = AccuracyManager()
        auto_ids = {c["id"] for c in mgr.list_auto_test_charts()}
        for c in mgr.list_golden(level="pending"):
            assert c["id"] not in auto_ids


class TestChartDiffEngine:
    def test_identical_charts_score_100(self):
        mgr = AccuracyManager()
        ref = mgr.get_chart("SC-C01")
        eng = mgr.run_engine_for_reference(ref)
        result = compare_charts(eng, ref)
        assert result["matched"] is True
        assert result["accuracy_score"] == 100.0
        assert result["critical_difference"] == []

    def test_critical_on_ziwei_mismatch(self):
        mgr = AccuracyManager()
        ref = mgr.get_chart("SC-C01")
        eng = mgr.run_engine_for_reference(ref)
        eng["meta"]["ziwei_position"] = "午"
        eng["fourteen_stars"]["紫微"]["branch"] = "午"
        result = compare_charts(eng, ref)
        assert result["accuracy_score"] < 100
        fields = [d["field"] for d in result["critical_difference"]]
        assert any("紫微" in f or f == "紫微位置" for f in fields)

    def test_normalize_has_main14_from_sc_c01(self):
        ref = normalize_chart(AccuracyManager().get_chart("SC-C01"))
        for name in MAIN_14:
            assert name in ref["stars"]
            assert ref["stars"][name]["branch"]


class TestValidationGate:
    def test_gate_pass_sc_c01(self):
        mgr = AccuracyManager()
        cmp = mgr.compare_with_engine("SC-C01")
        gate = AccuracyValidationGate(min_score=95)
        out = gate.evaluate(compare_result=cmp)
        assert out["passed"] is True
        assert out["allowed_for_ai"] is True

    def test_gate_blocks_critical(self):
        gate = AccuracyValidationGate(min_score=95)
        fake = {
            "accuracy_score": 99.0,
            "critical_difference": [{"field": "命宫", "engine": "子", "reference": "戌"}],
            "major_difference": [],
            "minor_difference": [],
        }
        out = gate.evaluate(compare_result=fake)
        assert out["passed"] is False


class TestAccuracyReport:
    def test_build_and_write(self):
        report = AccuracyReportBuilder().build()
        assert report["version"] == "1.4.0"
        assert report["accuracy"]["cases_tested"] >= 1
        path = write_accuracy_report(report, REPORT_PATH)
        assert path.exists()
        loaded = json.loads(path.read_text(encoding="utf-8"))
        assert loaded["cases"][0]["chart_id"] == "SC-C01"
        assert loaded["cases"][0]["matched"] is True
