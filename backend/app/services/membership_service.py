"""会员与积分服务 — 读写 Postgres user_membership / user_points。"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database.database import SessionLocal, is_database_ready

logger = logging.getLogger(__name__)

VALID_PLANS = frozenset({"free", "basic", "vip", "svip"})
PLAN_ADVISOR = {"free": False, "basic": False, "vip": True, "svip": True}
PLAN_ANALYSIS_QUOTA = {"free": 1, "basic": 10, "vip": None, "svip": None}
PLAN_DEFAULT_POINTS = {"free": 0, "basic": 0, "vip": 300, "svip": 9999}


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class MembershipService:
    @classmethod
    def get_status(cls, user_id: str, db: Session | None = None) -> dict[str, Any]:
        own = db is None
        db = db or SessionLocal()
        try:
            cls.ensure_user(user_id, db=db)
            row = db.execute(
                text(
                    """
                    SELECT plan_id, analysis_used, analysis_quota, advisor_enabled
                    FROM public.user_membership
                    WHERE user_id = CAST(:uid AS uuid) AND status = 'active'
                    ORDER BY updated_at DESC
                    LIMIT 1
                    """
                ),
                {"uid": user_id},
            ).mappings().first()
            balance = db.execute(
                text(
                    "SELECT balance FROM public.user_points WHERE user_id = CAST(:uid AS uuid)"
                ),
                {"uid": user_id},
            ).scalar()
            plan_id = str(row["plan_id"]) if row else "free"
            if plan_id not in VALID_PLANS:
                plan_id = "free"
            points = int(balance or 0)
            analysis_quota = row["analysis_quota"] if row else PLAN_ANALYSIS_QUOTA["free"]
            if analysis_quota is None and plan_id in {"vip", "svip"}:
                analysis_quota = 9999
            return {
                "plan_id": plan_id,
                "points": points,
                "analysis_used": int(row["analysis_used"] or 0) if row else 0,
                "analysis_quota": int(analysis_quota or 1),
                "advisor_enabled": bool(row["advisor_enabled"]) if row else PLAN_ADVISOR[plan_id],
            }
        except Exception as exc:  # noqa: BLE001
            logger.warning("读取会员状态失败，回退默认：%s", exc)
            return {
                "plan_id": "free",
                "points": 0,
                "analysis_used": 0,
                "analysis_quota": 1,
                "advisor_enabled": False,
            }
        finally:
            if own:
                db.commit()
                db.close()

    @classmethod
    def ensure_user(cls, user_id: str, db: Session | None = None) -> None:
        if not is_database_ready():
            return
        own = db is None
        db = db or SessionLocal()
        try:
            mem = db.execute(
                text(
                    """
                    SELECT id FROM public.user_membership
                    WHERE user_id = CAST(:uid AS uuid) AND status = 'active'
                    LIMIT 1
                    """
                ),
                {"uid": user_id},
            ).first()
            if not mem:
                db.execute(
                    text(
                        """
                        INSERT INTO public.user_membership
                            (user_id, plan_id, status, analysis_quota, advisor_enabled, knowledge_access)
                        VALUES
                            (CAST(:uid AS uuid), 'free', 'active', 1, false, 'none')
                        """
                    ),
                    {"uid": user_id},
                )
            pts = db.execute(
                text(
                    "SELECT id FROM public.user_points WHERE user_id = CAST(:uid AS uuid)"
                ),
                {"uid": user_id},
            ).first()
            if not pts:
                db.execute(
                    text(
                        """
                        INSERT INTO public.user_points (user_id, balance, lifetime_earned)
                        VALUES (CAST(:uid AS uuid), 0, 0)
                        """
                    ),
                    {"uid": user_id},
                )
            if own:
                db.commit()
        except Exception as exc:  # noqa: BLE001
            if own:
                db.rollback()
            logger.warning("初始化会员记录失败：%s", exc)
        finally:
            if own:
                db.close()

    @classmethod
    def set_plan_preview(cls, user_id: str, plan_id: str, db: Session | None = None) -> dict[str, Any]:
        if plan_id not in VALID_PLANS:
            raise ValueError(f"无效会员方案：{plan_id}")
        own = db is None
        db = db or SessionLocal()
        try:
            cls.ensure_user(user_id, db=db)
            target_points = PLAN_DEFAULT_POINTS[plan_id]
            advisor = PLAN_ADVISOR[plan_id]
            quota = PLAN_ANALYSIS_QUOTA[plan_id]

            db.execute(
                text(
                    """
                    UPDATE public.user_membership
                    SET plan_id = :plan_id,
                        advisor_enabled = :advisor,
                        analysis_quota = :quota,
                        knowledge_access = CASE
                            WHEN :plan_id = 'svip' THEN 'full'
                            WHEN :plan_id IN ('basic', 'vip') THEN 'partial'
                            ELSE 'none'
                        END,
                        updated_at = NOW()
                    WHERE user_id = CAST(:uid AS uuid) AND status = 'active'
                    """
                ),
                {
                    "uid": user_id,
                    "plan_id": plan_id,
                    "advisor": advisor,
                    "quota": quota,
                },
            )
            db.execute(
                text(
                    """
                    UPDATE public.user_points
                    SET balance = GREATEST(balance, :target),
                        lifetime_earned = GREATEST(lifetime_earned, :target),
                        updated_at = NOW()
                    WHERE user_id = CAST(:uid AS uuid)
                    """
                ),
                {"uid": user_id, "target": target_points},
            )
            if own:
                db.commit()
            return cls.get_status(user_id, db=db)
        except Exception:
            if own:
                db.rollback()
            raise
        finally:
            if own:
                db.close()

    @classmethod
    def consume_points(
        cls,
        user_id: str,
        amount: int,
        reason: str = "advisor_chat",
        db: Session | None = None,
    ) -> dict[str, Any]:
        own = db is None
        db = db or SessionLocal()
        try:
            status = cls.get_status(user_id, db=db)
            if status["plan_id"] == "svip":
                return {"success": True, "balance": status["points"], "message": "SVIP 不限积分"}
            balance = int(status["points"])
            if balance < amount:
                return {"success": False, "balance": balance, "message": "积分不足"}
            new_balance = balance - amount
            db.execute(
                text(
                    """
                    UPDATE public.user_points
                    SET balance = :bal, lifetime_spent = lifetime_spent + :amt, updated_at = NOW()
                    WHERE user_id = CAST(:uid AS uuid)
                    """
                ),
                {"uid": user_id, "bal": new_balance, "amt": amount},
            )
            db.execute(
                text(
                    """
                    INSERT INTO public.user_points_ledger
                        (user_id, delta, balance_after, reason)
                    VALUES (CAST(:uid AS uuid), :delta, :bal, :reason)
                    """
                ),
                {"uid": user_id, "delta": -amount, "bal": new_balance, "reason": reason},
            )
            if own:
                db.commit()
            return {"success": True, "balance": new_balance, "message": ""}
        except Exception as exc:  # noqa: BLE001
            if own:
                db.rollback()
            status = cls.get_status(user_id, db=db)
            return {"success": False, "balance": status["points"], "message": str(exc)}
        finally:
            if own:
                db.close()
