"""煞星：擎羊陀罗火星铃星地空地劫。"""

from __future__ import annotations

from app.ziwei.constants import EARTHLY_BRANCHES
from app.ziwei.rules.loader import RulesLoader
from app.ziwei_classical.validator.rule_trace import RuleTrace

YEAR_GROUPS = ("寅午戌", "申子辰", "巳酉丑", "亥卯未")


def _group_of(year_branch: str) -> str:
    for g in YEAR_GROUPS:
        if year_branch in g:
            return g
    return ""


def _move(base: str, direction: str, offset: int) -> str:
    idx = EARTHLY_BRANCHES.index(base)
    if direction == "forward":
        return EARTHLY_BRANCHES[(idx + offset) % 12]
    return EARTHLY_BRANCHES[(idx - offset) % 12]


def place_evil_stars(
    *,
    hour_index: int,
    year_branch: str,
    lu_cun_branch: str,
    trace: RuleTrace | None = None,
) -> dict[str, dict]:
    out: dict[str, dict] = {}

    def put(name: str, branch: str, rule: str) -> None:
        out[name] = {"branch": branch, "rule": rule, "tier": "煞星"}
        if trace is not None:
            trace.add(
                step=f"evil.{name}",
                rule=rule,
                inputs={"hour_index": hour_index, "year_branch": year_branch, "lu_cun": lu_cun_branch},
                outputs={"branch": branch},
                source="ziwei_classical.stars.evil_stars",
            )

    if lu_cun_branch:
        put("擎羊", _move(lu_cun_branch, "forward", 1), "禄存顺一位")
        put("陀罗", _move(lu_cun_branch, "backward", 1), "禄存逆一位")

    for star in ("火星", "铃星"):
        lookup = RulesLoader.get_star_lookup(star)
        bases = (lookup or {}).get("group_bases") or {}
        g = _group_of(year_branch)
        base = bases.get(g, "")
        if base:
            put(star, _move(base, "forward", hour_index), f"{g}组起{base}顺数至生时")

    # 地空地劫：亥起子时，逆/顺至生时
    put("地空", _move("亥", "backward", hour_index), "亥起子时逆数至生时")
    put("地劫", _move("亥", "forward", hour_index), "亥起子时顺数至生时")
    return out
