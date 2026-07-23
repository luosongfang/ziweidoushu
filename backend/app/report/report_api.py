"""Report & Growth Center API — V1.3。"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.database import get_db
from app.models.user import AuthUser
from app.report.report_models import (
    GrowthProfileResponse,
    ReportCreateRequest,
    ReportCreateResponse,
    ReportDetailResponse,
    ReportFeedbackRequest,
    ReportFeedbackResponse,
    ReportSummaryItem,
)
from app.report.report_service import GrowthCenterService, ReportService

router = APIRouter(tags=["report-v1.3"])


def _to_detail(record) -> ReportDetailResponse:
    body = record.report_json if isinstance(record.report_json, dict) else {}
    return ReportDetailResponse(
        id=record.id,
        chart_id=record.chart_id,
        report_type=record.report_type,
        engine_version=record.engine_version,
        summary=record.summary,
        report_sections=body.get("sections") or body,
        knowledge_trace=body.get("knowledge_trace"),
        safety_notice=str(body.get("safety_notice") or ""),
        created_at=record.created_at.isoformat() if record.created_at else "",
    )


@router.post("/report/create", response_model=ReportCreateResponse)
def create_report(
    body: ReportCreateRequest,
    user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ReportCreateResponse:
    try:
        record = ReportService.create_report(
            user,
            chart_id=body.chart_id,
            report_type=body.report_type,
            db=db,
        )
        db.commit()
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        db.rollback()
        raise HTTPException(status_code=500, detail=f"报告生成失败：{exc}") from exc
    detail = _to_detail(record)
    return ReportCreateResponse(
        report_id=detail.id,
        summary=detail.summary,
        report_sections=detail.report_sections,
        knowledge_trace=detail.knowledge_trace,
        safety_notice=detail.safety_notice,
    )


@router.get("/report/list", response_model=list[ReportSummaryItem])
def list_reports(
    user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ReportSummaryItem]:
    rows = ReportService.list_reports(user, db)
    return [
        ReportSummaryItem(
            id=r.id,
            chart_id=r.chart_id,
            report_type=r.report_type,
            summary=r.summary,
            engine_version=r.engine_version,
            created_at=r.created_at.isoformat() if r.created_at else "",
        )
        for r in rows
    ]


@router.get("/report/{report_id}", response_model=ReportDetailResponse)
def get_report(
    report_id: str,
    user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ReportDetailResponse:
    record = ReportService.get_report(user, report_id, db)
    if not record:
        raise HTTPException(status_code=404, detail="报告不存在")
    return _to_detail(record)


@router.post("/report/feedback", response_model=ReportFeedbackResponse)
def submit_feedback(
    body: ReportFeedbackRequest,
    user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ReportFeedbackResponse:
    try:
        row = ReportService.save_feedback(
            user,
            report_id=body.report_id,
            helpful=body.helpful,
            feedback_type=body.feedback_type,
            comment=body.comment,
            db=db,
        )
        db.commit()
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return ReportFeedbackResponse(id=row.id)


@router.get("/growth/profile", response_model=GrowthProfileResponse)
def growth_profile(
    user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> GrowthProfileResponse:
    data = GrowthCenterService.get_profile(user, db)
    return GrowthProfileResponse(**data)
