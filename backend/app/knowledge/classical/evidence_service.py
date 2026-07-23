"""Classical Evidence Service — keyword retrieval with full source traceability."""

from __future__ import annotations

import json
from typing import Any

from sqlalchemy import text

from app.database.database import SessionLocal
from app.knowledge.classical.authority_ranker import AuthorityRanker
from app.knowledge.classical.quote_models import clean_book_name


class EvidenceService:
    """
    Knowledge Evidence Layer entrypoint (V6.0 Phase 1).

    Sits *before* Theory Engine as a data source — does not replace V5.6 dispatcher.
    Returns original quotes + source_reference only (no summarization).
    """

    LAYER_VERSION = "6.0.0-phase1"

    @classmethod
    def get_quote(cls, quote_id: str) -> dict[str, Any] | None:
        db = SessionLocal()
        try:
            row = db.execute(
                text(
                    """
                    SELECT id::text, book, chapter, page, original_text, keywords,
                           source_reference, theory_category, source_file, content_hash,
                           created_at
                    FROM public.classical_quotes
                    WHERE id = CAST(:id AS uuid)
                    """
                ),
                {"id": quote_id},
            ).mappings().first()
            return cls._row_to_dict(row) if row else None
        finally:
            db.close()

    @classmethod
    def get_by_book_page(cls, book: str, page: int) -> list[dict[str, Any]]:
        book = clean_book_name(book)
        db = SessionLocal()
        try:
            rows = db.execute(
                text(
                    """
                    SELECT id::text, book, chapter, page, original_text, keywords,
                           source_reference, theory_category, source_file, content_hash,
                           created_at
                    FROM public.classical_quotes
                    WHERE book = :book AND page = :page
                    ORDER BY created_at
                    """
                ),
                {"book": book, "page": int(page)},
            ).mappings().all()
            return [cls._row_to_dict(r) for r in rows]
        finally:
            db.close()

    @classmethod
    def search_by_keywords(
        cls,
        keywords: list[str] | str,
        *,
        limit: int = 20,
        theory_category: str | None = None,
        min_authority: int | None = None,
    ) -> list[dict[str, Any]]:
        if isinstance(keywords, str):
            kws = [k.strip() for k in keywords.split() if k.strip()]
        else:
            kws = [str(k).strip() for k in (keywords or []) if str(k).strip()]
        if not kws:
            return []

        # Match keywords JSON containment OR original_text substring (rule-based only)
        or_parts: list[str] = []
        params: dict[str, Any] = {
            "theory": theory_category,
            "min_auth": min_authority,
            "lim": int(limit),
        }
        for i, kw in enumerate(kws[:12]):
            params[f"kw{i}"] = kw
            params[f"like{i}"] = f"%{kw}%"
            or_parts.append(
                f"(q.keywords @> CAST(:kwj{i} AS jsonb) OR q.original_text ILIKE :like{i})"
            )
            params[f"kwj{i}"] = json.dumps([kw], ensure_ascii=False)

        where_or = " OR ".join(or_parts)
        sql = f"""
            SELECT q.id::text, q.book, q.chapter, q.page, q.original_text, q.keywords,
                   q.source_reference, q.theory_category, q.source_file, q.content_hash,
                   q.created_at,
                   COALESCE(a.authority_level, 3) AS authority_level
            FROM public.classical_quotes q
            LEFT JOIN public.classical_authority_scores a ON a.book = q.book
            WHERE ({where_or})
              AND (:theory IS NULL OR q.theory_category = :theory)
              AND (:min_auth IS NULL OR COALESCE(a.authority_level, 3) >= :min_auth)
            ORDER BY COALESCE(a.authority_level, 3) DESC, q.page ASC
            LIMIT :lim
        """
        db = SessionLocal()
        try:
            rows = db.execute(text(sql), params).mappings().all()
            return [cls._row_to_dict(r) for r in rows]
        finally:
            db.close()

    @classmethod
    def evidence_for_entities(
        cls,
        *,
        stars: list[str] | None = None,
        palaces: list[str] | None = None,
        patterns: list[str] | None = None,
        limit: int = 15,
    ) -> dict[str, Any]:
        """Retrieve classical evidence for Theory Engine consumers (read-only)."""
        kws = list(
            dict.fromkeys(
                [*(stars or []), *(palaces or []), *(patterns or [])]
            )
        )
        quotes = cls.search_by_keywords(kws, limit=limit) if kws else []
        ranked = AuthorityRanker.rank_quotes(quotes)
        return {
            "layer": "classical_evidence",
            "layer_version": cls.LAYER_VERSION,
            "query": {"stars": stars or [], "palaces": palaces or [], "patterns": patterns or []},
            "evidence": [
                {
                    "quote_id": q.get("id"),
                    "book": q.get("book"),
                    "chapter": q.get("chapter"),
                    "page": q.get("page"),
                    "original_text": q.get("original_text"),
                    "keywords": q.get("keywords"),
                    "source_reference": q.get("source_reference"),
                    "authority_level": q.get("authority_level"),
                    "theory_category": q.get("theory_category"),
                }
                for q in ranked
            ],
            "count": len(ranked),
            # Explicit: Phase 1 does not mutate V5.6 theory dispatch
            "affects_v5_6_dispatch": False,
        }

    @classmethod
    def verify_traceability(cls, quote_id: str) -> dict[str, Any]:
        """Assert a quote has complete citation fields."""
        q = cls.get_quote(quote_id)
        if not q:
            return {"ok": False, "error": "quote_not_found"}
        ref = q.get("source_reference") or {}
        required = ["book", "page", "chapter"]
        missing = [k for k in required if ref.get(k) in (None, "")]
        ok = (
            bool(q.get("book"))
            and q.get("page") is not None
            and bool(q.get("original_text"))
            and bool(ref)
            and not missing
        )
        return {
            "ok": ok,
            "quote_id": quote_id,
            "book": q.get("book"),
            "page": q.get("page"),
            "chapter": q.get("chapter"),
            "source_reference": ref,
            "missing_fields": missing,
            "has_keywords": bool(q.get("keywords")),
        }

    @classmethod
    def stats(cls) -> dict[str, Any]:
        db = SessionLocal()
        try:
            quotes = int(db.execute(text("SELECT COUNT(*) FROM public.classical_quotes")).scalar() or 0)
            books = int(
                db.execute(text("SELECT COUNT(DISTINCT book) FROM public.classical_quotes")).scalar()
                or 0
            )
            interp = int(
                db.execute(text("SELECT COUNT(*) FROM public.classical_interpretations")).scalar()
                or 0
            )
            auth = int(
                db.execute(text("SELECT COUNT(*) FROM public.classical_authority_scores")).scalar()
                or 0
            )
            return {
                "quotes": quotes,
                "books": books,
                "interpretations": interp,
                "authority_scores": auth,
                "layer_version": cls.LAYER_VERSION,
            }
        finally:
            db.close()

    @classmethod
    def _row_to_dict(cls, row: Any) -> dict[str, Any]:
        item = dict(row)
        for key in ("keywords", "source_reference"):
            val = item.get(key)
            if isinstance(val, str):
                try:
                    item[key] = json.loads(val)
                except Exception:
                    pass
        if item.get("created_at"):
            item["created_at"] = item["created_at"].isoformat()
        return item
