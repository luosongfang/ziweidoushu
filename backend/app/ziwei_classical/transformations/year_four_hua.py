"""流年四化 — V1.0 占位。"""

from __future__ import annotations

from app.ziwei_classical.validator.rule_trace import RuleTrace


def year_four_hua(
    year_stem: str = "",
    star_to_palace: dict[str, str] | None = None,
    trace: RuleTrace | None = None,
) -> dict:
    out = {"stem": year_stem, "enabled": False}
    if year_stem and star_to_palace:
        from app.ziwei_classical.transformations.birth_four_hua import birth_four_hua

        out = birth_four_hua(year_stem, star_to_palace, trace=None)
        out["enabled"] = True
    if trace is not None:
        trace.add(
            step="year_four_hua",
            rule="流年干四化",
            inputs={"year_stem": year_stem},
            outputs=out,
            source="ziwei_classical.transformations.year_four_hua",
        )
    return out
