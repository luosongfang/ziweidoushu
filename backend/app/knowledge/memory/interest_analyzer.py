"""Interest weight updates from question types (rule-based, no LLM)."""

from __future__ import annotations

import re
from typing import Any

# Map classifier question_type → interest field deltas
_QTYPE_DELTAS: dict[str, dict[str, float]] = {
    "career": {"career_interest": 0.10, "growth_interest": 0.03},
    "entrepreneurship": {"career_interest": 0.12, "wealth_interest": 0.05, "growth_interest": 0.05},
    "career_switch": {"career_interest": 0.10, "growth_interest": 0.06},
    "wealth": {"wealth_interest": 0.10, "career_interest": 0.03},
    "relationship": {"relationship_interest": 0.10, "growth_interest": 0.03},
    "marriage": {"relationship_interest": 0.12, "family_interest": 0.05},
    "family": {"family_interest": 0.10, "relationship_interest": 0.03},
    "study": {"learning_interest": 0.10, "growth_interest": 0.05},
    "life_stage": {"growth_interest": 0.10, "career_interest": 0.03},
    "personality": {"growth_interest": 0.10, "learning_interest": 0.03},
}

_TOPIC_KEYWORDS: list[tuple[str, list[str]]] = [
    ("创业", ["创业", "开公司", "自己干", "做老板"]),
    ("事业", ["事业", "工作", "职业", "升职"]),
    ("财富规划", ["财富", "理财", "收入", "投资", "财务"]),
    ("感情", ["感情", "恋爱", "伴侣", "婚姻"]),
    ("家庭", ["家庭", "父母", "子女", "家人"]),
    ("学习成长", ["学习", "考试", "进修", "成长", "认识自己"]),
    ("人生规划", ["规划", "大限", "流年", "阶段", "未来"]),
]

_INTEREST_FIELDS = (
    "career_interest",
    "wealth_interest",
    "relationship_interest",
    "family_interest",
    "learning_interest",
    "growth_interest",
)

_FIELD_TO_LABEL = {
    "career_interest": "career",
    "wealth_interest": "wealth",
    "relationship_interest": "relationship",
    "family_interest": "family",
    "learning_interest": "learning",
    "growth_interest": "growth",
}


def _clamp(v: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, round(v, 4)))


class InterestAnalyzer:
    """Update interest profile weights from classified questions."""

    @classmethod
    def deltas_for_question_type(cls, question_type: str) -> dict[str, float]:
        return dict(_QTYPE_DELTAS.get(question_type or "", {"growth_interest": 0.05}))

    @classmethod
    def extract_keywords(cls, question: str, limit: int = 8) -> list[str]:
        text = question or ""
        found: list[str] = []
        for label, kws in _TOPIC_KEYWORDS:
            if any(k in text for k in kws):
                found.append(label)
        # light token harvest: 2–4 char Chinese phrases already matched only
        return found[:limit]

    @classmethod
    def apply_deltas(
        cls,
        profile: dict[str, Any],
        question_type: str,
        question: str = "",
    ) -> dict[str, Any]:
        out = {f: float(profile.get(f) or 0.0) for f in _INTEREST_FIELDS}
        for field, delta in cls.deltas_for_question_type(question_type).items():
            if field in out:
                out[field] = _clamp(out[field] + delta)

        keywords = list(profile.get("keywords") or [])
        for kw in cls.extract_keywords(question):
            if kw not in keywords:
                keywords.append(kw)
        out["keywords"] = keywords[:24]
        return out

    @classmethod
    def main_interests(cls, profile: dict[str, Any], top_n: int = 3) -> list[str]:
        scored = [
            (_FIELD_TO_LABEL[f], float(profile.get(f) or 0.0))
            for f in _INTEREST_FIELDS
            if float(profile.get(f) or 0.0) > 0
        ]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [name for name, _ in scored[:top_n]]

    @classmethod
    def sanitize_question(cls, question: str) -> str:
        """Strip obvious PII patterns; keep topic intent only."""
        text = question or ""
        text = re.sub(r"1[3-9]\d{9}", "[手机号]", text)
        text = re.sub(r"\b[\w.+-]+@[\w.-]+\.\w+\b", "[邮箱]", text)
        text = re.sub(r"\d{15,18}[Xx]?", "[证件号]", text)
        text = re.sub(r"(身份证|护照|银行卡|账号)[:：\s]*\S+", r"\1[已脱敏]", text)
        return text.strip()[:500]
