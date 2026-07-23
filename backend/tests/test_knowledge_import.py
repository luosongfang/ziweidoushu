"""Knowledge Core V3.0 Phase1 — import tests (no LLM)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from sqlalchemy import create_engine, text

from app.config import settings
from app.database.database import is_database_ready
from app.knowledge.importer.chunk_processor import build_chunks_for_page
from app.knowledge.importer.knowledge_importer import (
    KnowledgeImporter,
    apply_migration,
    scan_extracted_json,
)
from app.knowledge.importer.metadata_extractor import extract_tags
from app.knowledge.pdf_processor.pdf_reader import DEFAULT_OUT_DIR

PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXTRACTED = DEFAULT_OUT_DIR


@pytest.fixture(scope="module")
def require_postgres():
    if not settings.is_postgres:
        pytest.skip("requires PostgreSQL / Supabase")
    if not is_database_ready():
        pytest.skip("database not ready")


@pytest.fixture(scope="module")
def engine(require_postgres):
    url = settings.database_url
    if url.startswith("postgresql") and "sslmode=" not in url:
        url = f"{url}{'&' if '?' in url else '?'}sslmode=require"
    eng = create_engine(url, pool_pre_ping=True)
    apply_migration(eng)
    return eng


def test_asset_tables_exist(engine):
    with engine.connect() as conn:
        for table in (
            "knowledge_books",
            "knowledge_documents",
            "knowledge_chunks",
            "knowledge_relations",
            "knowledge_citations",
        ):
            exists = conn.execute(
                text("SELECT to_regclass(:t)"),
                {"t": f"public.{table}"},
            ).scalar()
            assert exists is not None, table


def test_extracted_json_readable():
    assert EXTRACTED.exists()
    files = list(EXTRACTED.glob("*.json"))
    assert len(files) >= 1000
    sample = json.loads(files[0].read_text(encoding="utf-8"))
    assert "book_name" in sample
    assert "page_number" in sample
    assert "content" in sample


def test_scan_finds_16_books():
    books = scan_extracted_json(EXTRACTED)
    assert len(books) == 16


def test_chunk_generation_and_tags():
    text_body = "紫微天府同宫，命宫与官禄宫互参，兼论化禄化权。杀破狼主变。" * 40
    chunks = build_chunks_for_page(
        book_name="测试书",
        page_number=23,
        content=text_body,
        chapter="紫微星",
    )
    assert len(chunks) >= 1
    assert all(1000 <= len(c.content) <= 1600 or c is chunks[-1] for c in chunks[:-1]) or len(chunks) == 1
    for c in chunks:
        assert c.source_reference["book"] == "测试书"
        assert c.source_reference["page"] == 23
        assert "紫微" in c.star_tags or "紫微" in c.content
        assert c.content  # original text preserved as substring
        assert text_body.find(c.content) >= 0


def test_metadata_extractor_tags_only():
    tags = extract_tags("天机在迁移，机月同梁，化忌提示压力。")
    assert "天机" in tags["star_tags"]
    assert "迁移" in tags["palace_tags"]
    assert "机月同梁" in tags["pattern_tags"]
    assert "化忌" in tags["keywords"]


def test_import_one_book_smoke(engine, tmp_path):
    # build tiny extracted set from real sample pages of one book
    books = scan_extracted_json(EXTRACTED)
    book_name, pages = next(iter(books.items()))
    sample_pages = pages[:3]
    work = tmp_path / "extracted"
    work.mkdir()
    for p in sample_pages:
        out = {
            "book_name": book_name,
            "page_number": p["page_number"],
            "content": p.get("content") or "",
            "source_file": p.get("source_file") or f"{book_name}.pdf",
        }
        fname = f"smoke_page_{int(p['page_number']):03d}.json"
        (work / fname).write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")

    importer = KnowledgeImporter(extracted_dir=work, reimport=True)
    # use same engine URL via env; import_all creates own engine
    summary = importer.import_all()
    assert summary["books"] == 1
    assert summary["chunks"] >= 1 or summary["characters"] == 0
    assert summary["documents"] >= 1

    with engine.connect() as conn:
        n_books = conn.execute(text("SELECT COUNT(*) FROM public.knowledge_books")).scalar()
        assert n_books >= 1
        row = conn.execute(
            text(
                """
                SELECT content, page_number, source_reference
                FROM public.knowledge_chunks
                ORDER BY created_at DESC
                LIMIT 1
                """
            )
        ).mappings().first()
        if row:
            assert row["content"] is not None
            ref = row["source_reference"]
            if isinstance(ref, str):
                ref = json.loads(ref)
            assert ref.get("book")
            assert "page" in ref


def test_phase1_acceptance_if_fully_imported(engine):
    """When full import has run: books>=16, chunks>1000, chunk fields present."""
    with engine.connect() as conn:
        n_books = conn.execute(text("SELECT COUNT(*) FROM public.knowledge_books")).scalar()
        n_chunks = conn.execute(text("SELECT COUNT(*) FROM public.knowledge_chunks")).scalar()
        if n_books < 16 or n_chunks <= 1000:
            pytest.skip("full Phase1 import not present yet")
        row = conn.execute(
            text(
                """
                SELECT content, page_number, source_reference
                FROM public.knowledge_chunks
                WHERE content IS NOT NULL AND length(content) > 0
                LIMIT 1
                """
            )
        ).mappings().one()
        ref = row["source_reference"]
        if isinstance(ref, str):
            ref = json.loads(ref)
        assert row["content"]
        assert row["page_number"] is not None
        assert ref.get("book")
        assert "page" in ref
        assert "chapter" in ref
