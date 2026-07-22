"""生年四化系统 — 十天干禄权科忌。"""

from __future__ import annotations

from dataclasses import dataclass

from app.ziwei.engines.four_transform_engine import FourTransformEngine
from app.ziwei.rules.loader import RulesLoader


@dataclass(frozen=True)
class FourHuaRule:
    """四化规则（对应 four_hua_rules 表）。"""

    year_gan: str
    hua_lu: str
    hua_quan: str
    hua_ke: str
    hua_ji: str


@dataclass(frozen=True)
class FourHuaResult:
    """四化计算结果。"""

    year_gan: str
    hua_lu: dict
    hua_quan: dict
    hua_ke: dict
    hua_ji: dict

    def to_dict(self) -> dict:
        return {
            "year_gan": self.year_gan,
            "hua_lu": self.hua_lu,
            "hua_quan": self.hua_quan,
            "hua_ke": self.hua_ke,
            "hua_ji": self.hua_ji,
        }


# 十天干四化标准表（与 RulesLoader / DB seeds 一致）
DEFAULT_FOUR_HUA_RULES: tuple[FourHuaRule, ...] = (
    FourHuaRule("甲", "廉贞", "破军", "武曲", "太阳"),
    FourHuaRule("乙", "天机", "天梁", "紫微", "太阴"),
    FourHuaRule("丙", "天同", "天机", "文昌", "廉贞"),
    FourHuaRule("丁", "太阴", "天同", "天机", "巨门"),
    FourHuaRule("戊", "贪狼", "太阴", "右弼", "天机"),
    FourHuaRule("己", "武曲", "贪狼", "天梁", "文曲"),
    FourHuaRule("庚", "太阳", "武曲", "太阴", "天同"),
    FourHuaRule("辛", "巨门", "太阳", "文曲", "文昌"),
    FourHuaRule("壬", "天梁", "紫微", "左辅", "武曲"),
    FourHuaRule("癸", "破军", "巨门", "太阴", "贪狼"),
)


class FourHuaCalculator:
    """四化计算器。"""

    @classmethod
    def get_rule(cls, year_gan: str) -> FourHuaRule:
        rule = RulesLoader.get_four_transform(year_gan)
        return FourHuaRule(
            year_gan=year_gan,
            hua_lu=rule.lu_star,
            hua_quan=rule.quan_star,
            hua_ke=rule.ke_star,
            hua_ji=rule.ji_star,
        )

    @classmethod
    def calculate(cls, year_gan: str, star_to_palace: dict[str, str]) -> FourHuaResult:
        transform = FourTransformEngine.compute(year_gan, star_to_palace)
        s = transform.summary
        return FourHuaResult(
            year_gan=year_gan,
            hua_lu={"star": s.lu.star, "palace": s.lu.palace, "type": "禄"},
            hua_quan={"star": s.quan.star, "palace": s.quan.palace, "type": "权"},
            hua_ke={"star": s.ke.star, "palace": s.ke.palace, "type": "科"},
            hua_ji={"star": s.ji.star, "palace": s.ji.palace, "type": "忌"},
        )

    @classmethod
    def all_rules(cls) -> list[FourHuaRule]:
        return list(DEFAULT_FOUR_HUA_RULES)
