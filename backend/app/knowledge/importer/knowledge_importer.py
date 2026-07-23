"""KnowledgeImporter — extracted_text JSON → Supabase knowledge asset tables."""

from __future__ import annotations

import json
import logging
import os
import uuid
from collections import defaultdict
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from app.knowledge.importer.chunk_processor import RawChunk, build_chunks_for_page
from app.knowledge.importer.metadata_extractor import extract_tags

logger = logging.getLogger(__name__)

BACKEND = Path(__file__).resolve().parents[3]
PROJECT_ROOT = BACKEND.parent
DEFAULT_EXTRACTED = PROJECT_ROOT / "knowledge" / "books" / "extracted_text"
MIGRATION_SQL = PROJECT_ROOT / "database" / "migrations" / "007_knowledge_asset_core.sql"

PAGES_PER_DOCUMENT = 20


def _load_env() -> None:
    load_dotenv(BACKEND / ".env", override=True)


def _engine() -> Engine:
    _load_env()
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL missing")
    if url.startswith("postgresql") and "sslmode=" not in url:
        url = f"{url}{'&' if '?' in url else '?'}sslmode=require"
    return create_engine(url, pool_pre_ping=True)


def _j(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False)


def _parse_page_file(path: Path) -> dict | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        logger.warning("skip bad json %s: %s", path.name, exc)
        return None
    if not isinstance(data, dict):
        return None
    if "book_name" not in data or "page_number" not in data:
        return None
    return data


def scan_extracted_json(extracted_dir: Path) -> dict[str, list[dict]]:
    by_book: dict[str, list[dict]] = defaultdict(list)
    for path in sorted(extracted_dir.glob("*.json")):
        data = _parse_page_file(path)
        if not data:
            continue
        data["_path"] = str(path)
        by_book[str(data["book_name"])].append(data)
    for pages in by_book.values():
        pages.sort(key=lambda p: int(p.get("page_number") or 0))
    return dict(by_book)


def apply_migration(eng: Engine | None = None) -> None:
    eng = eng or _engine()
    sql = MIGRATION_SQL.read_text(encoding="utf-8")
    statements = _split_sql(sql)
    with eng.connect() as conn:
        conn = conn.execution_options(isolation_level="AUTOCOMMIT")
        for stmt in statements:
            conn.execute(text(stmt))


def _split_sql(sql: str) -> list[str]:
    """Split SQL on semicolons, keeping DO $$ ... $$ blocks intact."""
    out: list[str] = []
    i = 0
    n = len(sql)
    start = 0
    while i < n:
        if sql.startswith("$$", i):
            j = sql.find("$$", i + 2)
            if j < 0:
                break
            i = j + 2
            continue
        if sql[i] == ";":
            chunk = sql[start:i].strip()
            body = "\n".join(
                ln for ln in chunk.splitlines() if ln.strip() and not ln.strip().startswith("--")
            ).strip()
            if body:
                out.append(body)
            start = i + 1
        i += 1
    tail = sql[start:].strip()
    body = "\n".join(
        ln for ln in tail.splitlines() if ln.strip() and not ln.strip().startswith("--")
    ).strip()
    if body:
        out.append(body)
    return out


