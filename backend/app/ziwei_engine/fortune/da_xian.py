"""大限计算。"""

from __future__ import annotations

from dataclasses import dataclass

from app.ziwei.engines.fortune_engine import FortuneEngine
from app.ziwei.engines.palace_engine import PalaceResult


@dataclass(frozen=True)
class DaXianRange:
    palace: str
    start_age: int
    end_age: int


class DaXianCalculator:
    """大限计算器。"""

    @classmethod
    def calculate(
        cls,
        palaces: list[PalaceResult],
        bureau_number: int,
        year_stem: str,
        gender: str,
    ) -> tuple[list[DaXianRange], str]:
        daxian_map, direction = FortuneEngine.calc_daxian(
            palaces, bureau_number, year_stem, gender
        )
        ranges = [
            DaXianRange(palace=name, start_age=dx.start_age, end_age=dx.end_age)
            for name, dx in daxian_map.items()
        ]
        return ranges, direction
