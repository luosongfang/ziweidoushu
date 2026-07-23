"""用户账户 API — V1.2（/api/user 与 /api/v1/user 双挂载）。"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.database import SessionLocal, get_db
from app.knowledge.memory.memory_models import UserQuestionHistory
from app.knowledge.memory.memory_service import MemoryService
from app.models.user import AuthUser
from app.services.membership_service import MembershipService
from app.services.profile_service import ProfileService
from app.services.user_identity_service import UserIdentityService
from app.services.user_chart_service import UserChartService

PLAN_LABELS = {
    "free": "免费用户",
    "basic": "普通会员",
    "vip": "VIP 会员",
    "svip": "SVIP 会员",
}


def _plan_label(plan_id: str) -> str:
    return PLAN_LABELS.get(plan_id, plan_id.upper())


router = APIRouter(prefix="/user", tags=["user-account"])


class UserProfileResponse(BaseModel):
    id: str
    auth_user_id: str
    nickname: str
    avatar_url: str | None = None
    email: str | None = None
    membership: str = "free"
    points: int = 0
    created_at: str = ""
    updated_at: str = ""


class UserChartSaveRequest(BaseModel):
    name: str = "未命名命盘"
    chart_data: dict
    birth_info: dict = Field(default_factory=dict)
    birth_date: str | None = None
    birth_time: str | None = None
    birth_place: str | None = None
    gender: str | None = None
    set_default: bool = True


class AnalysisSaveRequest(BaseModel):
    chart_id: str | None = None
    question: str = "命盘概览"
    analysis_type: str = "overview"
    summary: str


class UserChartSummary(BaseModel):
    id: str
    name: str
    is_default: bool
    ming_gong: str = ""
    five_element: str = ""
    birth_date: str | None = None
    created_at: str


class UserChartDetail(BaseModel):
    id: str
    user_id: str
    name: str
    is_default: bool
    chart_data: dict
    birth_info: dict
    birth_date: str | None = None
    birth_time: str | None = None
    birth_place: str | None = None
    gender: str | None = None
    created_at: str


class GrowthContextResponse(BaseModel):
    continuity_message: str = ""
    growth_goals: list[str] = Field(default_factory=list)
    focus_topics: list[str] = Field(default_factory=list)
    recent_questions: list[str] = Field(default_factory=list)
    career_focus: str | None = None
    growth_notes: str | None = None


class MembershipStatusResponse(BaseModel):
    plan_id: str = "free"
    plan_label: str = "免费用户"
    points: int = 0
    analysis_used: int = 0
    analysis_quota: int = 1
    advisor_enabled: bool = False


class MembershipPreviewRequest(BaseModel):
    plan_id: str = Field(..., pattern="^(free|basic|vip|svip)$")


class PointsConsumeRequest(BaseModel):
    amount: int = Field(default=2, ge=1)
    reason: str = "advisor_chat"


class PointsConsumeResponse(BaseModel):
    success: bool
    balance: int
    message: str = ""


class HistoryItem(BaseModel):
    id: str
    question: str
    analysis_type: str | None = None
    topic: str = ""
    summary: str = ""
    suggestions: list[str] = Field(default_factory=list)
    created_at: str


@router.get("/profile", response_model=UserProfileResponse)
def get_user_profile(
    user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserProfileResponse:
    data = UserIdentityService.get_or_create_profile(db, user)
    return UserProfileResponse(
        id=data["id"],
        auth_user_id=data["auth_user_id"],
        nickname=data["nickname"],
        avatar_url=data.get("avatar_url"),
        email=user.email,
        membership=data.get("membership", "free"),
        points=data.get("points", 0),
        created_at=data.get("created_at", ""),
        updated_at=data.get("updated_at", ""),
    )


@router.post("/charts", response_model=UserChartDetail)
def save_user_chart(
    body: UserChartSaveRequest,
    user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserChartDetail:
    try:
        record = UserChartService.save(
            db,
            user,
            name=body.name,
            chart_data=body.chart_data,
            birth_info=body.birth_info,
            set_default=body.set_default,
            birth_date=body.birth_date,
            birth_time=body.birth_time,
            birth_place=body.birth_place,
            gender=body.gender,
        )
        db.commit()
        return _to_detail(record)
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"保存命盘失败：{exc}") from exc


@router.get("/charts", response_model=list[UserChartSummary])
def list_user_charts(
    user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[UserChartSummary]:
    records = UserChartService.list_charts(db, user)
    return [_to_summary(r) for r in records]


@router.get("/charts/{chart_id}", response_model=UserChartDetail)
def get_user_chart(
    chart_id: UUID,
    user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserChartDetail:
    record = UserChartService.get_chart(db, user, chart_id)
    if not record:
        raise HTTPException(status_code=404, detail="命盘不存在")
    return _to_detail(record)


@router.post("/history", response_model=HistoryItem)
def save_analysis_history(
    body: AnalysisSaveRequest,
    user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> HistoryItem:
    try:
        record = UserIdentityService.save_analysis(
            db,
            user,
            chart_id=body.chart_id,
            question=body.question,
            analysis_type=body.analysis_type,
            summary=body.summary,
        )
        db.commit()
        return HistoryItem(
            id=record.id,
            question=record.question,
            analysis_type=record.analysis_type,
            topic=record.analysis_type,
            summary=record.summary,
            created_at=record.created_at.isoformat() if record.created_at else "",
        )
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/growth-context", response_model=GrowthContextResponse)
def get_growth_context(
    user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> GrowthContextResponse:
    ctx = MemoryService.get_user_context(str(user.id))
    gp = UserIdentityService.get_growth_profile(db, user)
    recent = _recent_questions(user)
    return GrowthContextResponse(
        continuity_message=str(ctx.get("continuity_message") or ""),
        growth_goals=[str(g) for g in (ctx.get("growth_goals") or [])[:5]],
        focus_topics=[str(t) for t in (ctx.get("main_interests") or ctx.get("previous_topics") or [])[:5]],
        recent_questions=recent,
        career_focus=gp.career_focus if gp else None,
        growth_notes=gp.growth_notes if gp else None,
    )


@router.get("/history", response_model=list[HistoryItem])
def list_question_history(
    user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[HistoryItem]:
    rows = UserIdentityService.list_analysis_history(db, user, limit=30)
    if rows:
        return [
            HistoryItem(
                id=r.id,
                question=r.question,
                analysis_type=r.analysis_type,
                topic=r.analysis_type or "分析",
                summary=r.summary,
                created_at=r.created_at.isoformat() if r.created_at else "",
            )
            for r in rows
        ]
    return _legacy_question_history(user)


@router.get("/membership", response_model=MembershipStatusResponse)
def get_membership_status(
    user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MembershipStatusResponse:
    status = MembershipService.get_status(str(user.id), db=db)
    return MembershipStatusResponse(
        plan_id=status["plan_id"],
        plan_label=_plan_label(status["plan_id"]),
        points=status["points"],
        analysis_used=status["analysis_used"],
        analysis_quota=status["analysis_quota"],
        advisor_enabled=status["advisor_enabled"],
    )


@router.post("/membership/preview", response_model=MembershipStatusResponse)
def preview_membership_plan(
    body: MembershipPreviewRequest,
    user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MembershipStatusResponse:
    """开发预览：切换会员方案（不产生真实支付）。"""
    try:
        status = MembershipService.set_plan_preview(str(user.id), body.plan_id, db=db)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return MembershipStatusResponse(
        plan_id=status["plan_id"],
        plan_label=_plan_label(status["plan_id"]),
        points=status["points"],
        analysis_used=status["analysis_used"],
        analysis_quota=status["analysis_quota"],
        advisor_enabled=status["advisor_enabled"],
    )


@router.post("/points/consume", response_model=PointsConsumeResponse)
def consume_points(
    body: PointsConsumeRequest,
    user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PointsConsumeResponse:
    result = MembershipService.consume_points(
        str(user.id), body.amount, body.reason, db=db
    )
    return PointsConsumeResponse(
        success=result["success"],
        balance=result["balance"],
        message=result.get("message") or "",
    )


def _recent_questions(user: AuthUser) -> list[str]:
    db = SessionLocal()
    try:
        rows = db.scalars(
            select(UserQuestionHistory)
            .where(UserQuestionHistory.user_id == user.id)
            .order_by(UserQuestionHistory.created_at.desc())
            .limit(5)
        ).all()
        return [r.question for r in rows if r.question]
    finally:
        db.close()


def _legacy_question_history(user: AuthUser) -> list[HistoryItem]:
    db = SessionLocal()
    try:
        rows = db.scalars(
            select(UserQuestionHistory)
            .where(UserQuestionHistory.user_id == user.id)
            .order_by(UserQuestionHistory.created_at.desc())
            .limit(30)
        ).all()
        items: list[HistoryItem] = []
        for row in rows:
            analysis = row.analysis_result if isinstance(row.analysis_result, dict) else {}
            suggestions = list(analysis.get("suggestions") or [])[:5]
            items.append(
                HistoryItem(
                    id=str(row.id),
                    question=row.question,
                    analysis_type=row.question_type,
                    topic=str(row.question_type or "分析"),
                    summary="; ".join(suggestions[:2]) if suggestions else "",
                    suggestions=[str(s) for s in suggestions],
                    created_at=row.created_at.isoformat() if row.created_at else "",
                )
            )
        return items
    finally:
        db.close()


def _to_summary(record) -> UserChartSummary:
    chart = record.chart_data if isinstance(record.chart_data, dict) else {}
    inner = chart.get("chart", chart) if isinstance(chart.get("chart"), dict) else chart
    return UserChartSummary(
        id=record.id,
        name=record.chart_name,
        is_default=bool(record.is_default),
        ming_gong=inner.get("ming_gong", ""),
        five_element=inner.get("five_element", ""),
        birth_date=record.birth_date,
        created_at=record.created_at.isoformat() if record.created_at else "",
    )


def _to_detail(record) -> UserChartDetail:
    return UserChartDetail(
        id=record.id,
        user_id=record.user_id,
        name=record.chart_name,
        is_default=bool(record.is_default),
        chart_data=record.chart_data,
        birth_info=record.birth_info or {},
        birth_date=record.birth_date,
        birth_time=record.birth_time,
        birth_place=record.birth_place,
        gender=record.gender,
        created_at=record.created_at.isoformat() if record.created_at else "",
    )
