"""命盘结构验证器 — 返回 warnings，不阻断排盘。"""

from __future__ import annotations

from app.ziwei.core.chart_schema_v2 import (
    AUXILIARY_STAR_NAMES,
    BRIGHTNESS_LEVELS,
    LUCKY_STAR_NAMES,
    MAIN_STAR_NAMES,
    SHA_STAR_NAMES,
    StandardChartSchemaV2,
    ZA_STAR_NAMES,
)


class ChartValidator:
    """StandardChartSchema V2 / V2.5 完整性检查。"""

    @classmethod
    def validate(cls, chart: StandardChartSchemaV2) -> list[str]:
        warnings: list[str] = []
        is_v25 = chart.schema_version == "2.5"

        if len(chart.palaces) != 12:
            warnings.append(f"十二宫数量异常：期望 12，实际 {len(chart.palaces)}")

        main_names = {s.name for s in chart.stars.main}
        if len(main_names) != 14:
            missing = set(MAIN_STAR_NAMES) - main_names
            extra = main_names - set(MAIN_STAR_NAMES)
            if missing:
                warnings.append(f"十四主星缺失：{', '.join(sorted(missing))}")
            if extra:
                warnings.append(f"十四主星多余：{', '.join(sorted(extra))}")
            if not missing and not extra and len(chart.stars.main) != 14:
                warnings.append(f"十四主星数量异常：期望 14，实际 {len(chart.stars.main)}")

        for star in chart.stars.main:
            if not star.brightness:
                warnings.append(f"主星亮度缺失：{star.name}")
            elif star.brightness not in BRIGHTNESS_LEVELS:
                warnings.append(f"主星亮度异常：{star.name}={star.brightness}")

        lucky_names = {s.name for s in chart.stars.lucky}
        for name in LUCKY_STAR_NAMES:
            if name not in lucky_names:
                warnings.append(f"六吉星缺失：{name}")

        sha_names = {s.name for s in chart.stars.sha}
        for name in SHA_STAR_NAMES:
            if name not in sha_names:
                warnings.append(f"六煞星缺失：{name}")

        if not chart.stars.lu_cun:
            warnings.append("禄存缺失")
        elif len(chart.stars.lu_cun) != 1:
            warnings.append(f"禄存数量异常：期望 1，实际 {len(chart.stars.lu_cun)}")

        za_names = {s.name for s in chart.stars.za}
        for name in ZA_STAR_NAMES:
            if name not in za_names:
                warnings.append(f"杂曜缺失：{name}")

        if is_v25:
            aux_names = {s.name for s in chart.stars.auxiliary}
            for name in AUXILIARY_STAR_NAMES:
                if name not in aux_names:
                    warnings.append(f"辅助杂曜缺失：{name}")
            for star in chart.stars.auxiliary:
                if star.category != "auxiliary":
                    warnings.append(f"辅助星分类异常：{star.name}={star.category}")
                if not star.trace:
                    warnings.append(f"辅助星 trace 缺失：{star.name}")

            if not chart.xiaoxian.enabled:
                warnings.append("小限未启用")
            elif not chart.xiaoxian.current_palace:
                warnings.append("小限当前宫位缺失")
            elif not chart.xiaoxian.yearly_cycle:
                warnings.append("小限 yearly_cycle 缺失")

            if chart.daxian_transform:
                dt = chart.daxian_transform
                for key, label in (("lu", "禄"), ("quan", "权"), ("ke", "科"), ("ji", "忌")):
                    item = getattr(dt, key)
                    if not item.star or not item.palace:
                        warnings.append(f"大限四化缺失：{label}")
            else:
                warnings.append("大限四化缺失")

            annual = chart.liunian.annual_transform
            if not annual:
                warnings.append("流年四化缺失")
            else:
                for key, label in (("lu", "禄"), ("quan", "权"), ("ke", "科"), ("ji", "忌")):
                    item = getattr(annual, key)
                    if not item.star or not item.palace:
                        warnings.append(f"流年四化缺失：{label}")

        ft = chart.four_transform
        transform_count = sum(
            1 for item in (ft.lu, ft.quan, ft.ke, ft.ji) if item.star and item.palace
        )
        if transform_count != 4:
            warnings.append(f"四化数量异常：期望 4，实际 {transform_count}")

        ming_palaces = [p for p in chart.palaces if p.is_ming_gong]
        if len(ming_palaces) != 1:
            warnings.append(f"命宫标记异常：期望 1，实际 {len(ming_palaces)}")
        elif chart.meta.mingGong and ming_palaces[0].branch != chart.meta.mingGong:
            warnings.append(
                f"命宫地支不一致：meta={chart.meta.mingGong} palace={ming_palaces[0].branch}"
            )

        shen_palaces = [p for p in chart.palaces if p.is_shen_gong]
        if len(shen_palaces) != 1:
            warnings.append(f"身宫标记异常：期望 1，实际 {len(shen_palaces)}")
        elif chart.meta.shenGong and shen_palaces[0].branch != chart.meta.shenGong:
            warnings.append(
                f"身宫地支不一致：meta={chart.meta.shenGong} palace={shen_palaces[0].branch}"
            )

        if not chart.meta.mingGong:
            warnings.append("meta.mingGong 缺失")
        if not chart.meta.shenGong:
            warnings.append("meta.shenGong 缺失")

        return warnings
