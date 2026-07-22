"""六吉星 / 辅星定位。"""

from __future__ import annotations

from app.ziwei.engines.palace_engine import PalaceResult
from app.ziwei.engines.star_placement_engine import StarPlacementEngine


class LuckyStarsCalculator:
    """辅星（左辅、右弼、文昌、文曲、天魁、天钺、禄存）。"""

    AUX_NAMES: tuple[str, ...] = (
        "左辅", "右弼", "文昌", "文曲", "天魁", "天钺", "禄存",
    )

    @classmethod
    def calculate(
        cls,
        palaces: list[PalaceResult],
        lunar_day: int,
        bureau_number: int,
        year_stem: str,
        year_branch: str,
        hour_branch_index: int,
        lunar_month: int,
    ) -> list[dict]:
        placement = StarPlacementEngine.compute(
            palaces, lunar_day, bureau_number,
            year_stem, year_branch, hour_branch_index, lunar_month,
        )
        result: list[dict] = []
        for palace_name, star_list in placement.aux_stars.items():
            for star in star_list:
                if star["name"] in cls.AUX_NAMES:
                    result.append({"name": star["name"], "palace": palace_name})
        return result
