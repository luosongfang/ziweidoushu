"""PDF processor data models — raw extraction only."""

from __future__ import annotations

from pydantic import BaseModel, Field


class PDFBook(BaseModel):
    book_name: str
    file_name: str
    file_path: str
    total_pages: int = 0


class PDFPage(BaseModel):
    book_name: str
    page_number: int
    content: str = ""
    source_file: str = ""


class ExtractSummary(BaseModel):
    books: int = 0
    pages: int = 0
    characters: int = 0
    output_dir: str = ""
    books_detail: list[dict] = Field(default_factory=list)
