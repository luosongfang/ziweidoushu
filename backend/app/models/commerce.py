"""商业化 — 会员计划与订单模型（Sprint 8）。"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field

OrderStatus = Literal["pending", "paid", "cancelled", "refunded"]
PlanId = Literal["basic", "premium"]


class MembershipPlan(BaseModel):
    id: PlanId
    name: str
    price_cents: int
    currency: str = "CNY"
    ai_quota: int
    duration_days: int
    features: list[str] = Field(default_factory=list)


class OrderOutput(BaseModel):
    id: UUID
    user_id: UUID
    plan_id: PlanId
    amount_cents: int
    currency: str = "CNY"
    status: OrderStatus
    payment_provider: Optional[str] = None
    payment_ref: Optional[str] = None
    created_at: datetime
    paid_at: Optional[datetime] = None


class CreateOrderRequest(BaseModel):
    plan_id: PlanId
    payment_provider: str = "stub"


class OrderConfirmResponse(BaseModel):
    order: OrderOutput
    profile_membership: str
    ai_quota: int
    message: str
