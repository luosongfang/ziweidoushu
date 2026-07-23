"""大限四化 — V1.2 Phase 2。"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.ziwei.engines.fortune_engine import FortuneEngine
from app.ziwei.engines.palace_engine import PalaceResult
from app.ziwei.rules.loader import RulesLoader


@dataclass
class TransformDetail:
    star: str
    palace: str
    type: str


@dataclass
class DaxianTransformResult:
    period: str = ""
    stem: str = ""
    palace: str = ""
    lu: TransformDetail | None = None
    quan: TransformDetail | None = None
    ke: TransformDetail | None = None
    ji: TransformDetail | None = None
    source: str = "four_transform_rules"
    trace: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        def _detail(item: TransformDetail | None) -> dict[str, str]:
            if not item:
                return {"star": "", "palace": "", "type": ""}
            return {"star": item.star, "palace": item.palace, "type": item.type}

        return {
            "period": self.period,
            "stem": self.stem,
            "palace": self.palace,
            "lu": _detail(self.lu),
            "quan": _detail(self.quan),
            "ke": _detail(self.ke),
            "ji": _detail(self.ji),
            "source": self.source,
            "trace": self.trace,
        }


class DaxianTransformCalculator:
    """大限干四化 — 取当前大限宫位天干查四化表。"""

    @classmethod
    def _build_detail(
        cls,
        star_name: str,
        label: str,
        star_to_palace: dict[str, str],
    ) -> TransformDetail:
        return TransformDetail(
            star=star_name,
            palace=star_to_palace.get(star_name, ""),
            type=label,
        )

    @classmethod
    def compute(
        cls,
        palaces: list[PalaceResult],
        daxian_map: dict[str, Any],
        star_to_palace: dict[str, str],
        gender: str,
        year_stem: str,
        virtual_age: int,
    ) -> DaxianTransformResult | None:
        current_palace_name = ""
        current_range = None
        for palace in palaces:
            dx = daxian_map.get(palace.name)
            if dx and dx.start_age <= virtual_age <= dx.end_age:
                current_palace_name = palace.name
                current_range = dx
                break
        if not current_palace_name or not current_range:
            return None

        palace = next(p for p in palaces if p.name == current_palace_name)
        stem = palace.ganzhi[0] if palace.ganzhi else ""
        if not stem:
            return None

        rule = RulesLoader.get_four_transform(stem)
        return DaxianTransformResult(
            period=f"{current_range.start_age}-{current_range.end_age}",
            stem=stem,
            palace=current_palace_name,
            lu=cls._build_detail(rule.lu_star, "禄", star_to_palace),
            quan=cls._build_detail(rule.quan_star, "权", star_to_palace),
            ke=cls._build_detail(rule.ke_star, "科", star_to_palace),
            ji=cls._build_detail(rule.ji_star, "忌", star_to_palace),
            source="four_transform_rules",
            trace={
                "engine": "daxian_transform",
                "source": "four_transform_rules",
                "stem": stem,
                "palace": current_palace_name,
                "period": f"{current_range.start_age}-{current_range.end_age}",
                "gender": gender,
                "year_stem": year_stem,
                "virtual_age": virtual_age,
            },
        )

    @classmethod
    def virtual_age(cls, birth, reference) -> int:
        return FortuneEngine._calc_age(birth, reference)  # noqa: SLF001
