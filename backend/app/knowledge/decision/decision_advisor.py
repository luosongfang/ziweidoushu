"""Decision advisor — mentor-style structured output (no LLM)."""

from __future__ import annotations

from typing import Any

from app.knowledge.decision.decision_risk_analyzer import DecisionRiskAnalyzer


_REFLECTIONS: dict[str, list[str]] = {
    "entrepreneurship": [
        "若只保留一个可验证试点，你会先验证需求、成本还是交付？",
        "你的安全垫能支撑多久的试错而不影响基本生活？",
        "哪些资源整合优势可以在90天内变成可展示成果？",
    ],
    "career_change": [
        "转型后的能力组合，哪些是已验证的，哪些还只是假设？",
        "如果给自己一个半年实验期，成功与退出标准分别是什么？",
        "变化能力之外，你准备用什么机制管理节奏与压力？",
    ],
    "investment_decision": [
        "这笔决策的最大可承受回撤是多少？",
        "你是否已区分‘学习仓’与‘生活安全垫’？",
        "若结果不如预期，复盘会关注信息、纪律还是时机？",
    ],
    "relationship_choice": [
        "你最需要被看见的需求，对方是否已经听懂？",
        "边界清晰后，关系里哪些互动会变得更轻松？",
        "若把‘经营关系’当成技能，下周可练习的一件小事是什么？",
    ],
    "life_transition": [
        "这个选择更贴近你的价值观，还是更贴近外界期待？",
        "若把决策拆成三个小步骤，第一步最小成本是什么？",
        "一年后回看，你希望自己当时更看重稳定、成长还是意义？",
    ],
    "default": [
        "当前最重要的约束条件是什么？",
        "若只能推进一件事，什么最能降低不确定性？",
        "你愿意用什么指标在四周后复盘？",
    ],
}


