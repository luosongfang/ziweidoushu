"""Evaluation APIs — Knowledge Core V5.5 / V5.6."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.knowledge.evaluation import EvaluationEngine
from app.knowledge.optimization import OptimizationService
from app.knowledge.multitheory.theory_dispatcher import TheoryDispatcher

router = APIRouter(tags=["evaluation"])


class EvaluateAnalysisRequest(BaseModel):
    analysis_result: dict[str, Any] = Field(default_factory=dict)
    feedback: dict[str, Any] | None = None
    knowledge_trace: dict[str, Any] | None = None
    sources: list[dict[str, Any]] | None = None
    theory_used: list[str] | None = None
    scenario: str | None = None
    analysis_id: str | None = None
    persist: bool = True


class EvaluateAnalysisResponse(BaseModel):
    success: bool = True
    quality_score: dict[str, Any] | None = None
    metrics: dict[str, Any] | None = None
    optimization: dict[str, Any] | None = None
    notice: str | None = None
    engine_version: str = "5.6"
    error: str | None = None


class AddCaseRequest(BaseModel):
    case_name: str = Field(..., min_length=1)
    birth_info_summary: str | None = "匿名教学案例"
    chart_features: dict[str, Any] = Field(default_factory=dict)
    main_patterns: list[Any] = Field(default_factory=list)
    life_stage: str | None = None
    question_type: str | None = None
    analysis_reference: dict[str, Any] = Field(default_factory=dict)
    case_source: str | None = "api"
    verification_level: str = "classic"


class AddCaseResponse(BaseModel):
    success: bool = True
    case: dict[str, Any] | None = None
    error: str | None = None


class TheoryStatsResponse(BaseModel):
    success: bool = True
    stats: list[dict[str, Any]] = Field(default_factory=list)
    ranking: dict[str, Any] = Field(default_factory=dict)
    engine_version: str = "5.6"
    error: str | None = None


class TheoryRouteResponse(BaseModel):
    success: bool = True
    scenario: str | None = None
    theories: list[dict[str, Any]] = Field(default_factory=list)
    weights: list[dict[str, Any]] = Field(default_factory=list)
    engine_version: str = "5.6"
    error: str | None = None


@router.post("/evaluation/analysis", response_model=EvaluateAnalysisResponse)
def evaluate_analysis(body: EvaluateAnalysisRequest) -> EvaluateAnalysisResponse:
    try:
        result = EvaluationEngine.evaluate_analysis(
            analysis_result=body.analysis_result,
            feedback=body.feedback,
            knowledge_trace=body.knowledge_trace,
            sources=body.sources,
            theory_used=body.theory_used,
            scenario=body.scenario,
            persist=body.persist,
            analysis_id=body.analysis_id,
        )
        return EvaluateAnalysisResponse(
            success=True,
            quality_score=result.get("quality_score"),
            metrics=result.get("metrics"),
            optimization=result.get("optimization"),
            notice=result.get("notice"),
            engine_version="5.6",
        )
    except Exception as exc:  # noqa: BLE001
        return EvaluateAnalysisResponse(success=False, error=str(exc))


@router.post("/evaluation/case", response_model=AddCaseResponse)
def add_evaluation_case(body: AddCaseRequest) -> AddCaseResponse:
    try:
        saved = EvaluationEngine.add_case(body.model_dump())
        return AddCaseResponse(success=True, case=saved)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        return AddCaseResponse(success=False, error=str(exc))


@router.get("/evaluation/theory-stats", response_model=TheoryStatsResponse)
def get_theory_stats(scenario: str | None = Query(default=None)) -> TheoryStatsResponse:
    try:
        data = EvaluationEngine.theory_stats(scenario=scenario)
        return TheoryStatsResponse(
            success=True,
            stats=data.get("stats") or [],
            ranking=data.get("ranking") or {},
            engine_version="5.6",
        )
    except Exception as exc:  # noqa: BLE001
        return TheoryStatsResponse(success=False, error=str(exc))


@router.get("/evaluation/theory-route", response_model=TheoryRouteResponse)
def get_theory_route(scenario: str = Query(default="entrepreneurship")) -> TheoryRouteResponse:
    """Dynamic Multi-Theory route from theory_dispatch_weights."""
    try:
        route = TheoryDispatcher.get_dynamic_theory_route(scenario)
        weights = OptimizationService.list_weights(scenario)
        return TheoryRouteResponse(
            success=True,
            scenario=route.get("scenario"),
            theories=route.get("theories") or [],
            weights=weights,
            engine_version="5.6",
        )
    except Exception as exc:  # noqa: BLE001
        return TheoryRouteResponse(success=False, error=str(exc))
