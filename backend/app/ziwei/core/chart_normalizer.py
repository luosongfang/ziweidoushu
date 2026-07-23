"""ChartBuilder 输出 → StandardChartSchema V2 转换器。"""

from __future__ import annotations

import uuid
from typing import Any

from app.ziwei.constants import PALACE_NAMES
from app.ziwei.core.chart_schema_v2 import (
    LU_CUN_STAR_NAME,
    LUCKY_STAR_NAMES,
    AuxiliaryStarSchemaV2,
    BirthSchemaV2,
    DaXianRangeV2,
    DaXianSchemaV2,
    FourTransformDetailV2,
    FourTransformSchemaV2,
    LiuNianSchemaV2,
    LunarDetailV2,
    MetaSchemaV2,
    PalaceSchemaV2,
    PalaceTransformV2,
    PeriodTransformSchemaV2,
    ShichenV2,
    StandardChartSchemaV2,
    StarSchemaV2,
    StarsSchemaV2,
    TraceSchemaV2,
    XiaoxianCycleV2,
    XiaoxianSchemaV2,
)
from app.ziwei.core.chart_validator import ChartValidator
from app.ziwei.engines.brightness_engine import BrightnessEngine
from app.ziwei.engines.palace_engine import OPPOSITE_PALACE, PalaceEngine


