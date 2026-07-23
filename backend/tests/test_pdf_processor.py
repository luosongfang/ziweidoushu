"""PDF Processor V1.0 tests — raw extract only (no AI)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.knowledge.pdf_processor.extract_service import ExtractService, extract_all_books
from app.knowledge.pdf_processor.pdf_models import PDFBook, PDFPage
from app.knowledge.pdf_processor.pdf_reader import DEFAULT_OUT_DIR, DEFAULT_PDF_DIR, PDFReader

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def pdf_dir() -> Path:
    return DEFAULT_PDF_DIR


@pytest.fixture(scope="module")
def reader(pdf_dir: Path, tmp_path_factory) -> PDFReader:
    out = tmp_path_factory.mktemp("extracted_text")
    return PDFReader(pdf_dir=pdf_dir, output_dir=out)


def test_pdf_directory_exists(pdf_dir: Path):
    assert pdf_dir.exists(), f"missing PDF dir: {pdf_dir}"
    assert pdf_dir.is_dir()


def test_pdf_count_is_16(pdf_dir: Path):
    reader = PDFReader(pdf_dir=pdf_dir)
    pdfs = reader.scan_pdfs()
    assert len(pdfs) == 16, f"expected 16 PDFs, got {len(pdfs)}"


def test_scan_pdfs(reader: PDFReader):
    files = reader.scan_pdfs()
    assert len(files) == 16
    for f in files:
        assert f.suffix.lower() == ".pdf"
        assert f.stat().st_size > 0


def test_book_metadata_and_page_count(reader: PDFReader):
    files = reader.scan_pdfs()
    book = reader.book_from_path(files[0])
    assert isinstance(book, PDFBook)
    assert book.book_name
    assert book.file_name.endswith(".pdf")
    assert book.total_pages >= 1
    assert Path(book.file_path).exists()


def test_extract_single_page_raw(reader: PDFReader):
    files = reader.scan_pdfs()
    # Prefer a text-layer PDF if possible: try first few pages across books
    content = ""
    chosen = files[0]
    for f in files:
        text = reader.extract_page_text(f, 0)
        if text and text.strip():
            content = text
            chosen = f
            break
    assert isinstance(content, str)
    page = PDFPage(
        book_name=chosen.stem,
        page_number=1,
        content=content,
        source_file=chosen.name,
    )
    out = reader.save_page_json(page)
    assert out.exists()
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["book_name"] == chosen.stem
    assert data["page_number"] == 1
    assert "content" in data
    assert data["source_file"] == chosen.name
    # raw extract: no AI fields
    assert "summary" not in data
    assert "interpretation" not in data


def test_extract_and_save_one_book_json(pdf_dir: Path, tmp_path: Path):
    reader = PDFReader(pdf_dir=pdf_dir, output_dir=tmp_path / "book_out")
    files = reader.scan_pdfs()
    target = min(files, key=lambda p: p.stat().st_size)
    detail = reader.extract_and_save_book(target)
    assert detail["pages"] >= 1
    assert detail["characters"] >= 0
    from app.knowledge.pdf_processor.pdf_reader import _safe_book_slug

    slug = _safe_book_slug(target.stem)
    json_files = sorted(reader.output_dir.glob(f"{slug}_page_*.json"))
    assert len(json_files) == detail["pages"]
    sample = json.loads(json_files[0].read_text(encoding="utf-8"))
    assert set(sample.keys()) >= {"book_name", "page_number", "content", "source_file"}
    total_chars = sum(
        len(json.loads(p.read_text(encoding="utf-8")).get("content") or "")
        for p in json_files
    )
    assert total_chars == detail["characters"]


def test_extract_service_summary_shape(tmp_path: Path, pdf_dir: Path):
    files = PDFReader(pdf_dir=pdf_dir).scan_pdfs()
    assert files
    smallest = min(files, key=lambda p: p.stat().st_size)
    work = tmp_path / "one"
    work.mkdir()
    dest = work / smallest.name
    dest.write_bytes(smallest.read_bytes())
    out = tmp_path / "out"
    summary = ExtractService(pdf_dir=work, output_dir=out).extract_all_books()
    assert summary.books == 1
    assert summary.pages >= 1
    assert summary.characters >= 0
    assert Path(summary.output_dir).exists()
    assert list(out.glob("*_page_*.json"))


def test_knowledge_dirs_layout():
    assert (PROJECT_ROOT / "knowledge" / "books" / "pdf_original").exists()
    assert (PROJECT_ROOT / "knowledge" / "books" / "extracted_text").exists()
    assert (PROJECT_ROOT / "knowledge" / "metadata").exists()
