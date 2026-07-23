"""Question classifier — maps user question to life_question_models.question_type."""

from __future__ import annotations

from app.knowledge.knowledge_loader import KnowledgeLoader


_KEYWORD_MAP: list[tuple[str, list[str]]] = [
    ("entrepreneurship", ["创业", "自己干", "开公司", "做老板"]),
    ("career_switch", ["转行", "换赛道", "跳槽方向", "职业转换"]),
    ("career", ["事业", "工作", "职业", "升职", "发展方向"]),
    ("wealth", ["财富", "赚钱", "收入", "投资", "理财", "财务"]),
    ("marriage", ["婚姻", "结婚", "婚后", "婚姻经营"]),
    ("relationship", ["感情", "恋爱", "伴侣", "相亲"]),
    ("study", ["学习", "考试", "学业", "进修", "考证"]),
    ("family", ["家庭", "父母", "子女", "家人"]),
    ("life_stage", ["未来", "阶段", "大限", "流年", "规划"]),
    ("personality", ["性格", "成长", "认识自己", "我是谁"]),
]


class QuestionClassifier:
    @classmethod
    def classify(cls, question: str) -> str:
        text = question or ""
        best = "personality"
        best_hits = 0
        for qtype, kws in _KEYWORD_MAP:
            hits = sum(1 for k in kws if k in text)
            if hits > best_hits:
                best_hits = hits
                best = qtype
        # ensure model exists; fallback career/personality
        if KnowledgeLoader.get_question_model(best) is None:
            return "career" if KnowledgeLoader.get_question_model("career") else "personality"
        return best
