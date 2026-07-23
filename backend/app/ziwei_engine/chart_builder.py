"""命盘组装器 — Phase 2 核心入口。"""

from __future__ import annotations

from datetime import datetime

from app.ziwei.constants import EARTHLY_BRANCHES, MING_ZHU_BY_BRANCH, SHEN_ZHU_BY_YEAR_BRANCH
from app.ziwei.engines.auxiliary_star_engine import AuxiliaryStarEngine
from app.ziwei.engines.calendar_engine import CalendarEngine
from app.ziwei.engines.fortune_engine import FortuneEngine
from app.ziwei.engines.palace_engine import PalaceEngine
from app.ziwei.engines.star_placement_engine import StarPlacementEngine, StarPlacementResult
from app.ziwei.fortune.xiaoxian import XiaoxianCalculator
from app.ziwei.rules.loader import RulesLoader
from app.ziwei.transformation.daxian_hua import DaxianTransformCalculator
from app.ziwei.transformation.liunian_hua import LiunianTransformCalculator
from app.ziwei_engine.calendar.ganzhi import GanzhiCalculator
from app.ziwei_engine.calendar.lunar_converter import LunarConverter
from app.ziwei_engine.fortune.da_xian import DaXianCalculator
from app.ziwei_engine.fortune.liu_nian import LiuNianCalculator
from app.ziwei_engine.palace.five_element import FiveElementCalculator
from app.ziwei_engine.palace.ming_gong import MingGongCalculator
from app.ziwei_engine.palace.shen_gong import ShenGongCalculator
from app.ziwei_engine.palace.twelve_palace import Palace, TwelvePalaceBuilder
from app.ziwei_engine.stars.fourteen_stars import FourteenStarsCalculator
from app.ziwei_engine.stars.tianfu import TianfuStarCalculator
from app.ziwei_engine.stars.ziwei import ZiweiStarCalculator
from app.ziwei_engine.transformation.four_hua import FourHuaCalculator


