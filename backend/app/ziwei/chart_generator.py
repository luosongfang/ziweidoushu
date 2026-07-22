"""命盘组装器 — Ziwei Engine 入口。"""

from __future__ import annotations

import uuid
from datetime import datetime

from app.models.birth import BirthLocation, ChartGenerateRequest
from app.models.chart import (
    BirthInfoOutput,
    ChartMetaOutput,
    ChartOutput,
    CombinationOutput,
    FeixingOutput,
    FortuneOutput,
    GanzhiInfo,
    LunarDetail,
    ShichenInfo,
    TraceOutput,
)
from app.models.palace import DaXianOutput, PalaceAnalysisTags, PalaceFourTransform, PalaceOutput
from app.models.star import StarOutput
from app.ziwei.constants import MING_ZHU_BY_BRANCH, SHEN_ZHU_BY_YEAR_BRANCH
from app.ziwei.engines.brightness_engine import BrightnessEngine
from app.ziwei.engines.bureau_engine import BureauEngine
from app.ziwei.engines.calendar_engine import CalendarEngine
from app.ziwei.engines.combination_engine import CombinationEngine
from app.ziwei.engines.fortune_engine import FortuneEngine
from app.ziwei.engines.four_transform_engine import FourTransformEngine
from app.ziwei.engines.palace_engine import PalaceEngine
from app.ziwei.engines.star_placement_engine import StarPlacementEngine
from app.ziwei.exceptions import UnsupportedCalendarError


