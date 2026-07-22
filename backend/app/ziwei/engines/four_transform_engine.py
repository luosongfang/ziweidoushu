"""四化引擎 — Sprint 5：生年四化。"""

from __future__ import annotations

from dataclasses import dataclass

from app.models.star import FourTransformDetail, FourTransformSummary
from app.ziwei.rules.loader import RulesLoader

SIHUA_LABELS = ("禄", "权", "科", "忌")
SIHUA_KEYS = ("lu", "quan", "ke", "ji")


@dataclass
class TransformResult:
    """四化计算结果。"""

    star_sihua: dict[str, str]
    summary: FourTransformSummary


class FourTransformEngine:
    """Four Transform Engine — 读 four_transform_rules 表。"""

    @staticmethod
    def compute(year_stem: str, star_to_palace: dict[str, str]) -> TransformResult:
        rule = RulesLoader.get_four_transform(year_stem)
        star_sihua: dict[str, str] = {}
        details: dict[str, FourTransformDetail] = {}

        star_map = {
            "lu": rule.lu_star,
            "quan": rule.quan_star,
            "ke": rule.ke_star,
            "ji": rule.ji_star,
        }

        for key, label in zip(SIHUA_KEYS, SIHUA_LABELS):
            star_name = star_map[key]
            palace = star_to_palace.get(star_name, "")
            star_sihua[star_name] = label
            details[key] = FourTransformDetail(star=star_name, palace=palace)

        summary = FourTransformSummary(
            yearStem=year_stem,
            lu=details["lu"],
            quan=details["quan"],
            ke=details["ke"],
            ji=details["ji"],
        )
        return TransformResult(star_sihua=star_sihua, summary=summary)
