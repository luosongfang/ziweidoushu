"""六煞星定位。"""

from __future__ import annotations

from app.ziwei.engines.palace_engine import PalaceResult
from app.ziwei.engines.star_placement_engine import StarPlacementEngine


class EvilStarsCalculator:
    """煞星（擎羊、陀罗、火星、铃星、地空、地劫）。"""

    SHA_NAMES: tuple[str, ...] = (
        "擎羊", "陀罗", "火星", "铃星", "地空", "地劫",
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
        for palace_name, star_list in placement.sha_stars.items():
            for star in star_list:
                if star["name"] in cls.SHA_NAMES:
                    result.append({"name": star["name"], "palace": palace_name})
        return result
