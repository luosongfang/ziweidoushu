"""AI 安全表达过滤 — 优先使用数据库 safety_expression_rules。"""

from __future__ import annotations

from app.knowledge.knowledge_loader import KnowledgeLoader, cached_safety_rules


_FALLBACK_RULES: list[tuple[str, str]] = [
    ("一定会发财", "可能具备财富管理优势，需要结合现实行动。"),
    ("稳赚不赔", "财务结果存在不确定性，建议控制风险。"),
    ("今年有灾", "这个阶段建议提高风险意识，做好规划。"),
    ("必有灾难", "建议提高准备度并制定预案。"),
    ("一定会", "比较可能"),
    ("必然", "较可能"),
    ("注定", "倾向于"),
    ("百分百", "在一定程度上"),
    ("疾病诊断", "健康议题请咨询专业医疗机构，这里只提供生活与压力管理建议。"),
    ("死亡预测", "关于寿命与重大健康风险，请以专业医疗建议为准。"),
]


class SafetyFilter:
    """对模型输出做安全替换。"""

    @classmethod
    def rules(cls) -> list[tuple[str, str]]:
        try:
            db_rules = list(cached_safety_rules())
            if db_rules:
                # longer forbidden first
                return sorted(db_rules, key=lambda x: len(x[0]), reverse=True)
        except Exception:
            pass
        return sorted(_FALLBACK_RULES, key=lambda x: len(x[0]), reverse=True)

    @classmethod
    def apply(cls, text: str) -> str:
        if not text:
            return text
        out = text
        for forbidden, safe in cls.rules():
            if forbidden and forbidden in out:
                out = out.replace(forbidden, safe)
        return out

    @classmethod
    def refresh_cache(cls) -> None:
        cached_safety_rules.cache_clear()
        # warm
        _ = KnowledgeLoader.list_safety_rules()
        cached_safety_rules()
