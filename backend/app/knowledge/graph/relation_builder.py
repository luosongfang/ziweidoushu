"""Relation builder — structural edges from co-occurrence and catalogs (no LLM)."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from app.knowledge.graph.entity_extractor import (
    detect_in_text,
)
from app.knowledge.graph.graph_models import GraphEdge

# Pattern membership (static catalog)
PATTERN_STARS: dict[str, list[str]] = {
    "紫府同宫": ["紫微", "天府"],
    "杀破狼": ["七杀", "破军", "贪狼"],
    "机月同梁": ["天机", "太阴", "天同", "天梁"],
}

# Simplified three-harmony / 三方四正 pairs for career axis
THREE_HARMONY_GROUPS: list[list[str]] = [
    ["命宫", "财帛宫", "官禄宫", "迁移宫"],
    ["夫妻宫", "迁移宫", "福德宫", "官禄宫"],
    ["兄弟宫", "疾厄宫", "田宅宫", "仆役宫"],
]

PALACE_LIFE: dict[str, str] = {
    "官禄宫": "事业",
    "财帛宫": "财富",
    "夫妻宫": "感情",
    "福德宫": "成长",
    "命宫": "成长",
}


def build_catalog_edges() -> list[GraphEdge]:
    """Static structural relations independent of chunk scan."""
    edges: list[GraphEdge] = []

    # star → meaning concept
    for star in [
        "紫微", "天府", "天机", "太阳", "武曲", "天同", "廉贞",
        "天相", "天梁", "巨门", "七杀", "破军", "贪狼", "太阴",
    ]:
        edges.append(
            GraphEdge(
                source_name=star,
                source_type="star",
                target_name="星曜含义",
                target_type="concept",
                relation_type="meaning",
                weight=1.0,
                metadata={"rule": "star_to_meaning"},
            )
        )

    # palace → meaning
    for palace in [
        "命宫", "兄弟宫", "夫妻宫", "财帛宫", "官禄宫", "迁移宫",
        "疾厄宫", "福德宫", "田宅宫", "父母宫", "子女宫", "仆役宫",
    ]:
        edges.append(
            GraphEdge(
                source_name=palace,
                source_type="palace",
                target_name="宫位含义",
                target_type="concept",
                relation_type="meaning",
                weight=1.0,
                metadata={"rule": "palace_to_meaning"},
            )
        )

    # four transform → influence concept
    for tf in ["化禄", "化权", "化科", "化忌"]:
        edges.append(
            GraphEdge(
                source_name=tf,
                source_type="four_transform",
                target_name="四化影响",
                target_type="concept",
                relation_type="four_transform",
                weight=1.0,
                metadata={"rule": "sihua_to_influence"},
            )
        )

    # pattern membership combination
    for pattern, stars in PATTERN_STARS.items():
        edges.append(
            GraphEdge(
                source_name=pattern,
                source_type="pattern",
                target_name="格局组合",
                target_type="concept",
                relation_type="combination",
                weight=1.0,
                metadata={"rule": "pattern_to_concept"},
            )
        )
        for star in stars:
            edges.append(
                GraphEdge(
                    source_name=star,
                    source_type="star",
                    target_name=pattern,
                    target_type="pattern",
                    relation_type="combination",
                    weight=1.0,
                    metadata={"rule": "star_in_pattern"},
                )
            )

    # palace belongs to life scene
    for palace, scene in PALACE_LIFE.items():
        edges.append(
            GraphEdge(
                source_name=palace,
                source_type="palace",
                target_name=scene,
                target_type="life_scene",
                relation_type="belongs",
                weight=1.0,
                metadata={"rule": "palace_life_scene"},
            )
        )

    # three harmony
    for group in THREE_HARMONY_GROUPS:
        for i, a in enumerate(group):
            for b in group[i + 1 :]:
                edges.append(
                    GraphEdge(
                        source_name=a,
                        source_type="palace",
                        target_name=b,
                        target_type="palace",
                        relation_type="three_harmony",
                        weight=1.0,
                        metadata={"rule": "sanfang_sizheng", "group": group},
                    )
                )
                edges.append(
                    GraphEdge(
                        source_name=a,
                        source_type="palace",
                        target_name="三方四正",
                        target_type="concept",
                        relation_type="three_harmony",
                        weight=0.5,
                        metadata={"rule": "palace_to_sanfang_concept"},
                    )
                )

    return edges


def build_chunk_edges(chunk: dict[str, Any]) -> list[GraphEdge]:
    """Co-occurrence edges for one chunk; attach source_chunk_id for citation."""
    content = chunk.get("content") or ""
    found = detect_in_text(content) if content else {
        "star": [],
        "palace": [],
        "four_transform": [],
        "pattern": [],
        "life_scene": [],
    }
    # Prefer Phase1 tags when present
    tag_stars = [s for s in (chunk.get("star_tags") or []) if isinstance(s, str)]
    tag_palaces_raw = [p for p in (chunk.get("palace_tags") or []) if isinstance(p, str)]
    tag_patterns = [p for p in (chunk.get("pattern_tags") or []) if isinstance(p, str)]
    life_tags = [x for x in (chunk.get("life_question_tags") or []) if isinstance(x, str)]

    stars = list(dict.fromkeys(found["star"] + tag_stars))
    # normalize palace names
    palace_alias = {
        "命宫": "命宫",
        "兄弟": "兄弟宫",
        "兄弟宫": "兄弟宫",
        "夫妻": "夫妻宫",
        "夫妻宫": "夫妻宫",
        "财帛": "财帛宫",
        "财帛宫": "财帛宫",
        "官禄": "官禄宫",
        "官禄宫": "官禄宫",
        "迁移": "迁移宫",
        "迁移宫": "迁移宫",
        "疾厄": "疾厄宫",
        "疾厄宫": "疾厄宫",
        "福德": "福德宫",
        "福德宫": "福德宫",
        "田宅": "田宅宫",
        "田宅宫": "田宅宫",
        "父母": "父母宫",
        "父母宫": "父母宫",
        "子女": "子女宫",
        "子女宫": "子女宫",
        "仆役": "仆役宫",
        "仆役宫": "仆役宫",
    }
    palaces = list(
        dict.fromkeys(
            found["palace"]
            + [palace_alias[p] for p in tag_palaces_raw if p in palace_alias]
        )
    )
    # pattern alias normalize
    pattern_alias = {
        "紫府": "紫府同宫",
        "紫府同宫": "紫府同宫",
        "紫府朝垣": "紫府同宫",
        "杀破狼": "杀破狼",
        "机月同梁": "机月同梁",
    }
    patterns = list(
        dict.fromkeys(
            found["pattern"]
            + [pattern_alias[p] for p in tag_patterns if p in pattern_alias]
        )
    )
    transforms = found["four_transform"]
    scene_map = {
        "career": "事业",
        "wealth": "财富",
        "relationship": "感情",
        "growth": "成长",
    }
    scenes = list(
        dict.fromkeys(
            found["life_scene"] + [scene_map[x] for x in life_tags if x in scene_map]
        )
    )

    chunk_id = str(chunk["id"]) if chunk.get("id") is not None else None
    edges: list[GraphEdge] = []

    # star ↔ palace influence / belongs
    for star in stars:
        for palace in palaces:
            edges.append(
                GraphEdge(
                    source_name=star,
                    source_type="star",
                    target_name=palace,
                    target_type="palace",
                    relation_type="belongs",
                    weight=1.0,
                    source_chunk_id=chunk_id,
                    metadata={"rule": "cooccur_star_palace"},
                )
            )
            edges.append(
                GraphEdge(
                    source_name=star,
                    source_type="star",
                    target_name=palace,
                    target_type="palace",
                    relation_type="influence",
                    weight=0.8,
                    source_chunk_id=chunk_id,
                    metadata={"rule": "cooccur_star_palace_influence"},
                )
            )

    # star combinations (pairwise)
    for i, a in enumerate(stars):
        for b in stars[i + 1 :]:
            edges.append(
                GraphEdge(
                    source_name=a,
                    source_type="star",
                    target_name=b,
                    target_type="star",
                    relation_type="combination",
                    weight=1.0,
                    source_chunk_id=chunk_id,
                    metadata={"rule": "cooccur_stars"},
                )
            )

    # four transform on stars / palaces
    for tf in transforms:
        for star in stars:
            edges.append(
                GraphEdge(
                    source_name=tf,
                    source_type="four_transform",
                    target_name=star,
                    target_type="star",
                    relation_type="four_transform",
                    weight=1.0,
                    source_chunk_id=chunk_id,
                    metadata={"rule": "sihua_star"},
                )
            )
        for palace in palaces:
            edges.append(
                GraphEdge(
                    source_name=tf,
                    source_type="four_transform",
                    target_name=palace,
                    target_type="palace",
                    relation_type="influence",
                    weight=0.9,
                    source_chunk_id=chunk_id,
                    metadata={"rule": "sihua_palace"},
                )
            )

    # pattern evidence from chunk
    for pattern in patterns:
        for star in PATTERN_STARS.get(pattern, []):
            if star not in stars:
                continue
            edges.append(
                GraphEdge(
                    source_name=star,
                    source_type="star",
                    target_name=pattern,
                    target_type="pattern",
                    relation_type="combination",
                    weight=1.2,
                    source_chunk_id=chunk_id,
                    metadata={"rule": "pattern_evidence"},
                )
            )

    # life scene links
    for scene in scenes:
        rel = {
            "事业": "career",
            "财富": "wealth",
            "感情": "relationship",
            "成长": "career",
        }.get(scene, "career")
        for star in stars:
            edges.append(
                GraphEdge(
                    source_name=star,
                    source_type="star",
                    target_name=scene,
                    target_type="life_scene",
                    relation_type=rel if rel in {"career", "wealth", "relationship"} else "influence",
                    weight=0.7,
                    source_chunk_id=chunk_id,
                    metadata={"rule": "star_life_scene"},
                )
            )
        for palace in palaces:
            edges.append(
                GraphEdge(
                    source_name=palace,
                    source_type="palace",
                    target_name=scene,
                    target_type="life_scene",
                    relation_type=rel if rel in {"career", "wealth", "relationship"} else "belongs",
                    weight=0.7,
                    source_chunk_id=chunk_id,
                    metadata={"rule": "palace_life_scene_chunk"},
                )
            )

    return edges


def aggregate_edges(edges: list[GraphEdge], *, keep_chunk_edges: bool = True) -> list[GraphEdge]:
    """
    Merge duplicate catalog edges by summing weights.
    Chunk-linked edges are kept distinct per chunk for citation integrity.
    """
    catalog: dict[tuple, GraphEdge] = {}
    chunked: list[GraphEdge] = []
    for e in edges:
        if e.source_chunk_id and keep_chunk_edges:
            chunked.append(e)
            continue
        key = (
            e.source_name,
            e.source_type,
            e.target_name,
            e.target_type,
            e.relation_type,
        )
        if key in catalog:
            catalog[key].weight += e.weight
        else:
            catalog[key] = e.model_copy(deep=True)
    return list(catalog.values()) + chunked
