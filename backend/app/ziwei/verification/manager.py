"""规则版本管理与验证调度。"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.ziwei.rules.loader import RulesLoader
from app.ziwei.verification.reference_runner import (
    load_reference_charts,
    verify_all_reference_charts,
)

CURRENT_RULES_VERSION = "2026.07.22"


@dataclass
class VerificationReport:
    passed: bool
    rules_version: str
    total_charts: int
    failed_charts: dict[str, list[str]] = field(default_factory=dict)
    message: str = ""


class VerificationManager:
    """运行标准命盘验证套件。"""

    @staticmethod
    def run_reference_suite() -> VerificationReport:
        data = load_reference_charts()
        charts = data.get("charts", [])
        failures = verify_all_reference_charts()
        passed = len(failures) == 0
        return VerificationReport(
            passed=passed,
            rules_version=RulesLoader.rules_version() or CURRENT_RULES_VERSION,
            total_charts=len(charts),
            failed_charts=failures,
            message="全部标准盘通过" if passed else f"{len(failures)} 张标准盘未通过",
        )
