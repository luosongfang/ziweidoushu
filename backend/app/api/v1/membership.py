"""会员与订单 API（Sprint 8）。"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_current_user
from app.models.commerce import (
    CreateOrderRequest,
    MembershipPlan,
    OrderConfirmResponse,
    OrderOutput,
)
from app.models.user import AuthUser
from app.services.commerce_service import CommerceService

router = APIRouter(prefix="/membership", tags=["membership"])


@router.get("/plans", response_model=list[MembershipPlan])
async def list_membership_plans() -> list[MembershipPlan]:
    """获取会员计划列表（公开）。"""
    return CommerceService.list_plans()


@router.post("/orders", response_model=OrderOutput)
async def create_order(
    body: CreateOrderRequest,
    user: AuthUser = Depends(get_current_user),
) -> OrderOutput:
    """创建订阅订单（支付流程占位）。"""
    return CommerceService.create_order(user, body)


@router.post("/orders/{order_id}/confirm", response_model=OrderConfirmResponse)
async def confirm_order(
    order_id: UUID,
    user: AuthUser = Depends(get_current_user),
) -> OrderConfirmResponse:
    """确认订单支付（开发环境 stub）。"""
    try:
        return CommerceService.confirm_order(user, order_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
