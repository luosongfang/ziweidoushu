"""用户问题分类 — 识别分析方向与相关宫位。"""

from __future__ import annotations

from app.ziwei_ai.schemas import QuestionRoute

_CATEGORY_RULES: list[tuple[str, list[str], list[str]]] = [
    (
        "事业",
        ["工作", "创业", "职业", "发展", "事业", "升职", "跳槽", "岗位", "方向"],
        ["命宫", "官禄宫", "财帛宫"],
    ),
    (
        "财富",
        ["赚钱", "收入", "投资", "财富", "理财", "财务", "钱", "资产"],
        ["财帛宫", "田宅宫"],
    ),
    (
        "感情",
        ["婚姻", "伴侣", "关系", "感情", "恋爱", "结婚", "桃花", "配偶"],
        ["夫妻宫", "福德宫"],
    ),
    (
        "成长",
        ["未来", "规划", "选择", "成长", "人生", "自我", "提升", "学习"],
        ["命宫", "大限", "流年"],
    ),
]


def route_question(question: str) -> QuestionRoute:
    """根据关键词识别问题类型；无命中时默认成长。"""
    text = (question or "").strip()
    best: QuestionRoute | None = None
    best_hits = 0

    for category, keywords, palaces in _CATEGORY_RULES:
        hits = [kw for kw in keywords if kw in text]
        if len(hits) > best_hits:
            best_hits = len(hits)
            best = QuestionRoute(
                type=category,
                related_palaces=list(palaces),
                keywords_hit=hits,
            )

    if best is None:
        return QuestionRoute(
            type="成长",
            related_palaces=["命宫", "大限", "流年"],
            keywords_hit=[],
        )
    return best
