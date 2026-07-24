"""十四主星 — 紫微系逆布 + 天府系顺布（逐步 trace）。"""

from __future__ import annotations

from app.ziwei.constants import EARTHLY_BRANCHES
from app.ziwei_classical.stars.tianfu_system import place_tianfu
from app.ziwei_classical.stars.ziwei_system import place_ziwei
from app.ziwei_classical.validator.rule_trace import RuleTrace

# 紫微系：相对紫微逆行
ZIWEI_SERIES: tuple[tuple[str, int], ...] = (
    ("紫微", 0),
    ("天机", 1),
    ("太阳", 3),
    ("武曲", 4),
    ("天同", 5),
    ("廉贞", 8),
)

# 天府系：相对天府顺行
TIANFU_SERIES: tuple[tuple[str, int], ...] = (
    ("天府", 0),
    ("太阴", 1),
    ("贪狼", 2),
    ("巨门", 3),
    ("天相", 4),
    ("天梁", 5),
    ("七杀", 6),
    ("破军", 10),
)

MAIN_14 = tuple(s for s, _ in ZIWEI_SERIES) + tuple(s for s, _ in TIANFU_SERIES)


def place_fourteen_stars(
    bureau_number: int,
    lunar_day: int,
    tianfu_rule: str = "traditional",
    trace: RuleTrace | None = None,
) -> dict:
    zw = place_ziwei(bureau_number, lunar_day, trace=trace)
    ziwei_idx = EARTHLY_BRANCHES.index(zw["branch"])
    tf = place_tianfu(zw["branch"], tianfu_rule=tianfu_rule, trace=trace)
    tianfu_idx = EARTHLY_BRANCHES.index(tf["branch"])

    branches: dict[str, str] = {}
    sequence: list[dict] = []

    for star, offset in ZIWEI_SERIES:
        if star == "紫微":
            idx = ziwei_idx
            rule = "紫微落宫表"
        else:
            idx = (ziwei_idx - offset) % 12
            rule = f"紫微系：自紫微逆行 {offset} 位"
        br = EARTHLY_BRANCHES[idx]
        branches[star] = br
        sequence.append(
            {
                "star": star,
                "branch": br,
                "series": "ziwei",
                "offset": offset,
                "direction": "self" if offset == 0 else "backward",
                "rule": rule,
            }
        )
        if trace is not None and star != "紫微":
            trace.add(
                step=f"star.{star}",
                rule=rule,
                inputs={"ziwei_branch": zw["branch"], "offset": offset},
                outputs={"branch": br},
                source="ziwei_classical.stars.fourteen_stars",
            )

    for star, offset in TIANFU_SERIES:
        if star == "天府":
            idx = tianfu_idx
            rule = tf["rule_doc"]
        else:
            idx = (tianfu_idx + offset) % 12
            rule = f"天府系：自天府顺行 {offset} 位"
        br = EARTHLY_BRANCHES[idx]
        branches[star] = br
        sequence.append(
            {
                "star": star,
                "branch": br,
                "series": "tianfu",
                "offset": offset,
                "direction": "self" if offset == 0 else "forward",
                "rule": rule,
            }
        )
        if trace is not None and star != "天府":
            trace.add(
                step=f"star.{star}",
                rule=rule,
                inputs={"tianfu_branch": tf["branch"], "offset": offset},
                outputs={"branch": br},
                source="ziwei_classical.stars.fourteen_stars",
            )

    return {
        "ziwei": zw,
        "tianfu": tf,
        "branches": branches,
        "sequence": sequence,
    }
