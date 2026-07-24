"""天府星定位 — 寅申轴镜像（三合派安天府）。"""

from __future__ import annotations

from app.ziwei.constants import EARTHLY_BRANCHES
from app.ziwei.rules.seed_generator import calc_tianfu_branch_index
from app.ziwei_engine.stars.ziwei import StarPlacement


class TianfuStarCalculator:
    """
    天府星定位。

    规则：以寅–申为轴镜像紫微地支（非简单对宫）。
    紫微在寅/申时与天府同宫；在巳/亥时才与对宫重合。
    """

    @staticmethod
    def calculate(
        ziwei_branch: str,
        branch_to_palace: dict[str, str] | None = None,
    ) -> StarPlacement:
        ziwei_index = EARTHLY_BRANCHES.index(ziwei_branch)
        tianfu_index = calc_tianfu_branch_index(ziwei_index)
        branch = EARTHLY_BRANCHES[tianfu_index]
        palace = branch_to_palace.get(branch) if branch_to_palace else None
        return StarPlacement(star="天府", branch=branch, palace=palace)
