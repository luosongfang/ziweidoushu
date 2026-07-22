"""亮度引擎 — Sprint 5。"""

from __future__ import annotations

from app.ziwei.rules.loader import RulesLoader


class BrightnessEngine:
    """Brightness Engine — 读 brightness_rules 表。"""

    @staticmethod
    def get_brightness(star_name: str, branch: str, school: str = RulesLoader.SCHOOL) -> str:
        return RulesLoader.get_brightness(star_name, branch, school=school)
