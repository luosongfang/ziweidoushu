"""成长记忆 API — GET /api/v1/memory/context"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select

from app.api.deps import get_current_user
from app.database.database import SessionLocal
from app.knowledge.memory.memory_models import AdvisorContinuityContext
from app.knowledge.memory.memory_service import MemoryService
from app.models.user import AuthUser

router = APIRouter(prefix="/memory", tags=["memory"])


class MemoryContextResponse(BaseModel):
    continuity_message: str = ""
    growth_goals: list[str] = Field(default_factory=list)
    focus_topics: list[str] = Field(default_factory=list)
    important_topics: list[str] = Field(default_factory=list)
    summary: str = ""


@router.get("/context", response_model=MemoryContextResponse)
def get_memory_context(user: AuthUser = Depends(get_current_user)) -> MemoryContextResponse:
    """加载 advisor_continuity_context + 成长记忆，供 AI 导师欢迎语。"""
    ctx = MemoryService.get_user_context(str(user.id))
    continuity_summary = ""
    important: list[str] = []

    db = SessionLocal()
    try:
        row = db.scalar(
            select(AdvisorContinuityContext).where(
                AdvisorContinuityContext.user_id == UUID(str(user.id))
            )
        )
        if row:
            continuity_summary = row.summary or ""
            important = list(row.important_topics or [])[:5]
    finally:
        db.close()

    msg = str(ctx.get("continuity_message") or continuity_summary or "")
    if not msg:
        msg = "用户正在建立个人成长档案，可从自我认知与当前阶段开始探索。"

    return MemoryContextResponse(
        continuity_message=msg,
        growth_goals=[str(g) for g in (ctx.get("growth_goals") or [])[:5]],
        focus_topics=[str(t) for t in (ctx.get("main_interests") or ctx.get("previous_topics") or [])[:5]],
        important_topics=important,
        summary=str(ctx.get("summary") or continuity_summary or ""),
    )
