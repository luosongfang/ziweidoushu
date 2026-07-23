"""Build knowledge_trace — visible citation / reasoning path (no LLM)."""

from __future__ import annotations

import json
import uuid
from typing import Any

from sqlalchemy import text

from app.database.database import SessionLocal


class ReferenceMapper:
    """Map analysis outputs to a user-visible knowledge_trace."""

    @classmethod
    def build_trace(
        cls,
        *,
        decision_analysis: dict[str, Any] | None = None,
        theory_analysis: dict[str, Any] | None = None,
        sources: list[dict[str, Any]] | None = None,
        stars: list[str] | None = None,
        theory_used: list[str] | None = None,
        selected_knowledge: list[dict[str, Any]] | None = None,
        persist: bool = False,
        analysis_type: str = "decision",
    ) -> dict[str, Any]:
        da = decision_analysis or {}
        ta = theory_analysis or {}
        entities: list[str] = []
        for s in stars or []:
            if s and s not in entities:
                entities.append(s)
        # extract from dimension sources / traditional factors
        for src in da.get("sources") or []:
            factor = src.get("factor") or src.get("entity") or src.get("name")
            if factor and str(factor) not in entities:
                entities.append(str(factor))

        books: list[dict[str, Any]] = []
        seen_books: set[tuple[Any, Any]] = set()

        def _add_book(name: Any, page: Any = None, chunk_id: Any = None) -> None:
            if not name:
                return
            key = (str(name), str(page) if page is not None else "")
            if key in seen_books:
                return
            seen_books.add(key)
            books.append(
                {
                    "name": str(name),
                    "page": str(page) if page is not None else "",
                    "chunk_id": str(chunk_id) if chunk_id else None,
                }
            )

        for s in sources or []:
            _add_book(s.get("book") or s.get("book_name") or s.get("name"), s.get("page") or s.get("page_number"))
        for ch in selected_knowledge or []:
            cite = ch.get("citation") or {}
            _add_book(
                cite.get("book") or ch.get("book_name") or ch.get("book_source"),
                cite.get("page") or ch.get("page_number"),
                ch.get("id") or ch.get("chunk_id"),
            )
            for tag in (ch.get("star_tags") or [])[:3]:
                if tag and tag not in entities:
                    entities.append(str(tag))
        for src in da.get("sources") or []:
            _add_book(src.get("source_reference") or src.get("book"), src.get("page"))

        theory_label = "、".join(theory_used or []) or "三合紫微"
        if "三合" not in theory_label and any(
            "三合" in str(t) for t in (theory_used or [])
        ):
            theory_label = "三合紫微"
        if entities and ("紫微" in entities or "天府" in entities):
            if "紫微" in theory_label or True:
                theory_label = theory_label if "紫微" in theory_label else f"{theory_label}·紫微结构"

        reasoning_path: list[str] = []
        if da.get("scenario"):
            reasoning_path.append(f"识别决策场景：{da.get('scenario')}")
        if ta.get("sanhe", {}).get("summary"):
            reasoning_path.append(f"三合观察：{str(ta['sanhe']['summary'])[:80]}")
        if ta.get("four_transform", {}).get("summary"):
            reasoning_path.append(f"四化观察：{str(ta['four_transform']['summary'])[:80]}")
        if da.get("traditional_view", {}).get("cycle"):
            reasoning_path.append(f"周期观察：{str(da['traditional_view']['cycle'])[:80]}")
        if entities:
            reasoning_path.append(f"关键实体：{'、'.join(entities[:6])}")
        if books:
            reasoning_path.append(
                f"知识来源：{books[0]['name']}"
                + (f" 第{books[0]['page']}页" if books[0].get("page") else "")
            )
        if da.get("strengths"):
            reasoning_path.append(f"优势提炼：{da['strengths'][0][:60]}")
        if da.get("action_suggestions"):
            reasoning_path.append(f"行动建议来自规则模板与维度映射：{da['action_suggestions'][0][:60]}")
        reasoning_path.append("结论定位：传统文化学习 + 人生规划辅助，不作绝对预测。")

        trace = {
            "theory": theory_label if "三合" in theory_label or "紫微" in theory_label else f"三合紫微·{theory_label}",
            "entities": entities[:12],
            "books": books[:8],
            "reasoning_path": reasoning_path[:12],
        }

        # ensure theory readable default
        if not trace["theory"] or trace["theory"] == "·":
            trace["theory"] = "三合紫微"

        if persist:
            cls.persist_map(trace, analysis_type=analysis_type)

        return trace

    @classmethod
    def persist_map(cls, trace: dict[str, Any], *, analysis_type: str = "decision") -> int:
        db = SessionLocal()
        n = 0
        try:
            for ent in trace.get("entities") or []:
                db.execute(
                    text(
                        """
                        INSERT INTO public.knowledge_reference_map
                            (analysis_type, entity_type, entity_id, relationship, weight)
                        VALUES
                            (:atype, 'star_or_factor', :eid, 'supports_analysis', 1.0)
                        """
                    ),
                    {"atype": analysis_type, "eid": str(ent)},
                )
                n += 1
            for book in trace.get("books") or []:
                chunk = book.get("chunk_id")
                db.execute(
                    text(
                        """
                        INSERT INTO public.knowledge_reference_map
                            (analysis_type, entity_type, entity_id, source_book, source_page,
                             source_chunk_id, relationship, weight)
                        VALUES
                            (:atype, 'book', :eid, :book, :page,
                             CAST(:chunk AS uuid), 'cited_by', 1.0)
                        """
                    ),
                    {
                        "atype": analysis_type,
                        "eid": str(book.get("name") or ""),
                        "book": book.get("name"),
                        "page": book.get("page") or None,
                        "chunk": chunk if chunk else None,
                    },
                )
                n += 1
            db.commit()
            return n
        except Exception:
            db.rollback()
            # retry books without chunk cast if null issues
            try:
                for book in trace.get("books") or []:
                    db.execute(
                        text(
                            """
                            INSERT INTO public.knowledge_reference_map
                                (analysis_type, entity_type, entity_id, source_book, source_page,
                                 relationship, weight)
                            VALUES
                                (:atype, 'book', :eid, :book, :page, 'cited_by', 1.0)
                            """
                        ),
                        {
                            "atype": analysis_type,
                            "eid": str(book.get("name") or ""),
                            "book": book.get("name"),
                            "page": book.get("page") or None,
                        },
                    )
                    n += 1
                db.commit()
            except Exception:
                db.rollback()
            return n
        finally:
            db.close()
