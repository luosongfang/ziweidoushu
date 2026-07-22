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