class ChartBuilder:
    """
    紫微斗数命盘组装器 V1.2。

    编排：历法 → 干支 → 十二宫 → 五行局 → 主星/辅煞 → 杂曜 → 四化 → 运限。
    算法源：app.ziwei 引擎 + RulesLoader（DB 规则驱动）。
    """

    @classmethod
    def build(
        cls,
        name: str,
        gender: str,
        solar_date: str,
        time: str,
        location: str | None = None,
        reference_year: int | None = None,
    ) -> dict:
        longitude = LunarConverter.parse_location(location)
        lunar, true_dt = LunarConverter.convert(solar_date, time, location)
        ganzhi = GanzhiCalculator.calculate(true_dt, longitude=longitude)

        cal = CalendarEngine.convert(true_dt, longitude=longitude)
        ming_idx, shen_idx, palace_results = PalaceEngine.compute(
            cal.lunar_month, cal.shichen_index, year_stem=cal.year_stem
        )

        ming_branch = MingGongCalculator.calculate(cal.lunar_month, cal.shichen_index)
        shen_branch = ShenGongCalculator.calculate(cal.lunar_month, cal.shichen_index)
        five_element = FiveElementCalculator.calculate(cal.year_stem, ming_idx)

        branch_to_palace = {p.branch: p.name for p in palace_results}
        ziwei = ZiweiStarCalculator.calculate(
            cal.lunar_day, five_element.bureau_number, branch_to_palace
        )
        tianfu = TianfuStarCalculator.calculate(ziwei.branch, branch_to_palace)

        placement = StarPlacementEngine.compute(
            palace_results,
            cal.lunar_day,
            five_element.bureau_number,
            cal.year_stem,
            cal.year_branch,
            cal.shichen_index,
            cal.lunar_month,
        )
        star_to_palace = placement.star_to_palace(branch_to_palace)

        main_stars = cls._main_stars_from_placement(placement, branch_to_palace)
        lucky = cls._lucky_stars_from_placement(placement)
        evil = cls._evil_stars_from_placement(placement)

        auxiliary = AuxiliaryStarEngine.compute(
            palace_results, cal.lunar_month, cal.year_branch
        )

        four_hua = FourHuaCalculator.calculate(cal.year_stem, star_to_palace)
        daxian_ranges, daxian_direction = DaXianCalculator.calculate(
            palace_results, five_element.bureau_number, cal.year_stem, gender
        )
        ref_year = reference_year or datetime.now().year
        ref_dt = datetime(ref_year, true_dt.month, true_dt.day, true_dt.hour, true_dt.minute)
        liu_nian = LiuNianCalculator.calculate(palace_results, ref_year)

        daxian_map, _ = FortuneEngine.calc_daxian(
            palace_results, five_element.bureau_number, cal.year_stem, gender
        )
        virtual_age = FortuneEngine._calc_age(true_dt, ref_dt)  # noqa: SLF001

        xiaoxian = XiaoxianCalculator.compute(
            palace_results, gender, cal.year_stem, true_dt, reference=ref_dt
        )
        daxian_transform = DaxianTransformCalculator.compute(
            palace_results, daxian_map, star_to_palace, gender, cal.year_stem, virtual_age
        )
        annual_transform = LiunianTransformCalculator.compute(ref_year, star_to_palace)

        _, _, palaces = TwelvePalaceBuilder.build(
            cal.lunar_month, cal.shichen_index, cal.year_stem
        )
        cls._attach_stars_to_palaces(palaces, placement, four_hua, daxian_ranges)

        trace_steps = [
            {"engine": "calendar", "output": {"yearGanzhi": cal.year_ganzhi}},
            {"engine": "palace", "output": {"mingGong": ming_branch, "shenGong": shen_branch}},
            {"engine": "star_placement", "output": {"mainStarCount": len(main_stars)}},
            {"engine": "auxiliary_star", "output": {"count": len(auxiliary)}},
            {"engine": "four_transform", "output": {"yearStem": cal.year_stem}},
            {"engine": "xiaoxian", "output": xiaoxian.trace},
            {"engine": "daxian_transform", "output": daxian_transform.trace if daxian_transform else {}},
            {"engine": "annual_transform", "output": annual_transform.trace},
        ]

        return {
            "name": name,
            "gender": gender,
            "birth": {
                "solar": true_dt.isoformat(),
                "lunar": lunar.lunar_text,
                "lunar_detail": {
                    "lunar_year": lunar.lunar_year,
                    "lunar_month": lunar.lunar_month,
                    "lunar_day": lunar.lunar_day,
                    "is_leap": lunar.is_leap,
                },
                "year_gan": ganzhi.year_gan,
                "year_zhi": ganzhi.year_zhi,
                "ganzhi": ganzhi.to_dict(),
                "shichen": cal.shichen_name,
            },
            "chart": {
                "ming_gong": ming_branch,
                "shen_gong": shen_branch,
                "five_element": five_element.bureau_name,
                "five_element_detail": five_element.to_dict(),
                "ming_zhu": MING_ZHU_BY_BRANCH.get(ming_branch, ""),
                "shen_zhu": SHEN_ZHU_BY_YEAR_BRANCH.get(cal.year_branch, ""),
                "ziwei": ziwei.to_dict(),
                "tianfu": tianfu.to_dict(),
                "main_stars": main_stars,
                "lucky_stars": lucky,
                "evil_stars": evil,
                "auxiliary_stars": AuxiliaryStarEngine.to_dict_list(auxiliary),
                "four_hua": four_hua.to_dict(),
                "daxian_direction": daxian_direction,
                "daxian_ranges": [
                    {"palace": r.palace, "start_age": r.start_age, "end_age": r.end_age}
                    for r in daxian_ranges
                ],
                "liu_nian": {
                    "year": liu_nian.year,
                    "branch": liu_nian.branch,
                    "palace": liu_nian.palace,
                    "annual_transform": annual_transform.to_dict(),
                },
                "xiaoxian": xiaoxian.to_dict(),
                "daxian_transform": daxian_transform.to_dict() if daxian_transform else None,
                "palaces": [p.to_dict() for p in palaces],
            },
            "trace_steps": trace_steps,
            "engine_version": "1.2",
            "rules_version": RulesLoader.RULES_VERSION,
        }

    @staticmethod
    def _main_stars_from_placement(
        placement: StarPlacementResult,
        branch_to_palace: dict[str, str],
    ) -> list[dict]:
        stars: list[dict] = []
        for name in FourteenStarsCalculator.MAIN_STAR_NAMES:
            branch = placement.star_branches.get(name)
            if branch:
                stars.append({
                    "name": name,
                    "branch": branch,
                    "palace": branch_to_palace.get(branch, ""),
                })
        return stars

    @staticmethod
    def _lucky_stars_from_placement(placement: StarPlacementResult) -> list[dict]:
        result: list[dict] = []
        for palace_name, star_list in placement.aux_stars.items():
            for star in star_list:
                result.append({"name": star["name"], "palace": palace_name})
        return result

    @staticmethod
    def _evil_stars_from_placement(placement: StarPlacementResult) -> list[dict]:
        result: list[dict] = []
        for palace_name, star_list in placement.sha_stars.items():
            for star in star_list:
                result.append({"name": star["name"], "palace": palace_name})
        return result

    @staticmethod
    def _attach_stars_to_palaces(
        palaces: list[Palace],
        placement: StarPlacementResult,
        four_hua,
        daxian_ranges: list,
    ) -> None:
        """将星曜与四化写入各宫。"""
        daxian_map = {r.palace: r for r in daxian_ranges}
        sihua_map = {
            four_hua.hua_lu["star"]: "禄",
            four_hua.hua_quan["star"]: "权",
            four_hua.hua_ke["star"]: "科",
            four_hua.hua_ji["star"]: "忌",
        }

        for palace in palaces:
            pname = palace.name
            stars: list[dict] = []

            for star_list, category in (
                (placement.main_stars.get(pname, []), "main"),
                (placement.aux_stars.get(pname, []), "aux"),
                (placement.sha_stars.get(pname, []), "sha"),
                (placement.za_stars.get(pname, []), "za"),
            ):
                for s in star_list:
                    entry = {"name": s["name"], "category": category}
                    if s["name"] in sihua_map:
                        entry["sihua"] = sihua_map[s["name"]]
                        palace.transformations.append({
                            "star": s["name"],
                            "type": sihua_map[s["name"]],
                        })
                    stars.append(entry)

            palace.stars = stars
            dx = daxian_map.get(pname)
            if dx:
                palace.stars.append({
                    "name": f"大限{dx.start_age}-{dx.end_age}",
                    "category": "daxian",
                })
