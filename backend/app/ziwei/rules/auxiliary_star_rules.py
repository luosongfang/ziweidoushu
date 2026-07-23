"""辅助杂曜规则 — 数据化传统安星表（三合派）。"""

from __future__ import annotations

RULES_VERSION = "2026.07.23"
SCHOOL = "sanhe"
SOURCE = "sanhe_traditional"

AUXILIARY_STAR_NAMES: tuple[str, ...] = (
    "天刑", "天姚", "红鸾", "天喜", "孤辰", "寡宿", "华盖", "天哭", "天虚",
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


def _huagai_group(year_branch: str) -> str:
    for group, branch in HUAGAI_GROUP_BRANCHES.items():
        if year_branch in group:
            return branch
    return ""


def generate_auxiliary_star_rules() -> list[dict]:
    """生成 auxiliary_star_rules 种子（与 migration 021 一致）。"""
    rows: list[dict] = [
        {
            "star_name": "红鸾",
            "category": "auxiliary",
            "rule_type": "branch_offset",
            "rule_expression": {
                "base_branch": "卯",
                "direction": "backward",
                "offset": 0,
                "by": "year_branch",
            },
            "source": SOURCE,
            "enabled": True,
            "school": SCHOOL,
            "version": RULES_VERSION,
        },
        {
            "star_name": "天喜",
            "category": "auxiliary",
            "rule_type": "opposite_branch",
            "rule_expression": {"base_star": "红鸾", "offset": 6},
            "source": SOURCE,
            "enabled": True,
            "school": SCHOOL,
            "version": RULES_VERSION,
        },
        {
            "star_name": "天姚",
            "category": "auxiliary",
            "rule_type": "branch_offset",
            "rule_expression": {
                "base_branch": "丑",
                "direction": "forward",
                "offset": 0,
                "by": "lunar_month",
            },
            "source": SOURCE,
            "enabled": True,
            "school": SCHOOL,
            "version": RULES_VERSION,
        },
        {
            "star_name": "天刑",
            "category": "auxiliary",
            "rule_type": "branch_offset",
            "rule_expression": {
                "base_branch": "酉",
                "direction": "backward",
                "offset": 0,
                "by": "year_branch",
            },
            "source": SOURCE,
            "enabled": True,
            "school": SCHOOL,
            "version": RULES_VERSION,
        },
        {
            "star_name": "天虚",
            "category": "auxiliary",
            "rule_type": "branch_offset",
            "rule_expression": {
                "base_branch": "午",
                "direction": "backward",
                "offset": 0,
                "by": "year_branch",
            },
            "source": SOURCE,
            "enabled": True,
            "school": SCHOOL,
            "version": RULES_VERSION,
        },
        {
            "star_name": "天哭",
            "category": "auxiliary",
            "rule_type": "branch_offset",
            "rule_expression": {
                "base_branch": "午",
                "direction": "forward",
                "offset": 0,
                "by": "year_branch",
            },
            "source": SOURCE,
            "enabled": True,
            "school": SCHOOL,
            "version": RULES_VERSION,
        },
        {
            "star_name": "孤辰",
            "category": "auxiliary",
            "rule_type": "branch_group",
            "rule_expression": {
                "by": "year_branch",
                "mapping": GUChen_GROUP_BRANCHES,
            },
            "source": SOURCE,
            "enabled": True,
            "school": SCHOOL,
            "version": RULES_VERSION,
        },
        {
            "star_name": "寡宿",
            "category": "auxiliary",
            "rule_type": "branch_group",
            "rule_expression": {
                "by": "year_branch",
                "mapping": GuASu_GROUP_BRANCHES,
            },
            "source": SOURCE,
            "enabled": True,
            "school": SCHOOL,
            "version": RULES_VERSION,
        },
        {
            "star_name": "华盖",
            "category": "auxiliary",
            "rule_type": "branch_group",
            "rule_expression": {
                "by": "year_branch",
                "mapping": HUAGAI_GROUP_BRANCHES,
            },
            "source": SOURCE,
            "enabled": True,
            "school": SCHOOL,
            "version": RULES_VERSION,
        },
    ]
    return rows
