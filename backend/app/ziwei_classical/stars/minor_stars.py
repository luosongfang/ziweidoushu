"""丙级杂曜安置（公式 + 起点 + 顺逆）。"""

from __future__ import annotations

from app.ziwei.constants import EARTHLY_BRANCHES
from app.ziwei_classical.validator.rule_trace import RuleTrace

# 传统常见安法（三合），显式编码为规则而非纯知识库
MINOR_RULES: dict[str, dict] = {
    "红鸾": {"base_by": "year_branch_map", "map_start": "卯", "note": "卯起子年逆数至生年支"},
    "天喜": {"base_by": "hongluan_opposite", "note": "红鸾对宫"},
    "天姚": {"base_by": "month_from_丑", "dir": "forward", "note": "丑起正月顺数至生月"},
    "天刑": {"base_by": "month_from_酉", "dir": "forward", "note": "酉起正月顺数至生月"},
    "孤辰": {"base_by": "year_triad_孤", "note": "年支三合前一位"},
    "寡宿": {"base_by": "year_triad_寡", "note": "年支三合后一位"},
    "华盖": {"base_by": "year_triad_墓", "note": "年支三合墓库"},
    "天哭": {"base_by": "year_from_午", "dir": "backward", "note": "午起子年逆数"},
    "天虚": {"base_by": "year_from_午", "dir": "forward", "note": "午起子年顺数"},
    "天官": {"base_by": "stem_table", "note": "年干查表"},
    "天福": {"base_by": "stem_table", "note": "年干查表"},
    "天寿": {"base_by": "ming_plus_hour", "note": "命宫起生时顺数（简化实现待专业表校验）"},
    "天才": {"base_by": "ming_plus_hour", "note": "命宫起生时顺数"},
    "天月": {"base_by": "month_table", "note": "生月查表"},
    "解神": {"base_by": "month_table", "note": "生月查表"},
    "天巫": {"base_by": "month_table", "note": "生月查表"},
}

# 孤辰寡宿华盖（三合）
TRIAD = {
    "寅": ("巳", "丑", "戌"),  # 孤, 寡, 华盖(墓)
    "午": ("巳", "丑", "戌"),
    "戌": ("巳", "丑", "戌"),
    "亥": ("寅", "戌", "未"),
    "卯": ("寅", "戌", "未"),
    "未": ("寅", "戌", "未"),
    "巳": ("申", "辰", "丑"),
    "酉": ("申", "辰", "丑"),
    "丑": ("申", "辰", "丑"),
    "申": ("亥", "未", "辰"),
    "子": ("亥", "未", "辰"),
    "辰": ("亥", "未", "辰"),
}

# 红鸾：卯起子年逆
def _hongluan(year_branch: str) -> str:
    # 子年红鸾在卯；自卯逆数到年支序
    year_order = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
    yi = year_order.index(year_branch)
    return EARTHLY_BRANCHES[(EARTHLY_BRANCHES.index("卯") - yi) % 12]


STEM_TIAN_GUAN = {
    "甲": "未", "乙": "辰", "丙": "巳", "丁": "寅", "戊": "卯",
    "己": "酉", "庚": "亥", "辛": "酉", "壬": "戌", "癸": "午",
}
STEM_TIAN_FU = {
    "甲": "酉", "乙": "申", "丙": "子", "丁": "亥", "戊": "卯",
    "己": "寅", "庚": "午", "辛": "巳", "壬": "午", "癸": "巳",
}

MONTH_TIAN_YUE = ["戌", "巳", "辰", "寅", "未", "卯", "亥", "未", "寅", "午", "戌", "寅"]
MONTH_JIE_SHEN = ["申", "申", "戌", "戌", "子", "子", "寅", "寅", "辰", "辰", "午", "午"]
MONTH_TIAN_WU = ["巳", "卯", "午", "寅", "午", "巳", "申", "酉", "亥", "酉", "亥", "寅"]


def place_minor_stars(
    *,
    lunar_month: int,
    hour_index: int,
    year_stem: str,
    year_branch: str,
    ming_branch: str,
    trace: RuleTrace | None = None,
) -> dict[str, dict]:
    out: dict[str, dict] = {}

    def put(name: str, branch: str, rule: str) -> None:
        if not branch:
            return
        out[name] = {"branch": branch, "rule": rule, "tier": "丙级"}
        if trace is not None:
            trace.add(
                step=f"minor.{name}",
                rule=rule,
                inputs={
                    "lunar_month": lunar_month,
                    "year_stem": year_stem,
                    "year_branch": year_branch,
                    "ming_branch": ming_branch,
                },
                outputs={"branch": branch},
                source="ziwei_classical.stars.minor_stars",
            )

    hl = _hongluan(year_branch)
    put("红鸾", hl, MINOR_RULES["红鸾"]["note"])
    put("天喜", EARTHLY_BRANCHES[(EARTHLY_BRANCHES.index(hl) + 6) % 12], MINOR_RULES["天喜"]["note"])

    put(
        "天姚",
        EARTHLY_BRANCHES[(EARTHLY_BRANCHES.index("丑") + lunar_month - 1) % 12],
        MINOR_RULES["天姚"]["note"],
    )
    put(
        "天刑",
        EARTHLY_BRANCHES[(EARTHLY_BRANCHES.index("酉") + lunar_month - 1) % 12],
        MINOR_RULES["天刑"]["note"],
    )

    triad = TRIAD.get(year_branch)
    if triad:
        put("孤辰", triad[0], MINOR_RULES["孤辰"]["note"])
        put("寡宿", triad[1], MINOR_RULES["寡宿"]["note"])
        put("华盖", triad[2], MINOR_RULES["华盖"]["note"])

    yi = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"].index(year_branch)
    put("天哭", EARTHLY_BRANCHES[(EARTHLY_BRANCHES.index("午") - yi) % 12], MINOR_RULES["天哭"]["note"])
    put("天虚", EARTHLY_BRANCHES[(EARTHLY_BRANCHES.index("午") + yi) % 12], MINOR_RULES["天虚"]["note"])

    put("天官", STEM_TIAN_GUAN.get(year_stem, ""), MINOR_RULES["天官"]["note"])
    put("天福", STEM_TIAN_FU.get(year_stem, ""), MINOR_RULES["天福"]["note"])

    ming_idx = EARTHLY_BRANCHES.index(ming_branch)
    put(
        "天寿",
        EARTHLY_BRANCHES[(ming_idx + hour_index) % 12],
        MINOR_RULES["天寿"]["note"],
    )
    put(
        "天才",
        EARTHLY_BRANCHES[(ming_idx + hour_index) % 12],
        MINOR_RULES["天才"]["note"],
    )

    mi = max(1, min(12, lunar_month)) - 1
    put("天月", MONTH_TIAN_YUE[mi], MINOR_RULES["天月"]["note"])
    put("解神", MONTH_JIE_SHEN[mi], MINOR_RULES["解神"]["note"])
    put("天巫", MONTH_TIAN_WU[mi], MINOR_RULES["天巫"]["note"])

    return out
