"""经典校准回归 — 仅 verification_level=verified_professional。"""

from __future__ import annotations

import pytest

from app.ziwei.chart_pipeline import ChartPipeline
from app.ziwei.core.chart_accuracy_validator import ChartAccuracyValidator
from app.ziwei.debug.classical_audit import MAIN_14, run_classical_audit
from app.ziwei.debug.reference_manager import compare_chart, list_auto_test_charts, list_charts
from app.ziwei.rules.cache import clear_rules_cache


def _verified_cases():
    return list_auto_test_charts()


@pytest.fixture(autouse=True)
def _rules():
    clear_rules_cache()
    yield
    clear_rules_cache()


class TestPendingExcluded:
    def test_pending_not_in_verified_list(self):
        pending = list_charts(level="pending")
        assert len(pending) >= 1
        verified_ids = {c["id"] for c in _verified_cases()}
        for p in pending:
            assert p["id"] not in verified_ids


class TestClassicalCalibration:
    @pytest.mark.parametrize("case", _verified_cases(), ids=lambda c: c["id"])
    def test_full_core_match(self, case):
        birth = case["birth"]
        audit = run_classical_audit(
            birth_date=birth["solar"],
            birth_time=birth["time"],
            gender=case["gender"],
            location=case.get("location") or birth.get("location"),
        )
        meta = case["meta"]
        ganzhi = (case.get("calendar") or {}).get("ganzhi") or {}

        assert audit.ganzhi["year"] == ganzhi["year"]
        assert audit.ganzhi["month"] == ganzhi["month"]
        assert audit.ganzhi["day"] == ganzhi["day"]
        assert audit.ganzhi["hour"] == ganzhi["hour"]

        assert audit.minggong == meta["minggong"]
        assert audit.shengong == meta["shengong"]
        assert audit.wuxingju == meta["wuxingju"]
        assert audit.ziwei_position == meta["ziwei_position"]

        fourteen = case.get("fourteen_stars") or {}
        for star in MAIN_14:
            exp = fourteen[star]
            assert audit.fourteen_star_positions[star] == exp["branch"], star
            assert audit.fourteen_star_palaces[star] == exp["palace"], star

        ft = case.get("four_transform") or {}
        for key in ("lu", "quan", "ke", "ji"):
            assert audit.four_transform[key]["star"] == ft[key]["star"]
            if ft[key].get("palace"):
                assert audit.four_transform[key]["palace"] == ft[key]["palace"]

        diff = compare_chart(case, audit=audit)
        assert diff.matched, [d.to_dict() for d in diff.diffs]

        accuracy = ChartAccuracyValidator.validate_audit(audit)
        assert accuracy["accuracy_score"] >= 95
        assert accuracy["allowed_for_ai"] is True

    @pytest.mark.parametrize("case", _verified_cases(), ids=lambda c: c["id"])
    def test_pipeline_v2(self, case):
        birth = case["birth"]
        chart, meta = ChartPipeline.generate(
            name=case["id"],
            gender=case["gender"],
            solar_date=birth["solar"],
            time=birth["time"],
            location=case.get("location") or birth.get("location"),
            require_accuracy=False,
        )
        assert chart.schema_version in ("2.0", "2.5")
        assert len(chart.palaces) == 12
        assert len(chart.stars.main) == 14
        assert meta["accuracy"]["accuracy_score"] >= 95
        assert chart.meta.mingGong == case["meta"]["minggong"]
        assert chart.meta.wuxingJu == case["meta"]["wuxingju"]
