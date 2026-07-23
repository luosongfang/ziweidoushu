"""Knowledge Core analyze API — POST /api/v1/knowledge/analyze."""

from __future__ import annotations

from typing import Any, Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.ai.reasoning_engine import ReasoningEngine
from app.ai.reasoning_engine_v2 import ReasoningEngineV2

router = APIRouter(tags=["knowledge-core"])


class KnowledgeAnalyzeRequest(BaseModel):
    chart_id: str | None = None
    question: str = Field(..., min_length=1)
    user_context: dict[str, Any] | None = None
    chart_data: dict[str, Any] | None = None
    engine_version: Literal[
        "1.1", "2.0", "2.1", "3.2", "3.3", "4.0", "4.1", "5.0", "5.1"
    ] = "5.1"
    persist_memory: bool = False
    persist_evidence: bool = False
    persist_growth_memory: bool | None = None
    persist_theory_results: bool = False
    user_id: str | None = None


class KnowledgeAnalyzeResponse(BaseModel):
    success: bool = True
    question_type: str | None = None
    engine_version: str = "5.1"
    traditional_analysis: Any = None
    theory_used: list[str] = Field(default_factory=list)
    sources: list[dict[str, Any]] = Field(default_factory=list)
    evidence: list[dict[str, Any]] = Field(default_factory=list)
    advisor_analysis: Any = None
    reasoning: list[dict[str, Any]] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    safety_notice: Any = None
    reflection_questions: list[str] = Field(default_factory=list)
    call_trace: list[str] = Field(default_factory=list)
    scenario_name: str | None = None
    life_advisor: dict[str, Any] | None = None
    matrix_summary: dict[str, Any] | None = None
    theory_route: dict[str, Any] | None = None
    user_context: dict[str, Any] | None = None
    theory_analysis: dict[str, Any] | None = None
    life_timeline: dict[str, Any] | None = None
    decision_analysis: dict[str, Any] | None = None
    decision_paths: dict[str, Any] | None = None
    knowledge_trace: dict[str, Any] | None = None
    decision_history_id: str | None = None
    error: str | None = None


@router.post("/knowledge/analyze", response_model=KnowledgeAnalyzeResponse)
def knowledge_analyze(body: KnowledgeAnalyzeRequest) -> KnowledgeAnalyzeResponse:
    if not body.chart_id and not body.chart_data:
        raise HTTPException(status_code=400, detail="需要 chart_id 或 chart_data")
    try:
        if body.engine_version == "1.1":
            result = ReasoningEngine.run(
                question=body.question,
                chart_id=body.chart_id,
                chart_data=body.chart_data,
                user_context=body.user_context,
            )
        else:
            result = ReasoningEngineV2.run(
                question=body.question,
                chart_id=body.chart_id,
                chart_data=body.chart_data,
                user_context=body.user_context,
                persist_memory=body.persist_memory,
                user_id=body.user_id,
                persist_evidence=body.persist_evidence,
                persist_growth_memory=body.persist_growth_memory,
                persist_theory_results=body.persist_theory_results,
            )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        return KnowledgeAnalyzeResponse(success=False, error=str(exc))

    traditional = getattr(result, "traditional_analysis_structured", None)
    if traditional is None:
        traditional = "；".join(result.traditional_analysis or [])
    elif isinstance(traditional, dict) and traditional.get("text"):
        traditional = traditional.get("text")
    elif isinstance(traditional, dict):
        traditional = "；".join(traditional.get("summary") or result.traditional_analysis or [])

    safety = result.safety_notice
    if not isinstance(safety, dict):
        safety = {
            "notice": safety,
            "level": "high",
            "positioning": "传统文化学习 + 自我认知辅助 + 人生规划参考",
        }

    return KnowledgeAnalyzeResponse(
        success=True,
        question_type=result.question_type,
        engine_version=getattr(result, "engine_version", body.engine_version),
        traditional_analysis=traditional,
        theory_used=getattr(result, "theory_used", None) or [],
        sources=getattr(result, "sources", None) or [],
        evidence=getattr(result, "evidence", None) or [],
        advisor_analysis=getattr(result, "advisor_analysis", None),
        reasoning=[r.model_dump() for r in result.reasoning],
        suggestions=result.suggestions,
        safety_notice=safety,
        reflection_questions=getattr(result, "reflection_questions", None) or [],
        call_trace=result.call_trace,
        scenario_name=getattr(result, "scenario_name", None),
        life_advisor=getattr(result, "life_advisor", None),
        matrix_summary=getattr(result, "matrix_summary", None),
        theory_route=getattr(result, "theory_route", None),
        user_context=getattr(result, "user_context", None),
        theory_analysis=getattr(result, "theory_analysis", None),
        life_timeline=getattr(result, "life_timeline", None),
        decision_analysis=getattr(result, "decision_analysis", None),
        decision_paths=getattr(result, "decision_paths", None),
        knowledge_trace=getattr(result, "knowledge_trace", None),
        decision_history_id=getattr(result, "decision_history_id", None),
    )
