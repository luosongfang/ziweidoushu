"""运限引擎 — Sprint 6：大限 + 流年 + 流月接口。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from lunar_python import Solar

from app.ziwei.constants import EARTHLY_BRANCHES
from app.ziwei.engines.palace_engine import PalaceResult
from app.ziwei.rules.loader import RulesLoader


@dataclass(frozen=True)
class DaXianRange:
    start_age: int
    end_age: int


@dataclass(frozen=True)
class FortuneSnapshot:
    direction: str
    current_daxian: dict[str, Any] | None
    annual_fortune: dict[str, Any] | None
    monthly_fortune: dict[str, Any] | None


class FortuneEngine:
    """Fortune Engine — 读 daxian_rules，计算大限/流年/流月。"""

    @staticmethod
    def is_daxian_forward(year_stem: str, gender: str) -> bool:
        rule = RulesLoader.get_daxian_rule(gender, year_stem)
        return rule.direction == "forward"

    @classmethod
    def calc_daxian(
        cls,
        palaces: list[PalaceResult],
        bureau_number: int,
        year_stem: str,
        gender: str,
    ) -> tuple[dict[str, DaXianRange], str]:
        rule = RulesLoader.get_daxian_rule(gender, year_stem)
        forward = rule.direction == "forward"
        count = len(palaces)
        result: dict[str, DaXianRange] = {}

        for i, palace in enumerate(palaces):
            offset = i if forward else (count - i) % count
            start = bureau_number + offset * 10
            result[palace.name] = DaXianRange(start_age=start, end_age=start + 9)

        return result, rule.direction

    @staticmethod
    def _calc_age(birth: datetime, reference: datetime) -> int:
        age = reference.year - birth.year
        if (reference.month, reference.day) < (birth.month, birth.day):
            age -= 1
        return max(age, 0)

    @staticmethod
    def _year_ganzhi(year: int) -> tuple[str, str]:
        lunar = Solar.fromYmd(year, 6, 15).getLunar()
        gz = lunar.getYearInGanZhi()
        return gz[0], gz[1]

    @classmethod
    def _find_current_daxian(
        cls,
        palaces: list[PalaceResult],
        daxian_map: dict[str, DaXianRange],
        birth: datetime,
        reference: datetime,
    ) -> dict[str, Any] | None:
        age = cls._calc_age(birth, reference)
        for palace in palaces:
            dx = daxian_map[palace.name]
            if dx.start_age <= age <= dx.end_age:
                return {
                    "palace": palace.name,
                    "branch": palace.branch,
                    "startAge": dx.start_age,
                    "endAge": dx.end_age,
                    "virtualAge": age,
                }
        return None

    @classmethod
    def _calc_annual(cls, palaces: list[PalaceResult], year: int) -> dict[str, Any]:
        stem, branch = cls._year_ganzhi(year)
        palace = next((p for p in palaces if p.branch == branch), None)
        return {
            "year": year,
            "yearGanzhi": stem + branch,
            "yearBranch": branch,
            "palace": palace.name if palace else "",
            "branch": branch,
        }

    @classmethod
    def _calc_monthly(cls, palaces: list[PalaceResult], year: int, month: int) -> dict[str, Any]:
        """流月：以流年命宫起正月，顺数至生月（简化算法）。"""
        annual = cls._calc_annual(palaces, year)
        liunian_palace = next((p for p in palaces if p.name == annual["palace"]), None)
        if not liunian_palace:
            return {"year": year, "month": month, "palace": "", "branch": ""}

        start_index = liunian_palace.branch_index
        target_index = (start_index + month - 1) % 12
        branch = EARTHLY_BRANCHES[target_index]
        palace = next((p for p in palaces if p.branch == branch), None)
        return {
            "year": year,
            "month": month,
            "palace": palace.name if palace else "",
            "branch": branch,
            "liunianPalace": annual["palace"],
        }

    @classmethod
    def build_snapshot(
        cls,
        palaces: list[PalaceResult],
        daxian_map: dict[str, DaXianRange],
        birth: datetime,
        gender: str,
        year_stem: str,
        reference: datetime | None = None,
    ) -> FortuneSnapshot:
        reference = reference or datetime.now()
        rule = RulesLoader.get_daxian_rule(gender, year_stem)
        return FortuneSnapshot(
            direction=rule.direction,
            current_daxian=cls._find_current_daxian(palaces, daxian_map, birth, reference),
            annual_fortune=cls._calc_annual(palaces, reference.year),
            monthly_fortune=cls._calc_monthly(palaces, reference.year, reference.month),
        )


calc_daxian_for_palaces = FortuneEngine.calc_daxian
is_daxian_forward = FortuneEngine.is_daxian_forward
