"""Knowledge Core 健康检查 — V1.3。"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from sqlalchemy import text

from app.database.database import SessionLocal, is_database_ready

logger = logging.getLogger(__name__)
BACKEND = Path(__file__).resolve().parents[3]
PDF_DIR = BACKEND / "app" / "knowledge" / "pdf"


class KnowledgeHealthChecker:
    @classmethod
    def check(cls) -> dict[str, Any]:
        pdf_count = cls._count_pdfs()
        db_counts = cls._db_counts()
        healthy = db_counts.get("chunks", 0) > 0 or pdf_count > 0
        return {
            "healthy": healthy,
            "pdf_count": pdf_count,
            "books_count": db_counts.get("books", 0),
            "chunks_count": db_counts.get("chunks", 0),
            "citations_count": db_counts.get("citations", 0),
            "graph_nodes_count": db_counts.get("graph_nodes", 0),
            "details": db_counts,
        }

    @staticmethod
    def _count_pdfs() -> int:
        try:
            if not PDF_DIR.exists():
                return 0
            return len(list(PDF_DIR.glob("*.pdf")))
        except Exception:
            return 0

    @classmethod
    def _db_counts(cls) -> dict[str, int]:
        if not is_database_ready():
            return {"books": 0, "chunks": 0, "citations": 0, "graph_nodes": 0}
        counts = {"books": 0, "chunks": 0, "citations": 0, "graph_nodes": 0}
        queries = {
            "books": "SELECT COUNT(*) FROM public.knowledge_books",
            "chunks": "SELECT COUNT(*) FROM public.knowledge_chunks",
            "citations": "SELECT COUNT(*) FROM public.knowledge_citations",
            "graph_nodes": "SELECT COUNT(*) FROM public.knowledge_graph_nodes",
        }
        db = SessionLocal()
        try:
            for key, sql in queries.items():
                try:
                    counts[key] = int(db.execute(text(sql)).scalar() or 0)
                except Exception:
                    counts[key] = 0
            return counts
        finally:
            db.close()
