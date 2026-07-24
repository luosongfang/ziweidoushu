"""accuracy_report — 生成 accuracy_report.json。"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.ziwei.accuracy.accuracy_manager import AccuracyManager

DEFAULT_REPORT_PATH = (
    Path(__file__).resolve().parents[1] / "accuracy" / "output" / "accuracy_report.json"
)


class AccuracyReportBuilder:
    """汇总 Professional Accuracy Center 检测结果。"""

    def __init__(self, manager: AccuracyManager | None = None) -> None:
        self.manager = manager or AccuracyManager()

    def build(self) -> dict[str, Any]:
        summary = self.manager.dataset_summary()
        compares = self.manager.compare_all_professional()
        scores = [c.get("accuracy_score") for c in compares if "accuracy_score" in c]
        avg = round(sum(scores) / len(scores), 2) if scores else None
        all_matched = all(c.get("matched") for c in compares) if compares else False

        critical_total = sum(len(c.get("critical_difference") or []) for c in compares)
        major_total = sum(len(c.get("major_difference") or []) for c in compares)
        minor_total = sum(len(c.get("minor_difference") or []) for c in compares)

        return {
            "version": "1.4.0",
            "title": "Ziwei Core Engine Professional Accuracy Report",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "policy": {
                "auto_test_level": AccuracyManager.AUTO_TEST_LEVEL,
                "algorithm_modification": "forbidden_in_this_phase",
                "scope": "detection_only",
            },
            "dataset": summary.get("counts") or {},
            "accuracy": {
                "average_score": avg,
                "all_matched": all_matched,
                "cases_tested": len(compares),
                "critical_difference_total": critical_total,
                "major_difference_total": major_total,
                "minor_difference_total": minor_total,
            },
            "cases": compares,
            "missing": summary.get("missing") or [],
            "notes": [
                "仅 verified_professional 进入自动对比",
                "reference 缺字段时记入 skipped_fields，不扣分",
                "辅星/煞星/杂曜/运限：若黄金盘未提供则跳过",
            ],
        }

    def build_and_write(self, path: Path | None = None) -> dict[str, Any]:
        report = self.build()
        write_accuracy_report(report, path)
        return report


def write_accuracy_report(report: dict[str, Any], path: Path | None = None) -> Path:
    out = path or DEFAULT_REPORT_PATH
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return out
