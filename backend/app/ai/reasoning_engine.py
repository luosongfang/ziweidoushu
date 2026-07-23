"""Reasoning Engine — Knowledge Core 推理管线（不调用 LLM）。"""

from __future__ import annotations

import json
from typing import Any

from sqlalchemy import select

from app.ai.prompt_builder import KnowledgeCorePromptBuilder
from app.ai.safety_filter import SafetyFilter
from app.database.database import SessionLocal
from app.database.models import ZiweiChart
from app.knowledge.knowledge_loader import KnowledgeLoader
from app.knowledge.knowledge_service import KnowledgeService
from app.knowledge.reasoning.life_reasoning import LifeReasoning
from app.knowledge.reasoning.question_classifier import QuestionClassifier
from app.knowledge.reasoning.schemas import PipelineResult


class ReasoningEngine:
    """
    用户问题 → QuestionClassifier → LifeQuestionModel → Chart Analysis
    → Knowledge Retrieval → Reasoning → Safety Filter → AI Prompt（仅生成，不调用）
    """

    @classmethod
    def load_chart(
        cls,
        chart_id: str | None = None,
        chart_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if chart_data:
            return chart_data
        if not chart_id:
            raise ValueError("需要 chart_id 或 chart_data")
        db = SessionLocal()
        try:
            row = db.scalar(select(ZiweiChart).where(ZiweiChart.id == chart_id))
            if not row:
                raise ValueError(f"未找到命盘: {chart_id}")
            data = row.chart_json if isinstance(row.chart_json, dict) else {}
            # normalize to include top-level palaces-friendly structure
            return data if data else {"chart_id": chart_id}
        finally:
            db.close()

    @classmethod
    def run(
        cls,
        question: str,
        chart_id: str | None = None,
        chart_data: dict[str, Any] | None = None,
        user_context: dict[str, Any] | None = None,
    ) -> PipelineResult:
        trace: list[str] = []
        qtype = QuestionClassifier.classify(question)
        trace.append(f"classify:{qtype}")

        model = KnowledgeLoader.get_question_model(qtype) or {}
        trace.append(f"life_question_model:{qtype}")

        chart = cls.load_chart(chart_id=chart_id, chart_data=chart_data)
        trace.append("chart_loaded")

        context = KnowledgeService.build_context(chart, question)
        trace.append("knowledge_retrieved")

        reasoning = LifeReasoning.analyze(chart, qtype)
        for r in reasoning:
            trace.extend(r.call_trace)

        traditional = []
        suggestions = []
        for r in reasoning:
            traditional.extend(r.traditional_basis)
            suggestions.extend(r.suggestions)

        safety = model.get("safety_notice") or "本分析仅供自我认知与人生规划参考。"
        # safety filter applied to textual fields
        traditional = [SafetyFilter.apply(x) for x in dict.fromkeys(traditional)]
        suggestions = [SafetyFilter.apply(x) for x in dict.fromkeys(suggestions)]
        for r in reasoning:
            r.observations = [SafetyFilter.apply(x) for x in r.observations]
            r.traditional_basis = [SafetyFilter.apply(x) for x in r.traditional_basis]
            r.strengths = [SafetyFilter.apply(x) for x in r.strengths]
            r.challenges = [SafetyFilter.apply(x) for x in r.challenges]
            r.suggestions = [SafetyFilter.apply(x) for x in r.suggestions]

        # build prompt for future LLM layer (not invoked here)
        prompt_messages = KnowledgeCorePromptBuilder.build(question, context)
        prompt_preview = json.dumps(prompt_messages, ensure_ascii=False)[:2000]
        trace.append("prompt_built_no_llm")

        if user_context:
            trace.append(f"user_context_keys:{','.join(user_context.keys())}")

        return PipelineResult(
            question_type=qtype,
            traditional_analysis=traditional[:12],
            reasoning=reasoning,
            suggestions=suggestions[:12],
            safety_notice=SafetyFilter.apply(str(safety)),
            prompt_preview=prompt_preview,
            call_trace=trace,
        )
