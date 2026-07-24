"""五行局 — 命宫干支纳音。"""

from __future__ import annotations

from app.ziwei.engines.bureau_engine import BureauEngine
from app.ziwei_classical.validator.rule_trace import RuleTrace

BUREAU_NAMES = {2: "水二局", 3: "木三局", 4: "金四局", 5: "土五局", 6: "火六局"}

BUREAU_RULE = (
    "五虎遁安命宫干支 → 纳音五行 → 局数："
    "水二、木三、金四、土五、火六"
)


def calc_five_element_bureau(
    year_stem: str,
    ming_branch_index: int,
    trace: RuleTrace | None = None,
) -> dict:
    bureau = BureauEngine.compute(year_stem, ming_branch_index)
    out = {
        "bureau_number": bureau.bureau_number,
        "bureau_name": bureau.bureau_name,
        "wuxing": BUREAU_NAMES.get(bureau.bureau_number, bureau.bureau_name),
        "ming_gong_ganzhi": bureau.ming_gong_ganzhi,
        "nayin": bureau.nayin,
        "element": getattr(bureau, "nayin_element", "") or "",
    }
    if trace is not None:
        trace.add(
            step="five_element_bureau",
            rule=BUREAU_RULE,
            inputs={"year_stem": year_stem, "ming_branch_index": ming_branch_index},
            outputs=out,
            source="ziwei_classical.bureau.five_element",
        )
    return out
