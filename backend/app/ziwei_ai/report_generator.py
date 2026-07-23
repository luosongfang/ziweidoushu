"""AI 报告生成编排：问题分类 → 知识检索 → 规则分析 → 安全过滤 → LLM。"""

from __future__ import annotations

import json
from typing import Any

from app.ai.siliconflow_client import (
    SiliconFlowClient,
    SiliconFlowEmptyResponseError,
    SiliconFlowNotConfiguredError,
    SiliconFlowRequestError,
)
from app.ziwei_ai.analysis_engine import analyze_chart, extract_palace_stars
from app.ziwei_ai.prompts import ZIWEI_AI_SYSTEM_PROMPT, build_analyze_user_prompt
from app.ziwei_ai.question_router import route_question
from app.ziwei_ai.safety_filter import apply_safety_filter
from app.ziwei_ai.schemas import AnalyzeResponse, QuestionRoute, RuleAnalysis


def _chart_digest(chart_data: dict[str, Any] | str) -> str:
    if isinstance(chart_data, str):
        return chart_data.strip()[:2000]
    palace_stars = extract_palace_stars(chart_data)
    if palace_stars:
        lines = [f"{k}：{'、'.join(v)}" for k, v in palace_stars.items()]
        return "\n".join(lines)[:2000]
    try:
        return json.dumps(chart_data, ensure_ascii=False)[:2000]
    except TypeError:
        return str(chart_data)[:2000]


class ZiweiAiReportGenerator:
    """紫微AI分析引擎 V1 报告生成器。"""

    @classmethod
    async def generate(
        cls,
        chart_data: dict[str, Any] | str,
        question: str,
    ) -> AnalyzeResponse:
        question = (question or "").strip()
        if not question:
            return AnalyzeResponse(success=False, error="请提供问题")

        if not SiliconFlowClient.is_configured():
            return AnalyzeResponse(success=False, error="AI服务未配置")

        route: QuestionRoute = route_question(question)
        analysis: RuleAnalysis = analyze_chart(chart_data, route.related_palaces)

        knowledge_text = "\n\n-----\n\n".join(analysis.knowledge_snippets[:6])
        user_prompt = build_analyze_user_prompt(
            question=question,
            category=route.type,
            related_palaces=route.related_palaces,
            traditional_analysis=analysis.traditional_analysis,
            modern_interpretation=analysis.modern_interpretation,
            strengths=analysis.strengths,
            knowledge_text=knowledge_text,
            chart_digest=_chart_digest(chart_data),
        )

        messages = [
            {"role": "system", "content": ZIWEI_AI_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]

        try:
            raw = await SiliconFlowClient.chat(messages)
        except SiliconFlowNotConfiguredError:
            return AnalyzeResponse(success=False, error="AI服务未配置")
        except SiliconFlowEmptyResponseError:
            return AnalyzeResponse(success=False, error="AI返回为空")
        except SiliconFlowRequestError:
            return AnalyzeResponse(success=False, error="AI服务调用失败")

        report = apply_safety_filter(raw)

        # 若模型输出仍过短，回退规则层拼接
        if len(report.strip()) < 40:
            report = apply_safety_filter(
                "\n\n".join(
                    [
                        "# 传统紫微分析",
                        analysis.traditional_analysis,
                        "# 现代解释",
                        analysis.modern_interpretation,
                        "# 优势分析",
                        "、".join(analysis.strengths) or "（待补充）",
                        "# 实际建议",
                        "建议把命盘象征当作自我观察工具，结合现实反馈分阶段验证与调整。",
                    ]
                )
            )

        return AnalyzeResponse(
            success=True,
            category=route.type,
            related_palaces=route.related_palaces,
            report=report,
            model=SiliconFlowClient.get_model(),
        )
