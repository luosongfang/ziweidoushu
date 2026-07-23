"""Life-question oriented reasoning aggregation."""

from __future__ import annotations

from typing import Any

from app.knowledge.knowledge_loader import KnowledgeLoader
from app.knowledge.reasoning.palace_reasoning import PalaceReasoning
from app.knowledge.reasoning.pattern_reasoning import PatternReasoning
from app.knowledge.reasoning.schemas import ReasoningResult


class LifeReasoning:
    @classmethod
    def analyze(cls, chart: dict[str, Any], question_type: str) -> list[ReasoningResult]:
        model = KnowledgeLoader.get_question_model(question_type) or {}
        palaces = list(model.get("required_palaces") or ["命宫"])
        palace_result = PalaceReasoning.analyze(chart, palaces, question_type)
        pattern_result = PatternReasoning.analyze(chart, question_type)

        if question_type == "entrepreneurship":
            synth = ReasoningResult(
                dimension="entrepreneurship_synthesis",
                observations=[
                    "创业议题按 Knowledge Core 拆为：人格倾向、资源能力、风险偏好、执行模式。",
                    "输出采用「优势 / 注意 / 建议」结构，不做是否创业的二元判决。",
                ],
                traditional_basis=palace_result.traditional_basis
                + pattern_result.traditional_basis,
                strengths=list(
                    dict.fromkeys(palace_result.strengths + pattern_result.strengths)
                )[:8],
                challenges=list(
                    dict.fromkeys(palace_result.challenges + pattern_result.challenges)
                )[:8],
                suggestions=list(
                    dict.fromkeys(
                        [
                            "若推进创业，建议先小范围验证需求，再放大投入。",
                            "同步建立止损线与个人能量补给计划。",
                            *palace_result.suggestions[:3],
                            *pattern_result.suggestions[:2],
                        ]
                    )
                ),
                sources=palace_result.sources + pattern_result.sources,
                call_trace=["life_reasoning:entrepreneurship_synthesis"],
            )
            return [palace_result, pattern_result, synth]

        return [palace_result, pattern_result]
