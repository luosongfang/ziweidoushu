"""ClassicalAccuracyGate — accuracy < 98% 禁止 AI 解释。"""

from __future__ import annotations

from typing import Any

CLASSICAL_BLOCK_MESSAGE = "命盘校准中，请勿生成解释"
DEFAULT_MIN_SCORE = 98.0


class ClassicalAccuracyGate:
    """经典引擎准确率门禁。"""

    def __init__(self, min_score: float = DEFAULT_MIN_SCORE) -> None:
        self.min_score = min_score

    def evaluate(
        self,
        *,
        accuracy_score: float | None = None,
        compare_result: dict[str, Any] | None = None,
        chart_meta: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        score = accuracy_score
        if score is None and compare_result is not None:
            # PASS 比例粗算
            keys = ["calendar", "palace", "bureau", "ziwei", "tianfu", "fourteen_stars"]
            vals = [compare_result.get(k) for k in keys if k in compare_result]
            if vals:
                score = 100.0 * sum(1 for v in vals if v == "PASS") / len(vals)
            elif compare_result.get("matched"):
                score = 100.0
            else:
                score = 0.0
        if score is None and chart_meta:
            score = float(chart_meta.get("classical_accuracy_score", 0))
        if score is None:
            score = 0.0

        passed = score >= self.min_score
        return {
            "passed": passed,
            "accuracy_score": score,
            "min_score": self.min_score,
            "allowed_for_ai": passed,
            "allowed_for_life_report": passed,
            "allowed_for_pattern_analysis": passed,
            "blocked_reason": None if passed else CLASSICAL_BLOCK_MESSAGE,
            "message": None if passed else CLASSICAL_BLOCK_MESSAGE,
        }

    def assert_pass(self, **kwargs: Any) -> dict[str, Any]:
        result = self.evaluate(**kwargs)
        if not result["passed"]:
            raise AssertionError(result["blocked_reason"])
        return result
