"""Professional reference sample validator."""

from __future__ import annotations

from typing import Any

from app.ziwei.reference.metadata import MAIN_14, PALACE_NAMES, REQUIRED_BIRTH, REQUIRED_CHART_REF


def validate_sample(sample: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    if not sample.get("id"):
        errors.append("缺少 id")
    if not sample.get("source"):
        warnings.append("缺少 source")

    birth = sample.get("birth") or {}
    for k in REQUIRED_BIRTH:
        if not birth.get(k):
            errors.append(f"birth.{k} 缺失")

    level = sample.get("verification_level") or "pending"
    ref = sample.get("chart_reference") or {}

    if level == "pending":
        return {
            "ok": len(errors) == 0,
            "errors": errors,
            "warnings": warnings + ["pending：不要求 chart_reference 完整"],
            "eligible_for_calibration": False,
        }

    for k in REQUIRED_CHART_REF:
        if k not in ref or ref.get(k) in (None, ""):
            if k == "palaces":
                if not ref.get("palaces"):
                    errors.append("chart_reference.palaces 缺失")
            else:
                errors.append(f"chart_reference.{k} 缺失")

    palaces = ref.get("palaces") or {}
    if palaces:
        missing_p = [n for n in PALACE_NAMES if n not in palaces]
        if missing_p:
            errors.append(f"宫位缺失: {missing_p}")
        stars: list[str] = []
        for n in PALACE_NAMES:
            p = palaces.get(n) or {}
            stars.extend(p.get("main_stars") or [])
        missing_s = [s for s in MAIN_14 if s not in stars]
        if missing_s:
            errors.append(f"十四主星缺失: {missing_s}")
        dups = sorted({s for s in stars if stars.count(s) > 1})
        if dups:
            errors.append(f"主星重复: {dups}")

    if level == "verified_professional" and sample.get("source") != "wenmo":
        warnings.append("verified_professional 建议 source=wenmo")

    return {
        "ok": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "eligible_for_calibration": level == "verified_professional" and len(errors) == 0,
    }
