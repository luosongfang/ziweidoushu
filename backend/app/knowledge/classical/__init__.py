"""Knowledge Core V6.0 Phase 1 — Classical Knowledge Evidence Layer."""

from app.knowledge.classical.authority_ranker import AuthorityRanker
from app.knowledge.classical.evidence_service import EvidenceService
from app.knowledge.classical.interpretation_mapper import InterpretationMapper
from app.knowledge.classical.quote_importer import QuoteImporter
from app.knowledge.classical.quote_models import (
    AuthorityScore,
    ClassicalQuote,
    build_keywords,
    build_source_reference,
    classify_theory,
    clean_book_name,
    detect_chapter,
)

__all__ = [
    "AuthorityRanker",
    "AuthorityScore",
    "ClassicalQuote",
    "EvidenceService",
    "InterpretationMapper",
    "QuoteImporter",
    "build_keywords",
    "build_source_reference",
    "classify_theory",
    "clean_book_name",
    "detect_chapter",
]
