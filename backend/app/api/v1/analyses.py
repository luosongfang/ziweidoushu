"""AI 分析 API 路由（Sprint 7–8）。"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from pydantic import BaseModel

from app.ai.analysis_service import AnalysisService
from app.api.deps import get_current_user
from app.models.analysis import AnalysisGenerateRequest, AnalysisOutput
from app.models.birth import BirthInput
from app.models.chart_record import AnalysisRecordOutput, AnalysisRecordSummary, PersistAnalysisRequest
from app.models.user import AuthUser
from app.services.analysis_persistence_service import AnalysisPersistenceService
from app.services.profile_service import ProfileService
from app.ziwei.exceptions import UnsupportedCalendarError, ZiweiEngineError

router = APIRouter(prefix="/analyses", tags=["analyses"])


@router.post("/generate", response_model=AnalysisOutput)
async def generate_analysis(request: AnalysisGenerateRequest) -> AnalysisOutput:
    """基于命盘 JSON 或出生信息生成 AI 解读。"""
    try:
        return await AnalysisService.generate(request)
    except UnsupportedCalendarError as exc:
        raise HTTPException(status_code=501, detail=str(exc)) from exc
    except ZiweiEngineError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


class BirthAnalysisRequest(BirthInput):
    """BirthInput + 分析参数。"""

    analysis_type: str = "overall"
    palace_name: str | None = None
    reference_date: str | None = None
    mode: str = "auto"


@router.post("/generate/birth-input", response_model=AnalysisOutput)
async def generate_analysis_from_birth(body: BirthAnalysisRequest) -> AnalysisOutput:
    """使用 BirthInput 排盘并生成 AI 解读。"""
    birth = BirthInput.model_validate(body.model_dump(exclude={
        "analysis_type", "palace_name", "reference_date", "mode",
    }))
    request = AnalysisGenerateRequest(
        birth=birth,
        analysis_type=body.analysis_type,  # type: ignore[arg-type]
        palace_name=body.palace_name,
        reference_date=body.reference_date,
        mode=body.mode,  # type: ignore[arg-type]
    )
    return await generate_analysis(request)


class PersistAnalysisResponse(BaseModel):
    """持久化解读响应。"""

    analysis: AnalysisOutput
    record: AnalysisRecordOutput
    ai_quota_remaining: int


@router.post("/persist", response_model=PersistAnalysisResponse)
async def persist_analysis(
    body: PersistAnalysisRequest,
    user: AuthUser = Depends(get_current_user),
) -> PersistAnalysisResponse:
    """生成 AI 解读、扣减配额并持久化（需登录）。"""
    try:
        result, record = await AnalysisPersistenceService.generate_and_persist(user, body)
        profile = ProfileService.get_me(user)
        return PersistAnalysisResponse(
            analysis=result,
            record=record,
            ai_quota_remaining=profile.ai_quota,
        )
    except ValueError as exc:
        detail = str(exc)
        status = 402 if "次数不足" in detail else 404
        raise HTTPException(status_code=status, detail=detail) from exc
    except UnsupportedCalendarError as exc:
        raise HTTPException(status_code=501, detail=str(exc)) from exc
    except ZiweiEngineError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/history", response_model=list[AnalysisRecordSummary])
async def list_analysis_history(
    user: AuthUser = Depends(get_current_user),
) -> list[AnalysisRecordSummary]:
    """列出用户 AI 解读历史。"""
    return AnalysisPersistenceService.list_analyses(user)


@router.get("/history/{analysis_id}", response_model=AnalysisRecordOutput)
async def get_analysis_record(
    analysis_id: UUID,
    user: AuthUser = Depends(get_current_user),
) -> AnalysisRecordOutput:
    """获取单条解读记录。"""
    try:
        return AnalysisPersistenceService.get_analysis(user, analysis_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
