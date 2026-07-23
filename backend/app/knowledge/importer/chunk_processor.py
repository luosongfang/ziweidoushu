"""Chunk processor — split raw page text into 1000–1500 char chunks without rewriting."""

from __future__ import annotations

from dataclasses import dataclass

from app.knowledge.importer.metadata_extractor import extract_tags


MIN_CHUNK = 1000
MAX_CHUNK = 1500


@dataclass
class RawChunk:
    chunk_index: int
    page_number: int
    content: str
    keywords: list[str]
    star_tags: list[str]
    palace_tags: list[str]
    pattern_tags: list[str]
    life_question_tags: list[str]
    source_reference: dict


def _split_preserving(text: str, min_size: int = MIN_CHUNK, max_size: int = MAX_CHUNK) -> list[str]:
    """Split text into chunks. Prefer newline boundaries; never alter characters."""
    if not text:
        return []
    if len(text) <= max_size:
        return [text]

    chunks: list[str] = []
    start = 0
    n = len(text)
    while start < n:
        if n - start <= max_size:
            chunks.append(text[start:])
            break
        window_end = min(start + max_size, n)
        # Prefer split after newline within [min_size, max_size]
        split_at = -1
        search_from = start + min_size
        for i in range(window_end - 1, search_from - 1, -1):
            if text[i] == "\n":
                split_at = i + 1
                break
        if split_at < 0:
            # fallback: punctuation
            for i in range(window_end - 1, search_from - 1, -1):
                if text[i] in "。！？；.!?;":
                    split_at = i + 1
                    break
        if split_at <= start:
            split_at = window_end
        chunks.append(text[start:split_at])
        start = split_at
    return chunks


def build_chunks_for_page(
    *,
    book_name: str,
    page_number: int,
    content: str,
    chapter: str,
    start_index: int = 0,
) -> list[RawChunk]:
    """Create tagged chunks from one page's original content."""
    pieces = _split_preserving(content or "")
    if not pieces and (content is not None):
        # Keep empty pages as empty chunk? Skip empty to avoid noise.
        return []

    out: list[RawChunk] = []
    for offset, piece in enumerate(pieces):
        tags = extract_tags(piece)
        out.append(
            RawChunk(
                chunk_index=start_index + offset,
                page_number=page_number,
                content=piece,  # original substring only
                keywords=tags["keywords"],
                star_tags=tags["star_tags"],
                palace_tags=tags["palace_tags"],
                pattern_tags=tags["pattern_tags"],
                life_question_tags=tags["life_question_tags"],
                source_reference={
                    "book": book_name,
                    "page": page_number,
                    "chapter": chapter,
                },
            )
        )
    return out


def pages_to_document_content(pages: list[dict]) -> str:
    """Concatenate page contents in order without rewriting each page body."""
    parts: list[str] = []
    for p in pages:
        body = p.get("content") or ""
        parts.append(body)
    return "\n".join(parts)
