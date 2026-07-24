"""辅助杂曜规则 — 数据化传统安星表（三合派）。含 V1.3 增补星。"""

from __future__ import annotations

RULES_VERSION = "2026.07.24"
SCHOOL = "sanhe"
SOURCE = "sanhe_traditional"

AUXILIARY_STAR_NAMES: tuple[str, ...] = (
    "天刑", "天姚", "红鸾", "天喜", "孤辰", "寡宿", "华盖", "天哭", "天虚",
    "咸池", "天官", "天福", "天寿", "天才", "天月",
)

# 年支三合组 → 目标地支（孤辰 / 寡宿 / 华盖）
_YEAR_BRANCH_GROUPS: dict[str, str] = {
    "寅": "寅卯辰", "卯": "寅卯辰", "辰": "寅卯辰",
    "巳": "巳午未", "午": "巳午未", "未": "巳午未",
    "申": "申酉戌", "酉": "申酉戌", "戌": "申酉戌",
    "亥": "亥子丑", "子": "亥子丑", "丑": "亥子丑",
}

GUChen_GROUP_BRANCHES: dict[str, str] = {
    "寅卯辰": "巳",
    "巳午未": "申",
    "申酉戌": "亥",
    "亥子丑": "寅",
}

GuASu_GROUP_BRANCHES: dict[str, str] = {
    "寅卯辰": "丑",
    "巳午未": "辰",
    "申酉戌": "未",
    "亥子丑": "戌",
}

HUAGAI_GROUP_BRANCHES: dict[str, str] = {
    "寅午戌": "戌",
    "申子辰": "辰",
    "巳酉丑": "丑",
    "亥卯未": "未",
}

# 咸池：年支三合桃花位
XIANCHI_GROUP_BRANCHES: dict[str, str] = {
    "寅午戌": "卯",
    "申子辰": "酉",
    "巳酉丑": "午",
    "亥卯未": "子",
}

# 天官：年干查表（三合派常用表）
TIANGUAN_BY_STEM: dict[str, str] = {
    "甲": "未", "乙": "辰", "丙": "巳", "丁": "寅", "戊": "卯",
    "己": "酉", "庚": "亥", "辛": "申", "壬": "酉", "癸": "未",
}

# 天福：年干查表
TIANFU_MINOR_BY_STEM: dict[str, str] = {
    "甲": "酉", "乙": "申", "丙": "子", "丁": "亥", "戊": "卯",
    "己": "寅", "庚": "午", "辛": "巳", "壬": "午", "癸": "巳",
}


def _rule(
    star_name: str,
    rule_type: str,
    rule_expression: dict,
    *,
    category: str = "auxiliary",
) -> dict:
    return {
        "star_name": star_name,
        "category": category,
        "rule_type": rule_type,
        "rule_expression": rule_expression,
        "source": SOURCE,
        "enabled": True,
        "school": SCHOOL,
        "version": RULES_VERSION,
    }


def generate_auxiliary_star_rules() -> list[dict]:
    """生成 auxiliary_star_rules 种子（含 V1.3 增补）。"""
    rows: list[dict] = [
        _rule(
            "红鸾",
            "branch_offset",
            {"base_branch": "卯", "direction": "backward", "offset": 0, "by": "year_branch"},
        ),
        _rule("天喜", "opposite_branch", {"base_star": "红鸾", "offset": 6}),
        _rule(
            "天姚",
            "branch_offset",
            {"base_branch": "丑", "direction": "forward", "offset": 0, "by": "lunar_month"},
        ),
        _rule(
            "天刑",
            "branch_offset",
            {"base_branch": "酉", "direction": "backward", "offset": 0, "by": "year_branch"},
        ),
        _rule(
            "天虚",
            "branch_offset",
            {"base_branch": "午", "direction": "backward", "offset": 0, "by": "year_branch"},
        ),
        _rule(
            "天哭",
            "branch_offset",
            {"base_branch": "午", "direction": "forward", "offset": 0, "by": "year_branch"},
        ),
        _rule(
            "孤辰",
            "branch_group",
            {"by": "year_branch", "mapping": GUChen_GROUP_BRANCHES},
        ),
        _rule(
            "寡宿",
            "branch_group",
            {"by": "year_branch", "mapping": GuASu_GROUP_BRANCHES},
        ),
        _rule(
            "华盖",
            "branch_group",
            {"by": "year_branch", "mapping": HUAGAI_GROUP_BRANCHES},
        ),
        # —— V1.3 增补 ——
        _rule(
            "咸池",
            "branch_group",
            {"by": "year_branch", "mapping": XIANCHI_GROUP_BRANCHES},
            category="peach",
        ),
        _rule(
            "天官",
            "stem_lookup",
            {"by": "year_stem", "mapping": TIANGUAN_BY_STEM},
        ),
        _rule(
            "天福",
            "stem_lookup",
            {"by": "year_stem", "mapping": TIANFU_MINOR_BY_STEM},
        ),
        _rule(
            "天寿",
            "branch_offset",
            {
                "base_by": "year_branch",
                "direction": "forward",
                "offset": 0,
                "by": "lunar_month",
            },
        ),
        _rule(
            "天才",
            "ming_to_year_branch",
            {"description": "命宫起子，顺数至生年支"},
        ),
        _rule(
            "天月",
            "branch_offset",
            {"base_branch": "戌", "direction": "backward", "offset": 0, "by": "lunar_month"},
        ),
    ]
    return rows