class ChartNormalizer:
    """将 ChartBuilder 原始 dict 规范化为 StandardChartSchema V2。"""

    _CATEGORY_TO_BUCKET = {
        "main": "main_stars",
        "aux": "lucky_stars",
        "sha": "sha_stars",
        "za": "za_stars",
    }

    @classmethod
    def normalize(cls, raw: dict[str, Any]) -> StandardChartSchemaV2:
        chart = raw.get("chart", {})
        birth_raw = raw.get("birth", {})
        branch_to_palace = {
            p.get("branch", ""): p.get("name", "")
            for p in chart.get("palaces", [])
            if p.get("branch")
        }

        meta = cls._build_meta(raw, chart)
        palaces = cls._build_palaces(chart, branch_to_palace)
        auxiliary = cls._build_auxiliary(chart.get("auxiliary_stars", []))
        cls._attach_auxiliary_to_palaces(palaces, auxiliary)
        stars = cls._build_stars_index(palaces, auxiliary)
        four_transform = cls._build_four_transform(chart.get("four_hua", {}))
        daxian = cls._build_daxian(chart)
        liunian = cls._build_liunian(chart.get("liu_nian", {}))
        daxian_transform = cls._build_period_transform(chart.get("daxian_transform"))
        xiaoxian = cls._build_xiaoxian(chart.get("xiaoxian", {}))
        sanhe = {p.name: list(p.sanhe) for p in palaces}
        opposite = {p.name: p.opposite for p in palaces if p.opposite}
        brightness = cls._build_brightness_map(stars.main)
        trace_steps = raw.get("trace_steps") or [{
            "engine": "chart_builder",
            "output": {
                "rulesVersion": raw.get("rules_version", ""),
                "engineVersion": raw.get("engine_version", "1.2"),
            },
        }]

        result = StandardChartSchemaV2(
            schema_version="2.5",
            name=raw.get("name", ""),
            gender=raw.get("gender", "male"),
            birth=cls._build_birth(birth_raw),
            meta=meta,
            palaces=palaces,
            stars=stars,
            four_transform=four_transform,
            daxian_transform=daxian_transform,
            brightness=brightness,
            sanhe=sanhe,
            opposite=opposite,
            daxian=daxian,
            liunian=liunian,
            xiaoxian=xiaoxian,
            trace=TraceSchemaV2(
                traceId=str(uuid.uuid4()),
                steps=trace_steps,
                rulesVersion=raw.get("rules_version", "2026.07.23"),
                source="chart_builder",
            ),
            engine_version=raw.get("engine_version", "1.2"),
            rules_version=raw.get("rules_version", "2026.07.23"),
        )
        result.warnings = ChartValidator.validate(result)
        return result

    @classmethod
    def _build_birth(cls, birth: dict[str, Any]) -> BirthSchemaV2:
        lunar_detail = birth.get("lunar_detail", {})
        ganzhi = birth.get("ganzhi", {})
        shichen_raw = birth.get("shichen", "")
        shichen = (
            ShichenV2(name=shichen_raw, branch=ganzhi.get("hour_zhi", ""))
            if isinstance(shichen_raw, str)
            else ShichenV2(**shichen_raw)
        )
        return BirthSchemaV2(
            solar=birth.get("solar", ""),
            lunar=birth.get("lunar", ""),
            lunar_detail=LunarDetailV2(
                lunar_year=lunar_detail.get("lunar_year", 0),
                lunar_month=lunar_detail.get("lunar_month", 0),
                lunar_day=lunar_detail.get("lunar_day", 0),
                is_leap=lunar_detail.get("is_leap", False),
            ),
            year_gan=birth.get("year_gan", ganzhi.get("year_gan", "")),
            year_zhi=birth.get("year_zhi", ganzhi.get("year_zhi", "")),
            ganzhi=ganzhi,
            shichen=shichen,
        )

    @classmethod
    def _build_meta(cls, raw: dict[str, Any], chart: dict[str, Any]) -> MetaSchemaV2:
        detail = chart.get("five_element_detail", {})
        ziwei = chart.get("ziwei", {})
        tianfu = chart.get("tianfu", {})
        return MetaSchemaV2(
            name=raw.get("name", ""),
            gender=raw.get("gender", "male"),
            mingGong=chart.get("ming_gong", ""),
            shenGong=chart.get("shen_gong", ""),
            mingGongGanZhi=detail.get("ming_gong_ganzhi", ""),
            wuxingJu=chart.get("five_element", ""),
            bureauNumber=detail.get("bureau_number", 0),
            mingZhu=chart.get("ming_zhu", ""),
            shenZhu=chart.get("shen_zhu", ""),
            nayinElement=detail.get("element", ""),
            ziweiBranch=ziwei.get("branch", ""),
            tianfuBranch=tianfu.get("branch", ""),
        )

    @classmethod
    def _resolve_star_type(cls, name: str, category: str) -> str:
        if category == "main":
            return "main"
        if name == LU_CUN_STAR_NAME:
            return "lu_cun"
        if name in LUCKY_STAR_NAMES:
            return "lucky"
        if category == "sha":
            return "sha"
        if category == "za":
            return "za"
        return category

    @classmethod
    def _resolve_star_category(cls, name: str, category: str) -> str:
        star_type = cls._resolve_star_type(name, category)
        if star_type == "lu_cun":
            return "lucky"
        if star_type in {"main", "lucky", "sha", "za"}:
            return star_type
        if category == "aux":
            return "lucky"
        return category

    @classmethod
    def _make_star(
        cls,
        name: str,
        palace_name: str,
        branch: str,
        category: str,
        sihua: str | None = None,
    ) -> StarSchemaV2:
        resolved_category = cls._resolve_star_category(name, category)
        star_type = cls._resolve_star_type(name, category)
        brightness = BrightnessEngine.get_brightness(name, branch) if resolved_category == "main" else ""
        return StarSchemaV2(
            name=name,
            palace=palace_name,
            branch=branch,
            category=resolved_category,  # type: ignore[arg-type]
            type=star_type,  # type: ignore[arg-type]
            brightness=brightness,
            sihua=sihua,  # type: ignore[arg-type]
            isMain=resolved_category == "main",
            source="star_placement_rules" if resolved_category == "main" else "star_placement_rules",
        )

    @classmethod
    def _build_palaces(
        cls,
        chart: dict[str, Any],
        branch_to_palace: dict[str, str],
    ) -> list[PalaceSchemaV2]:
        daxian_map = {
            r.get("palace", ""): r for r in chart.get("daxian_ranges", [])
        }
        chart_level_aux = {
            (s.get("name", ""), s.get("palace", ""))
            for s in chart.get("lucky_stars", [])
        }
        chart_level_sha = {
            (s.get("name", ""), s.get("palace", ""))
            for s in chart.get("evil_stars", [])
        }

        palaces: list[PalaceSchemaV2] = []
        for raw_palace in chart.get("palaces", []):
            name = raw_palace.get("name", "")
            branch = raw_palace.get("branch", "")
            opposite = OPPOSITE_PALACE.get(name, "")
            sanhe = PalaceEngine._sanhe_palace_names(branch, branch_to_palace)  # noqa: SLF001

            buckets: dict[str, list[StarSchemaV2]] = {
                "main_stars": [],
                "lucky_stars": [],
                "sha_stars": [],
                "za_stars": [],
            }
            seen: set[tuple[str, str]] = set()

            for star in raw_palace.get("stars", []):
                star_name = star.get("name", "")
                if not star_name or star_name.startswith("大限"):
                    continue
                category = star.get("category", "main")
                key = (star_name, name)
                if key in seen:
                    continue
                seen.add(key)
                bucket_key = cls._CATEGORY_TO_BUCKET.get(category)
                if not bucket_key:
                    continue
                buckets[bucket_key].append(
                    cls._make_star(
                        star_name,
                        name,
                        branch,
                        category,
                        star.get("sihua"),
                    )
                )

            for star_name, palace_name in chart_level_aux:
                if palace_name != name:
                    continue
                key = (star_name, name)
                if key in seen:
                    continue
                seen.add(key)
                buckets["lucky_stars"].append(
                    cls._make_star(star_name, name, branch, "aux")
                )

            for star_name, palace_name in chart_level_sha:
                if palace_name != name:
                    continue
                key = (star_name, name)
                if key in seen:
                    continue
                seen.add(key)
                buckets["sha_stars"].append(
                    cls._make_star(star_name, name, branch, "sha")
                )

            dx_raw = daxian_map.get(name)
            daxian = (
                DaXianRangeV2(
                    palace=name,
                    startAge=dx_raw.get("start_age", 0),
                    endAge=dx_raw.get("end_age", 0),
                )
                if dx_raw
                else None
            )

            transformations = [
                PalaceTransformV2(star=t.get("star", ""), type=t.get("type", "禄"))  # type: ignore[arg-type]
                for t in raw_palace.get("transformations", [])
                if t.get("star") and t.get("type")
            ]

            palaces.append(
                PalaceSchemaV2(
                    name=name,
                    branch=branch,
                    ganzhi=raw_palace.get("ganzhi", ""),
                    position=raw_palace.get("position", 0),
                    opposite=opposite,
                    sanhe=sanhe,
                    is_ming_gong=bool(raw_palace.get("is_ming_gong")),
                    is_shen_gong=bool(raw_palace.get("is_shen_gong")),
                    main_stars=buckets["main_stars"],
                    lucky_stars=buckets["lucky_stars"],
                    sha_stars=buckets["sha_stars"],
                    za_stars=buckets["za_stars"],
                    transformations=transformations,
                    daxian=daxian,
                )
            )

        order = {name: idx for idx, name in enumerate(PALACE_NAMES)}
        palaces.sort(key=lambda p: order.get(p.name, 99))
        return palaces

    @classmethod
    def _build_auxiliary(cls, items: list[dict]) -> list[AuxiliaryStarSchemaV2]:
        return [
            AuxiliaryStarSchemaV2(
                name=item.get("name", ""),
                palace=item.get("palace", ""),
                branch=item.get("branch", ""),
                category=item.get("category", "auxiliary"),
                source=item.get("source", "auxiliary_star_rules"),
                trace=item.get("trace", {}),
            )
            for item in items
            if item.get("name")
        ]

    @staticmethod
    def _attach_auxiliary_to_palaces(
        palaces: list[PalaceSchemaV2],
        auxiliary: list[AuxiliaryStarSchemaV2],
    ) -> None:
        by_palace: dict[str, list[AuxiliaryStarSchemaV2]] = {}
        for star in auxiliary:
            by_palace.setdefault(star.palace, []).append(star)
        for palace in palaces:
            palace.auxiliary_stars = by_palace.get(palace.name, [])

    @classmethod
    def _build_stars_index(
        cls,
        palaces: list[PalaceSchemaV2],
        auxiliary: list[AuxiliaryStarSchemaV2],
    ) -> StarsSchemaV2:
        main: list[StarSchemaV2] = []
        lucky: list[StarSchemaV2] = []
        lu_cun: list[StarSchemaV2] = []
        sha: list[StarSchemaV2] = []
        za: list[StarSchemaV2] = []
        all_stars: list[StarSchemaV2] = []

        for palace in palaces:
            for star in palace.main_stars:
                main.append(star)
                all_stars.append(star)
            for star in palace.lucky_stars:
                if star.type == "lu_cun":
                    lu_cun.append(star)
                else:
                    lucky.append(star)
                all_stars.append(star)
            for star in palace.sha_stars:
                sha.append(star)
                all_stars.append(star)
            for star in palace.za_stars:
                za.append(star)
                all_stars.append(star)

        return StarsSchemaV2(
            main=main, lucky=lucky, lu_cun=lu_cun, sha=sha, za=za,
            auxiliary=auxiliary, all=all_stars,
        )

    @classmethod
    def _build_four_transform(cls, four_hua: dict[str, Any]) -> FourTransformSchemaV2:
        def detail(key: str, fallback_type: str) -> FourTransformDetailV2:
            item = four_hua.get(key, {})
            return FourTransformDetailV2(
                star=item.get("star", ""),
                palace=item.get("palace", ""),
                type=item.get("type", fallback_type),  # type: ignore[arg-type]
            )

        return FourTransformSchemaV2(
            yearStem=four_hua.get("year_gan", ""),
            lu=detail("hua_lu", "禄"),
            quan=detail("hua_quan", "权"),
            ke=detail("hua_ke", "科"),
            ji=detail("hua_ji", "忌"),
        )

    @classmethod
    def _build_daxian(cls, chart: dict[str, Any]) -> DaXianSchemaV2:
        direction = chart.get("daxian_direction", "forward")
        if direction not in ("forward", "backward"):
            direction = "forward"
        ranges = [
            DaXianRangeV2(
                palace=r.get("palace", ""),
                startAge=r.get("start_age", 0),
                endAge=r.get("end_age", 0),
            )
            for r in chart.get("daxian_ranges", [])
        ]
        return DaXianSchemaV2(direction=direction, ranges=ranges)

    @classmethod
    def _build_period_transform(cls, raw: dict | None) -> PeriodTransformSchemaV2 | None:
        if not raw:
            return None

        def detail(key: str, fallback: str) -> FourTransformDetailV2:
            item = raw.get(key, {}) or {}
            return FourTransformDetailV2(
                star=item.get("star", ""),
                palace=item.get("palace", ""),
                type=item.get("type", fallback),  # type: ignore[arg-type]
            )

        return PeriodTransformSchemaV2(
            period=raw.get("period", ""),
            stem=raw.get("stem", ""),
            palace=raw.get("palace", ""),
            year=raw.get("year", 0),
            branch=raw.get("branch", ""),
            lu=detail("lu", "禄"),
            quan=detail("quan", "权"),
            ke=detail("ke", "科"),
            ji=detail("ji", "忌"),
            source=raw.get("source", "four_transform_rules"),
            trace=raw.get("trace", {}),
        )

    @classmethod
    def _build_xiaoxian(cls, raw: dict[str, Any]) -> XiaoxianSchemaV2:
        if not raw:
            return XiaoxianSchemaV2(enabled=False)
        cycle = [
            XiaoxianCycleV2(
                age=item.get("age", 0),
                palace=item.get("palace", ""),
                branch=item.get("branch", ""),
            )
            for item in raw.get("yearly_cycle", [])
        ]
        return XiaoxianSchemaV2(
            enabled=raw.get("enabled", True),
            current_age=raw.get("current_age", 0),
            current_palace=raw.get("current_palace", ""),
            current_branch=raw.get("current_branch", ""),
            direction=raw.get("direction", "forward"),
            yearly_cycle=cycle,
            ranges=cycle,
            trace=raw.get("trace", {}),
        )

    @classmethod
    def _build_liunian(cls, liu_nian: dict[str, Any]) -> LiuNianSchemaV2:
        annual = cls._build_period_transform(liu_nian.get("annual_transform"))
        return LiuNianSchemaV2(
            year=liu_nian.get("year", 0),
            branch=liu_nian.get("branch", ""),
            palace=liu_nian.get("palace", ""),
            annual_transform=annual,
        )

    @classmethod
    def _build_brightness_map(cls, main_stars: list[StarSchemaV2]) -> dict[str, str]:
        return {star.name: star.brightness for star in main_stars if star.brightness}
