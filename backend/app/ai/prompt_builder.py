"""LLM 提示词构建。"""

from __future__ import annotations

from typing import Any

from app.models.analysis import RagChunkRef


SYSTEM_PROMPT = """你是一位精通三合紫微斗数的专业命理分析师。
请基于提供的命盘结构化数据与知识库片段，给出专业、客观、有依据的解读。
要求：
1. 仅依据给定数据，不编造星曜或宫位
2. 语言清晰、结构分明，适合普通用户阅读
3. 区分「先天格局」与「运限变化」
4. 结尾提醒：命理仅供参考，人生仍由自身努力决定
"""


class PromptBuilder:
    @classmethod
    def build_llm_messages(
        cls,
        context: dict[str, Any],
        rag_chunks: list[RagChunkRef],
        analysis_type: str,
        palace_name: str | None,
    ) -> list[dict[str, str]]:
        user_content = cls._build_user_prompt(context, rag_chunks, analysis_type, palace_name)
        return [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ]

    @classmethod
    def _build_user_prompt(
        cls,
        context: dict[str, Any],
        rag_chunks: list[RagChunkRef],
        analysis_type: str,
        palace_name: str | None,
    ) -> str:
        meta = context["meta"]
        lines = [
            f"分析类型：{analysis_type}",
            f"姓名：{meta['name']}（{meta['gender']}）",
            f"命宫：{meta['mingGongGanZhi']}，身宫：{meta['shenGong']}，五行局：{meta['wuxingJu']}",
            f"四柱：{context['birth']['ganzhi']['year']} {context['birth']['ganzhi']['month']} "
            f"{context['birth']['ganzhi']['day']} {context['birth']['ganzhi']['hour']}",
        ]

        if analysis_type == "palace" and palace_name:
            lines.append(f"请重点解读「{palace_name}」")
        elif analysis_type == "daxian":
            lines.append("请重点解读当前大限运势")
        elif analysis_type == "liunian":
            lines.append("请重点解读流年运势")

        if context.get("four_transform"):
            ft = context["four_transform"]
            lines.append(
                f"生年四化（{ft['yearStem']}年）："
                f"禄-{ft['lu']['star']}({ft['lu']['palace']}) "
                f"权-{ft['quan']['star']}({ft['quan']['palace']}) "
                f"科-{ft['ke']['star']}({ft['ke']['palace']}) "
                f"忌-{ft['ji']['star']}({ft['ji']['palace']})"
            )

        if context.get("combinations"):
            combo_names = [c["name"] for c in context["combinations"]]
            lines.append(f"识别格局：{', '.join(combo_names)}")

        focused_palaces = [p for p in context["palaces"] if p.get("focused")] or [
            p for p in context["palaces"] if p["isMingGong"]
        ]
        for p in focused_palaces[:3]:
            stars = "、".join(p["mainStars"]) or "无主星"
            lines.append(f"{p['name']}（{p['ganzhi']}）：主星 {stars}")

        if rag_chunks:
            lines.append("\n【知识库参考】")
            for chunk in rag_chunks:
                title = chunk.title or chunk.category
                lines.append(f"- [{title}] {chunk.content}")

        lines.append("\n请输出结构化 Markdown 解读。")
        return "\n".join(lines)


KNOWLEDGE_CORE_SYSTEM_PROMPT = """你是一名东方人生规划 AI 助手。

你必须严格基于「Ziwei Knowledge Core」提供的数据进行分析，不得自行编造紫微解释。

定位：
传统文化分析参考 + 自我认知工具 + 人生规划辅助。
不是算命，不做绝对预测。

禁止：一定、必然、注定、百分百、灾难恐吓、疾病诊断、死亡预测、财富保证。
请使用：倾向、可能、优势、建议。

请只输出一个 JSON 对象（不要 Markdown 代码块），字段如下：
{
  "summary": "核心观察",
  "traditional_view": "传统紫微理论解释（仅基于给定知识）",
  "strengths": ["优势"],
  "challenges": ["需要注意"],
  "suggestions": ["成长建议"],
  "risk_warning": "风险提示",
  "disclaimer": "本分析基于传统文化理论，仅作为自我认知和人生规划参考，不代表确定预测"
}
"""


class KnowledgeCorePromptBuilder:
    """Knowledge Core V1.0 Prompt 构建器。"""

    @classmethod
    def build(cls, question: str, context: dict[str, Any]) -> list[dict[str, str]]:
        return [
            {"role": "system", "content": KNOWLEDGE_CORE_SYSTEM_PROMPT},
            {"role": "user", "content": cls._user_prompt(question, context)},
        ]

    @classmethod
    def _user_prompt(cls, question: str, context: dict[str, Any]) -> str:
        import json

        payload = {
            "question": question,
            "question_type": context.get("question_type"),
            "question_model": {
                "analysis_logic": (context.get("question_model") or {}).get("analysis_logic"),
                "safety_notice": (context.get("question_model") or {}).get("safety_notice"),
                "required_palaces": context.get("required_palaces"),
            },
            "chart_stars": context.get("chart_stars"),
            "stars_knowledge": [
                {
                    "star_name": s.get("star_name"),
                    "basic_meaning": s.get("basic_meaning"),
                    "traditional_description": s.get("traditional_description"),
                    "personality_positive": s.get("personality_positive"),
                    "personality_challenge": s.get("personality_challenge"),
                    "career_strength": s.get("career_strength"),
                    "growth_advice": s.get("growth_advice"),
                    "ai_prompt": s.get("ai_prompt"),
                }
                for s in (context.get("stars") or [])
            ],
            "palace_knowledge": [
                {
                    "palace_name": p.get("palace_name"),
                    "basic_meaning": p.get("basic_meaning"),
                    "positive_expression": p.get("positive_expression"),
                    "challenge_expression": p.get("challenge_expression"),
                    "development_direction": p.get("development_direction"),
                    "ai_prompt": p.get("ai_prompt"),
                }
                for p in (context.get("palaces") or [])
            ],
            "patterns": [
                {
                    "pattern_name": p.get("pattern_name"),
                    "traditional_meaning": p.get("traditional_meaning"),
                    "advantages": p.get("advantages"),
                    "challenges": p.get("challenges"),
                    "career_analysis": p.get("career_analysis"),
                    "growth_advice": p.get("growth_advice"),
                    "ai_prompt": p.get("ai_prompt"),
                }
                for p in (context.get("patterns") or [])
            ],
            "theory": [
                {
                    "topic": t.get("topic"),
                    "summary": t.get("summary"),
                    "content": t.get("content"),
                }
                for t in (context.get("theory") or [])[:5]
            ],
            "safety_rules": [
                {
                    "forbidden_expression": r.get("forbidden_expression"),
                    "safe_expression": r.get("safe_expression"),
                }
                for r in (context.get("safety_rules") or [])
            ],
        }
        return (
            "请仅基于下列 Knowledge Core JSON 回答用户问题，不得添加未提供的紫微结论：\n"
            + json.dumps(payload, ensure_ascii=False)
        )