class ChartGenerator:
    """Chart Generator — 编排全部引擎，输出 Chart JSON V1.0 Final。"""

    RULES_VERSION = "2026.07.22"
    SCHOOL = "sanhe"

    @staticmethod
    def _build_stars(
        star_data: list[dict],
        branch: str,
        star_sihua: dict[str, str],
    ) -> list[StarOutput]:
        stars: list[StarOutput] = []
        for item in star_data:
            name = item["name"]
            stars.append(StarOutput(
                name=name,
                brightness=BrightnessEngine.get_brightness(name, branch),
                sihua=star_sihua.get(name),
                isMain=item.get("isMain", False),
            ))
        return stars

    @staticmethod
    def _build_palace_transforms(
        palace_name: str,
        star_sihua: dict[str, str],
        star_to_palace: dict[str, str],
    ) -> PalaceFourTransform:
        incoming = [
            f"{star}{label}"
            for star, label in star_sihua.items()
            if star_to_palace.get(star) == palace_name
        ]
        return PalaceFourTransform(incoming=incoming)

    @classmethod
    def generate(
        cls,
        request: ChartGenerateRequest,
        reference_date: datetime | None = None,
    ) -> ChartOutput:
        if request.calendar_type != "solar":
            raise UnsupportedCalendarError("V1.0 Sprint 0–2 暂仅支持公历（solar）输入")

        dt: datetime = request.birth_datetime
        longitude = request.location.longitude if request.location else None
        timezone = request.timezone

        trace_steps: list[dict] = []

        # 1. Calendar Engine
        calendar = CalendarEngine.convert(dt, longitude=longitude, timezone=timezone)
        trace_steps.append({
            "engine": "calendar",
            "output": {
                "year_ganzhi": calendar.year_ganzhi,
                "used_true_solar": calendar.used_true_solar,
                "correction_minutes": calendar.correction_meta.get("total_correction_minutes"),
            },
        })

        # 2. Palace Engine
        ming_index, shen_index, palace_results = PalaceEngine.compute(
            calendar.lunar_month,
            calendar.shichen_index,
            year_stem=calendar.year_stem,
        )
        trace_steps.append({
            "engine": "palace",
            "output": {
                "mingGong": palace_results[0].branch,
                "shenGong": next(p.branch for p in palace_results if p.is_shen_gong),
                "mingGongGanZhi": palace_results[0].ganzhi,
            },
        })

        # 3. Bureau Engine
        bureau = BureauEngine.compute(calendar.year_stem, ming_index)
        trace_steps.append({
            "engine": "bureau",
            "output": {
                "wuxingJu": bureau.bureau_name,
                "nayin": bureau.nayin,
                "rulesVersion": bureau.rules_version,
            },
        })

        # 4. Star Placement Engine（Sprint 4：十四主星）
        star_placement = StarPlacementEngine.compute(
            palace_results,
            calendar.lunar_day,
            bureau.bureau_number,
            calendar.year_stem,
            calendar.year_branch,
            calendar.shichen_index,
            calendar.lunar_month,
        )
        trace_steps.append({
            "engine": "star_placement",
            "output": {
                "ziweiBranch": star_placement.ziwei_branch,
                "mainStarCount": sum(len(v) for v in star_placement.main_stars.values()),
                "auxStarCount": sum(len(v) for v in star_placement.aux_stars.values()),
                "shaStarCount": sum(len(v) for v in star_placement.sha_stars.values()),
            },
        })

        branch_to_palace = {p.branch: p.name for p in palace_results}
        star_to_palace = star_placement.star_to_palace(branch_to_palace)

        # 5. Four Transform Engine（Sprint 5）
        transform = FourTransformEngine.compute(calendar.year_stem, star_to_palace)
        trace_steps.append({
            "engine": "four_transform",
            "output": {
                "yearStem": calendar.year_stem,
                "lu": transform.summary.lu.star,
                "ji": transform.summary.ji.star,
            },
        })

        # 6. Fortune Engine
        daxian_map, direction = FortuneEngine.calc_daxian(
            palace_results, bureau.bureau_number, calendar.year_stem, request.gender
        )
        fortune_snapshot = FortuneEngine.build_snapshot(
            palace_results,
            daxian_map,
            dt,
            request.gender,
            calendar.year_stem,
            reference=reference_date,
        )
        trace_steps.append({
            "engine": "fortune",
            "output": {
                "daxianDirection": direction,
                "currentDaxian": fortune_snapshot.current_daxian,
            },
        })

        star_sihua = transform.star_sihua

        # 7. Combination Engine（Sprint 6）
        combinations = CombinationEngine.compute(
            palace_results, star_placement, star_sihua
        )
        trace_steps.append({
            "engine": "combination",
            "output": {
                "patternCount": len(combinations.patterns),
                "patterns": [p.name for p in combinations.patterns],
            },
        })

        # 组装宫位
        palaces: list[PalaceOutput] = []
        for pos in palace_results:
            dx = daxian_map[pos.name]
            palaces.append(
                PalaceOutput(
                    name=pos.name,
                    branch=pos.branch,
                    ganzhi=pos.ganzhi,
                    position=pos.position,
                    opposite=pos.opposite,
                    sanhe=pos.sanhe,
                    isMingGong=pos.is_ming_gong,
                    isShenGong=pos.is_shen_gong,
                    mainStars=cls._build_stars(
                        star_placement.main_stars.get(pos.name, []),
                        pos.branch,
                        star_sihua,
                    ),
                    auxStars=cls._build_stars(
                        star_placement.aux_stars.get(pos.name, []),
                        pos.branch,
                        star_sihua,
                    ),
                    shaStars=cls._build_stars(
                        star_placement.sha_stars.get(pos.name, []),
                        pos.branch,
                        star_sihua,
                    ),
                    zaStars=cls._build_stars(
                        star_placement.za_stars.get(pos.name, []),
                        pos.branch,
                        star_sihua,
                    ),
                    fourTransform=cls._build_palace_transforms(
                        pos.name, star_sihua, star_to_palace
                    ),
                    daxian=DaXianOutput(startAge=dx.start_age, endAge=dx.end_age),
                    analysis_tags=PalaceAnalysisTags(
                        tags=[t for t in (pos.keyword, pos.meaning) if t],
                    ),
                )
            )

        ming_branch = palace_results[0].branch
        shen_branch = next(p.branch for p in palace_results if p.is_shen_gong)

        location = request.location or BirthLocation()

        return ChartOutput(
            version="1.0-final",
            school=cls.SCHOOL,
            rulesVersion=cls.RULES_VERSION,
            meta=ChartMetaOutput(
                name=request.name,
                gender=request.gender,
                mingGong=ming_branch,
                shenGong=shen_branch,
                mingGongGanZhi=bureau.ming_gong_ganzhi,
                wuxingJu=bureau.bureau_name,
                bureauNumber=bureau.bureau_number,
                mingZhu=MING_ZHU_BY_BRANCH[ming_branch],
                shenZhu=SHEN_ZHU_BY_YEAR_BRANCH[calendar.year_branch],
                nayinElement=bureau.nayin_element,
            ),
            birth=BirthInfoOutput(
                solar=calendar.clock_datetime.isoformat(),
                trueSolarTime=calendar.true_solar_datetime.isoformat(),
                lunar=f"{calendar.lunar_year_cn}年{calendar.lunar_month_cn}{calendar.lunar_day_cn}",
                lunarDetail=LunarDetail(
                    year=calendar.lunar_year,
                    month=calendar.lunar_month,
                    day=calendar.lunar_day,
                    isLeap=calendar.is_leap_month,
                ),
                shichen=ShichenInfo(
                    name=calendar.shichen_name,
                    range=calendar.shichen_range,
                    branch=calendar.hour_branch,
                ),
                ganzhi=GanzhiInfo(
                    year=calendar.year_ganzhi,
                    month=calendar.month_ganzhi,
                    day=calendar.day_ganzhi,
                    hour=calendar.hour_ganzhi,
                ),
                location=location,
            ),
            palaces=palaces,
            fourTransformSummary=transform.summary,
            combinations=combinations,
            fortune=FortuneOutput(
                daxianDirection=direction,
                currentDaxian=fortune_snapshot.current_daxian,
                annualFortune=fortune_snapshot.annual_fortune,
                monthlyFortune=fortune_snapshot.monthly_fortune,
            ),
            feixing=FeixingOutput(enabled=False),
            trace=TraceOutput(
                traceId=str(uuid.uuid4()),
                steps=trace_steps,
                rulesVersion=cls.RULES_VERSION,
            ),
        )


# 向后兼容
ChartEngine = ChartGenerator
