"""四化引擎 V2 — 生年 / 大限 / 流年 / 宫干自化。"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.ziwei.engines.palace_engine import PalaceResult
from app.ziwei.rules.loader import RulesLoader
from app.ziwei.transformation.daxian_hua import DaxianTransformCalculator
from app.ziwei.transformation.liunian_hua import LiunianTransformCalculator
from app.ziwei_engine.transformation.four_hua import FourHuaCalculator


@dataclass
class SiHuaBlock:
    lu: str = ""
    quan: str = ""
    ke: str = ""
    ji: str = ""
    stem: str = ""
    source: str = "four_transform_rules"
    details: dict[str, Any] = field(default_factory=dict)
    trace: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "lu": self.lu,
            "quan": self.quan,
            "ke": self.ke,
            "ji": self.ji,
            "stem": self.stem,
            "source": self.source,
            "details": self.details,
            "trace": self.trace,
        }


@dataclass
class FourTransformV2Result:
    year: SiHuaBlock = field(default_factory=SiHuaBlock)
    daxian: SiHuaBlock = field(default_factory=SiHuaBlock)
    liunian: SiHuaBlock = field(default_factory=SiHuaBlock)
    self: list[dict[str, Any]] = field(default_factory=list)
    trace: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "year": self.year.to_dict(),
            "daxian": self.daxian.to_dict(),
            "liunian": self.liunian.to_dict(),
            "self": self.self,
            "birth_transform": self.year.to_dict(),
            "daxian_transform": self.daxian.to_dict(),
            "liunian_transform": self.liunian.to_dict(),
            "self_transform": self.self,
            "trace": self.trace,
        }


class FourTransformEngineV2:
    """完整四化：生年 + 大限 + 流年 + 宫干飞化/自化。"""

    @staticmethod
    def _block_from_four_hua(four_hua, stem: str) -> SiHuaBlock:
        def _star(key: str) -> str:
            item = getattr(four_hua, key, None) or {}
            if isinstance(item, dict):
                return item.get("star", "")
            return ""

        return SiHuaBlock(
            lu=_star("hua_lu") if hasattr(four_hua, "hua_lu") else "",
            quan=_star("hua_quan") if hasattr(four_hua, "hua_quan") else "",
            ke=_star("hua_ke") if hasattr(four_hua, "hua_ke") else "",
            ji=_star("hua_ji") if hasattr(four_hua, "hua_ji") else "",
            stem=stem,
            details=four_hua.to_dict() if hasattr(four_hua, "to_dict") else {},
            trace={"engine": "four_transform_v2", "layer": "birth", "stem": stem},
        )

    @staticmethod
    def _block_from_period(period_result) -> SiHuaBlock:
        if period_result is None:
            return SiHuaBlock(trace={"enabled": False})
        data = period_result.to_dict() if hasattr(period_result, "to_dict") else {}

        def _name(key: str) -> str:
            item = data.get(key) or {}
            return item.get("star", "") if isinstance(item, dict) else ""

        return SiHuaBlock(
            lu=_name("lu"),
            quan=_name("quan"),
            ke=_name("ke"),
            ji=_name("ji"),
            stem=data.get("stem", ""),
            details=data,
            source=data.get("source", "four_transform_rules"),
            trace=data.get("trace") or {"engine": "four_transform_v2"},
        )

    @classmethod
    def _self_transforms(
        cls,
        palaces: list[PalaceResult],
        star_to_palace: dict[str, str],
    ) -> list[dict[str, Any]]:
        """宫干飞化：以各宫天干查四化；落本宫为自化，落他宫为飞出。"""
        items: list[dict[str, Any]] = []
        for palace in palaces:
            ganzhi = palace.ganzhi or ""
            if len(ganzhi) < 1:
                continue
            stem = ganzhi[0]
            try:
                rule = RulesLoader.get_four_transform(stem)
            except Exception:
                continue
            mapping = {
                "禄": rule.lu_star,
                "权": rule.quan_star,
                "科": rule.ke_star,
                "忌": rule.ji_star,
            }
            for hua_type, star in mapping.items():
                target_palace = star_to_palace.get(star, "")
                kind = "self" if target_palace == palace.name else "fly"
                items.append({
                    "from_palace": palace.name,
                    "from_ganzhi": ganzhi,
                    "stem": stem,
                    "type": hua_type,
                    "star": star,
                    "to_palace": target_palace,
                    "kind": kind,
                    "rule_source": "four_transform_rules",
                    "trace": {
                        "engine": "four_transform_v2",
                        "layer": "self",
                        "palace_stem": stem,
                    },
                })
        return items

    @classmethod
    def compute(
        cls,
        *,
        year_stem: str,
        star_to_palace: dict[str, str],
        palaces: list[PalaceResult],
        daxian_map: dict[str, Any] | None = None,
        gender: str = "male",
        virtual_age: int = 1,
        reference_year: int | None = None,
    ) -> FourTransformV2Result:
        birth = FourHuaCalculator.calculate(year_stem, star_to_palace)
        # FourHua uses hua_lu dict shape
        year_block = SiHuaBlock(
            lu=(birth.hua_lu or {}).get("star", ""),
            quan=(birth.hua_quan or {}).get("star", ""),
            ke=(birth.hua_ke or {}).get("star", ""),
            ji=(birth.hua_ji or {}).get("star", ""),
            stem=year_stem,
            details=birth.to_dict(),
            trace={"engine": "four_transform_v2", "layer": "birth", "stem": year_stem},
        )

        daxian_block = SiHuaBlock(trace={"enabled": False})
        if daxian_map is not None:
            dax = DaxianTransformCalculator.compute(
                palaces, daxian_map, star_to_palace, gender, year_stem, virtual_age
            )
            daxian_block = cls._block_from_period(dax)

        liu_block = SiHuaBlock(trace={"enabled": False})
        if reference_year is not None:
            liu = LiunianTransformCalculator.compute(reference_year, star_to_palace)
            liu_block = cls._block_from_period(liu)

        self_items = cls._self_transforms(palaces, star_to_palace)

        return FourTransformV2Result(
            year=year_block,
            daxian=daxian_block,
            liunian=liu_block,
            self=self_items,
            trace={
                "engine": "four_transform_v2",
                "birth_stem": year_stem,
                "self_count": len(self_items),
            },
        )
