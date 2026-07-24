"""生年四化。"""

from __future__ import annotations

from app.ziwei_engine.transformation.four_hua import FourHuaCalculator
from app.ziwei_classical.validator.rule_trace import RuleTrace


def birth_four_hua(
    year_stem: str,
    star_to_palace: dict[str, str],
    trace: RuleTrace | None = None,
) -> dict:
    four = FourHuaCalculator.calculate(year_stem, star_to_palace)
    out = {
        "stem": year_stem,
        "lu": four.hua_lu,
        "quan": four.hua_quan,
        "ke": four.hua_ke,
        "ji": four.hua_ji,
    }
    if trace is not None:
        trace.add(
            step="birth_four_hua",
            rule="生年干查四化表",
            inputs={"year_stem": year_stem},
            outputs=out,
            source="ziwei_classical.transformations.birth_four_hua",
        )
    return out
