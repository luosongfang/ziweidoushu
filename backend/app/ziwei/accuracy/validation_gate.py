"""validation_gate — 准确率门禁（只检测，不改算法）。"""

from __future__ import annotations

from typing import Any

from app.ziwei.accuracy.reference_compare import compare_charts

DEFAULT_MIN_SCORE = 95.0


class AccuracyValidationGate:
    """accuracy_score < threshold → 阻断后续专业验收 / AI（本阶段仅返回门禁结果）。"""

    def __init__(self, min_score: float = DEFAULT_MIN_SCORE) -> None:
        self.min_score = min_score

    def evaluate(
        self,
        *,
        engine_chart: Any | None = None,
        reference_chart: Any | None = None,
        compare_result: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if compare_result is None:
            if engine_chart is None or reference_chart is None:
                raise ValueError("需要 compare_result 或 engine_chart+reference_chart")
            compare_result = compare_charts(engine_chart, reference_chart)

        score = float(compare_result.get("accuracy_score", 0))
        critical = compare_result.get("critical_difference") or []
        passed = score >= self.min_score and len(critical) == 0

        return {
            "passed": passed,
            "accuracy_score": score,
            "min_score": self.min_score,
            "critical_count": len(critical),
            "major_count": len(compare_result.get("major_difference") or []),
            "minor_count": len(compare_result.get("minor_difference") or []),
            "blocked_reason": None
            if passed
            else (
                f"critical_difference={len(critical)}"
                if critical
                else f"accuracy_score={score} < {self.min_score}"
            ),
            "allowed_for_professional_accept": passed,
            "allowed_for_ai": passed,
        }

    def assert_pass(self, **kwargs: Any) -> dict[str, Any]:
        result = self.evaluate(**kwargs)
        if not result["passed"]:
            raise AssertionError(
                f"AccuracyValidationGate failed: {result['blocked_reason']}"
            )
        return result
