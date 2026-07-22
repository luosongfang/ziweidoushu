"""星曜安置引擎 — Sprint 4/5：主星 + 辅煞杂曜（DB 驱动）。"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field

from app.ziwei.constants import EARTHLY_BRANCHES
from app.ziwei.engines.palace_engine import PalaceResult
from app.ziwei.exceptions import RuleNotFoundError
from app.ziwei.rules.loader import RulesLoader

MAIN_STAR_ORDER: tuple[str, ...] = (
    "紫微", "天机", "太阳", "武曲", "天同", "廉贞",
    "天府", "太阴", "贪狼", "巨门", "天相", "天梁", "七杀", "破军",
)

AUX_STAR_ORDER: tuple[str, ...] = (
    "左辅", "右弼", "文昌", "文曲", "天魁", "天钺", "禄存",
)

SHA_STAR_ORDER: tuple[str, ...] = (
    "擎羊", "陀罗", "火星", "铃星", "地空", "地劫",
)

ZA_STAR_ORDER: tuple[str, ...] = ("天马",)


@dataclass(frozen=True)
class PlacementContext:
    lunar_month: int
    lunar_day: int
    bureau_number: int
    year_stem: str
    year_branch: str
    hour_branch_index: int


@dataclass
class StarPlacementResult:
    """星曜落宫结果（按宫位名索引）。"""

    ziwei_branch: str = ""
    star_branches: dict[str, str] = field(default_factory=dict)
    main_stars: dict[str, list[dict]] = field(default_factory=dict)
    aux_stars: dict[str, list[dict]] = field(default_factory=dict)
    sha_stars: dict[str, list[dict]] = field(default_factory=dict)
    za_stars: dict[str, list[dict]] = field(default_factory=dict)

    def main_star_names(self, palace_name: str) -> list[str]:
        return [s["name"] for s in self.main_stars.get(palace_name, [])]

    def star_to_palace(self, branch_to_palace: dict[str, str]) -> dict[str, str]:
        """星名 → 宫位名（供四化引擎使用）。"""
        result: dict[str, str] = {}
        for branch_map in (self.star_branches,):
            for star_name, branch in branch_map.items():
                result[star_name] = branch_to_palace[branch]
        return result


class StarPlacementEngine:
    """Star Placement Engine — ziwei_position + star_placement + star_lookup 规则。"""

    _CATEGORY_MAP = {
        "main_star": "main_stars",
        "aux_star": "aux_stars",
        "sha_star": "sha_stars",
        "za_star": "za_stars",
    }

    _ORDER_MAP = {
        "main_stars": MAIN_STAR_ORDER,
        "aux_stars": AUX_STAR_ORDER,
        "sha_stars": SHA_STAR_ORDER,
        "za_stars": ZA_STAR_ORDER,
    }

    @staticmethod
    def _branch_index(branch: str) -> int:
        return EARTHLY_BRANCHES.index(branch)

    @classmethod
    def _move_branch(cls, base_index: int, direction: str, offset: int) -> int:
        if direction == "forward":
            return (base_index + offset) % 12
        if direction == "backward":
            return (base_index - offset + 12) % 12
        if direction == "opposite":
            return (base_index + 6) % 12
        raise ValueError(f"未知方向：{direction}")

    @classmethod
    def _resolve_group_base(cls, year_branch: str, group_bases: dict[str, str]) -> str:
        for group, base in group_bases.items():
            if year_branch in group:
                return base
        raise RuleNotFoundError(f"年支 {year_branch} 未匹配三合组")

    @classmethod
    def _resolve_rule_branch(
        cls,
        rule: dict,
        ctx: PlacementContext,
        star_indices: dict[str, int],
        ziwei_index: int,
    ) -> int:
        base_star = rule["base_star"]
        direction = rule["direction"]
        offset = rule["offset"]
        condition = rule.get("condition") or {}
        star_name = rule["star_name"]

        if base_star == "self":
            return ziwei_index
        if base_star:
            if base_star not in star_indices:
                raise RuleNotFoundError(f"基准星 {base_star} 未安置，无法计算 {star_name}")
            return cls._move_branch(star_indices[base_star], direction, offset)

        by = condition.get("by")
        if by == "lunar_month":
            base_idx = cls._branch_index(condition["base_branch"])
            return cls._move_branch(base_idx, direction, ctx.lunar_month - 1 + offset)
        if by == "hour_branch":
            base_idx = cls._branch_index(condition["base_branch"])
            return cls._move_branch(base_idx, direction, ctx.hour_branch_index + offset)
        if by == "year_stem":
            lookup_name = condition.get("lookup", star_name)
            lookup = RulesLoader.get_star_lookup(lookup_name)
            if not lookup or "mapping" not in lookup:
                raise RuleNotFoundError(f"查表规则未找到：{lookup_name}")
            return cls._branch_index(lookup["mapping"][ctx.year_stem])
        if by == "year_branch":
            lookup_name = condition.get("lookup", star_name)
            lookup = RulesLoader.get_star_lookup(lookup_name)
            if not lookup or "mapping" not in lookup:
                raise RuleNotFoundError(f"查表规则未找到：{lookup_name}")
            return cls._branch_index(lookup["mapping"][ctx.year_branch])
        if by == "year_branch_hour":
            lookup = RulesLoader.get_star_lookup(star_name)
            if not lookup or "group_bases" not in lookup:
                raise RuleNotFoundError(f"火铃查表未找到：{star_name}")
            base_branch = cls._resolve_group_base(ctx.year_branch, lookup["group_bases"])
            base_idx = cls._branch_index(base_branch)
            return cls._move_branch(base_idx, direction, ctx.hour_branch_index + offset)

        raise RuleNotFoundError(f"无法解析安星规则：{star_name}")

    @classmethod
    def _sort_stars(cls, category_key: str, stars: list[dict]) -> list[dict]:
        order = cls._ORDER_MAP.get(category_key, ())
        order_map = {name: i for i, name in enumerate(order)}
        return sorted(stars, key=lambda s: order_map.get(s["name"], 99))

    @classmethod
    def _resolve_all_stars(
        cls,
        ctx: PlacementContext,
        school: str = RulesLoader.SCHOOL,
    ) -> tuple[str, dict[str, str]]:
        ziwei_branch = RulesLoader.get_ziwei_position(
            ctx.bureau_number, ctx.lunar_day, school=school
        )
        ziwei_index = cls._branch_index(ziwei_branch)
        star_indices: dict[str, int] = {}

        for rule_type in ("main_star", "aux_star", "sha_star", "za_star"):
            for rule in RulesLoader.get_star_placement_rules(rule_type, school=school):
                star_indices[rule["star_name"]] = cls._resolve_rule_branch(
                    rule, ctx, star_indices, ziwei_index
                )

        star_branches = {
            name: EARTHLY_BRANCHES[idx] for name, idx in star_indices.items()
        }
        return ziwei_branch, star_branches

    @classmethod
    def compute(
        cls,
        palaces: list[PalaceResult],
        lunar_day: int,
        bureau_number: int,
        year_stem: str = "",
        year_branch: str = "",
        hour_branch_index: int = 0,
        lunar_month: int = 1,
    ) -> StarPlacementResult:
        ctx = PlacementContext(
            lunar_month=lunar_month,
            lunar_day=lunar_day,
            bureau_number=bureau_number,
            year_stem=year_stem,
            year_branch=year_branch,
            hour_branch_index=hour_branch_index,
        )
        branch_to_palace = {p.branch: p.name for p in palaces}
        ziwei_branch, star_branches = cls._resolve_all_stars(ctx)

        buckets: dict[str, dict[str, list[dict]]] = {
            "main_stars": defaultdict(list),
            "aux_stars": defaultdict(list),
            "sha_stars": defaultdict(list),
            "za_stars": defaultdict(list),
        }

        for rule_type in ("main_star", "aux_star", "sha_star", "za_star"):
            category = cls._CATEGORY_MAP[rule_type]
            is_main = rule_type == "main_star"
            for rule in RulesLoader.get_star_placement_rules(rule_type):
                star_name = rule["star_name"]
                palace_name = branch_to_palace[star_branches[star_name]]
                buckets[category][palace_name].append(
                    {"name": star_name, "isMain": is_main}
                )

        for category, palace_stars in buckets.items():
            for palace_name in palace_stars:
                palace_stars[palace_name] = cls._sort_stars(
                    category, palace_stars[palace_name]
                )

        return StarPlacementResult(
            ziwei_branch=ziwei_branch,
            star_branches=star_branches,
            main_stars=dict(buckets["main_stars"]),
            aux_stars=dict(buckets["aux_stars"]),
            sha_stars=dict(buckets["sha_stars"]),
            za_stars=dict(buckets["za_stars"]),
        )
