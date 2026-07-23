"""Case library management for expert evaluation (no PII, no LLM)."""

from __future__ import annotations

import json
import uuid
from typing import Any

from sqlalchemy import text

from app.database.database import SessionLocal
from app.knowledge.evaluation.seed_cases import SEED_CASES

_VALID_LEVELS = {"classic", "expert_reviewed", "community_feedback"}


class CaseLibrary:
    """CRUD for ziwei_case_library."""

    @classmethod
    def save_case(cls, payload: dict[str, Any]) -> dict[str, Any]:
        name = (payload.get("case_name") or "").strip()
        if not name:
            raise ValueError("case_name required")
        level = payload.get("verification_level") or "classic"
        if level not in _VALID_LEVELS:
            level = "classic"

        # reject obvious PII patterns in summary
        summary = str(payload.get("birth_info_summary") or "")
        for bad in ("身份证", "手机号", "真实姓名", "@"):
            if bad in summary:
                raise ValueError("birth_info_summary must not contain personal privacy")

        db = SessionLocal()
        try:
            row = db.execute(
                text(
                    """
                    INSERT INTO public.ziwei_case_library
                        (case_name, birth_info_summary, chart_features, main_patterns,
                         life_stage, question_type, analysis_reference, case_source,
                         verification_level)
                    VALUES
                        (:name, :summary, CAST(:features AS jsonb), CAST(:patterns AS jsonb),
                         :stage, :qtype, CAST(:aref AS jsonb), :source, :level)
                    RETURNING id::text, created_at
                    """
                ),
                {
                    "name": name,
                    "summary": summary or "匿名教学案例",
                    "features": json.dumps(payload.get("chart_features") or {}, ensure_ascii=False),
                    "patterns": json.dumps(payload.get("main_patterns") or [], ensure_ascii=False),
                    "stage": payload.get("life_stage"),
                    "qtype": payload.get("question_type"),
                    "aref": json.dumps(payload.get("analysis_reference") or {}, ensure_ascii=False),
                    "source": payload.get("case_source") or "manual",
                    "level": level,
                },
            ).mappings().first()
            db.commit()
            return {
                "id": row["id"] if row else None,
                "case_name": name,
                "verification_level": level,
                "saved": True,
            }
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    @classmethod
    def list_cases(
        cls,
        *,
        question_type: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        db = SessionLocal()
        try:
            if question_type:
                rows = db.execute(
                    text(
                        """
                        SELECT id::text, case_name, birth_info_summary, chart_features,
                               main_patterns, life_stage, question_type, analysis_reference,
                               case_source, verification_level, created_at
                        FROM public.ziwei_case_library
                        WHERE question_type = :qtype
                        ORDER BY created_at DESC
                        LIMIT :lim
                        """
                    ),
                    {"qtype": question_type, "lim": limit},
                ).mappings().all()
            else:
                rows = db.execute(
                    text(
                        """
                        SELECT id::text, case_name, birth_info_summary, chart_features,
                               main_patterns, life_stage, question_type, analysis_reference,
                               case_source, verification_level, created_at
                        FROM public.ziwei_case_library
                        ORDER BY created_at DESC
                        LIMIT :lim
                        """
                    ),
                    {"lim": limit},
                ).mappings().all()
            out = []
            for r in rows:
                item = dict(r)
                for k in ("chart_features", "main_patterns", "analysis_reference"):
                    v = item.get(k)
                    if isinstance(v, str):
                        item[k] = json.loads(v)
                if item.get("created_at"):
                    item["created_at"] = item["created_at"].isoformat()
                out.append(item)
            return out
        finally:
            db.close()

    @classmethod
    def get_case(cls, case_id: str) -> dict[str, Any] | None:
        db = SessionLocal()
        try:
            row = db.execute(
                text(
                    """
                    SELECT id::text, case_name, birth_info_summary, chart_features,
                           main_patterns, life_stage, question_type, analysis_reference,
                           case_source, verification_level, created_at
                    FROM public.ziwei_case_library
                    WHERE id = CAST(:cid AS uuid)
                    """
                ),
                {"cid": case_id},
            ).mappings().first()
            if not row:
                return None
            item = dict(row)
            for k in ("chart_features", "main_patterns", "analysis_reference"):
                v = item.get(k)
                if isinstance(v, str):
                    item[k] = json.loads(v)
            if item.get("created_at"):
                item["created_at"] = item["created_at"].isoformat()
            return item
        finally:
            db.close()

    @classmethod
    def seed_defaults(cls, *, clear: bool = False) -> int:
        db = SessionLocal()
        try:
            if clear:
                db.execute(text("DELETE FROM public.expert_review_records"))
                db.execute(text("DELETE FROM public.ziwei_case_library"))
            existing = db.execute(text("SELECT COUNT(*) FROM public.ziwei_case_library")).scalar()
            if int(existing or 0) > 0 and not clear:
                return int(existing)
            n = 0
            for case in SEED_CASES:
                db.execute(
                    text(
                        """
                        INSERT INTO public.ziwei_case_library
                            (case_name, birth_info_summary, chart_features, main_patterns,
                             life_stage, question_type, analysis_reference, case_source,
                             verification_level)
                        VALUES
                            (:name, :summary, CAST(:features AS jsonb), CAST(:patterns AS jsonb),
                             :stage, :qtype, CAST(:aref AS jsonb), :source, :level)
                        """
                    ),
                    {
                        "name": case["case_name"],
                        "summary": case.get("birth_info_summary"),
                        "features": json.dumps(case.get("chart_features") or {}, ensure_ascii=False),
                        "patterns": json.dumps(case.get("main_patterns") or [], ensure_ascii=False),
                        "stage": case.get("life_stage"),
                        "qtype": case.get("question_type"),
                        "aref": json.dumps(case.get("analysis_reference") or {}, ensure_ascii=False),
                        "source": case.get("case_source"),
                        "level": case.get("verification_level") or "classic",
                    },
                )
                n += 1
            db.commit()
            return n
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    @classmethod
    def count(cls) -> int:
        db = SessionLocal()
        try:
            return int(db.execute(text("SELECT COUNT(*) FROM public.ziwei_case_library")).scalar() or 0)
        finally:
            db.close()
