"""天府星定位 — 紫微天府对宫关系。"""

from __future__ import annotations

from app.ziwei.constants import EARTHLY_BRANCHES
from app.ziwei_engine.stars.ziwei import StarPlacement


class TianfuStarCalculator:
    """
    天府星定位。

    规则：天府与紫微同组对宫（安星规则 base=紫微, direction=opposite）。
    """

    @staticmethod
    def calculate(
        ziwei_branch: str,
        branch_to_palace: dict[str, str] | None = None,
    ) -> StarPlacement:
        ziwei_index = EARTHLY_BRANCHES.index(ziwei_branch)
        tianfu_index = (ziwei_index + 6) % 12
        branch = EARTHLY_BRANCHES[tianfu_index]
        palace = branch_to_palace.get(branch) if branch_to_palace else None
        return StarPlacement(star="天府", branch=branch, palace=palace)
