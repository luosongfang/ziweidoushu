"""身宫算法 — 寅起正月，顺数生月，顺数生时。"""

from __future__ import annotations

from app.ziwei.constants import EARTHLY_BRANCHES
from app.ziwei.engines.palace_engine import PalaceEngine


class ShenGongCalculator:
    """身宫地支计算器。"""

    @staticmethod
    def calculate(lunar_month: int, hour_branch_index: int) -> str:
        branch_index = PalaceEngine.calc_shen_gong_branch(lunar_month, hour_branch_index)
        return EARTHLY_BRANCHES[branch_index]

    @staticmethod
    def calculate_index(lunar_month: int, hour_branch_index: int) -> int:
        return PalaceEngine.calc_shen_gong_branch(lunar_month, hour_branch_index)
