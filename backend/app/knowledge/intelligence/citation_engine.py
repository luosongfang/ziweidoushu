"""Citation engine — user-visible source citations from evidence/chunks."""

from __future__ import annotations

from typing import Any


class CitationEngine:
    @classmethod
    def from_chunks(cls, chunks: list[dict[str, Any]], *, limit: int = 8) -> list[dict[str, Any]]:
        seen: set[tuple[Any, Any, Any]] = set()
        out: list[dict[str, Any]] = []
        for ch in chunks:
            cite = ch.get("citation") or {}
            book = cite.get("book") or ch.get("book_source") or ""
            page = cite.get("page") or ch.get("page_number")
            chapter = cite.get("chapter") or ch.get("chapter") or ""
            key = (book, page, chapter)
            if not book and page is None:
                continue
            if key in seen:
                continue
            seen.add(key)
            out.append(
                {
                    "book": book,
                    "page": page,
                    "chapter": chapter,
                    "display": cls.format_display(book, page, chapter),
                }
            )
            if len(out) >= limit:
                break
        return out

    @classmethod
    def from_evidence(cls, evidence: list[dict[str, Any]], *, limit: int = 8) -> list[dict[str, Any]]:
        chunks = [
            {
                "citation": {
                    "book": e.get("book_name") or "",
                    "page": e.get("page_number"),
                    "chapter": e.get("chapter") or "",
                }
            }
            for e in evidence
        ]
        return cls.from_chunks(chunks, limit=limit)

    @classmethod
    def format_display(cls, book: str, page: Any, chapter: str = "") -> str:
        parts = []
        if book:
            parts.append(f"《{book}》")
        if page is not None and page != "":
            parts.append(f"第{page}页")
        if chapter:
            parts.append(str(chapter))
        if not parts:
            return "依据：Knowledge Core 原文片段"
        return "依据：" + " ".join(parts)

    @classmethod
    def render_lines(cls, sources: list[dict[str, Any]]) -> list[str]:
        lines = []
        for s in sources:
            disp = s.get("display") or cls.format_display(
                s.get("book") or "", s.get("page"), s.get("chapter") or ""
            )
            lines.append(f"{disp}。传统理论相关表述仅作文化参考。")
        return lines
