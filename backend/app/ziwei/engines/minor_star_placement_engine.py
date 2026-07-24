"""杂曜安置引擎 V1.3 — 统一输出可追溯杂曜落宫。"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.ziwei.engines.auxiliary_star_engine import AuxiliaryStarEngine, AuxiliaryStarResult
from app.ziwei.engines.palace_engine import PalaceResult
from app.ziwei.rules.auxiliary_star_rules import AUXILIARY_STAR_NAMES


@dataclass
class MinorStarPlacement:
    star: str
    palace: str
    branch: str = ""
    rule_source: str = ""
    category: str = "auxiliary"
    trace: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "star": self.star,
            "palace": self.palace,
            "branch": self.branch,
            "rule_source": self.rule_source,
            "category": self.category,
            "trace": self.trace,
        }


class MinorStarPlacementEngine:
    """
    专业杂曜安置：红鸾/天喜/天姚/咸池/孤寡/华盖/天刑/天哭天虚/
    天官/天福/天寿/天才/天月。

    规则全部来自 auxiliary_star_rules（禁止 LLM 造规则）。
    """

    TARGET_STARS: tuple[str, ...] = AUXILIARY_STAR_NAMES

    @classmethod
    def compute(
        cls,
        palaces: list[PalaceResult],
        lunar_month: int,
        year_branch: str,
        year_stem: str = "",
    ) -> list[MinorStarPlacement]:
        raw: list[AuxiliaryStarResult] = AuxiliaryStarEngine.compute(
            palaces,
            lunar_month=lunar_month,
            year_branch=year_branch,
            year_stem=year_stem,
        )
        by_name = {s.name: s for s in raw}
        results: list[MinorStarPlacement] = []
        for name in cls.TARGET_STARS:
            item = by_name.get(name)
            if not item:
                continue
            results.append(
                MinorStarPlacement(
                    star=item.name,
                    palace=item.palace,
                    branch=item.branch,
                    rule_source=item.rule_source or item.source,
                    category=item.category,
                    trace=item.trace,
                )
            )
        return results

    @classmethod
    def to_dict_list(cls, stars: list[MinorStarPlacement]) -> list[dict]:
        return [s.to_dict() for s in stars]
