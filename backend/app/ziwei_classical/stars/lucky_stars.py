"""甲级辅星：左辅右弼文昌文曲天魁天钺 + 乙级禄存天马。"""

from __future__ import annotations

from app.ziwei.constants import EARTHLY_BRANCHES
from app.ziwei.rules.loader import RulesLoader
from app.ziwei_classical.validator.rule_trace import RuleTrace

# 显式规则说明（查表仍走 RulesLoader，避免单盘硬编码）
LUCKY_RULES = {
    "左辅": {"base": "辰", "by": "lunar_month", "dir": "forward", "note": "辰起正月顺数至生月"},
    "右弼": {"base": "戌", "by": "lunar_month", "dir": "backward", "note": "戌起正月逆数至生月"},
    "文昌": {"base": "戌", "by": "hour", "dir": "forward", "note": "戌起子时顺数至生时"},
    "文曲": {"base": "辰", "by": "hour", "dir": "backward", "note": "辰起子时逆数至生时"},
    "天魁": {"by": "year_stem_lookup", "note": "年干查表"},
    "天钺": {"by": "year_stem_lookup", "note": "年干查表"},
    "禄存": {"by": "year_stem_lookup", "note": "年干查表"},
    "天马": {"by": "year_branch_lookup", "note": "年支查表"},
}


def _move(base: str, direction: str, offset: int) -> str:
    idx = EARTHLY_BRANCHES.index(base)
    if direction == "forward":
        return EARTHLY_BRANCHES[(idx + offset) % 12]
    return EARTHLY_BRANCHES[(idx - offset) % 12]


def place_lucky_stars(
    *,
    lunar_month: int,
    hour_index: int,
    year_stem: str,
    year_branch: str,
    trace: RuleTrace | None = None,
) -> dict[str, dict]:
    out: dict[str, dict] = {}

    def put(name: str, branch: str, rule: str) -> None:
        out[name] = {"branch": branch, "rule": rule, "tier": "甲级" if name in (
            "左辅", "右弼", "文昌", "文曲", "天魁", "天钺"
        ) else "乙级"}
        if trace is not None:
            trace.add(
                step=f"lucky.{name}",
                rule=rule,
                inputs={
                    "lunar_month": lunar_month,
                    "hour_index": hour_index,
                    "year_stem": year_stem,
                    "year_branch": year_branch,
                },
                outputs={"branch": branch},
                source="ziwei_classical.stars.lucky_stars",
            )

    put("左辅", _move("辰", "forward", lunar_month - 1), LUCKY_RULES["左辅"]["note"])
    put("右弼", _move("戌", "backward", lunar_month - 1), LUCKY_RULES["右弼"]["note"])
    put("文昌", _move("戌", "forward", hour_index), LUCKY_RULES["文昌"]["note"])
    put("文曲", _move("辰", "backward", hour_index), LUCKY_RULES["文曲"]["note"])

    for name in ("天魁", "天钺", "禄存"):
        lookup = RulesLoader.get_star_lookup(name)
        mapping = (lookup or {}).get("mapping") or {}
        br = mapping.get(year_stem, "")
        put(name, br, LUCKY_RULES[name]["note"] + f" → {year_stem}")

    lookup = RulesLoader.get_star_lookup("天马")
    mapping = (lookup or {}).get("mapping") or {}
    put("天马", mapping.get(year_branch, ""), LUCKY_RULES["天马"]["note"] + f" → {year_branch}")

    return out
