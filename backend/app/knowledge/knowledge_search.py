"""KnowledgeSearch — 关键词 / 分类检索（预留 RAG）。"""

from __future__ import annotations

from typing import Any

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.knowledge.knowledge_models import (
    PalaceKnowledge,
    StarsKnowledge,
    TheoryKnowledge,
    ZiweiPattern,
)


class KnowledgeSearch:
    """支持关键词搜索、分类搜索；未来可扩展向量检索。"""

    @classmethod
    def search_stars(cls, keyword: str, limit: int = 20) -> list[dict[str, Any]]:
        db = SessionLocal()
        try:
            like = f"%{keyword}%"
            rows = db.scalars(
                select(StarsKnowledge)
                .where(
                    or_(
                        StarsKnowledge.star_name.ilike(like),
                        StarsKnowledge.basic_meaning.ilike(like),
                        StarsKnowledge.traditional_description.ilike(like),
                    )
                )
                .limit(limit)
            ).all()
            return [
                {
                    "star_name": r.star_name,
                    "category": r.category,
                    "basic_meaning": r.basic_meaning,
                    "traditional_description": r.traditional_description,
                }
                for r in rows
            ]
        finally:
            db.close()

    @classmethod
    def search_by_category(cls, category: str, limit: int = 50) -> list[dict[str, Any]]:
        """category: stars | palaces | patterns | theory"""
        db = SessionLocal()
        try:
            if category == "stars":
                rows = db.scalars(select(StarsKnowledge).limit(limit)).all()
                return [{"type": "star", "name": r.star_name, "data": r.basic_meaning} for r in rows]
            if category == "palaces":
                rows = db.scalars(select(PalaceKnowledge).limit(limit)).all()
                return [
                    {"type": "palace", "name": r.palace_name, "data": r.basic_meaning} for r in rows
                ]
            if category == "patterns":
                rows = db.scalars(select(ZiweiPattern).limit(limit)).all()
                return [
                    {"type": "pattern", "name": r.pattern_name, "data": r.traditional_meaning}
                    for r in rows
                ]
            if category == "theory":
                rows = db.scalars(select(TheoryKnowledge).limit(limit)).all()
                return [{"type": "theory", "name": r.topic, "data": r.summary} for r in rows]
            return []
        finally:
            db.close()

    @classmethod
    def keyword_search(cls, keyword: str, limit: int = 20) -> list[dict[str, Any]]:
        """跨表浅检索，后续可替换为 embedding RAG。"""
        results: list[dict[str, Any]] = []
        results.extend({"source": "stars", **x} for x in cls.search_stars(keyword, limit=limit))
        # palaces / patterns quick pass
        db = SessionLocal()
        try:
            like = f"%{keyword}%"
            for r in db.scalars(
                select(PalaceKnowledge).where(PalaceKnowledge.palace_name.ilike(like)).limit(limit)
            ):
                results.append(
                    {"source": "palace", "name": r.palace_name, "data": r.basic_meaning}
                )
            for r in db.scalars(
                select(ZiweiPattern).where(ZiweiPattern.pattern_name.ilike(like)).limit(limit)
            ):
                results.append(
                    {
                        "source": "pattern",
                        "name": r.pattern_name,
                        "data": r.traditional_meaning,
                    }
                )
        finally:
            db.close()
        return results[:limit]
