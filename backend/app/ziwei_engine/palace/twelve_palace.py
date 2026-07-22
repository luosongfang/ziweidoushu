"""十二宫结构与布宫。"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.ziwei.engines.palace_engine import PalaceEngine, PalaceResult


@dataclass
class Palace:
    """单宫数据结构（引擎层）。"""

    name: str
    position: int
    branch: str
    ganzhi: str = ""
    stars: list[dict] = field(default_factory=list)
    transformations: list[dict] = field(default_factory=list)
    is_ming_gong: bool = False
    is_shen_gong: bool = False

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "position": self.position,
            "branch": self.branch,
            "ganzhi": self.ganzhi,
            "stars": self.stars,
            "transformations": self.transformations,
            "is_ming_gong": self.is_ming_gong,
            "is_shen_gong": self.is_shen_gong,
        }


class TwelvePalaceBuilder:
    """十二宫布宫器。"""

    @classmethod
    def build(
        cls,
        lunar_month: int,
        hour_branch_index: int,
        year_stem: str | None = None,
    ) -> tuple[str, str, list[Palace]]:
        ming_idx, shen_idx, raw = PalaceEngine.compute(
            lunar_month, hour_branch_index, year_stem=year_stem
        )
        ming_branch = raw[0].branch if raw[0].is_ming_gong else next(p.branch for p in raw if p.is_ming_gong)
        shen_branch = next(p.branch for p in raw if p.is_shen_gong)
        palaces = [cls._from_result(p) for p in raw]
        return ming_branch, shen_branch, palaces

    @staticmethod
    def _from_result(result: PalaceResult) -> Palace:
        return Palace(
            name=result.name,
            position=result.position,
            branch=result.branch,
            ganzhi=result.ganzhi,
            is_ming_gong=result.is_ming_gong,
            is_shen_gong=result.is_shen_gong,
        )
