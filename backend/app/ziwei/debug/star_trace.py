"""Star Placement Trace — 排盘逐步审计（不修改算法）。

用于定位：与专业软件星位差异从哪一步开始偏移。
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any

from app.ziwei.constants import EARTHLY_BRANCHES
from app.ziwei.engines.bureau_engine import BureauEngine
from app.ziwei.engines.calendar_engine import CalendarEngine
from app.ziwei.engines.palace_engine import PalaceEngine
from app.ziwei.engines.star_placement_engine import MAIN_STAR_ORDER, StarPlacementEngine
from app.ziwei.rules.loader import RulesLoader
from app.ziwei.rules.seed_generator import calc_tianfu_branch_index, calc_ziwei_branch_index
from app.ziwei_engine.calendar.lunar_converter import LunarConverter

ZIWEI_SERIES = ("紫微", "天机", "太阳", "武曲", "天同", "廉贞")
TIANFU_SERIES = ("天府", "太阴", "贪狼", "巨门", "天相", "天梁", "七杀", "破军")

ZIWEI_POSITION_RULE_DOC = (
    "calc_ziwei_branch_index / ziwei_position_rules："
    "生日÷局数；不能整除则商+1；index=商-1，余≠0再-1；自寅顺数"
)
TIANFU_POSITION_RULE_DOC = (
    "calc_tianfu_branch_index：寅–申轴镜像 index=(4-ziwei_index)%12；"
    "非对宫(+6)；仅巳/亥时与对宫重合"
)


@dataclass
class StarPlacementTrace:
    input: dict[str, Any] = field(default_factory=dict)
    calendar_result: dict[str, Any] = field(default_factory=dict)
    ming_gong: str = ""
    shen_gong: str = ""
    wuxing_ju: str = ""
    bureau_number: int = 0
    lunar_day: int = 0
    ziwei_position_rule: str = ZIWEI_POSITION_RULE_DOC
    ziwei_position: str = ""
    ziwei_index: int = -1
    ziwei_from_formula: str = ""
    ziwei_from_rules_table: str = ""
    ziwei_formula_table_match: bool = False
    tianfu_position_rule: str = TIANFU_POSITION_RULE_DOC
    tianfu_position: str = ""
    tianfu_index: int = -1
    fourteen_star_sequence: list[dict[str, Any]] = field(default_factory=list)
    final_palace_mapping: dict[str, str] = field(default_factory=dict)
    final_branch_mapping: dict[str, str] = field(default_factory=dict)
    ziwei_series: dict[str, str] = field(default_factory=dict)
    tianfu_series: dict[str, str] = field(default_factory=dict)
    offset_hints: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _parse_dt(birth_date: str, birth_time: str) -> datetime:
    hour, minute = birth_time.split(":")[:2]
    y, m, d = birth_date.split("-")
    return datetime(int(y), int(m), int(d), int(hour), int(minute))


def run_star_trace(
    *,
    birth_date: str,
    birth_time: str,
    gender: str = "male",
    calendar_type: str = "solar",
    location: str | None = None,
    is_leap_month: bool = False,
) -> StarPlacementTrace:
    """完整排盘链路逐步 trace。"""
    solar_date = birth_date
    if calendar_type == "lunar":
        solar_date = LunarConverter.lunar_to_solar(birth_date, is_leap=is_leap_month)

    longitude = LunarConverter.parse_location(location)
    lunar, true_dt = LunarConverter.convert(solar_date, birth_time, location)
    cal = CalendarEngine.convert(true_dt, longitude=longitude)

    ming_idx, shen_idx, palaces = PalaceEngine.compute(
        cal.lunar_month, cal.shichen_index, year_stem=cal.year_stem
    )
    ming = next(p for p in palaces if p.is_ming_gong)
    shen = next(p for p in palaces if p.is_shen_gong)
    bureau = BureauEngine.compute(cal.year_stem, ming_idx)

    formula_idx = calc_ziwei_branch_index(cal.lunar_day, bureau.bureau_number)
    formula_branch = EARTHLY_BRANCHES[formula_idx]
    table_branch = RulesLoader.get_ziwei_position(bureau.bureau_number, cal.lunar_day)
    tf_idx = calc_tianfu_branch_index(formula_idx)
    tf_branch = EARTHLY_BRANCHES[tf_idx]

    placement = StarPlacementEngine.compute(
        palaces,
        cal.lunar_day,
        bureau.bureau_number,
        cal.year_stem,
        cal.year_branch,
        cal.shichen_index,
        cal.lunar_month,
    )
    branch_to_palace = {p.branch: p.name for p in palaces}
    star_to_palace = placement.star_to_palace(branch_to_palace)

    sequence: list[dict[str, Any]] = []
    for name in MAIN_STAR_ORDER:
        br = placement.star_branches.get(name, "")
        sequence.append(
            {
                "star": name,
                "branch": br,
                "palace": star_to_palace.get(name, ""),
                "series": "ziwei" if name in ZIWEI_SERIES else "tianfu",
            }
        )

    hints: list[str] = []
    if formula_branch != table_branch:
        hints.append(
            f"紫微公式={formula_branch} 与规则表={table_branch} 不一致（规则缓存可能过期）"
        )
    if placement.ziwei_branch != formula_branch:
        hints.append(
            f"引擎紫微={placement.ziwei_branch} 与公式={formula_branch} 偏移 → 查 RulesLoader"
        )
    if placement.star_branches.get("天府") != tf_branch:
        hints.append(
            f"天府引擎={placement.star_branches.get('天府')} 与镜像公式={tf_branch} 偏移"
        )
    if not hints:
        hints.append(
            "引擎内部：历法→命宫→局→紫微公式/表→天府镜像→十四主星序列 自洽；"
            "若与文墨仍不同，偏差更可能在：真太阳时/历法边界/命宫起法/流派（对宫天府）"
        )

    return StarPlacementTrace(
        input={
            "birth_date": birth_date,
            "birth_time": birth_time,
            "gender": gender,
            "calendar_type": calendar_type,
            "location": location,
            "solar_date_used": solar_date,
            "true_solar": true_dt.isoformat(),
        },
        calendar_result={
            "lunar_year": cal.lunar_year,
            "lunar_month": cal.lunar_month,
            "lunar_day": cal.lunar_day,
            "is_leap_month": cal.is_leap_month,
            "year_ganzhi": cal.year_ganzhi,
            "month_ganzhi": cal.month_ganzhi,
            "day_ganzhi": cal.day_ganzhi,
            "hour_ganzhi": cal.hour_ganzhi,
            "shichen": cal.shichen_name,
            "used_true_solar": cal.used_true_solar,
            "lunar_text": getattr(lunar, "lunar_text", ""),
        },
        ming_gong=ming.branch,
        shen_gong=shen.branch,
        wuxing_ju=bureau.bureau_name,
        bureau_number=bureau.bureau_number,
        lunar_day=cal.lunar_day,
        ziwei_position=placement.ziwei_branch,
        ziwei_index=EARTHLY_BRANCHES.index(placement.ziwei_branch)
        if placement.ziwei_branch in EARTHLY_BRANCHES
        else -1,
        ziwei_from_formula=formula_branch,
        ziwei_from_rules_table=table_branch,
        ziwei_formula_table_match=formula_branch == table_branch,
        tianfu_position=tf_branch,
        tianfu_index=tf_idx,
        fourteen_star_sequence=sequence,
        final_palace_mapping={n: star_to_palace.get(n, "") for n in MAIN_STAR_ORDER},
        final_branch_mapping={n: placement.star_branches.get(n, "") for n in MAIN_STAR_ORDER},
        ziwei_series={n: placement.star_branches.get(n, "") for n in ZIWEI_SERIES},
        tianfu_series={n: placement.star_branches.get(n, "") for n in TIANFU_SERIES},
        offset_hints=hints,
    )


def compare_trace_to_reference(
    trace: StarPlacementTrace,
    reference_fourteen: dict[str, Any],
) -> dict[str, Any]:
    """逐步对比 reference 十四主星，标出首个偏移步骤。"""
    diffs: list[dict[str, Any]] = []
    first_offset_step: str | None = None

    ref_ziwei = None
    for star, val in reference_fourteen.items():
        if star == "紫微":
            ref_ziwei = val.get("branch") if isinstance(val, dict) else val
            break
    if ref_ziwei and trace.ziwei_position != ref_ziwei:
        first_offset_step = "ziwei_position"
        diffs.append(
            {
                "step": "ziwei_position",
                "engine": trace.ziwei_position,
                "reference": ref_ziwei,
            }
        )

    ref_tf = None
    for star, val in reference_fourteen.items():
        if star == "天府":
            ref_tf = val.get("branch") if isinstance(val, dict) else val
            break
    if ref_tf and trace.tianfu_position != ref_tf:
        if first_offset_step is None:
            first_offset_step = "tianfu_position"
        diffs.append(
            {
                "step": "tianfu_position",
                "engine": trace.tianfu_position,
                "reference": ref_tf,
            }
        )

    for star in MAIN_STAR_ORDER:
        exp = reference_fourteen.get(star)
        if not exp:
            continue
        exp_br = exp.get("branch") if isinstance(exp, dict) else exp
        exp_pal = exp.get("palace") if isinstance(exp, dict) else None
        eng_br = trace.final_branch_mapping.get(star)
        eng_pal = trace.final_palace_mapping.get(star)
        if exp_br and eng_br != exp_br:
            if first_offset_step is None:
                first_offset_step = f"fourteen.{star}"
            diffs.append(
                {
                    "step": f"fourteen.{star}.branch",
                    "engine": eng_br,
                    "reference": exp_br,
                }
            )
        if exp_pal and eng_pal != exp_pal:
            if first_offset_step is None:
                first_offset_step = f"fourteen.{star}.palace"
            diffs.append(
                {
                    "step": f"fourteen.{star}.palace",
                    "engine": eng_pal,
                    "reference": exp_pal,
                }
            )

    return {
        "matched": len(diffs) == 0,
        "first_offset_step": first_offset_step,
        "differences": diffs,
        "trace_summary": {
            "ming_gong": trace.ming_gong,
            "wuxing_ju": trace.wuxing_ju,
            "ziwei": trace.ziwei_position,
            "tianfu": trace.tianfu_position,
        },
    }