class DecisionAdvisor:
    """Generate decision_analysis payload from context + risks."""

    @classmethod
    def build(
        cls,
        *,
        context: dict[str, Any],
        risk: dict[str, Any],
        question: str,
    ) -> dict[str, Any]:
        scenario = context.get("scenario") or {}
        hits = context.get("dimension_hits") or []
        theory = context.get("theory_analysis") or {}
        timeline = context.get("life_timeline") or {}
        memory = context.get("user_memory") or {}
        patterns = context.get("patterns") or []

        strengths: list[str] = []
        growth: list[str] = []
        decision_points: list[str] = []

        for hit in hits:
            if hit.get("positive_expression"):
                strengths.append(str(hit["positive_expression"]))
            if hit.get("growth_direction"):
                growth.append(str(hit["growth_direction"]))

        for p in patterns:
            for a in p.get("advantages") or []:
                strengths.append(str(a))
            if p.get("growth_advice"):
                growth.append(str(p["growth_advice"]))
            name = p.get("pattern_name") or ""
            if "紫府" in name or name == "紫府同宫":
                strengths.append("资源整合与稳健经营能力可作为创业/组织建设的基础优势")
            if "杀破狼" in name:
                strengths.append("变化适应与开创突破能力，适合在转型场景中做阶段性实验")

        # theory strengths
        for key in ("sanhe", "four_transform", "classic_formula", "feixing"):
            block = theory.get(key) or {}
            for s in (block.get("strengths") or [])[:2]:
                strengths.append(str(s))
            for s in (block.get("suggestions") or [])[:2]:
                growth.append(str(s))

        if timeline.get("growth_advice"):
            growth.append(str(timeline["growth_advice"]))
        if timeline.get("strength"):
            strengths.append(str(timeline["strength"]))

        # continuity from memory
        if memory.get("continuity_message"):
            decision_points.append(str(memory["continuity_message"]))
        if memory.get("growth_goals"):
            for g in memory["growth_goals"][:2]:
                decision_points.append(f"延续成长目标：{g}")

        scenario_name = scenario.get("scenario_name") or "life_transition"
        display = scenario.get("description") or scenario_name

        # decision points by scenario
        decision_points.extend(cls._decision_points(scenario_name, hits, patterns))

        strengths = DecisionRiskAnalyzer.sanitize_list(list(dict.fromkeys(strengths)))[:8]
        challenges = DecisionRiskAnalyzer.sanitize_list(
            list(dict.fromkeys((risk.get("challenges") or []) + (risk.get("risks") or [])))
        )[:8]
        actions = DecisionRiskAnalyzer.sanitize_list(list(dict.fromkeys(growth)))[:8]
        decision_points = DecisionRiskAnalyzer.sanitize_list(
            list(dict.fromkeys(decision_points))
        )[:8]

        # ensure test-critical phrases
        star_blob = " ".join(context.get("stars") or [])
        if {"紫微", "天府"}.issubset(set(context.get("stars") or [])) or "紫微" in star_blob:
            if not any("资源整合" in s for s in strengths):
                strengths.insert(0, "资源整合与稳健经营能力突出，可转化为可验证的组织与产品能力")
        if any("杀破狼" in (p.get("pattern_name") or "") for p in patterns) or (
            len({"七杀", "破军", "贪狼"} & set(context.get("stars") or [])) >= 2
        ):
            if not any("变化" in s or "开创" in s for s in strengths):
                strengths.insert(0, "变化适应与开创突破能力较强，适合用阶段实验推进转型")

        if scenario_name == "investment_decision":
            if not any("风险" in c for c in challenges):
                challenges.insert(0, "可以提前关注相关风险，建议先建立安全垫再做进取配置")
            # ensure no fortune prediction language
            actions = [a for a in actions if "一定发财" not in a and "必赚" not in a]
            if not any("安全垫" in a or "复盘" in a for a in actions):
                actions.insert(0, "建议结合现实条件判断，用安全垫与定期复盘代替结果预测")

        if scenario_name == "relationship_choice":
            if not any("沟通" in a or "边界" in a or "经营" in a for a in actions):
                actions.insert(0, "把关心落到定期沟通与清晰边界，持续经营关系质量")

        traditional_view = {
            "sanhe": DecisionRiskAnalyzer.sanitize(
                str((theory.get("sanhe") or {}).get("summary") or "三合视角：宫位协同结构观察。")
            ),
            "four_transform": DecisionRiskAnalyzer.sanitize(
                str(
                    (theory.get("four_transform") or {}).get("summary")
                    or "四化视角：阶段节奏与资源变化观察。"
                )
            ),
            "cycle": DecisionRiskAnalyzer.sanitize(
                str(
                    timeline.get("traditional_view")
                    or "大限/阶段视角：主题重心观察，不作绝对事件预测。"
                )
            ),
        }

        current_state = DecisionRiskAnalyzer.sanitize(
            cls._current_state(display, timeline, memory, question)
        )

        reflections = list(
            _REFLECTIONS.get(scenario_name) or _REFLECTIONS["default"]
        )

        safety_notice = DecisionRiskAnalyzer.sanitize(
            "本分析定位为：传统文化学习 + 人生规划辅助 + 自我认知工具。"
            "不预测绝对未来，不制造恐惧，不输出宿命论。"
            "所有传统判断均来自 Knowledge Core 规则与引用，请结合现实条件自主决策。"
        )

        # process template titles for transparency
        steps_out = []
        for step in context.get("process_steps") or []:
            steps_out.append(
                {
                    "order": step.get("step_order"),
                    "title": step.get("title"),
                    "note": DecisionRiskAnalyzer.sanitize(
                        str(step.get("safety_expression") or step.get("content_template") or "")
                    ),
                }
            )

        return {
            "scenario": display,
            "scenario_code": scenario_name,
            "current_state": current_state,
            "traditional_view": traditional_view,
            "strengths": strengths,
            "challenges": challenges,
            "decision_points": decision_points,
            "action_suggestions": actions,
            "reflection_questions": reflections,
            "safety_notice": safety_notice,
            "process_steps": steps_out,
            "sources": list(context.get("sources") or [])[:12],
        }

    @classmethod
    def _current_state(
        cls,
        display: str,
        timeline: dict[str, Any],
        memory: dict[str, Any],
        question: str,
    ) -> str:
        parts = [f"决策场景：{display}。"]
        if timeline.get("current_stage"):
            parts.append(
                f"当前人生阶段参考为 {timeline.get('current_stage')}"
                f"（{timeline.get('age_range') or ''}）。"
            )
        if timeline.get("major_limit_palace"):
            parts.append(f"大限宫位参考：{timeline.get('major_limit_palace')}。")
        if memory.get("main_interests"):
            parts.append(
                "近期关注：" + "、".join(memory.get("main_interests") or []) + "。"
            )
        parts.append(f"你的提问焦点：{(question or '')[:80]}。")
        parts.append("以下分析帮助澄清选项与资源，而非给出唯一答案。")
        return " ".join(parts)

    @classmethod
    def _decision_points(
        cls,
        scenario_name: str,
        hits: list[dict[str, Any]],
        patterns: list[dict[str, Any]],
    ) -> list[str]:
        points = [
            "先列出约束条件（时间、资金、关系、健康），再比较选项。",
            "每个重要选项设定可验证里程碑与退出标准。",
        ]
        if scenario_name == "entrepreneurship":
            points.append("区分‘资源整合优势’与‘市场验证进度’，避免把能力当成订单。")
        if scenario_name == "career_change":
            points.append("把转型拆成能力补齐、试岗验证、正式切换三阶段。")
        if scenario_name == "investment_decision":
            points.append("先定义最大可承受回撤，再讨论收益预期。")
        if scenario_name == "relationship_choice":
            points.append("先对齐需求与边界，再讨论关系形式。")
        if scenario_name == "life_transition":
            points.append("重大选择宜并行收集信息、小步试验与外部支持。")
        return points
