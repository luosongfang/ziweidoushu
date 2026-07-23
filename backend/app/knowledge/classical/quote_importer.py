"""Import extracted_text JSON pages into classical_quotes (verbatim, no LLM)."""

from __future__ import annotations

import json
import logging
from collections import defaultdict
from pathlib import Path
from typing import Any

from sqlalchemy import text

from app.database.database import SessionLocal
from app.knowledge.classical.authority_ranker import AuthorityRanker
from app.knowledge.classical.interpretation_mapper import InterpretationMapper
from app.knowledge.classical.quote_models import (
    ClassicalQuote,
    build_keywords,
    build_source_reference,
    classify_theory,
    clean_book_name,
    content_hash,
    detect_chapter,
)

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_EXTRACTED = PROJECT_ROOT / "knowledge" / "books" / "extracted_text"
DEFAULT_PROFILES = PROJECT_ROOT / "knowledge" / "books" / "metadata" / "book_profiles.json"


class QuoteImporter:
    """
    Read knowledge/books/extracted_text/*.json
    Persist original_text unchanged — only add location + keyword tags.
    """

    def __init__(
        self,
        extracted_dir: str | Path | None = None,
        profiles_path: str | Path | None = None,
    ) -> None:
        self.extracted_dir = Path(extracted_dir or DEFAULT_EXTRACTED)
        self.profiles_path = Path(profiles_path or DEFAULT_PROFILES)

    @staticmethod
    def parse_page_file(path: Path) -> dict[str, Any] | None:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            logger.warning("skip bad json %s: %s", path.name, exc)
            return None
        if not isinstance(data, dict):
            return None
        if "book_name" not in data or "page_number" not in data:
            return None
        content = data.get("content")
        if content is None:
            return None
        return data

    def scan(self) -> dict[str, list[dict[str, Any]]]:
        by_book: dict[str, list[dict[str, Any]]] = defaultdict(list)
        if not self.extracted_dir.is_dir():
            return {}
        for path in sorted(self.extracted_dir.glob("*.json")):
            data = self.parse_page_file(path)
            if not data:
                continue
            book = clean_book_name(str(data["book_name"]))
            data = dict(data)
            data["book_name"] = book
            data["_path"] = str(path)
            by_book[book].append(data)
        for pages in by_book.values():
            pages.sort(key=lambda p: int(p.get("page_number") or 0))
        return dict(by_book)

    def page_to_quote(self, page_data: dict[str, Any]) -> ClassicalQuote | None:
        book = clean_book_name(str(page_data.get("book_name") or ""))
        try:
            page = int(page_data.get("page_number") or 0)
        except (TypeError, ValueError):
            return None
        # Keep original text verbatim — no strip of meaningful whitespace beyond storage
        original = page_data.get("content")
        if original is None:
            return None
        original_text = str(original)
        if not original_text.strip():
            return None

        chapter = detect_chapter(original_text, page)
        keywords = build_keywords(original_text)
        theory = classify_theory(original_text, keywords)
        source_file = page_data.get("source_file")
        if source_file is not None:
            source_file = str(source_file)
        ref = build_source_reference(
            book=book,
            chapter=chapter,
            page=page,
            source_file=source_file,
        )
        return ClassicalQuote(
            book=book,
            page=page,
            original_text=original_text,
            chapter=chapter,
            keywords=keywords,
            source_reference=ref,
            theory_category=theory,
            source_file=source_file,
            content_hash=content_hash(original_text),
        )

    def upsert_quote(self, quote: ClassicalQuote) -> str | None:
        db = SessionLocal()
        try:
            row = db.execute(
                text(
                    """
                    INSERT INTO public.classical_quotes
                        (book, chapter, page, original_text, keywords, source_reference,
                         theory_category, source_file, content_hash)
                    VALUES
                        (:book, :chapter, :page, :original_text,
                         CAST(:keywords AS jsonb), CAST(:source_reference AS jsonb),
                         :theory_category, :source_file, :content_hash)
                    ON CONFLICT (book, page, content_hash) DO UPDATE SET
                        chapter = EXCLUDED.chapter,
                        keywords = EXCLUDED.keywords,
                        source_reference = EXCLUDED.source_reference,
                        theory_category = EXCLUDED.theory_category,
                        source_file = EXCLUDED.source_file
                    RETURNING id::text
                    """
                ),
                {
                    "book": quote.book,
                    "chapter": quote.chapter,
                    "page": quote.page,
                    "original_text": quote.original_text,
                    "keywords": json.dumps(quote.keywords, ensure_ascii=False),
                    "source_reference": json.dumps(quote.source_reference, ensure_ascii=False),
                    "theory_category": quote.theory_category,
                    "source_file": quote.source_file,
                    "content_hash": quote.content_hash,
                },
            ).mappings().first()
            db.commit()
            return row["id"] if row else None
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def import_books(
        self,
        *,
        book_names: list[str] | None = None,
        max_pages_per_book: int | None = None,
        max_total: int | None = None,
        map_interpretations: bool = True,
        seed_authority: bool = True,
    ) -> dict[str, Any]:
        scanned = self.scan()
        if book_names:
            wanted = {clean_book_name(b) for b in book_names}
            scanned = {k: v for k, v in scanned.items() if k in wanted}

        if seed_authority:
            AuthorityRanker.seed_from_profiles(self.profiles_path)

        imported = 0
        mapped = 0
        books_done: list[str] = []
        samples: list[dict[str, Any]] = []

        for book, pages in sorted(scanned.items()):
            books_done.append(book)
            limit_pages = pages
            if max_pages_per_book is not None:
                limit_pages = pages[: max(0, int(max_pages_per_book))]
            for page_data in limit_pages:
                if max_total is not None and imported >= max_total:
                    return {
                        "books": books_done,
                        "imported": imported,
                        "mapped": mapped,
                        "samples": samples,
                        "truncated": True,
                    }
                quote = self.page_to_quote(page_data)
                if not quote:
                    continue
                qid = self.upsert_quote(quote)
                if not qid:
                    continue
                imported += 1
                quote.id = qid
                if map_interpretations:
                    mapped += InterpretationMapper.map_quote(quote)
                if len(samples) < 5:
                    samples.append(
                        {
                            "id": qid,
                            "book": quote.book,
                            "page": quote.page,
                            "chapter": quote.chapter,
                            "keywords": quote.keywords[:8],
                            "source_reference": quote.source_reference,
                            "original_text_preview": quote.original_text[:80],
                        }
                    )

        return {
            "books": books_done,
            "book_count": len(books_done),
            "imported": imported,
            "mapped": mapped,
            "samples": samples,
            "truncated": False,
        }

    @classmethod
    def count_quotes(cls) -> int:
        db = SessionLocal()
        try:
            return int(db.execute(text("SELECT COUNT(*) FROM public.classical_quotes")).scalar() or 0)
        finally:
            db.close()
