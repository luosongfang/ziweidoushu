"""PDF knowledge acquisition — raw extract only (no AI rewrite)."""

from app.knowledge.pdf_processor.extract_service import ExtractService, extract_all_books
from app.knowledge.pdf_processor.pdf_models import PDFBook, PDFPage
from app.knowledge.pdf_processor.pdf_reader import PDFReader

__all__ = [
    "ExtractService",
    "PDFBook",
    "PDFPage",
    "PDFReader",
    "extract_all_books",
]
