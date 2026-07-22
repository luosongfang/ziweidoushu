"""宫位引擎：命宫、身宫、十二宫、对宫、三合。"""

from __future__ import annotations

from dataclasses import dataclass, field, replace

from app.ziwei.constants import EARTHLY_BRANCHES, PALACE_NAMES, YIN_BRANCH_INDEX
from app.ziwei.engines.calendar_engine import stem_branch_at_palace
from app.ziwei.rules.loader import RulesLoader

# 对宫映射
OPPOSITE_PALACE: dict[str, str] = {
    "命宫": "迁移", "迁移": "命宫",
    "兄弟": "交友", "交友": "兄弟",
    "夫妻": "官禄", "官禄": "夫妻",
    "子女": "田宅", "田宅": "子女",
    "财帛": "福德", "福德": "财帛",
    "疾厄": "父母", "父母": "疾厄",
}

# 地支三合组
BRANCH_SANHE: dict[str, tuple[str, str, str]] = {
    "申": ("申", "子", "辰"),
    "子": ("申", "子", "辰"),
    "辰": ("申", "子", "辰"),
    "寅": ("寅", "午", "戌"),
    "午": ("寅", "午", "戌"),
    "戌": ("寅", "午", "戌"),
    "巳": ("巳", "酉", "丑"),
    "酉": ("巳", "酉", "丑"),
    "丑": ("巳", "酉", "丑"),
    "亥": ("亥", "卯", "未"),
    "卯": ("亥", "卯", "未"),
    "未": ("亥", "卯", "未"),
}


@dataclass(frozen=True)
class PalaceResult:
    """单宫结果。"""

    name: str
    branch: str
    branch_index: int
    position: int
    opposite: str
    sanhe: list[str] = field(default_factory=list)
    is_ming_gong: bool = False
    is_shen_gong: bool = False
    ganzhi: str = ""
    keyword: str = ""
    meaning: str = ""


class PalaceEngine:
    """Palace Engine — 安宫、布十二宫、宫位干支与语义（Sprint 3）。"""

    @staticmethod
    def attach_ganzhi(palaces: list[PalaceResult], year_stem: str) -> list[PalaceResult]:
        """五虎遁：为每宫附上干支。"""
        return [
            replace(p, ganzhi=stem_branch_at_palace(year_stem, p.branch_index))
            for p in palaces
        ]

    @staticmethod
    def attach_meanings(palaces: list[PalaceResult], school: str = RulesLoader.SCHOOL) -> list[PalaceResult]:
        """从 palace_meaning_rules 附加宫位语义。"""
        enriched: list[PalaceResult] = []
        for p in palaces:
            rule = RulesLoader.get_palace_meaning(p.name, school=school)
            keyword = rule["keyword"] if rule else ""
            meaning = rule["meaning"] if rule else ""
            enriched.append(replace(p, keyword=keyword, meaning=meaning))
        return enriched

    @classmethod
    def enrich(cls, palaces: list[PalaceResult], year_stem: str) -> list[PalaceResult]:
        return cls.attach_meanings(cls.attach_ganzhi(palaces, year_stem))

    @staticmethod
    def calc_month_palace_branch(lunar_month: int) -> int:
        return (YIN_BRANCH_INDEX + lunar_month - 1) % 12

    @staticmethod
    def calc_ming_gong_branch(lunar_month: int, hour_branch_index: int) -> int:
        month_branch = PalaceEngine.calc_month_palace_branch(lunar_month)
        return (month_branch - hour_branch_index + 12) % 12

    @staticmethod
    def calc_shen_gong_branch(lunar_month: int, hour_branch_index: int) -> int:
        month_branch = PalaceEngine.calc_month_palace_branch(lunar_month)
        return (month_branch + hour_branch_index) % 12

    @staticmethod
    def _sanhe_palace_names(branch: str, branch_to_palace: dict[str, str]) -> list[str]:
        group = BRANCH_SANHE[branch]
        names = [branch_to_palace[b] for b in group if b in branch_to_palace]
        return [n for n in names if branch_to_palace.get(branch) != n or len(names) <= 1][:2]

    @classmethod
    def build_twelve_palaces(
        cls,
        ming_gong_index: int,
        shen_gong_index: int,
    ) -> list[PalaceResult]:
        palaces: list[PalaceResult] = []
        branch_to_palace: dict[str, str] = {}

        for i, name in enumerate(PALACE_NAMES):
            branch_index = (ming_gong_index - i + 12) % 12
            branch = EARTHLY_BRANCHES[branch_index]
            branch_to_palace[branch] = name

        for i, name in enumerate(PALACE_NAMES):
            branch_index = (ming_gong_index - i + 12) % 12
            branch = EARTHLY_BRANCHES[branch_index]
            sanhe = cls._sanhe_palace_names(branch, branch_to_palace)
            palaces.append(
                PalaceResult(
                    name=name,
                    branch=branch,
                    branch_index=branch_index,
                    position=i + 1,
                    opposite=OPPOSITE_PALACE[name],
                    sanhe=sanhe,
                    is_ming_gong=(branch_index == ming_gong_index),
                    is_shen_gong=(branch_index == shen_gong_index),
                )
            )
        return palaces

    @classmethod
    def compute(
        cls,
        lunar_month: int,
        hour_branch_index: int,
        year_stem: str | None = None,
    ) -> tuple[int, int, list[PalaceResult]]:
        ming = cls.calc_ming_gong_branch(lunar_month, hour_branch_index)
        shen = cls.calc_shen_gong_branch(lunar_month, hour_branch_index)
        palaces = cls.build_twelve_palaces(ming, shen)
        if year_stem:
            palaces = cls.enrich(palaces, year_stem)
        return ming, shen, palaces


# 向后兼容
PalacePosition = PalaceResult
calc_month_palace_branch = PalaceEngine.calc_month_palace_branch
calc_ming_gong_branch = PalaceEngine.calc_ming_gong_branch
calc_shen_gong_branch = PalaceEngine.calc_shen_gong_branch
build_twelve_palaces = PalaceEngine.build_twelve_palaces
