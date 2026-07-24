"""十四主星专业验证门禁 — 控制 Phase 5 辅星扩展。"""

from __future__ import annotations

from typing import Any

from app.ziwei.debug.reference_manager import list_auto_test_charts
from app.ziwei.debug.star_trace import compare_trace_to_reference, run_star_trace
from app.ziwei.engines.star_placement_engine import (
    AUX_STAR_ORDER,
    MAIN_STAR_ORDER,
    SHA_STAR_ORDER,
    ZA_STAR_ORDER,
)

MIN_PROFESSIONAL_FOR_CLAIM = 30

MISSING_STAR_GROUPS: dict[str, tuple[str, ...]] = {
    "岁前十二神": (
        "岁建", "晦气", "丧门", "贯索", "官符", "小耗",
        "大耗", "龙德", "白虎", "天德", "吊客", "病符",
    ),
    "将前十二神": (
        "将星", "攀鞍", "岁驿", "息神", "华盖", "劫煞",
        "灾煞", "天煞", "指背", "咸池", "月煞", "亡神",
    ),
    "长生十二神": (
        "长生", "沐浴", "冠带", "临官", "帝旺", "衰",
        "病", "死", "墓", "绝", "胎", "养",
    ),
    "博士十二神": (
        "博士", "力士", "青龙", "小耗", "将军", "奏书",
        "飞廉", "喜神", "病符", "大耗", "伏兵", "官府",
    ),
}


def _fourteen_professional_status() -> dict[str, Any]:
    cases = list_auto_test_charts()
    n = len(cases)
    matched = 0
    for case in cases:
        birth = case.get("birth") or {}
        trace = run_star_trace(
            birth_date=birth.get("solar") or birth.get("solar_date"),
            birth_time=birth.get("time"),
            gender=case.get("gender") or birth.get("gender") or "male",
            location=case.get("location") or birth.get("location"),
        )
        fourteen = dict(case.get("fourteen_stars") or {})
        if not fourteen:
            for p in case.get("palaces") or []:
                for s in p.get("main_stars") or []:
                    name = s if isinstance(s, str) else (
                        s.get("name") if isinstance(s, dict) else None
                    )
                    if name:
                        fourteen[name] = {
                            "branch": p.get("branch", ""),
                            "palace": p.get("name", ""),
                        }
        if compare_trace_to_reference(trace, fourteen)["matched"]:
            matched += 1
    claim = n >= MIN_PROFESSIONAL_FOR_CLAIM and matched == n and n > 0
    return {
        "verified_count": n,
        "matched_count": matched,
        "claim_allowed": claim,
    }


def can_expand_professional_aux_systems() -> dict[str, Any]:
    """仅当十四主星专业准确率可宣称时允许扩展岁前/将前/长生/博士。"""
    st = _fourteen_professional_status()
    claim = st["claim_allowed"]
    return {
        "allowed": claim,
        "reason_code": (
            "ok" if claim else "fourteen_stars_not_professionally_verified"
        ),
        "verified_count": st["verified_count"],
        "matched_count": st["matched_count"],
        "min_required": MIN_PROFESSIONAL_FOR_CLAIM,
        "message": (
            "十四主星专业验证已满足，可开发岁前/将前/长生/博士"
            if claim
            else (
                f"十四主星未达专业宣称条件"
                f"（{st['verified_count']}/{MIN_PROFESSIONAL_FOR_CLAIM}），禁止扩展"
            )
        ),
    }


def missing_star_inventory() -> dict[str, Any]:
    """当前引擎相对专业完整星曜的缺失分组（检测清单，不实现）。"""
    present = set(MAIN_STAR_ORDER) | set(AUX_STAR_ORDER) | set(SHA_STAR_ORDER) | set(ZA_STAR_ORDER)
    try:
        from app.ziwei.rules.loader import RulesLoader

        for rule_type in ("aux_star", "sha_star", "za_star"):
            for rule in RulesLoader.get_star_placement_rules(rule_type):
                present.add(rule["star_name"])
    except Exception:
        pass

    missing_groups: dict[str, list[str]] = {}
    flat_missing: list[str] = []
    for group, stars in MISSING_STAR_GROUPS.items():
        absent = [s for s in stars if s not in present]
        missing_groups[group] = absent
        flat_missing.extend(absent)

    return {
        "missing_groups": missing_groups,
        "missing_star_list": sorted(set(flat_missing)),
        "present_main_14": list(MAIN_STAR_ORDER),
        "note": "Phase5 实现前仅作清单；须先通过十四主星专业门禁",
    }
