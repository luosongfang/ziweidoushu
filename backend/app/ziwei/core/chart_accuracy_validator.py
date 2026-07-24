"""排盘准确性门槛 — accuracy_score < 95 时禁止进入 AI 分析。"""

from __future__ import annotations

from typing import Any

from app.ziwei.debug.classical_audit import MAIN_14, ClassicalAuditReport, run_classical_audit


class ChartAccuracyValidator:
    """核心盘完整性/一致性检测（不含杂曜/小限/飞星）。"""

    @classmethod
    def validate_audit(cls, audit: ClassicalAuditReport) -> dict[str, Any]:
        errors: list[str] = []
        warnings: list[str] = []
        checks: dict[str, bool] = {}

        checks["has_minggong"] = bool(audit.minggong)
        checks["has_shengong"] = bool(audit.shengong)
        checks["has_wuxingju"] = bool(audit.wuxingju)
        checks["has_ziwei"] = bool(audit.ziwei_position)

        from app.ziwei.constants import EARTHLY_BRANCHES

        star_branches = [audit.fourteen_star_positions.get(n, "") for n in MAIN_14]
        filled = [b for b in star_branches if b]
        checks["fourteen_count"] = len(filled) == 14
        # Multiple main stars legitimately share the same branch (palace).
        checks["fourteen_branches_valid"] = len(filled) == 14 and all(
            b in EARTHLY_BRANCHES for b in filled
        )

        ft = audit.four_transform
        checks["four_transform"] = all(
            (ft.get(k) or {}).get("star") for k in ("lu", "quan", "ke", "ji")
        )
        checks["ganzhi_year"] = bool(audit.ganzhi.get("year"))
        checks["shichen"] = bool(audit.shichen.get("name"))

        # 十二宫主星覆盖：命盘应有 12 个地支宫位概念（由 palaces_main_stars 间接验证）
        checks["palaces_mapped"] = sum(len(v) for v in audit.palaces_main_stars.values()) == 14

        for key, ok in checks.items():
            if not ok:
                errors.append(f"check_failed:{key}")

        passed = sum(1 for v in checks.values() if v)
        total = max(len(checks), 1)
        score = int(round(100 * passed / total))

        return {
            "accuracy_score": score,
            "errors": errors,
            "warnings": warnings,
            "checks": checks,
            "pass_threshold": 95,
            "allowed_for_ai": score >= 95 and not errors,
        }

    @classmethod
    def validate_birth(
        cls,
        *,
        birth_date: str,
        birth_time: str,
        gender: str = "male",
        calendar_type: str = "solar",
        location: str | None = None,
    ) -> dict[str, Any]:
        audit = run_classical_audit(
            birth_date=birth_date,
            birth_time=birth_time,
            gender=gender,
            calendar_type=calendar_type,
            location=location,
        )
        result = cls.validate_audit(audit)
        result["audit_summary"] = {
            "minggong": audit.minggong,
            "shengong": audit.shengong,
            "wuxingju": audit.wuxingju,
            "ziwei": audit.ziwei_position,
        }
        return result

    @classmethod
    def assert_ai_allowed(cls, accuracy: dict[str, Any]) -> None:
        if not accuracy.get("allowed_for_ai"):
            raise PermissionError(
                f"排盘准确率不足，禁止 AI 分析：score={accuracy.get('accuracy_score')} "
                f"errors={accuracy.get('errors')}"
            )
