"""Save / load decision feedback rows."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import text

from app.database.database import SessionLocal

_VALID_TYPES = {"helpful", "not_helpful", "partially_helpful", "future_check"}
_VALID_STATUS = {"pending", "confirmed", "changed", "unknown"}


def parse_user_id(user_id: str | uuid.UUID | None) -> uuid.UUID | None:
    if user_id is None:
        return None
    if isinstance(user_id, uuid.UUID):
        return user_id
    try:
        return uuid.UUID(str(user_id))
    except (ValueError, TypeError):
        return uuid.uuid5(uuid.NAMESPACE_DNS, f"ziwei.user:{user_id}")


class FeedbackService:
    """Persist user feedback on decision advice."""

    @classmethod
    def save_feedback(
        cls,
        *,
        user_id: str | uuid.UUID,
        feedback_type: str,
        feedback_content: str | None = None,
        decision_history_id: str | uuid.UUID | None = None,
        result_status: str = "pending",
    ) -> dict[str, Any]:
        uid = parse_user_id(user_id)
        if uid is None:
            raise ValueError("invalid user_id")
        ftype = (feedback_type or "").strip()
        if ftype not in _VALID_TYPES:
            raise ValueError(f"feedback_type must be one of {_VALID_TYPES}")
        status = (result_status or "pending").strip()
        if status not in _VALID_STATUS:
            status = "pending"

        hid = None
        if decision_history_id:
            try:
                hid = str(uuid.UUID(str(decision_history_id)))
            except Exception:
                hid = None

        db = SessionLocal()
        try:
            row = db.execute(
                text(
                    """
                    INSERT INTO public.decision_feedback
                        (user_id, decision_history_id, feedback_type, feedback_content, result_status)
                    VALUES
                        (CAST(:uid AS uuid),
                         CASE WHEN :hid IS NULL THEN NULL ELSE CAST(:hid AS uuid) END,
                         :ftype, :content, :status)
                    RETURNING id::text, created_at
                    """
                ),
                {
                    "uid": str(uid),
                    "hid": hid,
                    "ftype": ftype,
                    "content": (feedback_content or "")[:2000] or None,
                    "status": status,
                },
            ).mappings().first()
            db.commit()
            return {
                "id": row["id"] if row else None,
                "user_id": str(uid),
                "decision_history_id": hid,
                "feedback_type": ftype,
                "feedback_content": feedback_content,
                "result_status": status,
                "created_at": row["created_at"].isoformat() if row and row.get("created_at") else None,
                "saved": True,
            }
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    @classmethod
    def list_feedback(cls, user_id: str | uuid.UUID, *, limit: int = 50) -> list[dict[str, Any]]:
        uid = parse_user_id(user_id)
        if uid is None:
            return []
        db = SessionLocal()
        try:
            rows = db.execute(
                text(
                    """
                    SELECT id::text, user_id::text, decision_history_id::text,
                           feedback_type, feedback_content, result_status, created_at
                    FROM public.decision_feedback
                    WHERE user_id = :uid
                    ORDER BY created_at DESC
                    LIMIT :lim
                    """
                ),
                {"uid": str(uid), "lim": limit},
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

    @classmethod
    def delete_user_data(cls, user_id: str | uuid.UUID) -> None:
        uid = parse_user_id(user_id)
        if uid is None:
            return
        db = SessionLocal()
        try:
            db.execute(text("DELETE FROM public.decision_feedback WHERE user_id = :uid"), {"uid": str(uid)})
            db.execute(text("DELETE FROM public.user_decision_profile WHERE user_id = :uid"), {"uid": str(uid)})
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()
