"""命盘持久化 API（Sprint 8）。"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_current_user
from app.models.chart_record import ChartRecordOutput, ChartRecordSummary, ChartSaveRequest
from app.models.user import AuthUser
from app.services.chart_service import ChartPersistenceService
from app.ziwei.exceptions import UnsupportedCalendarError, ZiweiEngineError

router = APIRouter(prefix="/charts/saved", tags=["charts-saved"])


@router.post("", response_model=ChartRecordOutput)
async def save_chart(
    body: ChartSaveRequest,
    user: AuthUser = Depends(get_current_user),
) -> ChartRecordOutput:
    """保存命盘到用户账户。"""
    try:
        return ChartPersistenceService.save(user, body)
    except UnsupportedCalendarError as exc:
        raise HTTPException(status_code=501, detail=str(exc)) from exc
    except ZiweiEngineError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("", response_model=list[ChartRecordSummary])
async def list_saved_charts(
    user: AuthUser = Depends(get_current_user),
) -> list[ChartRecordSummary]:
    """列出用户已保存命盘。"""
    return ChartPersistenceService.list_charts(user)


@router.get("/{chart_id}", response_model=ChartRecordOutput)
async def get_saved_chart(
    chart_id: UUID,
    user: AuthUser = Depends(get_current_user),
) -> ChartRecordOutput:
    """获取已保存命盘详情。"""
    try:
        return ChartPersistenceService.get_chart(user, chart_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/{chart_id}", status_code=204)
async def delete_saved_chart(
    chart_id: UUID,
    user: AuthUser = Depends(get_current_user),
) -> None:
    """删除已保存命盘。"""
    try:
        ChartPersistenceService.delete_chart(user, chart_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
