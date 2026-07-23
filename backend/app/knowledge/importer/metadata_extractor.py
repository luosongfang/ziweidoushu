"""Metadata tag extraction — keyword tagging only, no interpretation."""

from __future__ import annotations

STAR_KEYWORDS: list[str] = [
    "紫微",
    "天府",
    "天机",
    "太阳",
    "武曲",
    "七杀",
    "破军",
    "廉贞",
    "贪狼",
    "巨门",
    "天相",
    "天梁",
    "太阴",
    "天同",
]

PALACE_KEYWORDS: list[str] = [
    "命宫",
    "兄弟",
    "夫妻",
    "财帛",
    "官禄",
    "迁移",
    "疾厄",
    "福德",
    "田宅",
    "父母",
    "子女",
    "仆役",
]

PATTERN_KEYWORDS: list[str] = [
    "紫府",
    "杀破狼",
    "机月同梁",
]

FOUR_TRANSFORM_KEYWORDS: list[str] = [
    "化禄",
    "化权",
    "化科",
    "化忌",
]

LIFE_QUESTION_KEYWORDS: dict[str, list[str]] = {
    "career": ["事业", "官禄", "职业", "工作"],
    "wealth": ["财帛", "财富", "钱财", "禄"],
    "relationship": ["夫妻", "感情", "婚姻", "桃花"],
    "growth": ["福德", "性格", "心性", "修心"],
}


def extract_tags(content: str) -> dict[str, list[str]]:
    """Detect keyword tags only. Does not rewrite or explain text."""
    text = content or ""
    stars = [k for k in STAR_KEYWORDS if k in text]
    palaces = [k for k in PALACE_KEYWORDS if k in text]
    patterns = [k for k in PATTERN_KEYWORDS if k in text]
    transforms = [k for k in FOUR_TRANSFORM_KEYWORDS if k in text]
    life_tags: list[str] = []
    for tag, kws in LIFE_QUESTION_KEYWORDS.items():
        if any(k in text for k in kws):
            life_tags.append(tag)
    keywords = list(dict.fromkeys(stars + palaces + patterns + transforms))
    return {
        "keywords": keywords,
        "star_tags": stars,
        "palace_tags": palaces,
        "pattern_tags": patterns,
        "life_question_tags": life_tags,
        "four_transform_tags": transforms,
    }


def infer_relation_types(tags: dict[str, list[str]]) -> list[str]:
    """Suggest relation_type labels from tags (no graph linking in Phase1 required)."""
    types: list[str] = []
    if tags.get("star_tags"):
        types.append("star_meaning")
    if tags.get("palace_tags"):
        types.append("palace_meaning")
    if tags.get("pattern_tags"):
        types.append("combination")
    if tags.get("four_transform_tags"):
        types.append("four_transform")
    life = set(tags.get("life_question_tags") or [])
    if "career" in life:
        types.append("career")
    if "wealth" in life:
        types.append("wealth")
    if "relationship" in life:
        types.append("relationship")
    return types
