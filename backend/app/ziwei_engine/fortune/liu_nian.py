"""流年计算。"""

from __future__ import annotations

from dataclasses import dataclass

from app.ziwei.engines.fortune_engine import FortuneEngine
from app.ziwei.engines.palace_engine import PalaceResult


@dataclass(frozen=True)
class LiuNianResult:
    year: int
    branch: str
    palace: str


class LiuNianCalculator:
    """流年太岁宫计算器。"""

    @classmethod
    def calculate(cls, palaces: list[PalaceResult], year: int) -> LiuNianResult:
        annual = FortuneEngine._calc_annual(palaces, year)
        return LiuNianResult(
            year=year,
            branch=annual.get("branch", ""),
            palace=annual.get("palace", ""),
        )
