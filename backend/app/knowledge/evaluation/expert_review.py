"""Expert review scoring records (process quality, not destiny accuracy)."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import text

from app.database.database import SessionLocal


def _clamp_score(v: Any, default: int = 0) -> int:
    try:
        n = int(v)
    except (TypeError, ValueError):
        n = default
    return max(0, min(100, n))


class ExpertReview:
    """Store expert / internal review scores on cases or analyses."""

    @classmethod
    def submit(
        cls,
        *,
        case_id: str | None = None,
        reviewer_type: str = "internal",
        review_score: int | None = None,
        logic_score: int | None = None,
        safety_score: int | None = None,
        value_score: int | None = None,
        comments: str | None = None,
    ) -> dict[str, Any]:
        # theory basis uses review_score field as "理论依据" dimension
        theory = _clamp_score(review_score, 0) if review_score is not None else None
        logic = _clamp_score(logic_score, 0) if logic_score is not None else None
        safety = _clamp_score(safety_score, 0) if safety_score is not None else None
        value = _clamp_score(value_score, 0) if value_score is not None else None

        scores = [s for s in (theory, logic, safety, value) if s is not None]
        if not scores:
            raise ValueError("at least one score required")

        # if overall review_score omitted, average available
        if theory is None:
            theory = int(round(sum(scores) / len(scores)))

        cid = None
        if case_id:
            try:
                cid = str(uuid.UUID(str(case_id)))
            except Exception as exc:
                raise ValueError("invalid case_id") from exc

        db = SessionLocal()
        try:
            row = db.execute(
                text(
                    """
                    INSERT INTO public.expert_review_records
                        (case_id, reviewer_type, review_score, logic_score,
                         safety_score, value_score, comments)
                    VALUES
                        (CASE WHEN :cid IS NULL THEN NULL ELSE CAST(:cid AS uuid) END,
                         :rtype, :review, :logic, :safety, :value, :comments)
                    RETURNING id::text, created_at
                    """
                ),
                {
                    "cid": cid,
                    "rtype": reviewer_type or "internal",
                    "review": theory,
                    "logic": logic if logic is not None else theory,
                    "safety": safety if safety is not None else theory,
                    "value": value if value is not None else theory,
                    "comments": (comments or "")[:2000] or None,
                },
            ).mappings().first()
            db.commit()
            return {
                "id": row["id"] if row else None,
                "case_id": cid,
                "reviewer_type": reviewer_type or "internal",
                "theory_score": theory,
                "review_score": theory,
                "logic_score": logic if logic is not None else theory,
                "safety_score": safety if safety is not None else theory,
                "value_score": value if value is not None else theory,
                "comments": comments,
                "saved": True,
            }
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    @classmethod
    def list_for_case(cls, case_id: str) -> list[dict[str, Any]]:
        db = SessionLocal()
        try:
            rows = db.execute(
                text(
                    """
                    SELECT id::text, case_id::text, reviewer_type, review_score,
                           logic_score, safety_score, value_score, comments, created_at
                    FROM public.expert_review_records
                    WHERE case_id = CAST(:cid AS uuid)
                    ORDER BY created_at DESC
                    """
                ),
                {"cid": case_id},
            ).mappings().all()
            out = []
            for r in rows:
                item = dict(r)
                if item.get("created_at"):
                    item["created_at"] = item["created_at"].isoformat()
                out.append(item)
            return out
        finally:
            db.close()
