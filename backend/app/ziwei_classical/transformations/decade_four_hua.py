"""大限四化 — V1.0 占位（依赖大限天干）。"""

from __future__ import annotations

from app.ziwei_classical.validator.rule_trace import RuleTrace


def decade_four_hua(
    decade_stem: str = "",
    star_to_palace: dict[str, str] | None = None,
    trace: RuleTrace | None = None,
) -> dict:
    out = {"stem": decade_stem, "lu": {}, "quan": {}, "ke": {}, "ji": {}, "enabled": bool(decade_stem)}
    if decade_stem and star_to_palace:
        from app.ziwei_classical.transformations.birth_four_hua import birth_four_hua

        out = birth_four_hua(decade_stem, star_to_palace, trace=None)
        out["enabled"] = True
    if trace is not None:
        trace.add(
            step="decade_four_hua",
            rule="大限天干四化（需大限干）",
            inputs={"decade_stem": decade_stem},
            outputs=out,
            source="ziwei_classical.transformations.decade_four_hua",
        )
    return out
