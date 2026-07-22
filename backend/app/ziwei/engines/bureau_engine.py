"""五行局引擎 — Sprint 1 改用 RulesLoader。"""

from __future__ import annotations

from dataclasses import dataclass

from app.ziwei.engines.calendar_engine import stem_branch_at_palace
from app.ziwei.rules.loader import RulesLoader


@dataclass(frozen=True)
class BureauResult:
    ming_gong_ganzhi: str
    nayin: str
    nayin_element: str
    bureau_number: int
    bureau_name: str
    rules_version: str = RulesLoader.RULES_VERSION


class BureauEngine:
    """Bureau Engine — 读 nayin_rules（经 RulesLoader，Sprint 3 完整验证）。"""

    @staticmethod
    def compute(year_stem: str, ming_gong_branch_index: int) -> BureauResult:
        ming_gong_ganzhi = stem_branch_at_palace(year_stem, ming_gong_branch_index)
        rule = RulesLoader.get_nayin_by_ganzhi(ming_gong_ganzhi)
        _, _, bureau_name = RulesLoader.get_bureau(rule.heavenly_stem, rule.earthly_branch)

        return BureauResult(
            ming_gong_ganzhi=ming_gong_ganzhi,
            nayin=rule.nayin,
            nayin_element=rule.element,
            bureau_number=rule.bureau_number,
            bureau_name=bureau_name,
            rules_version=RulesLoader.rules_version(),
        )

    @staticmethod
    def compute_for_ganzhi(ming_gong_ganzhi: str) -> BureauResult:
        """直接由命宫干支查五行局（供测试与验证）。"""
        rule = RulesLoader.get_nayin_by_ganzhi(ming_gong_ganzhi)
        _, _, bureau_name = RulesLoader.get_bureau(rule.heavenly_stem, rule.earthly_branch)
        return BureauResult(
            ming_gong_ganzhi=ming_gong_ganzhi,
            nayin=rule.nayin,
            nayin_element=rule.element,
            bureau_number=rule.bureau_number,
            bureau_name=bureau_name,
            rules_version=RulesLoader.rules_version(),
        )


WuXingJu = BureauResult
calc_wuxing_ju = BureauEngine.compute
