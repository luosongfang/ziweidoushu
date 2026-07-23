"""Analysis quality metrics — scores the analysis process, not life outcomes."""

from __future__ import annotations

import json
import re
import uuid
from typing import Any

from sqlalchemy import text

from app.database.database import SessionLocal
from app.knowledge.decision.decision_risk_analyzer import DecisionRiskAnalyzer

_BANNED = (
    "一定会",
    "必然发生",
    "命中注定",
    "必有灾难",
    "一定发财",
    "必须离婚",
    "你一定会失败",
    "今年必有灾",
    "横死",
    "大难临头",
)

_GROWTH_MARKERS = (
    "建议",
    "复盘",
    "小步",
    "规划",
    "成长",
    "安全垫",
    "沟通",
    "边界",
    "验证",
    "里程碑",
    "学习",
    "参考",
)

_LOGIC_MARKERS = (
    "宫",
    "星",
    "格局",
    "三合",
    "四化",
    "大限",
    "阶段",
    "维度",
    "理论",
    "依据",
)


def _clamp(n: float) -> int:
    return max(0, min(100, int(round(n))))


def _blob_from_analysis(analysis: dict[str, Any]) -> str:
    parts: list[str] = []
    for k, v in analysis.items():
        if isinstance(v, str):
            parts.append(v)
        elif isinstance(v, list):
            parts.extend(str(x) for x in v)
        elif isinstance(v, dict):
            parts.append(_blob_from_analysis(v))
    return " ".join(parts)


