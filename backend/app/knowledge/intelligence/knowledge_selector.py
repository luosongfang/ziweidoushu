"""Knowledge selector — retrieve chunks by theory route tags (no LLM)."""

from __future__ import annotations

import json
from functools import lru_cache
from typing import Any

from sqlalchemy import text

from app.database.database import engine


def _norm_ref(ref: Any) -> dict[str, Any]:
    if isinstance(ref, dict):
        return ref
    if isinstance(ref, str):
        try:
            return json.loads(ref)
        except Exception:
            return {}
    return {}


def _overlap(tags: list[str], wanted: set[str]) -> int:
    return sum(1 for t in tags if t in wanted)


@lru_cache(maxsize=1)
def _cached_knowledge_chunks() -> tuple[dict[str, Any], ...]:
    """全库 chunk 候选集（进程内缓存，避免每次分析新建连接）。"""
    try:
        with engine.connect() as conn:
            conn.execute(text("SET statement_timeout = '30s'"))
            rows = conn.execute(
                text(
                    """
                    SELECT id, content, page_number, source_reference,
                           star_tags, palace_tags, pattern_tags, keywords
                    FROM public.knowledge_chunks
                    WHERE content IS NOT NULL AND length(content) > 20
                    LIMIT 200
                    """
                )
            ).mappings().all()
            return tuple(dict(r) for r in rows)
    except Exception:
        return ()


class KnowledgeSelector:
    """Select related knowledge_chunks for a theory route."""

    @classmethod
    def warm_cache(cls) -> None:
        _cached_knowledge_chunks()

    @classmethod
    def select(
        cls,
        route: dict[str, Any],
        *,
        limit: int = 12,
        chart_stars: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        stars = list(dict.fromkeys((route.get("required_stars") or []) + (chart_stars or [])))
        palaces = list(route.get("required_palaces") or [])
        patterns = list(route.get("required_patterns") or [])
        palace_tags: list[str] = []
        for p in palaces:
            palace_tags.append(p)
            if p.endswith("宫") and len(p) > 1:
                palace_tags.append(p[:-1])
        wanted = set(stars + palace_tags + patterns)

        candidates = list(_cached_knowledge_chunks())
        if not candidates:
            return []

        scored: list[tuple[int, dict[str, Any]]] = []
        for r in candidates:
            tags = list(r.get("star_tags") or []) + list(r.get("palace_tags") or [])
            tags += list(r.get("pattern_tags") or []) + list(r.get("keywords") or [])
            score = _overlap([str(t) for t in tags], wanted) if wanted else 1
            if wanted and score <= 0:
                # soft match on content keywords
                content = r.get("content") or ""
                score = sum(1 for w in wanted if w and w in content)
            if score > 0 or not wanted:
                scored.append((score, r))
        scored.sort(key=lambda x: x[0], reverse=True)

        out: list[dict[str, Any]] = []
        for _score, r in scored[:limit]:
            ref = _norm_ref(r.get("source_reference"))
            out.append(
                {
                    "chunk_id": str(r.get("id")),
                    "content": (r.get("content") or "")[:500],
                    "page_number": r.get("page_number"),
                    "book_source": ref.get("book") or "",
                    "chapter": ref.get("chapter") or "",
                    "citation": {
                        "book": ref.get("book") or "",
                        "page": ref.get("page") or r.get("page_number"),
                        "chapter": ref.get("chapter") or "",
                    },
                    "star_tags": list(r.get("star_tags") or []),
                    "palace_tags": list(r.get("palace_tags") or []),
                    "pattern_tags": list(r.get("pattern_tags") or []),
                }
            )
        return out
