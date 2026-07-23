"""Authority ranking for classical books (from profiles, not LLM)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sqlalchemy import text

from app.database.database import SessionLocal
from app.knowledge.classical.quote_models import AuthorityScore, clean_book_name

PROJECT_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_PROFILES = PROJECT_ROOT / "knowledge" / "books" / "metadata" / "book_profiles.json"


class AuthorityRanker:
    """Load / query classical_authority_scores."""

    @classmethod
    def load_profiles(cls, path: str | Path | None = None) -> list[dict[str, Any]]:
        p = Path(path or DEFAULT_PROFILES)
        if not p.is_file():
            return []
        data = json.loads(p.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            return []
        out = []
        for row in data:
            if not isinstance(row, dict):
                continue
            name = clean_book_name(str(row.get("book_name") or ""))
            if not name:
                continue
            item = dict(row)
            item["book_name"] = name
            out.append(item)
        return out

    @classmethod
    def seed_from_profiles(cls, path: str | Path | None = None) -> int:
        profiles = cls.load_profiles(path)
        if not profiles:
            return 0
        db = SessionLocal()
        n = 0
        try:
            for row in profiles:
                book = clean_book_name(str(row.get("book_name") or ""))
                level = int(row.get("authority_level") or 3)
                level = max(1, min(5, level))
                db.execute(
                    text(
                        """
                        INSERT INTO public.classical_authority_scores
                            (book, authority_level, book_type, main_topics,
                             suitable_questions, description, updated_at)
                        VALUES
                            (:book, :level, :btype,
                             CAST(:topics AS jsonb), CAST(:questions AS jsonb),
                             :desc, NOW())
                        ON CONFLICT (book) DO UPDATE SET
                            authority_level = EXCLUDED.authority_level,
                            book_type = EXCLUDED.book_type,
                            main_topics = EXCLUDED.main_topics,
                            suitable_questions = EXCLUDED.suitable_questions,
                            description = EXCLUDED.description,
                            updated_at = NOW()
                        """
                    ),
                    {
                        "book": book,
                        "level": level,
                        "btype": row.get("book_type"),
                        "topics": json.dumps(row.get("main_topics") or [], ensure_ascii=False),
                        "questions": json.dumps(
                            row.get("suitable_questions") or [], ensure_ascii=False
                        ),
                        "desc": row.get("description"),
                    },
                )
                n += 1
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()
        return n

    @classmethod
    def get(cls, book: str) -> AuthorityScore | None:
        book = clean_book_name(book)
        db = SessionLocal()
        try:
            row = db.execute(
                text(
                    """
                    SELECT id::text, book, authority_level, book_type,
                           main_topics, suitable_questions, description
                    FROM public.classical_authority_scores
                    WHERE book = :book
                    """
                ),
                {"book": book},
            ).mappings().first()
            if not row:
                return None
            return AuthorityScore(
                id=row["id"],
                book=row["book"],
                authority_level=int(row["authority_level"]),
                book_type=row.get("book_type"),
                main_topics=list(row.get("main_topics") or []),
                suitable_questions=list(row.get("suitable_questions") or []),
                description=row.get("description"),
            )
        finally:
            db.close()

    @classmethod
    def list_all(cls) -> list[AuthorityScore]:
        db = SessionLocal()
        try:
            rows = db.execute(
                text(
                    """
                    SELECT id::text, book, authority_level, book_type,
                           main_topics, suitable_questions, description
                    FROM public.classical_authority_scores
                    ORDER BY authority_level DESC, book
                    """
                )
            ).mappings().all()
            return [
                AuthorityScore(
                    id=r["id"],
                    book=r["book"],
                    authority_level=int(r["authority_level"]),
                    book_type=r.get("book_type"),
                    main_topics=list(r.get("main_topics") or []),
                    suitable_questions=list(r.get("suitable_questions") or []),
                    description=r.get("description"),
                )
                for r in rows
            ]
        finally:
            db.close()

    @classmethod
    def rank_quotes(cls, quotes: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Attach authority_level and sort higher first. Does not alter original_text."""
        levels = {a.book: a.authority_level for a in cls.list_all()}
        enriched = []
        for q in quotes:
            item = dict(q)
            item["authority_level"] = levels.get(clean_book_name(str(q.get("book") or "")), 3)
            enriched.append(item)
        enriched.sort(
            key=lambda x: (-int(x.get("authority_level") or 0), int(x.get("page") or 0))
        )
        return enriched
