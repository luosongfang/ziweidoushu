"""命宫算法 — 寅起正月，顺数生月，逆数生时。"""

from __future__ import annotations

from app.ziwei.constants import EARTHLY_BRANCHES
from app.ziwei.engines.palace_engine import PalaceEngine


class MingGongCalculator:
    """命宫地支计算器。"""

    @staticmethod
    def calculate(lunar_month: int, hour_branch_index: int) -> str:
        """
        计算命宫地支。

        Parameters
        ----------
        lunar_month : 农历月份（1-12）
        hour_branch_index : 时辰地支索引（0=子 … 11=亥）
        """
        branch_index = PalaceEngine.calc_ming_gong_branch(lunar_month, hour_branch_index)
        return EARTHLY_BRANCHES[branch_index]

    @staticmethod
    def calculate_index(lunar_month: int, hour_branch_index: int) -> int:
        """返回命宫地支索引。"""
        return PalaceEngine.calc_ming_gong_branch(lunar_month, hour_branch_index)
