"""Extract service — orchestrate PDF → raw JSON pages."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from app.knowledge.pdf_processor.pdf_models import ExtractSummary
from app.knowledge.pdf_processor.pdf_reader import (
    DEFAULT_OUT_DIR,
    DEFAULT_PDF_DIR,
    PROJECT_ROOT,
    PDFReader,
)

logger = logging.getLogger(__name__)


class ExtractService:
    """PDF directory → PDFReader → page JSON files."""

    def __init__(
        self,
        pdf_dir: str | Path | None = None,
        output_dir: str | Path | None = None,
    ) -> None:
        self.reader = PDFReader(pdf_dir=pdf_dir, output_dir=output_dir)

    def extract_all_books(self) -> ExtractSummary:
        pdfs = self.reader.scan_pdfs()
        details: list[dict] = []
        total_pages = 0
        total_chars = 0

        for path in pdfs:
            logger.info("Extracting: %s", path.name)
            try:
                detail = self.reader.extract_and_save_book(path)
            except Exception as exc:  # noqa: BLE001
                logger.exception("Failed to extract %s", path.name)
                detail = {
                    "book_name": path.stem,
                    "file_name": path.name,
                    "pages": 0,
                    "characters": 0,
                    "error": str(exc),
                }
            details.append(detail)
            total_pages += int(detail.get("pages") or 0)
            total_chars += int(detail.get("characters") or 0)

        summary = ExtractSummary(
            books=len(pdfs),
            pages=total_pages,
            characters=total_chars,
            output_dir=str(self.reader.output_dir.resolve()),
            books_detail=details,
        )

        meta_dir = PROJECT_ROOT / "knowledge" / "metadata"
        meta_dir.mkdir(parents=True, exist_ok=True)
        meta_path = meta_dir / "extract_summary.json"
        meta_path.write_text(
            json.dumps(summary.model_dump(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return summary


def extract_all_books(
    pdf_dir: str | Path | None = None,
    output_dir: str | Path | None = None,
) -> dict:
    """Module-level entry used by scripts and tests."""
    service = ExtractService(pdf_dir=pdf_dir or DEFAULT_PDF_DIR, output_dir=output_dir or DEFAULT_OUT_DIR)
    return service.extract_all_books().model_dump()
