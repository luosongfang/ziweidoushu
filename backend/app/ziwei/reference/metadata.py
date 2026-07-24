"""Professional Reference metadata & schema helpers — V1.6."""

from __future__ import annotations

from typing import Any, Literal

VerificationLevel = Literal["pending", "verified_manual", "verified_professional"]
SourceType = Literal["wenmo", "manual", "other"]

REQUIRED_BIRTH = ("date", "time")
REQUIRED_CHART_REF = ("ming_gong", "shen_gong", "wuxing", "ziwei", "tianfu", "palaces")

PALACE_NAMES = (
    "命宫", "兄弟", "夫妻", "子女", "财帛", "疾厄",
    "迁移", "交友", "官禄", "田宅", "福德", "父母",
)

MAIN_14 = (
    "紫微", "天机", "太阳", "武曲", "天同", "廉贞",
    "天府", "太阴", "贪狼", "巨门", "天相", "天梁", "七杀", "破军",
)


def empty_palaces() -> dict[str, dict[str, list]]:
    return {n: {"main_stars": [], "aux_stars": []} for n in PALACE_NAMES}


def sample_template(
    sample_id: str,
    *,
    gender: str = "male",
    date: str = "",
    time: str = "12:00",
    location: str | None = None,
) -> dict[str, Any]:
    return {
        "id": sample_id,
        "source": "wenmo",
        "verification_level": "pending",
        "birth": {
            "date": date,
            "time": time,
            "gender": gender,
            "location": location,
            "true_solar_time": True,
        },
        "settings": {
            "calendar": "solar",
            "school": "sanhe",
            "tianfu_rule": "traditional",
        },
        "chart_reference": {
            "ming_gong": "",
            "shen_gong": "",
            "wuxing": "",
            "ziwei": "",
            "tianfu": "",
            "palaces": empty_palaces(),
        },
        "notes": "pending wenmo screenshot — 禁止入测宣称",
    }
