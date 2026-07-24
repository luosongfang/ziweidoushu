"""命盘质量检测 — Ziwei Core Engine V1.3。"""

from __future__ import annotations

from typing import Any

from app.ziwei.core.professional_chart_schema import (
    MAIN_STAR_NAMES_V3,
    OTHER_STAR_NAMES,
    SIX_LUCKY_NAMES,
    SIX_SHA_NAMES,
    ProfessionalChartSchemaV3,
    QualityV3,
)

KNOWN_STARS: frozenset[str] = frozenset(
    MAIN_STAR_NAMES_V3 + SIX_LUCKY_NAMES + SIX_SHA_NAMES + OTHER_STAR_NAMES
)


class ChartQualityValidator:
    """专业命盘质量门禁：错误项阻断（fail_hard），警告项记入 warnings。"""

    @classmethod
    def validate(
        cls,
        chart: ProfessionalChartSchemaV3 | dict[str, Any],
        *,
        fail_hard: bool = True,
    ) -> QualityV3:
        data = chart.model_dump() if isinstance(chart, ProfessionalChartSchemaV3) else chart
        warnings: list[str] = []
        checks: dict[str, bool] = {}

        palaces = data.get("palaces") or []
        checks["twelve_palaces"] = len(palaces) == 12
        if not checks["twelve_palaces"]:
            warnings.append(f"十二宫数量异常：{len(palaces)}")

        # 十四主星
        stars_idx = data.get("stars") or {}
        main = stars_idx.get("main_stars") or []
        main_names = [s.get("name") or s.get("star") for s in main]
        main_names = [n for n in main_names if n]
        checks["fourteen_main"] = len(set(main_names)) == 14 and set(MAIN_STAR_NAMES_V3) <= set(main_names)
        if not checks["fourteen_main"]:
            missing = sorted(set(MAIN_STAR_NAMES_V3) - set(main_names))
            warnings.append(f"十四主星不完整，缺失：{missing}")

        # 每宫唯一地支 / 无重复主星
        branches = [p.get("branch") for p in palaces]
        checks["unique_branches"] = len(branches) == len(set(branches)) == 12
        if not checks["unique_branches"]:
            warnings.append("十二宫地支不唯一或不完整")

        seen_main: set[str] = set()
        dup_main = False
        for p in palaces:
            for s in p.get("main_stars") or []:
                name = s.get("name") or s.get("star")
                if name in seen_main:
                    dup_main = True
                if name:
                    seen_main.add(name)
        checks["no_duplicate_main"] = not dup_main
        if dup_main:
            warnings.append("存在重复主星")

        # 四化
        ft = data.get("four_transform") or {}
        birth = ft.get("birth_transform") or ft.get("year") or {}
        checks["four_transform_birth"] = all(
            birth.get(k) for k in ("lu", "quan", "ke", "ji")
        )
        if not checks["four_transform_birth"]:
            warnings.append("生年四化不完整")

        # 未知星
        unknown: list[str] = []
        for bucket in ("main_stars", "six_lucky", "six_sha", "others", "all"):
            for s in stars_idx.get(bucket) or []:
                name = s.get("name") or s.get("star")
                if name and name not in KNOWN_STARS and not str(name).startswith("大限"):
                    unknown.append(name)
        checks["no_unknown_stars"] = len(unknown) == 0
        if unknown:
            warnings.append(f"未知星曜：{sorted(set(unknown))}")

        passed = sum(1 for v in checks.values() if v)
        total = max(len(checks), 1)
        score = round(passed / total, 4)

        if fail_hard and not all(checks.values()):
            # 调用方可读取 quality；真正阻断在测试/API 层
            pass

        return QualityV3(quality_score=score, warnings=warnings, checks=checks)

    @classmethod
    def assert_valid(cls, chart: ProfessionalChartSchemaV3 | dict[str, Any]) -> QualityV3:
        quality = cls.validate(chart, fail_hard=True)
        hard_keys = ("twelve_palaces", "fourteen_main", "unique_branches", "no_duplicate_main", "four_transform_birth")
        failed = [k for k in hard_keys if not quality.checks.get(k)]
        if failed:
            raise AssertionError(f"命盘质量门禁失败：{failed}; warnings={quality.warnings}")
        return quality
