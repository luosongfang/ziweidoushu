"""辅助杂曜安置引擎 — V1.3：支持年干查表 / 命宫起数 / 天寿。"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.ziwei.constants import EARTHLY_BRANCHES
from app.ziwei.engines.palace_engine import PalaceResult
from app.ziwei.rules.loader import RulesLoader


@dataclass(frozen=True)
class AuxiliaryStarContext:
    lunar_month: int
    year_branch: str
    year_branch_index: int
    year_stem: str = ""
    ming_gong_branch: str = ""
    ming_gong_index: int = 0


@dataclass
class AuxiliaryStarResult:
    name: str
    branch: str
    palace: str
    category: str = "auxiliary"
    source: str = "auxiliary_star_rules"
    rule_source: str = ""
    trace: dict = field(default_factory=dict)


class AuxiliaryStarEngine:
    """Auxiliary Star Engine — 读 auxiliary_star_rules。"""

    @staticmethod
    def _branch_index(branch: str) -> int:
        return EARTHLY_BRANCHES.index(branch)

    @classmethod
    def _move(cls, base_index: int, direction: str, offset: int) -> int:
        if direction == "forward":
            return (base_index + offset) % 12
        if direction == "backward":
            return (base_index - offset + 12) % 12
        raise ValueError(f"未知方向：{direction}")

    @classmethod
    def _resolve_group_branch(cls, year_branch: str, mapping: dict[str, str]) -> str:
        for group, branch in mapping.items():
            if year_branch in group:
                return branch
        return ""

    @classmethod
    def _resolve_branch(
        cls,
        rule: dict,
        ctx: AuxiliaryStarContext,
        resolved: dict[str, str],
    ) -> str:
        expr = rule.get("rule_expression") or {}
        rule_type = rule.get("rule_type", "")

        if rule_type == "opposite_branch":
            base_star = expr.get("base_star", "")
            base_branch = resolved.get(base_star, "")
            if not base_branch:
                return ""
            offset = expr.get("offset", 6)
            return EARTHLY_BRANCHES[(cls._branch_index(base_branch) + offset) % 12]

        if rule_type == "branch_group":
            mapping = expr.get("mapping", {})
            return cls._resolve_group_branch(ctx.year_branch, mapping)

        if rule_type == "stem_lookup":
            mapping = expr.get("mapping", {})
            return mapping.get(ctx.year_stem, "")

        if rule_type == "ming_to_year_branch":
            # 命宫起子，顺数至生年支
            if not ctx.ming_gong_branch:
                return ""
            year_idx = ctx.year_branch_index
            # 命宫当子(0)，目标年支相对子的步数 = year_idx
            return EARTHLY_BRANCHES[(ctx.ming_gong_index + year_idx) % 12]

        if rule_type == "branch_offset":
            direction = expr.get("direction", "forward")
            offset = expr.get("offset", 0)
            by = expr.get("by", "year_branch")
            if expr.get("base_by") == "year_branch":
                # 天寿：年支起子位，顺数至生月
                base_idx = ctx.year_branch_index
            else:
                base_branch = expr.get("base_branch", "寅")
                base_idx = cls._branch_index(base_branch)
            if by == "year_branch":
                step = ctx.year_branch_index + offset
            elif by == "lunar_month":
                step = ctx.lunar_month - 1 + offset
            else:
                step = offset
            return EARTHLY_BRANCHES[cls._move(base_idx, direction, step)]

        return ""

    @classmethod
    def compute(
        cls,
        palaces: list[PalaceResult],
        lunar_month: int,
        year_branch: str,
        year_stem: str = "",
        school: str = RulesLoader.SCHOOL,
    ) -> list[AuxiliaryStarResult]:
        branch_to_palace = {p.branch: p.name for p in palaces}
        ming = next((p for p in palaces if p.is_ming_gong), None)
        ctx = AuxiliaryStarContext(
            lunar_month=lunar_month,
            year_branch=year_branch,
            year_branch_index=EARTHLY_BRANCHES.index(year_branch),
            year_stem=year_stem,
            ming_gong_branch=ming.branch if ming else "",
            ming_gong_index=ming.branch_index if ming else 0,
        )
        resolved_branches: dict[str, str] = {}
        results: list[AuxiliaryStarResult] = []

        for rule in RulesLoader.get_auxiliary_star_rules(school=school):
            if not rule.get("enabled", True):
                continue
            star_name = rule["star_name"]
            branch = cls._resolve_branch(rule, ctx, resolved_branches)
            if not branch:
                continue
            resolved_branches[star_name] = branch
            palace = branch_to_palace.get(branch, "")
            rule_source = f"{rule.get('source', 'auxiliary_star_rules')}:{rule.get('rule_type')}"
            results.append(
                AuxiliaryStarResult(
                    name=star_name,
                    branch=branch,
                    palace=palace,
                    category=rule.get("category", "auxiliary"),
                    source=rule.get("source", "auxiliary_star_rules"),
                    rule_source=rule_source,
                    trace={
                        "engine": "auxiliary_star",
                        "rule_type": rule.get("rule_type"),
                        "rule_expression": rule.get("rule_expression"),
                        "rule_source": rule_source,
                        "source": rule.get("source", "auxiliary_star_rules"),
                    },
                )
            )
        return results

    @classmethod
    def to_dict_list(cls, stars: list[AuxiliaryStarResult]) -> list[dict]:
        return [
            {
                "name": s.name,
                "branch": s.branch,
                "palace": s.palace,
                "category": s.category,
                "source": s.source,
                "rule_source": s.rule_source,
                "trace": s.trace,
            }
            for s in stars
        ]
