"""排盘算法调试快照 — 不依赖 UI。"""

from __future__ import annotations

from typing import Any

MAIN_14 = (
    "紫微", "天机", "太阳", "武曲", "天同", "廉贞",
    "天府", "太阴", "贪狼", "巨门", "天相", "天梁", "七杀", "破军",
)


def build_algorithm_debug(
    *,
    lunar_date: str,
    ju: str,
    ziwei_position: str,
    tianfu_position: str,
    star_branches: dict[str, str],
) -> dict[str, Any]:
    """输出经典核对用的十四主星地支快照。"""
    fourteen = {name: star_branches.get(name, "") for name in MAIN_14}
    return {
        "lunarDate": lunar_date,
        "ju": ju,
        "ziweiPosition": ziwei_position,
        "tianfuPosition": tianfu_position,
        "fourteenStars": fourteen,
    }
