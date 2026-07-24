"""ProfessionalNormalizer — ChartBuilder raw → ProfessionalChartSchema V3。"""

from __future__ import annotations

import uuid
from typing import Any

from app.ziwei.constants import YANG_STEMS
from app.ziwei.core.chart_normalizer import ChartNormalizer
from app.ziwei.core.chart_quality_validator import ChartQualityValidator
from app.ziwei.core.professional_chart_schema import (
    MAIN_STAR_NAMES_V3,
    OTHER_STAR_NAMES,
    SIX_LUCKY_NAMES,
    SIX_SHA_NAMES,
    BaziV3,
    BirthV3,
    CombinationV3,
    FortunePeriodV3,
    FortuneV3,
    FourTransformV3,
    MetaV3,
    PalaceV3,
    ProfessionalChartSchemaV3,
    SiHuaBlockV3,
    StarPlacementV3,
    StarsIndexV3,
    TraceV3,
)
from app.ziwei.engines.brightness_engine import BrightnessEngine


class ProfessionalNormalizer:
    """将 ChartBuilder 原始 dict 规范化为 ProfessionalChartSchema V3。"""

    @classmethod
    def normalize(cls, raw: dict[str, Any], *, include_legacy_v2: bool = True) -> ProfessionalChartSchemaV3:
        chart = raw.get("chart") or {}
        birth_raw = raw.get("birth") or {}
        ganzhi = birth_raw.get("ganzhi") or {}

        year_gz = f"{ganzhi.get('year_gan', birth_raw.get('year_gan', ''))}{ganzhi.get('year_zhi', birth_raw.get('year_zhi', ''))}"
        month_gz = f"{ganzhi.get('month_gan', '')}{ganzhi.get('month_zhi', '')}"
        day_gz = f"{ganzhi.get('day_gan', '')}{ganzhi.get('day_zhi', '')}"
        hour_gz = f"{ganzhi.get('hour_gan', '')}{ganzhi.get('hour_zhi', '')}"

        year_stem = birth_raw.get("year_gan") or ganzhi.get("year_gan", "")
        yin_yang = "yang" if year_stem in YANG_STEMS else "yin"

        birth = BirthV3(
            solar_date=birth_raw.get("solar", ""),
            lunar_date=birth_raw.get("lunar", ""),
            lunar_detail=birth_raw.get("lunar_detail") or {},
            ganzhi_year=year_gz,
            ganzhi_month=month_gz,
            ganzhi_day=day_gz,
            ganzhi_hour=hour_gz,
            true_solar_time=birth_raw.get("true_solar_time"),
            shichen=birth_raw.get("shichen", ""),
        )
        bazi = BaziV3(year=year_gz, month=month_gz, day=day_gz, hour=hour_gz)

        detail = chart.get("five_element_detail") or {}
        meta = MetaV3(
            name=raw.get("name", ""),
            gender=raw.get("gender", "male"),
            ming_gong=chart.get("ming_gong", ""),
            shen_gong=chart.get("shen_gong", ""),
            ming_zhu=chart.get("ming_zhu", ""),
            shen_zhu=chart.get("shen_zhu", ""),
            wuxing_ju=chart.get("five_element", ""),
            bureau_number=detail.get("bureau_number", 0),
            yin_yang=yin_yang,
            ming_gong_ganzhi=detail.get("ming_gong_ganzhi", ""),
            ziwei_branch=(chart.get("ziwei") or {}).get("branch", ""),
            tianfu_branch=(chart.get("tianfu") or {}).get("branch", ""),
        )

        ft_v2 = chart.get("four_transform_v2") or {}
        four_transform = cls._build_four_transform(ft_v2, chart)

        palaces = cls._build_palaces(chart, four_transform)
        stars = cls._build_stars_index(chart, palaces)
        brightness = {
            s.name: s.brightness for s in stars.main_stars if s.brightness
        }

        fortune = cls._build_fortune(chart)
        combinations = [
            CombinationV3(
                name=c.get("name", ""),
                palaces=c.get("palaces") or [],
                stars=c.get("stars") or [],
                source=c.get("source", "traditional"),
                match_type=c.get("match_type", ""),
            )
            for c in (chart.get("combinations") or [])
        ]

        sanhe = {p.palace_name: list(p.sanhe) for p in palaces}

        result = ProfessionalChartSchemaV3(
            schema_version="3.0",
            name=raw.get("name", ""),
            gender=raw.get("gender", "male"),
            birth=birth,
            bazi=bazi,
            meta=meta,
            palaces=palaces,
            stars=stars,
            four_transform=four_transform,
            fortune=fortune,
            brightness=brightness,
            star_combination=combinations,
            sanhe_structure=sanhe,
            feixing={
                "enabled": bool(four_transform.self_transform),
                "items": four_transform.self_transform,
            },
            trace=TraceV3(
                trace_id=str(uuid.uuid4()),
                steps=raw.get("trace_steps") or [],
                rules_version=raw.get("rules_version", ""),
                engine_version=raw.get("engine_version", "1.3"),
                source="chart_builder",
            ),
            engine_version=raw.get("engine_version", "1.3"),
            rules_version=raw.get("rules_version", ""),
            school="sanhe",
        )

        if include_legacy_v2:
            try:
                v2 = ChartNormalizer.normalize(raw)
                result.legacy_v2 = v2.model_dump()
            except Exception:
                result.legacy_v2 = None

        result.quality = ChartQualityValidator.validate(result)
        return result

    @classmethod
    def _sihua_block(cls, data: dict[str, Any] | None) -> SiHuaBlockV3:
        data = data or {}
        return SiHuaBlockV3(
            lu=data.get("lu", ""),
            quan=data.get("quan", ""),
            ke=data.get("ke", ""),
            ji=data.get("ji", ""),
            stem=data.get("stem", ""),
            source=data.get("source", ""),
            details=data.get("details") or data,
            trace=data.get("trace") or {},
        )

    @classmethod
    def _build_four_transform(cls, ft_v2: dict, chart: dict) -> FourTransformV3:
        if ft_v2:
            year = cls._sihua_block(ft_v2.get("year") or ft_v2.get("birth_transform"))
            dax = cls._sihua_block(ft_v2.get("daxian") or ft_v2.get("daxian_transform"))
            liu = cls._sihua_block(ft_v2.get("liunian") or ft_v2.get("liunian_transform"))
            self_items = ft_v2.get("self") or ft_v2.get("self_transform") or []
        else:
            # 回退生年四化旧字段
            fh = chart.get("four_hua") or {}
            year = SiHuaBlockV3(
                lu=(fh.get("hua_lu") or {}).get("star", ""),
                quan=(fh.get("hua_quan") or {}).get("star", ""),
                ke=(fh.get("hua_ke") or {}).get("star", ""),
                ji=(fh.get("hua_ji") or {}).get("star", ""),
                details=fh,
            )
            dax = cls._sihua_block(chart.get("daxian_transform"))
            liu = cls._sihua_block((chart.get("liu_nian") or {}).get("annual_transform"))
            self_items = []

        return FourTransformV3(
            birth_transform=year,
            daxian_transform=dax,
            liunian_transform=liu,
            self_transform=list(self_items),
            year=year,
            daxian=dax,
            liunian=liu,
            self=list(self_items),
        )

    @classmethod
    def _star_item(
        cls,
        name: str,
        palace: str,
        branch: str = "",
        category: str = "",
        sihua: str | None = None,
        rule_source: str = "",
        trace: dict | None = None,
    ) -> StarPlacementV3:
        brightness = ""
        if category == "main" or name in MAIN_STAR_NAMES_V3:
            brightness = BrightnessEngine.get_brightness(name, branch) if branch else ""
        return StarPlacementV3(
            name=name,
            palace=palace,
            branch=branch,
            brightness=brightness,
            sihua=sihua,
            category=category,
            rule_source=rule_source,
            trace=trace or {},
        )

    @classmethod
    def _build_palaces(cls, chart: dict, four_transform: FourTransformV3) -> list[PalaceV3]:
        sihua_map = {
            four_transform.birth_transform.lu: "禄",
            four_transform.birth_transform.quan: "权",
            four_transform.birth_transform.ke: "科",
            four_transform.birth_transform.ji: "忌",
        }
        sihua_map = {k: v for k, v in sihua_map.items() if k}

        minor_by_palace: dict[str, list[dict]] = {}
        for m in chart.get("minor_stars") or chart.get("auxiliary_stars") or []:
            minor_by_palace.setdefault(m.get("palace", ""), []).append(m)

        daxian_by_palace = {
            r["palace"]: r for r in (chart.get("daxian_ranges") or []) if r.get("palace")
        }
        liu = chart.get("liu_nian") or {}
        xiao = chart.get("xiaoxian") or {}
        xiao_current = xiao.get("current_palace", "")

        result: list[PalaceV3] = []
        for raw in chart.get("palaces") or []:
            pname = raw.get("name", "")
            branch = raw.get("branch", "")
            main_stars: list[StarPlacementV3] = []
            lucky_stars: list[StarPlacementV3] = []
            evil_stars: list[StarPlacementV3] = []
            brightness: dict[str, str] = {}
            transformations: list[dict[str, str]] = []

            for s in raw.get("stars") or []:
                name = s.get("name", "")
                if not name or str(name).startswith("大限"):
                    continue
                cat = s.get("category", "")
                item = cls._star_item(
                    name,
                    pname,
                    branch=branch,
                    category="main" if cat == "main" else cat,
                    sihua=s.get("sihua") or sihua_map.get(name),
                )
                if item.brightness:
                    brightness[name] = item.brightness
                if item.sihua:
                    transformations.append({"star": name, "type": item.sihua})
                if cat == "main" or name in MAIN_STAR_NAMES_V3:
                    main_stars.append(item)
                elif cat == "sha" or name in SIX_SHA_NAMES:
                    evil_stars.append(item)
                elif cat in {"aux", "lucky"} or name in SIX_LUCKY_NAMES or name == "禄存":
                    lucky_stars.append(item)

            minors = [
                cls._star_item(
                    m.get("name") or m.get("star", ""),
                    pname,
                    branch=m.get("branch", branch),
                    category="minor",
                    rule_source=m.get("rule_source", ""),
                    trace=m.get("trace"),
                )
                for m in minor_by_palace.get(pname, [])
            ]

            result.append(
                PalaceV3(
                    palace_name=pname,
                    branch=branch,
                    ganzhi=raw.get("ganzhi", ""),
                    position=raw.get("position", 0),
                    opposite=raw.get("opposite", ""),
                    sanhe=raw.get("sanhe") or [],
                    is_ming_gong=bool(raw.get("is_ming_gong")),
                    is_shen_gong=bool(raw.get("is_shen_gong")),
                    main_stars=main_stars,
                    lucky_stars=lucky_stars,
                    evil_stars=evil_stars,
                    minor_stars=minors,
                    brightness=brightness,
                    transformations=transformations,
                    daxian=daxian_by_palace.get(pname),
                    liunian={"year": liu.get("year"), "branch": liu.get("branch")}
                    if liu.get("palace") == pname
                    else None,
                    xiaoxian={"current": True} if xiao_current == pname else None,
                )
            )
        return result

    @classmethod
    def _build_stars_index(cls, chart: dict, palaces: list[PalaceV3]) -> StarsIndexV3:
        main: list[StarPlacementV3] = []
        lucky: list[StarPlacementV3] = []
        sha: list[StarPlacementV3] = []
        others: list[StarPlacementV3] = []

        for p in palaces:
            main.extend(p.main_stars)
            for s in p.lucky_stars:
                if s.name in SIX_LUCKY_NAMES:
                    lucky.append(s)
                else:
                    others.append(s)
            sha.extend(p.evil_stars)
            others.extend(p.minor_stars)

        # 天马等 za
        for p in chart.get("palaces") or []:
            for s in p.get("stars") or []:
                name = s.get("name", "")
                if name in OTHER_STAR_NAMES and name == "天马":
                    others.append(
                        cls._star_item(name, p.get("name", ""), branch=p.get("branch", ""), category="za")
                    )

        # 去重 others by name
        seen: set[str] = set()
        uniq_others: list[StarPlacementV3] = []
        for s in others:
            if s.name in seen:
                continue
            seen.add(s.name)
            uniq_others.append(s)

        all_stars = main + lucky + sha + uniq_others
        return StarsIndexV3(
            main_stars=main,
            six_lucky=lucky,
            six_sha=sha,
            others=uniq_others,
            all=all_stars,
        )

    @classmethod
    def _build_fortune(cls, chart: dict) -> FortuneV3:
        daxian_ranges = chart.get("daxian_ranges") or []
        xiao = chart.get("xiaoxian") or {}
        liu = chart.get("liu_nian") or {}

        return FortuneV3(
            daxian=FortunePeriodV3(
                enabled=True,
                items=daxian_ranges,
                direction=chart.get("daxian_direction", ""),
                current={},
            ),
            liuxian=FortunePeriodV3(
                enabled=True,
                current={
                    "year": liu.get("year"),
                    "branch": liu.get("branch"),
                    "palace": liu.get("palace"),
                },
                items=[],
            ),
            xiaoxian=FortunePeriodV3(
                enabled=bool(xiao.get("enabled", True)),
                items=xiao.get("yearly_cycle") or [],
                current={
                    "age": xiao.get("current_age"),
                    "palace": xiao.get("current_palace"),
                    "branch": xiao.get("current_branch"),
                },
                direction=xiao.get("direction", ""),
                trace=xiao.get("trace") or {},
            ),
            # 流月/流日/流时：未实现则 enabled=False，禁止假数据
            liuyue=FortunePeriodV3(enabled=False, trace={"status": "not_implemented"}),
            liuri=FortunePeriodV3(enabled=False, trace={"status": "not_implemented"}),
            liushi=FortunePeriodV3(enabled=False, trace={"status": "not_implemented"}),
        )
