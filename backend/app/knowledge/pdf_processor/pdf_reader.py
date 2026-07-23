"""PDFReader — scan / read / extract text page-by-page (no AI)."""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path

from app.knowledge.pdf_processor.pdf_models import PDFBook, PDFPage

logger = logging.getLogger(__name__)

# Project defaults
PROJECT_ROOT = Path(__file__).resolve().parents[4]  # E:\ziweixai
DEFAULT_PDF_DIR = PROJECT_ROOT / "knowledge" / "books" / "pdf_original"
DEFAULT_OUT_DIR = PROJECT_ROOT / "knowledge" / "books" / "extracted_text"


def _safe_book_slug(name: str) -> str:
    """Filesystem-safe book name for output files."""
    slug = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", name).strip().rstrip(".")
    slug = re.sub(r"\s+", "_", slug)
    return slug[:80] or "book"


class PDFReader:
    """Scan pdf_original and extract page text via PyMuPDF (fallback: pdfplumber)."""

    def __init__(
        self,
        pdf_dir: str | Path | None = None,
        output_dir: str | Path | None = None,
    ) -> None:
        self.pdf_dir = Path(pdf_dir) if pdf_dir else DEFAULT_PDF_DIR
        self.output_dir = Path(output_dir) if output_dir else DEFAULT_OUT_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def scan_pdfs(self) -> list[Path]:
        if not self.pdf_dir.exists():
            logger.warning("PDF directory missing: %s", self.pdf_dir)
            return []
        # Windows is case-insensitive: *.pdf and *.PDF would double-count
        by_key: dict[str, Path] = {}
        for pattern in ("*.pdf", "*.PDF"):
            for path in self.pdf_dir.glob(pattern):
                by_key[str(path.resolve()).lower()] = path
        return sorted(by_key.values(), key=lambda p: p.name.lower())

    def book_from_path(self, path: Path) -> PDFBook:
        total = self.count_pages(path)
        return PDFBook(
            book_name=path.stem,
            file_name=path.name,
            file_path=str(path.resolve()),
            total_pages=total,
        )

    def count_pages(self, path: Path) -> int:
        try:
            import fitz  # PyMuPDF

            with fitz.open(path) as doc:
                return int(doc.page_count)
        except Exception as exc:  # noqa: BLE001
            logger.debug("PyMuPDF count failed for %s: %s", path.name, exc)
        try:
            import pdfplumber

            with pdfplumber.open(path) as pdf:
                return len(pdf.pages)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Cannot count pages for %s: %s", path.name, exc)
            return 0

    def extract_page_text(self, path: Path, page_index: int) -> str:
        """Extract one page (0-based index). Raw text only — no rewrite."""
        text = self._extract_pymupdf(path, page_index)
        if text is not None:
            return text
        text = self._extract_pdfplumber(path, page_index)
        return text or ""

    def _extract_pymupdf(self, path: Path, page_index: int) -> str | None:
        try:
            import fitz

            with fitz.open(path) as doc:
                if page_index < 0 or page_index >= doc.page_count:
                    return ""
                page = doc.load_page(page_index)
                return page.get_text("text") or ""
        except Exception as exc:  # noqa: BLE001
            logger.debug("PyMuPDF extract failed %s p%s: %s", path.name, page_index, exc)
            return None

    def _extract_pdfplumber(self, path: Path, page_index: int) -> str | None:
        try:
            import pdfplumber

            with pdfplumber.open(path) as pdf:
                if page_index < 0 or page_index >= len(pdf.pages):
                    return ""
                page = pdf.pages[page_index]
                return page.extract_text() or ""
        except Exception as exc:  # noqa: BLE001
            logger.warning("pdfplumber extract failed %s p%s: %s", path.name, page_index, exc)
            return None

    def extract_book_pages(self, path: Path) -> list[PDFPage]:
        book = self.book_from_path(path)
        pages: list[PDFPage] = []
        for i in range(book.total_pages):
            content = self.extract_page_text(path, i)
            pages.append(
                PDFPage(
                    book_name=book.book_name,
                    page_number=i + 1,
                    content=content,
                    source_file=book.file_name,
                )
            )
        return pages

    def save_page_json(self, page: PDFPage) -> Path:
        slug = _safe_book_slug(page.book_name)
        out = self.output_dir / f"{slug}_page_{page.page_number:03d}.json"
        payload = {
            "book_name": page.book_name,
            "page_number": page.page_number,
            "content": page.content,
            "source_file": page.source_file,
        }
        out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return out

    def extract_and_save_book(self, path: Path) -> dict:
        pages = self.extract_book_pages(path)
        saved = 0
        chars = 0
        for page in pages:
            self.save_page_json(page)
            saved += 1
            chars += len(page.content or "")
        return {
            "book_name": path.stem,
            "file_name": path.name,
            "pages": saved,
            "characters": chars,
        }
