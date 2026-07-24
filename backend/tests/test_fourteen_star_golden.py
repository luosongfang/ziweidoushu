"""十四主星专业黄金验证 — V1.5。

禁止：单案例通过即认为正确。
要求：至少 MIN_PROFESSIONAL_CASES 个 verified_professional 才允许宣称准确率。
"""

from __future__ import annotations

from typing import Any

import pytest

from app.ziwei.debug.reference_manager import list_auto_test_charts, load_chart
from app.ziwei.debug.star_trace import compare_trace_to_reference, run_star_trace
from app.ziwei.engines.star_placement_engine import MAIN_STAR_ORDER
from app.ziwei.rules.cache import clear_rules_cache

MIN_PROFESSIONAL_CASES = 30
MAIN_14 = MAIN_STAR_ORDER


@pytest.fixture(autouse=True)
def _rules():
    clear_rules_cache()
    yield
    clear_rules_cache()


def build_fourteen_star_verification_report() -> dict[str, Any]:
    cases = list_auto_test_charts()
    per_case: list[dict[str, Any]] = []
    star_hits = {s: {"match": 0, "total": 0} for s in MAIN_14}

    for case in cases:
        birth = case.get("birth") or {}
        solar = birth.get("solar") or birth.get("solar_date")
        time = birth.get("time")
        trace = run_star_trace(
            birth_date=solar,
            birth_time=time,
            gender=case.get("gender") or birth.get("gender") or "male",
            location=case.get("location") or birth.get("location"),
        )
        fourteen = case.get("fourteen_stars") or {}
        if not fourteen:
            # derive from palaces
            for p in case.get("palaces") or []:
                for s in p.get("main_stars") or []:
                    name = s if isinstance(s, str) else s.get("name")
                    if name:
                        fourteen[name] = {
                            "branch": p.get("branch", ""),
                            "palace": p.get("name", ""),
                        }
        cmp = compare_trace_to_reference(trace, fourteen)
        for star in MAIN_14:
            exp = fourteen.get(star)
            if not exp:
                continue
            star_hits[star]["total"] += 1
            exp_br = exp.get("branch") if isinstance(exp, dict) else exp
            if trace.final_branch_mapping.get(star) == exp_br:
                star_hits[star]["match"] += 1
            exp_pal = exp.get("palace") if isinstance(exp, dict) else None
            # palace optional

        per_case.append(
            {
                "id": case.get("id"),
                "matched": cmp["matched"],
                "first_offset_step": cmp["first_offset_step"],
                "diff_count": len(cmp["differences"]),
            }
        )

    n = len(cases)
    matched = sum(1 for c in per_case if c["matched"])
    claim_allowed = n >= MIN_PROFESSIONAL_CASES and matched == n and n > 0
    star_accuracy = {
        s: (
            round(star_hits[s]["match"] / star_hits[s]["total"] * 100, 2)
            if star_hits[s]["total"]
            else None
        )
        for s in MAIN_14
    }

    return {
        "min_required": MIN_PROFESSIONAL_CASES,
        "verified_count": n,
        "matched_count": matched,
        "status": "verified" if claim_allowed else "insufficient_samples",
        "accuracy_claim_allowed": claim_allowed,
        "overall_match_rate": round(matched / n * 100, 2) if n else None,
        "star_accuracy": star_accuracy,
        "cases": per_case,
        "message": (
            f"已有 {n}/{MIN_PROFESSIONAL_CASES} 个 verified_professional；"
            + (
                "可宣称十四主星专业准确率"
                if claim_allowed
                else "禁止因单案例/少量案例认定十四主星正确"
            )
        ),
    }


class TestFourteenStarProfessionalGate:
    def test_cannot_claim_with_single_case(self):
        report = build_fourteen_star_verification_report()
        assert report["verified_count"] < MIN_PROFESSIONAL_CASES
        assert report["accuracy_claim_allowed"] is False
        assert report["status"] == "insufficient_samples"

    def test_available_professional_still_match_engine(self):
        """现有专业盘应与引擎一致（不代表总体准确）。"""
        cases = list_auto_test_charts()
        assert len(cases) >= 1
        report = build_fourteen_star_verification_report()
        for c in report["cases"]:
            assert c["matched"] is True, c

    @pytest.mark.skipif(
        len(list_auto_test_charts()) < MIN_PROFESSIONAL_CASES,
        reason=f"需要至少 {MIN_PROFESSIONAL_CASES} 个 verified_professional 才跑全量宣称测试",
    )
    def test_thirty_professional_all_match(self):
        report = build_fourteen_star_verification_report()
        assert report["accuracy_claim_allowed"] is True
        assert report["matched_count"] == report["verified_count"]


class TestStarTraceBasic:
    def test_sc_c01_trace_shape(self):
        case = load_chart("SC-C01")
        birth = case["birth"]
        trace = run_star_trace(
            birth_date=birth["solar"],
            birth_time=birth["time"],
            location=case.get("location") or birth.get("location"),
        )
        d = trace.to_dict()
        for key in (
            "calendar_result",
            "ming_gong",
            "wuxing_ju",
            "ziwei_position_rule",
            "ziwei_position",
            "tianfu_position_rule",
            "tianfu_position",
            "fourteen_star_sequence",
            "final_palace_mapping",
        ):
            assert key in d
        assert len(trace.fourteen_star_sequence) == 14
        assert trace.ziwei_formula_table_match is True
        assert trace.ziwei_position == "巳"
        assert trace.tianfu_position == "亥"
