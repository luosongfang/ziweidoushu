"""Entity extractor — keyword scan of knowledge_chunks (no interpretation)."""

from __future__ import annotations

from collections import Counter
from typing import Any, Iterable

from app.knowledge.graph.graph_models import GraphEntity

# 十四主星
STARS: list[str] = [
    "紫微",
    "天府",
    "天机",
    "太阳",
    "武曲",
    "天同",
    "廉贞",
    "天相",
    "天梁",
    "巨门",
    "七杀",
    "破军",
    "贪狼",
    "太阴",
]

# 十二宫（命宫写全称，其余可用简称命中）
PALACES: list[tuple[str, list[str]]] = [
    ("命宫", ["命宫"]),
    ("兄弟宫", ["兄弟宫", "兄弟"]),
    ("夫妻宫", ["夫妻宫", "夫妻"]),
    ("财帛宫", ["财帛宫", "财帛"]),
    ("官禄宫", ["官禄宫", "官禄"]),
    ("迁移宫", ["迁移宫", "迁移"]),
    ("疾厄宫", ["疾厄宫", "疾厄"]),
    ("福德宫", ["福德宫", "福德"]),
    ("田宅宫", ["田宅宫", "田宅"]),
    ("父母宫", ["父母宫", "父母"]),
    ("子女宫", ["子女宫", "子女"]),
    ("仆役宫", ["仆役宫", "仆役"]),
]

FOUR_TRANSFORMS: list[str] = ["化禄", "化权", "化科", "化忌"]

PATTERNS: list[tuple[str, list[str]]] = [
    ("紫府同宫", ["紫府同宫", "紫府朝垣", "紫府"]),
    ("杀破狼", ["杀破狼"]),
    ("机月同梁", ["机月同梁"]),
]

LIFE_SCENES: list[tuple[str, list[str]]] = [
    ("事业", ["事业", "职业", "工作", "官禄"]),
    ("财富", ["财富", "钱财", "财帛", "理财"]),
    ("感情", ["感情", "婚姻", "夫妻", "桃花"]),
    ("成长", ["成长", "心性", "性格", "福德"]),
]

CONCEPTS: list[str] = [
    "星曜含义",
    "宫位含义",
    "格局组合",
    "四化影响",
    "三方四正",
]


def canonical_entities() -> list[GraphEntity]:
    """Seed catalog of graph entities (tag-only, no generated lore)."""
    out: list[GraphEntity] = []
    for name in STARS:
        out.append(
            GraphEntity(
                name=name,
                entity_type="star",
                description="紫微十四主星实体",
                metadata={"catalog": "fourteen_main"},
            )
        )
    for name, _ in PALACES:
        out.append(
            GraphEntity(
                name=name,
                entity_type="palace",
                description="十二宫实体",
                metadata={"catalog": "twelve_palaces"},
            )
        )
    for name in FOUR_TRANSFORMS:
        out.append(
            GraphEntity(
                name=name,
                entity_type="four_transform",
                description="四化实体",
                metadata={"catalog": "sihua"},
            )
        )
    for name, aliases in PATTERNS:
        out.append(
            GraphEntity(
                name=name,
                entity_type="pattern",
                description="格局实体",
                metadata={"aliases": aliases},
            )
        )
    for name, aliases in LIFE_SCENES:
        out.append(
            GraphEntity(
                name=name,
                entity_type="life_scene",
                description="人生场景实体",
                metadata={"aliases": aliases},
            )
        )
    for name in CONCEPTS:
        out.append(
            GraphEntity(
                name=name,
                entity_type="concept",
                description="图谱概念锚点",
                metadata={"catalog": "concept"},
            )
        )
    return out


def detect_in_text(content: str) -> dict[str, list[str]]:
    """Return entity names found in raw text (keyword hit only)."""
    text = content or ""
    stars = [s for s in STARS if s in text]
    palaces: list[str] = []
    for name, aliases in PALACES:
        if any(a in text for a in aliases):
            palaces.append(name)
    transforms = [t for t in FOUR_TRANSFORMS if t in text]
    patterns: list[str] = []
    for name, aliases in PATTERNS:
        if any(a in text for a in aliases):
            patterns.append(name)
    scenes: list[str] = []
    for name, aliases in LIFE_SCENES:
        if any(a in text for a in aliases):
            scenes.append(name)
    return {
        "star": stars,
        "palace": palaces,
        "four_transform": transforms,
        "pattern": patterns,
        "life_scene": scenes,
    }


def aggregate_chunk_mentions(chunks: Iterable[dict[str, Any]]) -> dict[str, Counter]:
    """Count entity mentions across chunks by type."""
    counters: dict[str, Counter] = {
        "star": Counter(),
        "palace": Counter(),
        "four_transform": Counter(),
        "pattern": Counter(),
        "life_scene": Counter(),
    }
    for ch in chunks:
        found = detect_in_text(ch.get("content") or "")
        # also honor precomputed tags when present
        for s in ch.get("star_tags") or []:
            if s in STARS:
                found["star"] = list(dict.fromkeys(found["star"] + [s]))
        for p in ch.get("palace_tags") or []:
            for name, aliases in PALACES:
                if p == name or p in aliases:
                    found["palace"] = list(dict.fromkeys(found["palace"] + [name]))
        for t in found:
            for name in found[t]:
                counters[t][name] += 1
    return counters
