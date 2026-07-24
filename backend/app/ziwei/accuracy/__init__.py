"""Professional Accuracy Center — Ziwei Core Engine V1.4。

只建立检测能力；禁止修改排盘算法。
"""

from app.ziwei.accuracy.accuracy_manager import AccuracyManager
from app.ziwei.accuracy.accuracy_report import AccuracyReportBuilder, write_accuracy_report
from app.ziwei.accuracy.chart_diff_engine import ChartDiffEngine, DiffItem
from app.ziwei.accuracy.coverage_report import build_coverage_report
from app.ziwei.accuracy.fourteen_star_gate import (
    can_expand_professional_aux_systems,
    missing_star_inventory,
)
from app.ziwei.accuracy.reference_compare import ReferenceCompare, compare_charts
from app.ziwei.accuracy.root_cause_analyzer import analyze_root_cause
from app.ziwei.accuracy.validation_gate import AccuracyValidationGate

__all__ = [
    "AccuracyManager",
    "AccuracyReportBuilder",
    "AccuracyValidationGate",
    "ChartDiffEngine",
    "DiffItem",
    "ReferenceCompare",
    "analyze_root_cause",
    "build_coverage_report",
    "can_expand_professional_aux_systems",
    "compare_charts",
    "missing_star_inventory",
    "write_accuracy_report",
]
