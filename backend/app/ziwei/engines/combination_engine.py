"""组合引擎 — Sprint 6：星曜格局识别。"""

from __future__ import annotations

from collections import defaultdict

from app.models.chart import CombinationOutput, CombinationPattern
from app.ziwei.engines.palace_engine import PalaceResult
from app.ziwei.engines.star_placement_engine import StarPlacementResult
from app.ziwei.rules.loader import RulesLoader

MAIN_STAR_NAMES = frozenset({
    "紫微", "天机", "太阳", "武曲", "天同", "廉贞",
    "天府", "太阴", "贪狼", "巨门", "天相", "天梁", "七杀", "破军",
})


class CombinationEngine:
    """Combination Engine — 读 star_combination_rules，匹配命盘格局。"""

    @staticmethod
    def _collect_palace_stars(
        star_placement: StarPlacementResult,
    ) -> dict[str, set[str]]:
        palace_stars: dict[str, set[str]] = defaultdict(set)
        for bucket in (
            star_placement.main_stars,
            star_placement.aux_stars,
            star_placement.sha_stars,
            star_placement.za_stars,
        ):
            for palace, stars in bucket.items():
                for star in stars:
                    palace_stars[palace].add(star["name"])
        return palace_stars

    @staticmethod
    def _palaces_for_stars(
        stars: list[str],
        star_to_palace: dict[str, str],
    ) -> list[str]:
        return [star_to_palace[s] for s in stars if s in star_to_palace]

    @classmethod
    def _find_same_palace(cls, stars: list[str], star_to_palace: dict[str, str]) -> str | None:
        if len(stars) < 1:
            return None
        palaces = cls._palaces_for_stars(stars, star_to_palace)
        if len(palaces) != len(stars):
            return None
        return palaces[0] if len(set(palaces)) == 1 else None

    @classmethod
    def _match_rule(
        cls,
        rule: dict,
        palace_order: list[str],
        star_to_palace: dict[str, str],
        palace_stars: dict[str, set[str]],
        star_sihua: dict[str, str],
    ) -> tuple[bool, list[str]]:
        stars: list[str] = rule["stars"]
        match_type: str = rule.get("match_type", "chart_present")

        if match_type == "same_palace":
            palace = cls._find_same_palace(stars, star_to_palace)
            if palace:
                return True, [palace]
            return False, []

        if match_type == "chart_present":
            if all(s in star_to_palace for s in stars):
                return True, sorted(set(cls._palaces_for_stars(stars, star_to_palace)))
            return False, []

        if match_type == "both_present":
            if not all(s in star_to_palace for s in stars):
                return False, []
            if cls._find_same_palace(stars, star_to_palace):
                return False, []
            return True, sorted(set(cls._palaces_for_stars(stars, star_to_palace)))

        if match_type == "flank_ming" and len(stars) == 2:
            left = palace_order[1]
            right = palace_order[11]
            p0 = star_to_palace.get(stars[0])
            p1 = star_to_palace.get(stars[1])
            if p0 and p1 and {p0, p1} == {left, right}:
                return True, [left, right]
            return False, []

        if match_type == "flank_ji" and len(stars) == 2:
            # 羊陀夹忌：擎羊/陀罗夹住化忌星所在宫
            ji_palace = ""
            for sname, hua in star_sihua.items():
                if hua == "忌":
                    ji_palace = star_to_palace.get(sname, "")
                    break
            if not ji_palace or ji_palace not in palace_order:
                return False, []
            idx = palace_order.index(ji_palace)
            left = palace_order[(idx - 1) % 12]
            right = palace_order[(idx + 1) % 12]
            p0 = star_to_palace.get(stars[0])
            p1 = star_to_palace.get(stars[1])
            if p0 and p1 and {p0, p1} == {left, right}:
                return True, [left, ji_palace, right]
            return False, []

        if match_type == "sole_main_star" and stars == ["紫微"]:
            palace = star_to_palace.get("紫微")
            if not palace:
                return False, []
            main_count = len(palace_stars.get(palace, set()) & MAIN_STAR_NAMES)
            if main_count == 1:
                return True, [palace]
            return False, []

        if match_type == "sihua":
            star_name = stars[0]
            if star_sihua.get(star_name) == rule.get("required_sihua"):
                palace = star_to_palace.get(star_name, "")
                return True, [palace] if palace else []
            return False, []

        return False, []

    @classmethod
    def compute(
        cls,
        palace_results: list[PalaceResult],
        star_placement: StarPlacementResult,
        star_sihua: dict[str, str] | None = None,
    ) -> CombinationOutput:
        star_sihua = star_sihua or {}
        branch_to_palace = {p.branch: p.name for p in palace_results}
        star_to_palace = star_placement.star_to_palace(branch_to_palace)
        palace_order = [p.name for p in palace_results]
        palace_stars = cls._collect_palace_stars(star_placement)

        patterns: list[CombinationPattern] = []
        for rule in RulesLoader.get_star_combinations():
            matched, palaces = cls._match_rule(
                rule, palace_order, star_to_palace, palace_stars, star_sihua
            )
            if not matched:
                continue
            tags = [
                t for t in (rule.get("personality"), rule.get("career"), rule.get("wealth"))
                if t
            ]
            patterns.append(CombinationPattern(
                name=rule["combination_name"],
                category=rule["category"],
                stars=rule["stars"],
                palaces=palaces,
                tags=tags,
                ai_prompt_ref=rule.get("ai_prompt"),
            ))

        return CombinationOutput(patterns=patterns)
