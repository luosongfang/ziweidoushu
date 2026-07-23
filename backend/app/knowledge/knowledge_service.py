"""KnowledgeService — 根据命盘结果组装 Knowledge Core 上下文。"""

from __future__ import annotations

from typing import Any

from app.knowledge.knowledge_loader import KnowledgeLoader


class KnowledgeService:
    """根据命盘 JSON / 宫位星曜，调用星曜、宫位、组合、人生模型知识。"""

    @classmethod
    def detect_question_type(cls, question: str) -> str:
        from app.knowledge.reasoning.question_classifier import QuestionClassifier

        return QuestionClassifier.classify(question)

    @classmethod
    def extract_stars_from_chart(cls, chart_data: dict[str, Any] | str) -> list[str]:
        if isinstance(chart_data, str):
            # naive: split common separators
            stars: list[str] = []
            for token in ["紫微", "天府", "天机", "太阳", "武曲", "七杀", "破军", "天相", "太阴", "贪狼"]:
                if token in chart_data:
                    stars.append(token)
            return stars

        names: list[str] = []
        # {命宫:{stars:[...]}}
        for key, val in chart_data.items():
            if isinstance(val, dict) and "stars" in val:
                for s in val.get("stars") or []:
                    names.append(s if isinstance(s, str) else str(s.get("name", "")))
        inner = chart_data.get("chart") if isinstance(chart_data.get("chart"), dict) else None
        if inner and isinstance(inner.get("palaces"), list):
            for p in inner["palaces"]:
                for s in p.get("stars") or []:
                    names.append(s if isinstance(s, str) else str(s.get("name", "")))
        return [n for n in dict.fromkeys(names) if n]

    @classmethod
    def match_patterns(cls, star_names: list[str]) -> list[dict[str, Any]]:
        star_set = set(star_names)
        matched: list[dict[str, Any]] = []
        for pattern in KnowledgeLoader.list_patterns():
            related = set(pattern.get("related_stars") or [])
            cond = pattern.get("conditions") or {}
            ok = False
            if related and related.issubset(star_set):
                ok = True
            ming_req = set(cond.get("ming_gong_contains") or [])
            if ming_req and ming_req.issubset(star_set):
                ok = True
            has_req = set(cond.get("has_stars") or [])
            if has_req and has_req.issubset(star_set):
                ok = True
            if ok:
                matched.append(pattern)
        return matched

    @classmethod
    def build_context(
        cls,
        chart_data: dict[str, Any] | str,
        question: str,
    ) -> dict[str, Any]:
        """组装 AI 可用的 Knowledge Core 上下文（禁止模型脱离此数据编造）。"""
        qtype = cls.detect_question_type(question)
        model = KnowledgeLoader.get_question_model(qtype) or {}
        required_palaces = list(model.get("required_palaces") or [])
        stars = cls.extract_stars_from_chart(chart_data)

        star_knowledge = []
        for name in stars:
            row = KnowledgeLoader.get_star(name)
            if row:
                star_knowledge.append(row)

        palace_knowledge = []
        for pname in required_palaces:
            row = KnowledgeLoader.get_palace(pname)
            if row:
                palace_knowledge.append(row)

        patterns = cls.match_patterns(stars)
        theory = KnowledgeLoader.list_theory()
        safety = KnowledgeLoader.list_safety_rules()

        return {
            "question_type": qtype,
            "question_model": model,
            "stars": star_knowledge,
            "palaces": palace_knowledge,
            "patterns": patterns,
            "theory": theory,
            "safety_rules": safety,
            "chart_stars": stars,
            "required_palaces": required_palaces,
        }
