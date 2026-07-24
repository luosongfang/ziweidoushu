"""规则加载器 — Sprint 1：内存规则缓存（与 database/rules seeds 一致）。"""

from __future__ import annotations

from dataclasses import dataclass

from app.ziwei.constants import ELEMENT_TO_JU_NAME, YANG_STEMS
from app.ziwei.exceptions import RuleNotFoundError
from app.ziwei.rules.cache import get_rules_cache


@dataclass(frozen=True)
class NayinRule:
    heavenly_stem: str
    earthly_branch: str
    nayin: str
    element: str
    bureau_number: int


@dataclass(frozen=True)
class FourTransformRule:
    heavenly_stem: str
    lu_star: str
    quan_star: str
    ke_star: str
    ji_star: str


@dataclass(frozen=True)
class DaxianRule:
    gender: str
    year_yinyang: str
    direction: str
    start_age_formula: str


class RulesLoader:
    """
    统一规则加载入口。

    Sprint 1：从 seed_generator 内存缓存读取（与 DB seeds 数据一致）；
    Sprint 2+：优先 Supabase 查询，缓存失效时回退内存。
    """

    RULES_VERSION = "2026.07.24"
    SCHOOL = "sanhe"

    @classmethod
    def _cache(cls) -> dict:
        return get_rules_cache()

    @classmethod
    def get_nayin(cls, heavenly_stem: str, earthly_branch: str) -> NayinRule:
        for row in cls._cache()["nayin_rules"]:
            if row["heavenly_stem"] == heavenly_stem and row["earthly_branch"] == earthly_branch:
                return NayinRule(
                    heavenly_stem=row["heavenly_stem"],
                    earthly_branch=row["earthly_branch"],
                    nayin=row["nayin"],
                    element=row["element"],
                    bureau_number=row["bureau_number"],
                )
        raise RuleNotFoundError(f"纳音规则未找到：{heavenly_stem}{earthly_branch}")

    @classmethod
    def get_nayin_by_ganzhi(cls, ganzhi: str) -> NayinRule:
        return cls.get_nayin(ganzhi[0], ganzhi[1])

    @classmethod
    def get_bureau(cls, heavenly_stem: str, earthly_branch: str) -> tuple[str, int, str]:
        rule = cls.get_nayin(heavenly_stem, earthly_branch)
        return rule.element, rule.bureau_number, ELEMENT_TO_JU_NAME[rule.element]

    @classmethod
    def get_ziwei_position(cls, bureau: int, lunar_day: int, school: str = SCHOOL) -> str:
        for row in cls._cache()["ziwei_position_rules"]:
            if row["bureau"] == bureau and row["lunar_day"] == lunar_day and row["school"] == school:
                return row["ziwei_branch"]
        raise RuleNotFoundError(f"紫微定位未找到：局={bureau}, 日={lunar_day}")

    @classmethod
    def get_four_transform(cls, heavenly_stem: str, school: str = SCHOOL) -> FourTransformRule:
        for row in cls._cache()["four_transform_rules"]:
            if row["heavenly_stem"] == heavenly_stem and row["school"] == school:
                return FourTransformRule(
                    heavenly_stem=row["heavenly_stem"],
                    lu_star=row["lu"],
                    quan_star=row["quan"],
                    ke_star=row["ke"],
                    ji_star=row["ji"],
                )
        raise RuleNotFoundError(f"四化规则未找到：{heavenly_stem}")

    @classmethod
    def get_daxian_rule(cls, gender: str, year_stem: str, school: str = SCHOOL) -> DaxianRule:
        year_yinyang = "yang" if year_stem in YANG_STEMS else "yin"
        for row in cls._cache()["daxian_rules"]:
            if (
                row["gender"] == gender
                and row["year_yinyang"] == year_yinyang
                and row["school"] == school
            ):
                return DaxianRule(
                    gender=row["gender"],
                    year_yinyang=row["year_yinyang"],
                    direction=row["direction"],
                    start_age_formula=row["start_age_formula"],
                )
        raise RuleNotFoundError(f"大限规则未找到：{gender}, {year_yinyang}")

    @classmethod
    def get_brightness(cls, star_name: str, branch: str, school: str = SCHOOL) -> str:
        for row in cls._cache()["brightness_rules"]:
            if row["star_name"] == star_name and row["branch"] == branch and row["school"] == school:
                return row["brightness"]
        return ""

    @classmethod
    def get_star_placement_rules(cls, rule_type: str | None = None, school: str = SCHOOL) -> list[dict]:
        rules = cls._cache()["star_placement_rules"]
        filtered = [r for r in rules if r["school"] == school]
        if rule_type:
            filtered = [r for r in filtered if r["rule_type"] == rule_type]
        return filtered

    @classmethod
    def get_star_combinations(cls, school: str = SCHOOL) -> list[dict]:
        return [r for r in cls._cache()["star_combination_rules"] if r["school"] == school]

    @classmethod
    def get_palace_meaning(cls, palace_name: str, school: str = SCHOOL) -> dict | None:
        for row in cls._cache()["palace_meaning_rules"]:
            if row["palace_name"] == palace_name and row["school"] == school:
                return row
        return None

    @classmethod
    def get_star_metadata(cls, star_name: str) -> dict | None:
        for row in cls._cache()["stars"]:
            if row["name"] == star_name:
                return row
        return None

    @classmethod
    def get_star_lookup(cls, star_name: str, school: str = SCHOOL) -> dict | None:
        for row in cls._cache().get("star_lookup_rules", []):
            if row["star_name"] == star_name and row["school"] == school:
                return row
        return None

    @classmethod
    def get_auxiliary_star_rules(cls, school: str = SCHOOL) -> list[dict]:
        return [
            row for row in cls._cache().get("auxiliary_star_rules", [])
            if row.get("school", school) == school and row.get("enabled", True)
        ]

    @classmethod
    def get_star_brightness_rule(cls, star_name: str, branch: str, school: str = SCHOOL) -> str:
        for row in cls._cache().get("star_brightness_rules", []):
            if (
                row["star_name"] == star_name
                and row["branch"] == branch
                and row.get("school", school) == school
            ):
                return row["brightness"]
        return cls.get_brightness(star_name, branch, school=school)

    @classmethod
    def rules_version(cls) -> str:
        return cls._cache()["version"]
