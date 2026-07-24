"""reference_compare — engine_chart vs reference_chart。"""

from __future__ import annotations

from typing import Any

from app.ziwei.accuracy.chart_diff_engine import ChartDiffEngine, DiffResult


class ReferenceCompare:
    """输入引擎盘与标准盘，输出分级差异与 accuracy_score。"""

    def __init__(self, engine: ChartDiffEngine | None = None) -> None:
        self.engine = engine or ChartDiffEngine()

    def compare(self, engine_chart: Any, reference_chart: Any) -> dict[str, Any]:
        result: DiffResult = self.engine.compare(engine_chart, reference_chart)
        by = result.by_impact()
        score = result.accuracy_score()
        return {
            "critical_difference": by["critical"],
            "major_difference": by["major"],
            "minor_difference": by["minor"],
            "accuracy_score": score,
            "diff_count": len(result.diffs),
            "skipped_fields": result.skipped,
            "matched": len(result.diffs) == 0,
        }


def compare_charts(engine_chart: Any, reference_chart: Any) -> dict[str, Any]:
    return ReferenceCompare().compare(engine_chart, reference_chart)
