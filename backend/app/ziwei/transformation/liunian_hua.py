"""流年四化 — V1.2 Phase 2。"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.ziwei.engines.fortune_engine import FortuneEngine
from app.ziwei.rules.loader import RulesLoader


@dataclass
class AnnualTransformDetail:
    star: str
    palace: str
    type: str


@dataclass
class AnnualTransformResult:
    year: int = 0
    stem: str = ""
    branch: str = ""
    lu: AnnualTransformDetail | None = None
    quan: AnnualTransformDetail | None = None
    ke: AnnualTransformDetail | None = None
    ji: AnnualTransformDetail | None = None
    source: str = "four_transform_rules"
    trace: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        def _detail(item: AnnualTransformDetail | None) -> dict[str, str]:
            if not item:
                return {"star": "", "palace": "", "type": ""}
            return {"star": item.star, "palace": item.palace, "type": item.type}

        return {
            "year": self.year,
            "stem": self.stem,
            "branch": self.branch,
            "lu": _detail(self.lu),
            "quan": _detail(self.quan),
            "ke": _detail(self.ke),
            "ji": _detail(self.ji),
            "source": self.source,
            "trace": self.trace,
        }


class LiunianTransformCalculator:
    """流年天干四化。"""

    @classmethod
    def _build_detail(
        cls,
        star_name: str,
        label: str,
        star_to_palace: dict[str, str],
    ) -> AnnualTransformDetail:
        return AnnualTransformDetail(
            star=star_name,
            palace=star_to_palace.get(star_name, ""),
            type=label,
        )

    @classmethod
    def compute(cls, year: int, star_to_palace: dict[str, str]) -> AnnualTransformResult:
        stem, branch = FortuneEngine._year_ganzhi(year)  # noqa: SLF001
        rule = RulesLoader.get_four_transform(stem)
        return AnnualTransformResult(
            year=year,
            stem=stem,
            branch=branch,
            lu=cls._build_detail(rule.lu_star, "禄", star_to_palace),
            quan=cls._build_detail(rule.quan_star, "权", star_to_palace),
            ke=cls._build_detail(rule.ke_star, "科", star_to_palace),
            ji=cls._build_detail(rule.ji_star, "忌", star_to_palace),
            source="four_transform_rules",
            trace={
                "engine": "annual_transform",
                "source": "four_transform_rules",
                "year": year,
                "stem": stem,
                "branch": branch,
            },
        )
