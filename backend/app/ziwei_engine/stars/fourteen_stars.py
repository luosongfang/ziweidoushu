"""十四主星定位框架。"""

from __future__ import annotations

from app.ziwei.constants import EARTHLY_BRANCHES
from app.ziwei.engines.palace_engine import PalaceResult
from app.ziwei.engines.star_placement_engine import StarPlacementEngine
from app.ziwei_engine.stars.ziwei import StarPlacement


class FourteenStarsCalculator:
    """十四主星安置 — 委托 StarPlacementEngine（DB 规则）。"""

    MAIN_STAR_NAMES: tuple[str, ...] = (
        "紫微", "天机", "太阳", "武曲", "天同", "廉贞",
        "天府", "太阴", "贪狼", "巨门", "天相", "天梁", "七杀", "破军",
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
    ) -> list[StarPlacement]:
        placement = StarPlacementEngine.compute(
            palaces,
            lunar_day,
            bureau_number,
            year_stem,
            year_branch,
            hour_branch_index,
            lunar_month,
        )
        branch_to_palace = {p.branch: p.name for p in palaces}
        stars: list[StarPlacement] = []
        for name in cls.MAIN_STAR_NAMES:
            branch = placement.star_branches.get(name)
            if branch:
                stars.append(StarPlacement(
                    star=name,
                    branch=branch,
                    palace=branch_to_palace.get(branch),
                ))
        return stars

    @classmethod
    def to_dict_list(cls, stars: list[StarPlacement]) -> list[dict]:
        return [{"name": s.star, "palace": s.palace, "branch": s.branch} for s in stars]