class QualityMetrics:
    """Rule-based quality scoring for analysis artifacts."""

    @classmethod
    def score(
        cls,
        *,
        analysis_result: dict[str, Any] | None = None,
        feedback: dict[str, Any] | None = None,
        knowledge_trace: dict[str, Any] | None = None,
        sources: list[dict[str, Any]] | None = None,
        persist: bool = False,
        analysis_id: str | None = None,
    ) -> dict[str, Any]:
        analysis = analysis_result or {}
        trace = knowledge_trace or analysis.get("knowledge_trace") or {}
        srcs = sources or analysis.get("sources") or []
        blob = _blob_from_analysis(analysis)
        if trace:
            blob += " " + _blob_from_analysis(trace)

        theory_accuracy = cls._citation_score(trace, srcs, analysis)
        logic_score = cls._logic_score(analysis, trace, blob)
        safety_score = cls._safety_score(blob)
        growth_value = cls._growth_value(blob, analysis)
        user_helpful = cls._user_helpful(feedback)

        # overall: weighted average of process dimensions
        overall = (
            theory_accuracy * 0.25
            + logic_score * 0.25
            + safety_score * 0.30
            + growth_value * 0.15
            + user_helpful * 0.05
        )
        # if no feedback, redistribute last weight
        if feedback is None:
            overall = (
                theory_accuracy * 0.28
                + logic_score * 0.27
                + safety_score * 0.30
                + growth_value * 0.15
            )

        result = {
            "theory_accuracy": _clamp(theory_accuracy),
            "citation_score": _clamp(theory_accuracy),
            "logic_score": _clamp(logic_score),
            "safety_score": _clamp(safety_score),
            "growth_value": _clamp(growth_value),
            "user_helpful_score": _clamp(user_helpful),
            "overall_score": _clamp(overall),
            "scoring_target": "analysis_process",
            "notice": "评分对象是分析过程质量，不是人生结果真假或宿命准确率。",
        }

        if persist:
            aid = analysis_id or str(uuid.uuid4())
            cls.persist(aid, result)
            result["analysis_id"] = aid

        return result

    @classmethod
    def _citation_score(
        cls,
        trace: dict[str, Any],
        sources: list[dict[str, Any]],
        analysis: dict[str, Any],
    ) -> float:
        score = 40.0
        books = trace.get("books") or []
        entities = trace.get("entities") or []
        path = trace.get("reasoning_path") or []
        if books:
            score += min(25, 8 * len(books))
        if entities:
            score += min(20, 5 * len(entities))
        if path:
            score += min(15, 3 * len(path))
        if sources:
            score += min(15, 4 * len(sources))
        # decision / theory blocks present
        if analysis.get("traditional_view") or analysis.get("theory_used"):
            score += 5
        if analysis.get("decision_analysis") or analysis.get("scenario"):
            score += 5
        return min(100.0, score)

    @classmethod
    def _logic_score(
        cls,
        analysis: dict[str, Any],
        trace: dict[str, Any],
        blob: str,
    ) -> float:
        score = 35.0
        hits = sum(1 for m in _LOGIC_MARKERS if m in blob)
        score += min(30, hits * 4)
        # structured fields
        for key in (
            "strengths",
            "challenges",
            "action_suggestions",
            "suggestions",
            "reflection_questions",
            "decision_points",
        ):
            if analysis.get(key):
                score += 5
        if trace.get("reasoning_path"):
            score += min(15, 3 * len(trace["reasoning_path"]))
        da = analysis.get("decision_analysis") or analysis
        tv = da.get("traditional_view") if isinstance(da, dict) else None
        if isinstance(tv, dict) and tv:
            score += 5 * min(3, len(tv))
        return min(100.0, score)

    @classmethod
    def _safety_score(cls, blob: str) -> float:
        text = blob or ""
        # start high; deduct for banned absolutist / fear language
        score = 100.0
        for b in _BANNED:
            if b in text:
                score -= 25
        # reward positioning language
        for good in ("不作绝对", "人生规划", "传统文化学习", "自我认知", "结合现实"):
            if good in text:
                score += 2
        # sanitized sample
        sanitized = DecisionRiskAnalyzer.sanitize(text[:500])
        if sanitized != text[:500] and any(b in text for b in _BANNED):
            score = min(score, 40)
        return max(0.0, min(100.0, score))

    @classmethod
    def _growth_value(cls, blob: str, analysis: dict[str, Any]) -> float:
        score = 30.0
        hits = sum(1 for m in _GROWTH_MARKERS if m in (blob or ""))
        score += min(40, hits * 5)
        actions = (
            analysis.get("action_suggestions")
            or analysis.get("suggestions")
            or (analysis.get("decision_analysis") or {}).get("action_suggestions")
            or []
        )
        if actions:
            score += min(20, 5 * len(actions))
        reflections = (
            analysis.get("reflection_questions")
            or (analysis.get("decision_analysis") or {}).get("reflection_questions")
            or []
        )
        if reflections:
            score += min(15, 5 * len(reflections))
        return min(100.0, score)

    @classmethod
    def _user_helpful(cls, feedback: dict[str, Any] | None) -> float:
        if not feedback:
            return 50.0  # neutral when unknown
        ftype = feedback.get("feedback_type") or feedback.get("type")
        mapping = {
            "helpful": 95.0,
            "partially_helpful": 65.0,
            "future_check": 55.0,
            "not_helpful": 20.0,
        }
        if ftype in mapping:
            return mapping[ftype]
        # numeric override
        if feedback.get("score") is not None:
            try:
                return float(feedback["score"])
            except (TypeError, ValueError):
                pass
        return 50.0

    @classmethod
    def persist(cls, analysis_id: str, scores: dict[str, Any]) -> None:
        db = SessionLocal()
        try:
            db.execute(
                text(
                    """
                    INSERT INTO public.analysis_quality_metrics
                        (analysis_id, citation_score, logic_score, safety_score,
                         user_helpful_score, overall_score)
                    VALUES
                        (CAST(:aid AS uuid), :cite, :logic, :safety, :helpful, :overall)
                    """
                ),
                {
                    "aid": analysis_id,
                    "cite": scores.get("citation_score") or scores.get("theory_accuracy"),
                    "logic": scores.get("logic_score"),
                    "safety": scores.get("safety_score"),
                    "helpful": scores.get("user_helpful_score"),
                    "overall": scores.get("overall_score"),
                },
            )
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()
