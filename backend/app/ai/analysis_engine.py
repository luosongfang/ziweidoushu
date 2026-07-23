"""Knowledge Core AI 分析引擎 — 基于数据库知识，禁止编造。"""

from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel, Field

from app.ai.safety_filter import SafetyFilter
from app.ai.siliconflow_client import (
    SiliconFlowClient,
    SiliconFlowEmptyResponseError,
    SiliconFlowNotConfiguredError,
    SiliconFlowRequestError,
)
from app.knowledge.knowledge_service import KnowledgeService
from app.ai.prompt_builder import KnowledgeCorePromptBuilder


DEFAULT_DISCLAIMER = (
    "本分析基于传统文化理论，仅作为自我认知和人生规划参考，不代表确定预测"
)


class KnowledgeCoreReport(BaseModel):
    summary: str = ""
    traditional_view: str = ""
    strengths: list[str] = Field(default_factory=list)
    challenges: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    risk_warning: str = ""
    disclaimer: str = DEFAULT_DISCLAIMER
    question_type: str | None = None
    model: str | None = None
    success: bool = True
    error: str | None = None


class AnalysisEngine:
    """
    用户问题 → Life Question Model → Chart JSON → Knowledge Core
    → Prompt → LLM → Safety Filter → 标准输出
    """

    @classmethod
    async def analyze(
        cls,
        chart_data: dict[str, Any] | str,
        question: str,
    ) -> KnowledgeCoreReport:
        question = (question or "").strip()
        if not question:
            return KnowledgeCoreReport(success=False, error="请提供问题")

        if not SiliconFlowClient.is_configured():
            return KnowledgeCoreReport(success=False, error="AI服务未配置")

        context = KnowledgeService.build_context(chart_data, question)
        messages = KnowledgeCorePromptBuilder.build(question=question, context=context)

        try:
            raw = await SiliconFlowClient.chat(messages)
        except SiliconFlowNotConfiguredError:
            return KnowledgeCoreReport(success=False, error="AI服务未配置")
        except SiliconFlowEmptyResponseError:
            return KnowledgeCoreReport(success=False, error="AI返回为空")
        except SiliconFlowRequestError:
            return KnowledgeCoreReport(success=False, error="AI服务调用失败")

        filtered = SafetyFilter.apply(raw)
        report = cls._parse_report(filtered, context)
        report.model = SiliconFlowClient.get_model()
        report.question_type = context.get("question_type")
        return report

    @classmethod
    def _parse_report(cls, text: str, context: dict[str, Any]) -> KnowledgeCoreReport:
        """优先解析 JSON；失败则用知识库拼装兜底。"""
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            if cleaned.startswith("json"):
                cleaned = cleaned[4:].strip()
        try:
            data = json.loads(cleaned)
            return KnowledgeCoreReport(
                summary=str(data.get("summary") or ""),
                traditional_view=str(data.get("traditional_view") or ""),
                strengths=list(data.get("strengths") or []),
                challenges=list(data.get("challenges") or []),
                suggestions=list(data.get("suggestions") or []),
                risk_warning=str(data.get("risk_warning") or ""),
                disclaimer=str(data.get("disclaimer") or DEFAULT_DISCLAIMER),
            )
        except Exception:
            return cls._fallback_from_knowledge(context, text)

    @classmethod
    def _fallback_from_knowledge(cls, context: dict[str, Any], raw: str) -> KnowledgeCoreReport:
        stars = context.get("stars") or []
        patterns = context.get("patterns") or []
        strengths: list[str] = []
        challenges: list[str] = []
        traditional_bits: list[str] = []
        for s in stars:
            strengths.extend(s.get("personality_positive") or [])
            challenges.extend(s.get("personality_challenge") or [])
            if s.get("traditional_description"):
                traditional_bits.append(str(s["traditional_description"]))
        for p in patterns:
            strengths.extend(p.get("advantages") or [])
            challenges.extend(p.get("challenges") or [])
            if p.get("traditional_meaning"):
                traditional_bits.append(str(p["traditional_meaning"]))

        notice = (context.get("question_model") or {}).get("safety_notice") or ""
        return KnowledgeCoreReport(
            summary=SafetyFilter.apply(raw[:280] if raw else "基于 Knowledge Core 的参考观察"),
            traditional_view="；".join(traditional_bits) or "请参考命盘相关宫位与星曜知识条目。",
            strengths=list(dict.fromkeys(strengths))[:6],
            challenges=list(dict.fromkeys(challenges))[:6],
            suggestions=[
                "把命盘象征当作自我观察工具，结合现实反馈分阶段验证。",
                "优先把优势落到可执行的小目标上。",
            ],
            risk_warning=notice or "涉及未来与重大风险时，请保持谨慎并制定预案。",
            disclaimer=DEFAULT_DISCLAIMER,
        )
