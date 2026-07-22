"""会员与订单服务（Sprint 8）。"""

from __future__ import annotations

from uuid import UUID

from app.db.repository import Repository, get_repository
from app.models.commerce import (
    CreateOrderRequest,
    MembershipPlan,
    OrderConfirmResponse,
    OrderOutput,
)
from app.models.user import AuthUser


class CommerceService:
    @staticmethod
    def list_plans() -> list[MembershipPlan]:
        return Repository.list_plans()

    @classmethod
    def create_order(
        cls,
        user: AuthUser,
        body: CreateOrderRequest,
        repo: Repository | None = None,
    ) -> OrderOutput:
        repository = repo or get_repository()
        repository.ensure_profile(user.id, user.email)
        order = repository.create_order(user.id, body.plan_id, body.payment_provider)
        return cls._to_output(order)

    @classmethod
    def confirm_order(
        cls,
        user: AuthUser,
        order_id: UUID,
        repo: Repository | None = None,
    ) -> OrderConfirmResponse:
        repository = repo or get_repository()
        order, profile = repository.confirm_order(order_id, user.id)
        plan = Repository.list_plans()
        plan_name = next(p.name for p in plan if p.id == order.plan_id)
        return OrderConfirmResponse(
            order=cls._to_output(order),
            profile_membership=profile.membership,
            ai_quota=profile.ai_quota,
            message=f"已成功开通{plan_name}，AI 解读次数已充值。",
        )

    @staticmethod
    def _to_output(order) -> OrderOutput:
        return OrderOutput(
            id=order.id,
            user_id=order.user_id,
            plan_id=order.plan_id,
            amount_cents=order.amount_cents,
            currency=order.currency,
            status=order.status,
            payment_provider=order.payment_provider,
            payment_ref=order.payment_ref,
            created_at=order.created_at,
            paid_at=order.paid_at,
        )
