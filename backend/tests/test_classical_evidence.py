"""Knowledge Core V6.0 Phase 1 — classical evidence layer tests (no LLM)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.config import settings
from app.database.database import is_database_ready
from app.knowledge.classical import (
    AuthorityRanker,
    EvidenceService,
    QuoteImporter,
    detect_chapter,
)
from app.knowledge.multitheory.theory_dispatcher import TheoryDispatcher
from app.knowledge.optimization import WeightOptimizer

PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXTRACTED = PROJECT_ROOT / "knowledge" / "books" / "extracted_text"
SAMPLE_BOOK = "紫微斗数原理与宫位说明"
SAMPLE_PAGE = 10


@pytest.fixture(scope="module")
def require_postgres():
    if not settings.is_postgres:
        pytest.skip("requires PostgreSQL")
    if not is_database_ready():
        pytest.skip("database not ready")


@pytest.fixture(scope="module")
def imported_sample(require_postgres):
    """Import a small deterministic slice for tests (does not wipe full corpus)."""
    AuthorityRanker.seed_from_profiles()
    importer = QuoteImporter(extracted_dir=EXTRACTED)
    # Prefer known page with star keywords
    page_path = EXTRACTED / f"{SAMPLE_BOOK}_page_{SAMPLE_PAGE:03d}.json"
    assert page_path.is_file(), f"missing sample page {page_path}"
    raw = json.loads(page_path.read_text(encoding="utf-8"))
    quote = importer.page_to_quote(raw)
    assert quote is not None
    qid = importer.upsert_quote(quote)
    assert qid
    quote.id = qid
    from app.knowledge.classical import InterpretationMapper

    InterpretationMapper.map_quote(quote)

    # Also import page 1 from 天纪 for multi-book coverage
    importer.import_books(
        book_names=["天纪--紫微斗数", SAMPLE_BOOK],
        max_pages_per_book=2,
        map_interpretations=True,
        seed_authority=False,
    )
    return {"quote_id": qid, "raw": raw, "quote": quote}


def test_pdf_quote_accuracy(imported_sample):
    """Imported original_text must match extracted JSON content exactly."""
    raw = imported_sample["raw"]
    rows = EvidenceService.get_by_book_page(SAMPLE_BOOK, SAMPLE_PAGE)
    assert rows, "expected imported quote for sample book/page"
    # At least one row must equal raw content verbatim
    assert any(r["original_text"] == raw["content"] for r in rows)
    q = next(r for r in rows if r["original_text"] == raw["content"])
    assert "武曲" in q["original_text"] or "天同" in q["original_text"]
    # Chapter locator exists (parsed or page label) — text itself not rewritten
    assert q["chapter"]
    assert detect_chapter(raw["content"], SAMPLE_PAGE) == q["chapter"] or q["chapter"].startswith("第")


def test_source_traceability(imported_sample):
    qid = imported_sample["quote_id"]
    trace = EvidenceService.verify_traceability(qid)
    assert trace["ok"] is True
    assert trace["book"] == SAMPLE_BOOK
    assert trace["page"] == SAMPLE_PAGE
    ref = trace["source_reference"]
    assert ref["book"] == SAMPLE_BOOK
    assert ref["page"] == SAMPLE_PAGE
    assert "chapter" in ref
    q = EvidenceService.get_quote(qid)
    assert q is not None
    assert q["source_reference"]["book"] == q["book"]
    assert q["source_reference"]["page"] == q["page"]


def test_authority_level_exists(require_postgres, imported_sample):
    scores = AuthorityRanker.list_all()
    assert len(scores) >= 10  # 16-book profiles
    sample = AuthorityRanker.get(SAMPLE_BOOK)
    assert sample is not None
    assert 1 <= sample.authority_level <= 5
    # Ranked evidence attaches authority
    ev = EvidenceService.evidence_for_entities(stars=["武曲"], limit=5)
    assert ev["affects_v5_6_dispatch"] is False
    assert ev["count"] >= 1
    assert all("authority_level" in e for e in ev["evidence"])
    assert all(e.get("source_reference") for e in ev["evidence"])


def test_keyword_search(imported_sample):
    hits = EvidenceService.search_by_keywords(["武曲"], limit=10)
    assert hits
    assert any("武曲" in (h.get("original_text") or "") or "武曲" in (h.get("keywords") or []) for h in hits)
    # Required citation fields present on every hit
    for h in hits:
        assert h.get("book")
        assert h.get("page") is not None
        assert h.get("original_text")
        assert h.get("source_reference")
        assert "keywords" in h


def test_v5_6_unaffected(require_postgres):
    """Evidence layer must not break dispatcher / weight reads."""
    route = TheoryDispatcher.get_dynamic_theory_route("entrepreneurship")
    assert route.get("theories")
    weights = WeightOptimizer.list_weights("entrepreneurship")
    assert weights
    # Layer flag documents non-interference
    payload = EvidenceService.evidence_for_entities(palaces=["命宫"], limit=3)
    assert payload["affects_v5_6_dispatch"] is False
    assert payload["layer"] == "classical_evidence"
