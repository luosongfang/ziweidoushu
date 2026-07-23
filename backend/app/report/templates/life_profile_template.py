"""人生档案报告固定结构模板 — V1.3。"""

from __future__ import annotations

from typing import Any


def empty_life_profile() -> dict[str, Any]:
    return {
        "identity": {
            "chart_summary": "",
            "traditional_basis": "",
            "modern_interpretation": "",
        },
        "personality": {
            "strengths": [],
            "challenges": [],
            "growth_direction": [],
        },
        "career": {
            "traditional_view": "",
            "advantages": [],
            "development_advice": [],
        },
        "wealth": {
            "resource_pattern": "",
            "risk_awareness": "",
            "growth_advice": "",
        },
        "relationship": {
            "interaction_style": "",
            "growth_advice": "",
        },
        "life_cycle": {
            "current_stage": "",
            "focus": "",
            "advice": "",
        },
        "advisor_message": "",
    }


REPORT_SECTIONS = [
    ("identity", "自我认知"),
    ("personality", "性格优势"),
    ("career", "事业方向"),
    ("wealth", "财富规划"),
    ("relationship", "关系成长"),
    ("life_cycle", "人生阶段"),
]
