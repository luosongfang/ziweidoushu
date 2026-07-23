"""Build advisor continuity context from history / interests / goals (no LLM)."""

from __future__ import annotations

from typing import Any

from app.knowledge.memory.interest_analyzer import InterestAnalyzer

_INTEREST_CN = {
    "career": "事业发展",
    "wealth": "财富规划",
    "relationship": "感情关系",
    "family": "家庭关系",
    "learning": "学习成长",
    "growth": "自我成长",
}

_QTYPE_TOPIC = {
    "career": "事业",
    "entrepreneurship": "创业",
    "career_switch": "职业转换",
    "wealth": "财富规划",
    "relationship": "感情",
    "marriage": "婚姻",
    "family": "家庭",
    "study": "学习",
    "life_stage": "人生规划",
    "personality": "自我认知",
}

# Heuristic memory extraction from user-stated intent (no LLM)
_MEMORY_RULES: list[tuple[str, list[str], str]] = [
    (
        "goal",
        ["准备创业", "想创业", "计划创业", "创业", "开公司"],
        "用户关注创业方向，希望了解自身优势和风险管理。",
    ),
    (
        "goal",
        ["想转行", "准备转行", "换赛道", "职业转换"],
        "用户关注职业转换，希望明确方向与阶段节奏。",
    ),
    (
        "goal",
        ["升职", "晋升", "事业发展", "职业规划"],
        "用户关注事业路径，希望把优势落到可执行规划。",
    ),
    (
        "goal",
        ["理财", "财富规划", "投资", "提高收入"],
        "用户关注财富规划，希望建立稳健的资源配置意识。",
    ),
    (
        "challenge",
        ["纠结", "迷茫", "压力", "焦虑", "困难", "挑战"],
        "用户表达了阶段性困惑，适合用复盘与小步验证推进。",
    ),
    (
        "decision",
        ["要不要", "该不该", "如何选择", "做决定", "决策"],
        "用户面临选择点，适合对照价值观与资源约束做决策框架。",
    ),
    (
        "plan",
        ["计划", "规划", "下一步", "怎么做", "行动"],
        "用户希望形成可执行计划，适合拆成阶段目标与复盘节点。",
    ),
    (
        "reflection",
        ["反思", "复盘", "认识自己", "我是谁", "性格"],
        "用户关注自我认知与复盘，适合结合传统文化做成长对照。",
    ),
]


class GrowthContextBuilder:
    """Assemble advisor_context + continuity_message for next consultation."""

    @classmethod
    def extract_growth_memories(cls, question: str) -> list[dict[str, str]]:
        text = question or ""
        out: list[dict[str, str]] = []
        seen_types: set[str] = set()
        for memory_type, kws, content in _MEMORY_RULES:
            if any(k in text for k in kws):
                # allow one per type per question to avoid spam
                if memory_type in seen_types:
                    continue
                seen_types.add(memory_type)
                out.append({"memory_type": memory_type, "content": content})
        return out

    @classmethod
    def previous_topics(
        cls,
        history: list[dict[str, Any]],
        keywords: list[str] | None = None,
        limit: int = 6,
    ) -> list[str]:
        topics: list[str] = []
        for kw in keywords or []:
            if kw and kw not in topics:
                topics.append(kw)
        for row in history:
            qtype = row.get("question_type") or ""
            label = _QTYPE_TOPIC.get(qtype)
            if label and label not in topics:
                topics.append(label)
            for kw in InterestAnalyzer.extract_keywords(str(row.get("question") or "")):
                if kw not in topics:
                    topics.append(kw)
        return topics[:limit]

    @classmethod
    def continuity_message(
        cls,
        *,
        main_interests: list[str],
        previous_topics: list[str],
        question_type: str,
        has_history: bool,
    ) -> str:
        if not has_history:
            focus = _INTEREST_CN.get(main_interests[0], _QTYPE_TOPIC.get(question_type, "成长")) if main_interests else _QTYPE_TOPIC.get(question_type, "自我认知")
            return f"这是你的首次咨询记录。本次将围绕「{focus}」做传统文化学习与人生规划参考。"

        focus_cn = _INTEREST_CN.get(
            main_interests[0] if main_interests else "",
            _QTYPE_TOPIC.get(question_type, "成长"),
        )
        topic_hint = "、".join(previous_topics[:3]) if previous_topics else focus_cn
        return (
            f"根据你之前关注的发展方向（{topic_hint}），"
            f"本次重点分析{focus_cn}相关路径，帮助你延续学习与规划。"
        )

    @classmethod
    def build_summary(
        cls,
        *,
        main_interests: list[str],
        previous_topics: list[str],
        goals: list[str],
    ) -> str:
        parts: list[str] = []
        if main_interests:
            cn = [_INTEREST_CN.get(i, i) for i in main_interests]
            parts.append("主要关注：" + "、".join(cn))
        if previous_topics:
            parts.append("近期主题：" + "、".join(previous_topics[:5]))
        if goals:
            parts.append("成长目标：" + "；".join(goals[:3]))
        return "。".join(parts) if parts else "用户正在建立个人成长档案。"

    @classmethod
    def build_user_context_payload(
        cls,
        *,
        profile: dict[str, Any],
        history: list[dict[str, Any]],
        memories: list[dict[str, Any]],
        continuity: dict[str, Any] | None,
        question_type: str,
    ) -> dict[str, Any]:
        main = InterestAnalyzer.main_interests(profile)
        prev = cls.previous_topics(history, keywords=list(profile.get("keywords") or []))
        goals = [m["content"] for m in memories if m.get("memory_type") == "goal"]
        has_history = len(history) >= 2
        msg = cls.continuity_message(
            main_interests=main,
            previous_topics=prev,
            question_type=question_type,
            has_history=has_history,
        )
        return {
            "main_interests": main,
            "previous_topics": prev,
            "continuity_message": msg,
            "growth_goals": goals[:5],
            "interest_scores": {
                "career": float(profile.get("career_interest") or 0),
                "wealth": float(profile.get("wealth_interest") or 0),
                "relationship": float(profile.get("relationship_interest") or 0),
                "family": float(profile.get("family_interest") or 0),
                "learning": float(profile.get("learning_interest") or 0),
                "growth": float(profile.get("growth_interest") or 0),
            },
            "summary": (continuity or {}).get("summary")
            or cls.build_summary(main_interests=main, previous_topics=prev, goals=goals),
        }

    @classmethod
    def advisor_context(
        cls,
        user_context_payload: dict[str, Any],
        question_type: str,
    ) -> dict[str, Any]:
        """Compact context for AdvisorEngine consumption."""
        return {
            "main_interests": user_context_payload.get("main_interests") or [],
            "previous_topics": user_context_payload.get("previous_topics") or [],
            "continuity_message": user_context_payload.get("continuity_message") or "",
            "growth_goals": user_context_payload.get("growth_goals") or [],
            "question_type": question_type,
            "focus_hint": user_context_payload.get("continuity_message") or "",
        }
