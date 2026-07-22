"""紫微星定位 — 五行局 + 农历生日。"""

from __future__ import annotations

from dataclasses import dataclass

from app.ziwei.constants import EARTHLY_BRANCHES
from app.ziwei.rules.loader import RulesLoader


@dataclass(frozen=True)
class StarPlacement:
    star: str
    branch: str
    palace: str | None = None

    def to_dict(self) -> dict:
        return {"star": self.star, "branch": self.branch, "palace": self.palace}


class ZiweiStarCalculator:
    """紫微星定位计算器（规则表驱动）。"""

    @classmethod
    def calculate(
        cls,
        lunar_day: int,
        bureau_number: int,
        branch_to_palace: dict[str, str] | None = None,
        school: str = RulesLoader.SCHOOL,
    ) -> StarPlacement:
        branch = RulesLoader.get_ziwei_position(bureau_number, lunar_day, school=school)
        palace = branch_to_palace.get(branch) if branch_to_palace else None
        return StarPlacement(star="紫微", branch=branch, palace=palace)

    @staticmethod
    def branch_index(branch: str) -> int:
        return EARTHLY_BRANCHES.index(branch)
