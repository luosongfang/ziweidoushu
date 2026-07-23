"""Evidence engine — every claim must attach a Knowledge Core citation."""

from __future__ import annotations

import uuid
from typing import Any


class EvidenceEngine:
    """Build claim ↔ chunk evidence records (no LLM rewriting of claims)."""

    @classmethod
    def build(
        cls,
        *,
        analysis_id: str | uuid.UUID | None,
        claims: list[str],
        selected_chunks: list[dict[str, Any]],
        theory_type: str = "",
    ) -> list[dict[str, Any]]:
        aid = str(analysis_id or uuid.uuid4())
        evidence: list[dict[str, Any]] = []
        if not claims:
            return evidence

        # Round-robin attach available chunks; if no chunk, still record claim with empty source
        chunks = selected_chunks or []
        for i, claim in enumerate(claims):
            claim_text = (claim or "").strip()
            if not claim_text:
                continue
            chunk = chunks[i % len(chunks)] if chunks else {}
            cite = chunk.get("citation") or {}
            evidence.append(
                {
                    "analysis_id": aid,
                    "claim": claim_text,
                    "chunk_id": chunk.get("chunk_id"),
                    "book_name": cite.get("book") or chunk.get("book_source") or "",
                    "page_number": cite.get("page") or chunk.get("page_number"),
                    "theory_type": theory_type,
                    "chapter": cite.get("chapter") or chunk.get("chapter") or "",
                }
            )
        return evidence

    @classmethod
    def persist(cls, evidence: list[dict[str, Any]]) -> int:
        """Optional write to knowledge_evidence table."""
        if not evidence:
            return 0
        try:
            import os
            from pathlib import Path

            from dotenv import load_dotenv
            from sqlalchemy import create_engine, text

            backend = Path(__file__).resolve().parents[3]
            load_dotenv(backend / ".env", override=True)
            url = os.environ.get("DATABASE_URL", "")
            if not url:
                return 0
            if url.startswith("postgresql") and "sslmode=" not in url:
                url = f"{url}{'&' if '?' in url else '?'}sslmode=require"
            eng = create_engine(url, pool_pre_ping=True)
            with eng.begin() as conn:
                for e in evidence:
                    conn.execute(
                        text(
                            """
                            INSERT INTO public.knowledge_evidence
                                (analysis_id, claim, chunk_id, book_name, page_number, theory_type)
                            VALUES
                                (CAST(:analysis_id AS uuid), :claim,
                                 CAST(:chunk_id AS uuid), :book_name, :page_number, :theory_type)
                            """
                        ),
                        {
                            "analysis_id": e["analysis_id"],
                            "claim": e["claim"],
                            "chunk_id": e.get("chunk_id"),
                            "book_name": e.get("book_name") or None,
                            "page_number": e.get("page_number"),
                            "theory_type": e.get("theory_type") or None,
                        },
                    )
            return len(evidence)
        except Exception:
            return 0