class KnowledgeImporter:
    """Import raw PDF page JSON into knowledge_books / documents / chunks."""

    def __init__(
        self,
        extracted_dir: str | Path | None = None,
        *,
        reimport: bool = True,
    ) -> None:
        self.extracted_dir = Path(extracted_dir) if extracted_dir else DEFAULT_EXTRACTED
        self.reimport = reimport
        self.engine = _engine()

    def ensure_schema(self) -> None:
        apply_migration(self.engine)

    def import_all(self) -> dict[str, Any]:
        self.ensure_schema()
        books_map = scan_extracted_json(self.extracted_dir)
        summary: dict[str, Any] = {
            "books": 0,
            "documents": 0,
            "chunks": 0,
            "characters": 0,
            "citations": 0,
            "book_names": [],
        }

        with self.engine.begin() as conn:
            for book_name, pages in books_map.items():
                result = self._import_book(conn, book_name, pages)
                summary["books"] += 1
                summary["documents"] += result["documents"]
                summary["chunks"] += result["chunks"]
                summary["characters"] += result["characters"]
                summary["citations"] += result["citations"]
                summary["book_names"].append(book_name)
                logger.info(
                    "imported book=%s pages=%s chunks=%s",
                    book_name,
                    len(pages),
                    result["chunks"],
                )

        return summary

    def _import_book(self, conn, book_name: str, pages: list[dict]) -> dict[str, int]:
        file_name = next((str(p.get("source_file") or "") for p in pages if p.get("source_file")), "")

        if self.reimport:
            conn.execute(
                text("DELETE FROM public.knowledge_books WHERE book_name = :n"),
                {"n": book_name},
            )

        book_id = conn.execute(
            text(
                """
                INSERT INTO public.knowledge_books
                    (book_name, author, school, description, file_name, total_pages, status)
                VALUES
                    (:book_name, NULL, 'sanhe', :description, :file_name, :total_pages, 'imported')
                RETURNING id
                """
            ),
            {
                "book_name": book_name,
                "description": "PDF 原文导入（未改写）",
                "file_name": file_name,
                "total_pages": len(pages),
            },
        ).scalar_one()

        docs = 0
        chunks_n = 0
        chars = 0
        citations = 0

        chunk_rows: list[dict[str, Any]] = []
        cite_rows: list[dict[str, Any]] = []

        for i in range(0, len(pages), PAGES_PER_DOCUMENT):
            window = pages[i : i + PAGES_PER_DOCUMENT]
            page_start = int(window[0]["page_number"])
            page_end = int(window[-1]["page_number"])
            chapter = f"第{page_start}-{page_end}页"
            title = f"{book_name} {chapter}"
            content = "\n".join((p.get("content") or "") for p in window)
            source_file = str(window[0].get("source_file") or file_name)

            doc_id = conn.execute(
                text(
                    """
                    INSERT INTO public.knowledge_documents
                        (book_id, title, chapter, source_file, page_start, page_end, content)
                    VALUES
                        (:book_id, :title, :chapter, :source_file, :page_start, :page_end, :content)
                    RETURNING id
                    """
                ),
                {
                    "book_id": book_id,
                    "title": title,
                    "chapter": chapter,
                    "source_file": source_file,
                    "page_start": page_start,
                    "page_end": page_end,
                    "content": content,
                },
            ).scalar_one()
            docs += 1

            chunk_index = 0
            for page in window:
                page_no = int(page.get("page_number") or 0)
                page_content = page.get("content") or ""
                chars += len(page_content)
                raw_chunks = build_chunks_for_page(
                    book_name=book_name,
                    page_number=page_no,
                    content=page_content,
                    chapter=chapter,
                    start_index=chunk_index,
                )
                if not raw_chunks and page_content:
                    tags = extract_tags(page_content)
                    raw_chunks = [
                        RawChunk(
                            chunk_index=chunk_index,
                            page_number=page_no,
                            content=page_content,
                            keywords=tags["keywords"],
                            star_tags=tags["star_tags"],
                            palace_tags=tags["palace_tags"],
                            pattern_tags=tags["pattern_tags"],
                            life_question_tags=tags["life_question_tags"],
                            source_reference={
                                "book": book_name,
                                "page": page_no,
                                "chapter": chapter,
                            },
                        )
                    ]

                for rc in raw_chunks:
                    chunk_id = uuid.uuid4()
                    chunk_rows.append(
                        {
                            "id": chunk_id,
                            "document_id": doc_id,
                            "book_id": book_id,
                            "chunk_index": rc.chunk_index,
                            "page_number": rc.page_number,
                            "content": rc.content,
                            "keywords": _j(rc.keywords),
                            "star_tags": _j(rc.star_tags),
                            "palace_tags": _j(rc.palace_tags),
                            "pattern_tags": _j(rc.pattern_tags),
                            "life_question_tags": _j(rc.life_question_tags),
                            "source_reference": _j(rc.source_reference),
                        }
                    )
                    cite_rows.append(
                        {
                            "chunk_id": chunk_id,
                            "citation_text": (rc.content or "")[:200],
                            "source_book": book_name,
                            "page_number": page_no,
                        }
                    )
                    chunks_n += 1
                    citations += 1
                    chunk_index = rc.chunk_index + 1

        # bulk insert chunks / citations
        if chunk_rows:
            conn.execute(
                text(
                    """
                    INSERT INTO public.knowledge_chunks
                        (id, document_id, book_id, chunk_index, page_number, content,
                         keywords, star_tags, palace_tags, pattern_tags,
                         life_question_tags, source_reference)
                    VALUES
                        (:id, :document_id, :book_id, :chunk_index, :page_number, :content,
                         CAST(:keywords AS jsonb), CAST(:star_tags AS jsonb),
                         CAST(:palace_tags AS jsonb), CAST(:pattern_tags AS jsonb),
                         CAST(:life_question_tags AS jsonb), CAST(:source_reference AS jsonb))
                    """
                ),
                chunk_rows,
            )
        if cite_rows:
            conn.execute(
                text(
                    """
                    INSERT INTO public.knowledge_citations
                        (chunk_id, citation_text, source_book, page_number)
                    VALUES
                        (:chunk_id, :citation_text, :source_book, :page_number)
                    """
                ),
                cite_rows,
            )

        return {
            "documents": docs,
            "chunks": chunks_n,
            "characters": chars,
            "citations": citations,
        }


def import_knowledge_books(extracted_dir: str | Path | None = None) -> dict[str, Any]:
    importer = KnowledgeImporter(extracted_dir=extracted_dir)
    return importer.import_all()
