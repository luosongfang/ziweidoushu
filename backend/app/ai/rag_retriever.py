"""RAG 知识检索 — 内存种子 + 关键词匹配（Sprint 7）。"""

from __future__ import annotations

from app.ai.knowledge_seed import KNOWLEDGE_SEED
from app.models.analysis import RagChunkRef


class RagRetriever:
    """
    知识检索器。

    Sprint 7：内存种子 + 关键词评分；
    后续：Supabase match_knowledge + OpenAI embedding。
    """

    @classmethod
    def retrieve(cls, queries: list[str], limit: int = 5) -> list[RagChunkRef]:
        if not queries:
            return []

        scored: list[tuple[float, dict]] = []
        query_tokens = set()
        for q in queries:
            query_tokens.update(q)

        for chunk in KNOWLEDGE_SEED:
            score = cls._score_chunk(chunk, queries, query_tokens)
            if score > 0:
                scored.append((score, chunk))

        scored.sort(key=lambda x: x[0], reverse=True)
        results: list[RagChunkRef] = []
        for score, chunk in scored[:limit]:
            results.append(RagChunkRef(
                id=chunk["id"],
                source=chunk["source"],
                category=chunk["category"],
                title=chunk.get("title"),
                content=chunk["content"],
                score=round(score, 3),
            ))
        return results

    @staticmethod
    def _score_chunk(chunk: dict, queries: list[str], query_tokens: set[str]) -> float:
        score = 0.0
        keywords = chunk.get("keywords", [])
        title = chunk.get("title", "")
        content = chunk.get("content", "")
        category = chunk.get("category", "")

        for q in queries:
            if not q:
                continue
            if q in title or q in content:
                score += 2.0
            if q in keywords:
                score += 3.0
            if q in category:
                score += 1.0
            for kw in keywords:
                if q in kw or kw in q:
                    score += 1.5

        overlap = query_tokens & set("".join(keywords))
        score += len(overlap) * 0.1
        return score
