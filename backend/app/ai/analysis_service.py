"""AI 分析服务 — 编排上下文、RAG、规则解读与 LLM。"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from app.ai.context_builder import ContextBuilder
from app.ai.llm_client import LlmClient
from app.ai.prompt_builder import PromptBuilder
from app.ai.rag_retriever import RagRetriever
from app.models.analysis import AnalysisGenerateRequest, AnalysisOutput, AnalysisSection
from app.models.birth import BirthInput, ChartGenerateRequest
from app.models.chart import ChartOutput
from app.ziwei.chart_generator import ChartGenerator


class AnalysisService:
    """AI 分析入口。"""

    @classmethod
    async def generate(cls, request: AnalysisGenerateRequest) -> AnalysisOutput:
        chart = cls._resolve_chart(request)
        context = ContextBuilder.build(
            chart,
            request.analysis_type,
            request.palace_name,
        )
        rag_chunks = RagRetriever.retrieve(context["rag_queries"])

        use_llm = cls._should_use_llm(request.mode)
        if use_llm:
            return await cls._generate_llm(
                chart, context, rag_chunks, request.analysis_type, request.palace_name
            )
        return cls._generate_rules(
            chart, context, rag_chunks, request.analysis_type, request.palace_name
        )

    @staticmethod
    def _resolve_chart(request: AnalysisGenerateRequest) -> ChartOutput:
        if request.chart is not None:
            chart = request.chart
        else:
            assert request.birth is not None
            birth = request.birth
            if request.reference_date:
                ref = datetime.strptime(request.reference_date, "%Y-%m-%d")
            else:
                ref = datetime.now()
            gen_request = ChartGenerateRequest.from_birth_input(birth)
            chart = ChartGenerator.generate(gen_request, reference_date=ref)
        return chart

    @staticmethod
    def _should_use_llm(mode: str) -> bool:
        if mode == "rules":
            return False
        if mode == "llm":
            if not LlmClient.is_available():
                raise RuntimeError("mode=llm 但未配置 OPENAI_API_KEY")
            return True
        return LlmClient.is_available()

    @classmethod
    def _generate_rules(
        cls,
        chart: ChartOutput,
        context: dict[str, Any],
        rag_chunks: list,
        analysis_type: str,
        palace_name: str | None,
    ) -> AnalysisOutput:
        sections: list[AnalysisSection] = []

        if analysis_type == "overall":
            sections.append(cls._section_overview(context))
            sections.append(cls._section_ming_gong(context))
            sections.append(cls._section_combinations(context))
            sections.append(cls._section_four_transform(context))
            sections.append(cls._section_fortune(context))
        elif analysis_type == "palace":
            sections.append(cls._section_palace_focus(context, palace_name))
        elif analysis_type == "daxian":
            sections.append(cls._section_daxian(context))
        elif analysis_type == "liunian":
            sections.append(cls._section_liunian(context))

        if rag_chunks:
            sections.append(cls._section_knowledge(rag_chunks))

        sections.append(cls._section_disclaimer())
        result_text = "\n\n".join(f"## {s.title}\n\n{s.content}" for s in sections)

        return AnalysisOutput(
            prompt_version=ContextBuilder.PROMPT_VERSION,
            analysis_type=analysis_type,
            mode="rules",
            sections=sections,
            result_text=result_text,
            input_context=context,
            rag_chunks=rag_chunks,
            chart_summary=cls._chart_summary(chart),
        )

    @classmethod
    async def _generate_llm(
        cls,
        chart: ChartOutput,
        context: dict[str, Any],
        rag_chunks: list,
        analysis_type: str,
        palace_name: str | None,
    ) -> AnalysisOutput:
        messages = PromptBuilder.build_llm_messages(
            context, rag_chunks, analysis_type, palace_name
        )
        result_text, tokens = await LlmClient.chat(messages)
        sections = [AnalysisSection(title="AI 解读", content=result_text, sources=["llm"])]

        return AnalysisOutput(
            prompt_version=ContextBuilder.PROMPT_VERSION,
            analysis_type=analysis_type,
            mode="llm",
            sections=sections,
            result_text=result_text,
            input_context=context,
            rag_chunks=rag_chunks,
            tokens_used=tokens,
            chart_summary=cls._chart_summary(chart),
        )

    @staticmethod
    def _chart_summary(chart: ChartOutput) -> dict[str, Any]:
        return {
            "name": chart.meta.name,
            "mingGong": chart.meta.mingGong,
            "wuxingJu": chart.meta.wuxingJu,
            "combinationCount": len(chart.combinations.patterns),
        }

    @staticmethod
    def _section_overview(context: dict[str, Any]) -> AnalysisSection:
        meta = context["meta"]
        birth = context["birth"]
        gz = birth["ganzhi"]
        content = (
            f"**{meta['name']}**（{'男' if meta['gender'] == 'male' else '女'}）\n\n"
            f"- 阳历：{birth['solar']}\n"
            f"- 农历：{birth['lunar']}\n"
            f"- 四柱：{gz['year']} {gz['month']} {gz['day']} {gz['hour']}\n"
            f"- 时辰：{birth['shichen']}\n"
            f"- 命宫：{meta['mingGongGanZhi']}（{meta['mingGong']}）\n"
            f"- 身宫：{meta['shenGong']}\n"
            f"- 五行局：{meta['wuxingJu']}\n"
            f"- 命主：{meta['mingZhu']}，身主：{meta['shenZhu']}"
        )
        return AnalysisSection(title="命盘概览", content=content, sources=["chart"])

    @staticmethod
    def _section_ming_gong(context: dict[str, Any]) -> AnalysisSection:
        ming = next((p for p in context["palaces"] if p["isMingGong"]), None)
        if not ming:
            return AnalysisSection(title="命宫解读", content="未找到命宫数据。", sources=[])

        stars = "、".join(ming["mainStars"]) if ming["mainStars"] else "无主星"
        lines = [
            f"命宫位于 **{ming['ganzhi']}**，主星：{stars}。",
            f"宫位语义：{ming['meaning']}",
        ]
        if ming["ai_prompt"]:
            lines.append(ming["ai_prompt"])

        star_prompts = [
            sp for sp in context["star_prompts"]
            if sp["star"] in ming["mainStars"]
        ]
        for sp in star_prompts:
            lines.append(f"- {sp['prompt']}")

        return AnalysisSection(title="命宫解读", content="\n\n".join(lines), sources=["rules"])

    @staticmethod
    def _section_combinations(context: dict[str, Any]) -> AnalysisSection:
        combos = context.get("combinations", [])
        if not combos:
            return AnalysisSection(title="格局分析", content="本盘未识别特殊格局。", sources=["rules"])

        lines = [f"共识别 **{len(combos)}** 个格局：\n"]
        for c in combos:
            palaces = f"（{', '.join(c['palaces'])}）" if c["palaces"] else ""
            lines.append(f"**{c['name']}**{palaces}")
            if c.get("tags"):
                lines.append(f"  特质：{', '.join(c['tags'])}")
            if c.get("ai_prompt"):
                lines.append(f"  {c['ai_prompt']}")
            lines.append("")

        return AnalysisSection(title="格局分析", content="\n".join(lines), sources=["rules"])

    @staticmethod
    def _section_four_transform(context: dict[str, Any]) -> AnalysisSection:
        ft = context.get("four_transform")
        if not ft:
            return AnalysisSection(title="四化分析", content="无生年四化数据。", sources=[])

        lines = [
            f"**{ft['yearStem']}年** 生年四化：\n",
            f"- **化禄**：{ft['lu']['star']} → {ft['lu']['palace']}宫",
            f"- **化权**：{ft['quan']['star']} → {ft['quan']['palace']}宫",
            f"- **化科**：{ft['ke']['star']} → {ft['ke']['palace']}宫",
            f"- **化忌**：{ft['ji']['star']} → {ft['ji']['palace']}宫",
            "",
            "四化落宫决定该领域得与失的方向，化禄主机遇、化权主掌控、化科主名声、化忌主阻碍。",
        ]
        return AnalysisSection(title="四化分析", content="\n".join(lines), sources=["rules"])

    @staticmethod
    def _section_fortune(context: dict[str, Any]) -> AnalysisSection:
        fortune = context.get("fortune", {})
        lines = [f"大限方向：**{'顺行' if fortune.get('daxianDirection') == 'forward' else '逆行'}**"]

        if fortune.get("currentDaxian"):
            dx = fortune["currentDaxian"]
            lines.append(
                f"当前大限：**{dx.get('palace', '未知')}宫**"
                f"（{dx.get('startAge', '?')}–{dx.get('endAge', '?')} 岁）"
            )
        if fortune.get("annualFortune"):
            af = fortune["annualFortune"]
            lines.append(f"流年太岁：**{af.get('branch', '')}** → {af.get('palace', '')}宫")
        if fortune.get("monthlyFortune"):
            mf = fortune["monthlyFortune"]
            lines.append(f"流月：**{mf.get('month', '?')}月** → {mf.get('palace', '')}宫")

        return AnalysisSection(title="运限概览", content="\n".join(lines), sources=["chart"])

    @staticmethod
    def _section_palace_focus(context: dict[str, Any], palace_name: str | None) -> AnalysisSection:
        palace = next(
            (p for p in context["palaces"] if p["name"] == palace_name),
            None,
        )
        if not palace:
            return AnalysisSection(
                title=f"{palace_name}解读",
                content=f"未找到「{palace_name}」宫位数据。",
                sources=[],
            )

        stars = "、".join(palace["mainStars"]) if palace["mainStars"] else "无主星"
        aux = "、".join(
            s for s in palace["stars"] if s not in palace["mainStars"]
        )
        lines = [
            f"**{palace['name']}**（{palace['ganzhi']}，{palace['branch']}支）",
            f"主星：{stars}",
        ]
        if aux:
            lines.append(f"辅煞星：{aux}")
        lines.append(f"\n宫位语义：{palace['meaning']}")
        if palace["ai_prompt"]:
            lines.append(palace["ai_prompt"])

        if palace.get("daxian"):
            dx = palace["daxian"]
            lines.append(f"\n该宫大限：{dx['startAge']}–{dx['endAge']} 岁")

        return AnalysisSection(
            title=f"{palace_name}解读",
            content="\n".join(lines),
            sources=["rules"],
        )

    @staticmethod
    def _section_daxian(context: dict[str, Any]) -> AnalysisSection:
        fortune = context.get("fortune", {})
        dx = fortune.get("currentDaxian")
        if not dx:
            return AnalysisSection(title="大限运势", content="暂无大限数据。", sources=[])

        palace_name = dx.get("palace", "")
        palace = next(
            (p for p in context["palaces"] if p["name"] == palace_name),
            None,
        )
        lines = [
            f"当前处于 **{palace_name}宫** 大限（{dx.get('startAge')}–{dx.get('endAge')} 岁）。",
        ]
        if palace:
            stars = "、".join(palace["mainStars"]) if palace["mainStars"] else "无主星"
            lines.append(f"该宫主星：{stars}")
            if palace["ai_prompt"]:
                lines.append(palace["ai_prompt"])

        lines.append(
            f"\n大限方向：{'顺行' if fortune.get('daxianDirection') == 'forward' else '逆行'}。"
            "此十年该宫星曜与四化主导人生重心，宜结合三方四正综合判断。"
        )
        return AnalysisSection(title="大限运势", content="\n".join(lines), sources=["rules", "chart"])

    @staticmethod
    def _section_liunian(context: dict[str, Any]) -> AnalysisSection:
        fortune = context.get("fortune", {})
        af = fortune.get("annualFortune")
        if not af:
            return AnalysisSection(title="流年运势", content="暂无流年数据。", sources=[])

        palace_name = af.get("palace", "")
        palace = next(
            (p for p in context["palaces"] if p["name"] == palace_name),
            None,
        )
        lines = [
            f"流年太岁 **{af.get('branch', '')}** 入 **{palace_name}宫**。",
        ]
        if palace:
            stars = "、".join(palace["mainStars"]) if palace["mainStars"] else "无主星"
            lines.append(f"该宫主星：{stars}")
            if palace["ai_prompt"]:
                lines.append(palace["ai_prompt"])

        if fortune.get("monthlyFortune"):
            mf = fortune["monthlyFortune"]
            lines.append(f"\n当前流月：{mf.get('month')}月 → {mf.get('palace')}宫")

        return AnalysisSection(title="流年运势", content="\n".join(lines), sources=["rules", "chart"])

    @staticmethod
    def _section_knowledge(rag_chunks: list) -> AnalysisSection:
        lines = ["以下知识库片段供参考：\n"]
        for chunk in rag_chunks:
            title = chunk.title or chunk.category
            lines.append(f"**[{title}]**（{chunk.source}）")
            lines.append(chunk.content)
            lines.append("")
        return AnalysisSection(
            title="知识库参考",
            content="\n".join(lines),
            sources=[c.source for c in rag_chunks],
        )

    @staticmethod
    def _section_disclaimer() -> AnalysisSection:
        return AnalysisSection(
            title="温馨提示",
            content="以上解读基于三合紫微斗数规则引擎与知识库，仅供文化研究与自我参考，不构成任何决策建议。人生走向仍取决于个人选择与努力。",
            sources=[],
        )
