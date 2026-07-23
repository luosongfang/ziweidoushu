"""Classical quote models & rule-based tagging (no LLM, no rewrite)."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from typing import Any

# Reuse existing keyword lists — tagging only, never rewrite original_text
from app.knowledge.importer.metadata_extractor import (
    FOUR_TRANSFORM_KEYWORDS,
    PALACE_KEYWORDS,
    PATTERN_KEYWORDS,
    STAR_KEYWORDS,
    extract_tags,
)

CHAPTER_RE = re.compile(
    r"(第[一二三四五六七八九十百千零〇\d]+[章节回部篇][：:\s]*[^\n]{0,48})"
)

THEORY_HINTS: dict[str, list[str]] = {
    "four_transform": ["化禄", "化权", "化科", "化忌", "四化", "飞化"],
    "sanhe": ["三合", "宫干", "十二宫", "命宫", "三方四正", "对宫"],
    "feixing": ["飞星", "自化", "向心", "离心"],
    "classic_formula": ["古诀", "口诀", "断曰", "赋云", "格局", "杀破狼", "紫府", "机月同梁"],
    "palace": ["宫位", "命宫", "财帛", "官禄", "夫妻", "福德", "田宅"],
    "star": ["紫微", "天府", "武曲", "七杀", "破军", "贪狼", "星曜"],
    "foundation": ["原理", "概念", "结构", "基础", "安星"],
}


def clean_book_name(name: str) -> str:
    """Strip control chars (incl. DEL 0x7F) from book titles — does not alter quote text."""
    return "".join(
        ch for ch in (name or "") if ord(ch) >= 32 and ord(ch) != 127
    ).strip()


def content_hash(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()[:32]


def detect_chapter(content: str, page: int) -> str:
    """Locate chapter label from text if present; else page locator. Never invents content."""
    text = content or ""
    m = CHAPTER_RE.search(text)
    if m:
        return m.group(1).strip()
    return f"第{int(page)}页"


def classify_theory(content: str, keywords: list[str] | None = None) -> str:
    """Rule-based theory category from keyword presence only."""
    text = content or ""
    bag = set(keywords or [])
    scores: dict[str, int] = {}
    for theory, hints in THEORY_HINTS.items():
        hit = sum(1 for h in hints if h in text or h in bag)
        if hit:
            scores[theory] = hit
    if not scores:
        return "general"
    return max(scores.items(), key=lambda x: x[1])[0]


def build_keywords(content: str) -> list[str]:
    tags = extract_tags(content or "")
    return list(tags.get("keywords") or [])


def build_source_reference(
    *,
    book: str,
    chapter: str,
    page: int,
    source_file: str | None = None,
) -> dict[str, Any]:
    ref: dict[str, Any] = {
        "book": book,
        "chapter": chapter,
        "page": int(page),
    }
    if source_file:
        ref["source_file"] = source_file
    return ref


@dataclass
class ClassicalQuote:
    book: str
    page: int
    original_text: str
    chapter: str = ""
    keywords: list[str] = field(default_factory=list)
    source_reference: dict[str, Any] = field(default_factory=dict)
    theory_category: str = "general"
    source_file: str | None = None
    content_hash: str = ""
    id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "book": self.book,
            "chapter": self.chapter,
            "page": self.page,
            "original_text": self.original_text,
            "keywords": self.keywords,
            "source_reference": self.source_reference,
            "theory_category": self.theory_category,
            "source_file": self.source_file,
            "content_hash": self.content_hash,
        }


@dataclass
class AuthorityScore:
    book: str
    authority_level: int
    book_type: str | None = None
    main_topics: list[str] = field(default_factory=list)
    suitable_questions: list[str] = field(default_factory=list)
    description: str | None = None
    id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "book": self.book,
            "authority_level": self.authority_level,
            "book_type": self.book_type,
            "main_topics": self.main_topics,
            "suitable_questions": self.suitable_questions,
            "description": self.description,
        }


# Export keyword constants for tests / mappers
__all__ = [
    "STAR_KEYWORDS",
    "PALACE_KEYWORDS",
    "PATTERN_KEYWORDS",
    "FOUR_TRANSFORM_KEYWORDS",
    "ClassicalQuote",
    "AuthorityScore",
    "clean_book_name",
    "content_hash",
    "detect_chapter",
    "classify_theory",
    "build_keywords",
    "build_source_reference",
    "extract_tags",
]
