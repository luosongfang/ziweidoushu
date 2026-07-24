"""V1.6 Professional Reference Calibration tests."""

from __future__ import annotations

import copy

import pytest

from app.ziwei.reference import (
    ReferenceImporter,
    diff_sample_against_engine,
    evaluate_accuracy_gate_v16,
    validate_sample,
)
from app.ziwei.reference.diff_report import aggregate_offset_frequency
from app.ziwei.rules.cache import clear_rules_cache
from app.ziwei_classical.config_loader import resolve_school_config, switch_school
from app.ziwei_classical.stars.boshi import place_boshi
from app.ziwei_classical.stars.changsheng import place_changsheng
from app.ziwei_classical.stars.jiang_qian import place_jiang_qian
from app.ziwei_classical.stars.sui_qian import place_sui_qian
from app.ziwei_classical.validator.rule_trace import RuleTrace


@pytest.fixture(autouse=True)
def _rules():
    clear_rules_cache()
    yield
    clear_rules_cache()


class TestReferenceImport:
    def test_load_p001(self):
        s = ReferenceImporter().load("SC-P001")
        assert s["id"] == "SC-P001"
        assert s["source"] == "wenmo"
        assert s["verification_level"] == "verified_professional"
        v = validate_sample(s)
        assert v["ok"] is True
        assert v["eligible_for_calibration"] is True

    def test_fifty_samples_exist(self):
        samples = ReferenceImporter().list_samples()
        assert len(samples) == 50
        males = sum(1 for s in samples if s["birth"]["gender"] == "male")
        females = sum(1 for s in samples if s["birth"]["gender"] == "female")
        assert males == 25
        assert females == 25

    def test_pending_not_eligible(self):
        pending = ReferenceImporter().list_samples(level="pending")
        assert len(pending) >= 49
        assert validate_sample(pending[0])["eligible_for_calibration"] is False


class TestDiffEngine:
    def test_p001_match(self):
        s = ReferenceImporter().load("SC-P001")
        rep = diff_sample_against_engine(s)
        assert rep["matched"] is True
        assert rep["first_offset_step"] is None
        assert rep["difference"] == []

    def test_first_offset_ziwei(self):
        s = copy.deepcopy(ReferenceImporter().load("SC-P001"))
        s["chart_reference"]["ziwei"] = "午"
        # keep ming/wuxing same so first offset is ziwei
        rep = diff_sample_against_engine(s)
        assert rep["matched"] is False
        assert rep["first_offset_step"] == "ziwei"

    def test_first_offset_ming(self):
        s = copy.deepcopy(ReferenceImporter().load("SC-P001"))
        s["chart_reference"]["ming_gong"] = "子"
        rep = diff_sample_against_engine(s)
        assert rep["first_offset_step"] == "ming_gong"


class TestOffsetFrequency:
    def test_aggregate_no_change_under_70(self):
        reports = [
            {"verification_level": "verified_professional", "matched": True, "first_offset_step": None},
            {
                "verification_level": "verified_professional",
                "matched": False,
                "first_offset_step": "ziwei",
            },
        ]
        stats = aggregate_offset_frequency(reports)
        assert stats["formula_change_allowed"] is False


class TestConfigurationSwitch:
    def test_sanhe_vs_feixing_tianfu(self):
        sanhe = resolve_school_config("sanhe")
        fei = resolve_school_config("feixing")
        assert sanhe["tianfu_rule"] in ("yin_shen_mirror", "traditional")
        assert fei["tianfu_rule"] == "opposite"
        cfg = switch_school("feixing")
        assert cfg.tianfu_rule == "opposite"


class TestAccuracyGateV16:
    def test_claim_not_allowed_with_one_sample(self):
        gate = evaluate_accuracy_gate_v16()
        assert gate["verified_professional_count"] == 1
        assert gate["accuracy_claim_allowed"] is False
        assert gate["fourteen_star_accuracy"] == 100.0


class TestTwelveGodsFramework:
    def test_frameworks_have_rule_formula_trace(self):
        tr = RuleTrace()
        a = place_sui_qian("午", trace=tr)
        b = place_jiang_qian("午", trace=tr)
        c = place_changsheng(5, trace=tr)
        d = place_boshi("申", trace=tr)
        for block in (a, b, c, d):
            assert block["rule_source"]
            assert block["formula"]
            assert block["enabled_framework"] is True
            assert block["stars"]
        assert any(s.step == "sui_qian" for s in tr.steps)
        assert any(s.step == "boshi" for s in tr.steps)
