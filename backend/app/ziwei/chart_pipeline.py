"""统一排盘生产入口 — ChartPipeline → StandardChartSchema V2。

V1.2.6：生产 API 只走本入口；内部仍复用 ChartBuilder 核心计算，
再经 ChartNormalizer 输出 V2.5（校准阶段不以 V3/杂曜为验收标准）。
"""

from __future__ import annotations

from typing import Any

from app.ziwei.core.chart_accuracy_validator import ChartAccuracyValidator
from app.ziwei.core.chart_normalizer import ChartNormalizer
from app.ziwei.core.chart_schema_v2 import StandardChartSchemaV2
from app.ziwei.debug.classical_audit import run_classical_audit
from app.ziwei_engine.chart_builder import ChartBuilder


class ChartPipeline:
    """统一排盘流水线。"""

    @classmethod
    def generate(
        cls,
        *,
        name: str,
        gender: str,
        solar_date: str,
        time: str,
        location: str | None = None,
        reference_year: int | None = None,
        require_accuracy: bool = True,
    ) -> tuple[StandardChartSchemaV2, dict[str, Any]]:
        """
        Returns
        -------
        chart : StandardChartSchemaV2
        meta : {accuracy, classical_audit_summary, engine_version}
        """
        raw = ChartBuilder.build(
            name=name,
            gender=gender,
            solar_date=solar_date,
            time=time,
            location=location,
            reference_year=reference_year,
        )
        chart = ChartNormalizer.normalize(raw)

        accuracy = ChartAccuracyValidator.validate_birth(
            birth_date=solar_date[:10] if "T" in solar_date else solar_date,
            birth_time=time,
            gender=gender,
            calendar_type="solar",
            location=location,
        )
        if require_accuracy:
            ChartAccuracyValidator.assert_ai_allowed(accuracy)

        audit = run_classical_audit(
            birth_date=solar_date[:10] if "T" in solar_date else solar_date,
            birth_time=time,
            gender=gender,
            location=location,
        )
        meta = {
            "accuracy": accuracy,
            "classical_audit_summary": {
                "minggong": audit.minggong,
                "shengong": audit.shengong,
                "wuxingju": audit.wuxingju,
                "ziwei": audit.ziwei_position,
                "tianfu": audit.tianfu_position,
                "formula_notes": audit.formula_notes,
            },
            "engine_version": raw.get("engine_version", "1.3"),
            "pipeline": "ChartPipeline/ChartBuilder/ChartNormalizer/V2.5",
        }
        return chart, meta

    @classmethod
    def generate_raw(cls, **kwargs: Any) -> dict[str, Any]:
        """仅排盘，不跑准确率门槛（调试用）。"""
        return ChartBuilder.build(**kwargs)
