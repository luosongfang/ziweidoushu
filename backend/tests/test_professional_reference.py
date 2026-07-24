"""专业黄金盘自动测试 — 仅 verification_level=verified_professional。"""

from __future__ import annotations

import pytest

from app.ziwei.core.chart_accuracy_validator import ChartAccuracyValidator
from app.ziwei.debug.classical_audit import MAIN_14
from app.ziwei.debug.reference_manager import (
    AUTO_TEST_LEVEL,
    compare_chart,
    export_report,
    list_auto_test_charts,
    list_charts,
    validate_reference,
)
from app.ziwei.rules.cache import clear_rules_cache


@pytest.fixture(autouse=True)
def _rules():
    clear_rules_cache()
    yield
    clear_rules_cache()


def _professional_cases():
    return list_auto_test_charts()


class TestVerificationPolicy:
    def test_only_professional_in_auto_list(self):
        auto = list_auto_test_charts()
        for c in auto:
            assert c["verification_level"] == AUTO_TEST_LEVEL
        pending = list_charts(level="pending")
        auto_ids = {c["id"] for c in auto}
        for p in pending:
            assert p["id"] not in auto_ids

    def test_pending_not_eligible(self):
        for c in list_charts(level="pending"):
            v = validate_reference(c)
            assert v["eligible_for_auto_test"] is False


class TestProfessionalReference:
    def test_dataset_has_professional_cases(self):
        cases = _professional_cases()
        assert len(cases) >= 1, "至少需要 1 个 verified_professional 案例"

    @pytest.mark.parametrize("case", _professional_cases(), ids=lambda c: c["id"])
    def test_reference_structure_valid(self, case):
        v = validate_reference(case)
        assert v["ok"], v["errors"]
        assert v["eligible_for_auto_test"] is True

    @pytest.mark.parametrize("case", _professional_cases(), ids=lambda c: c["id"])
    def test_engine_matches_reference(self, case):
        rep = compare_chart(case)
        assert rep.matched, [d.to_dict() for d in rep.diffs]
        critical = [d for d in rep.diffs if d.impact == "critical"]
        assert critical == []

    @pytest.mark.parametrize("case", _professional_cases(), ids=lambda c: c["id"])
    def test_fourteen_stars_complete(self, case):
        stars = set()
        for p in case.get("palaces") or []:
            stars.update(p.get("main_stars") or [])
        assert set(MAIN_14) <= stars

    @pytest.mark.parametrize("case", _professional_cases(), ids=lambda c: c["id"])
    def test_accuracy_gate(self, case):
        from app.ziwei.debug.classical_audit import run_classical_audit

        birth = case["birth"]
        audit = run_classical_audit(
            birth_date=birth["solar"],
            birth_time=birth["time"],
            gender=case.get("gender", "male"),
            location=case.get("location") or birth.get("location"),
        )
        acc = ChartAccuracyValidator.validate_audit(audit)
        assert acc["accuracy_score"] >= 95
        assert acc["allowed_for_ai"] is True


class TestExportReport:
    def test_export_counts(self):
        report = export_report()
        assert report["counts"]["total"] >= 10
        assert report["counts"]["verified_professional"] >= 1
        assert report["counts"]["pending"] >= 1
        assert report["policy"]["auto_test_level"] == AUTO_TEST_LEVEL
