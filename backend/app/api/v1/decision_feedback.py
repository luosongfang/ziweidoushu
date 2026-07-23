"""Decision feedback & profile APIs — V5.1."""

from __future__ import annotations

from typing import Any, Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.knowledge.decision_feedback import DecisionProfile, FeedbackService

router = APIRouter(tags=["decision-feedback"])


class DecisionFeedbackRequest(BaseModel):
    user_id: str = Field(..., min_length=1)
    feedback_type: Literal["helpful", "not_helpful", "partially_helpful", "future_check"]
    feedback_content: str | None = None
    decision_history_id: str | None = None
    result_status: Literal["pending", "confirmed", "changed", "unknown"] = "pending"
    update_profile: bool = True
    # V5.6 optional hooks for theory weight sync
    scenario: str | None = None
    theory_used: list[str] | None = None
    update_theory_weights: bool = True


class DecisionFeedbackResponse(BaseModel):
    success: bool = True
    feedback: dict[str, Any] | None = None
    profile: dict[str, Any] | None = None
    optimization: dict[str, Any] | None = None
    error: str | None = None


class DecisionProfileRequest(BaseModel):
    user_id: str = Field(..., min_length=1)
    refresh: bool = False


class DecisionProfileResponse(BaseModel):
    success: bool = True
    profile: dict[str, Any] | None = None
    error: str | None = None


@router.post("/decision/feedback", response_model=DecisionFeedbackResponse)
def submit_decision_feedback(body: DecisionFeedbackRequest) -> DecisionFeedbackResponse:
    try:
        saved = FeedbackService.save_feedback(
            user_id=body.user_id,
            feedback_type=body.feedback_type,
            feedback_content=body.feedback_content,
            decision_history_id=body.decision_history_id,
            result_status=body.result_status,
        )
        profile = None
        if body.update_profile:
            profile = DecisionProfile.refresh_profile(body.user_id)

        optimization = None
        if body.update_theory_weights:
            try:
                from app.knowledge.optimization import OptimizationService

                optimization = OptimizationService.update_from_feedback(
                    feedback_type=body.feedback_type,
                    scenario=body.scenario,
                    theory_used=body.theory_used,
                    decision_history_id=body.decision_history_id,
                    source="decision_feedback",
                )
            except Exception as opt_exc:  # noqa: BLE001
                optimization = {"error": str(opt_exc)}

        return DecisionFeedbackResponse(
            success=True,
            feedback=saved,
            profile=profile,
            optimization=optimization,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        return DecisionFeedbackResponse(success=False, error=str(exc))


@router.post("/decision/profile", response_model=DecisionProfileResponse)
def get_decision_profile(body: DecisionProfileRequest) -> DecisionProfileResponse:
    try:
        if body.refresh:
            profile = DecisionProfile.refresh_profile(body.user_id)
        else:
            profile = DecisionProfile.get_profile(body.user_id)
        return DecisionProfileResponse(success=True, profile=profile)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        return DecisionProfileResponse(success=False, error=str(exc))
