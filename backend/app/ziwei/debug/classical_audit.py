"""经典命例校准审计 — Ziwei Core Engine V1.2.6。

输入出生资料 → 逐步跑历法/命身宫/五行局/紫微/十四主星/生年四化，
产出 ClassicalAuditReport，并可与 reference 对比生成 difference_report。
不写入虚假数据；不调用 LLM。
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any

from app.ziwei.constants import EARTHLY_BRANCHES, MING_ZHU_BY_BRANCH, SHEN_ZHU_BY_YEAR_BRANCH
from app.ziwei.engines.bureau_engine import BureauEngine
from app.ziwei.engines.calendar_engine import CalendarEngine
from app.ziwei.engines.palace_engine import PalaceEngine
from app.ziwei.engines.star_placement_engine import StarPlacementEngine
from app.ziwei.rules.seed_generator import calc_tianfu_branch_index, calc_ziwei_branch_index
from app.ziwei_engine.calendar.lunar_converter import LunarConverter
from app.ziwei_engine.transformation.four_hua import FourHuaCalculator

MAIN_14 = (
    "紫微", "天机", "太阳", "武曲", "天同", "廉贞",
    "天府", "太阴", "贪狼", "巨门", "天相", "天梁", "七杀", "破军",
)


@dataclass
class ClassicalAuditReport:
    input: dict[str, Any] = field(default_factory=dict)
    calendar_result: dict[str, Any] = field(default_factory=dict)
    lunar_date: str = ""
    ganzhi: dict[str, str] = field(default_factory=dict)
    shichen: dict[str, Any] = field(default_factory=dict)
    minggong: str = ""
    shengong: str = ""
    wuxingju: str = ""
    minggong_ganzhi: str = ""
    mingzhu: str = ""
    shenzhu: str = ""
    ziwei_position: str = ""
    tianfu_position: str = ""
    fourteen_star_positions: dict[str, str] = field(default_factory=dict)
    fourteen_star_palaces: dict[str, str] = field(default_factory=dict)
    palaces_main_stars: dict[str, list[str]] = field(default_factory=dict)
    four_transform: dict[str, Any] = field(default_factory=dict)
    formula_notes: dict[str, str] = field(default_factory=dict)
    trace: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _parse_dt(birth_date: str, birth_time: str) -> datetime:
    hour, minute = birth_time.split(":")[:2]
    y, m, d = birth_date.split("-")
    return datetime(int(y), int(m), int(d), int(hour), int(minute))


def run_classical_audit(
    *,
    birth_date: str,
    birth_time: str,
    gender: str = "male",
    calendar_type: str = "solar",
    location: str | None = None,
    is_leap_month: bool = False,
) -> ClassicalAuditReport:
    """跑完整核心排盘链路并返回可追溯审计报告。"""
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

    zw_idx = calc_ziwei_branch_index(cal.lunar_day, bureau.bureau_number)
    zw_branch = EARTHLY_BRANCHES[zw_idx]
    tf_branch = EARTHLY_BRANCHES[calc_tianfu_branch_index(zw_idx)]

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
    fourteen_branches = {n: placement.star_branches.get(n, "") for n in MAIN_14}
    fourteen_palaces = {n: star_to_palace.get(n, "") for n in MAIN_14}

    by_palace: dict[str, list[str]] = {p.name: [] for p in palaces}
    for name in MAIN_14:
        pal = fourteen_palaces.get(name)
        if pal:
            by_palace.setdefault(pal, []).append(name)

    four = FourHuaCalculator.calculate(cal.year_stem, star_to_palace)

    month_palace = PalaceEngine.calc_month_palace_branch(cal.lunar_month)
    report = ClassicalAuditReport(
        input={
            "birth_date": birth_date,
            "birth_time": birth_time,
            "gender": gender,
            "calendar_type": calendar_type,
            "location": location,
            "solar_date_used": solar_date,
            "true_solar": true_dt.isoformat(),
            "longitude": longitude,
        },
        calendar_result={
            "lunar_year": cal.lunar_year,
            "lunar_month": cal.lunar_month,
            "lunar_day": cal.lunar_day,
            "is_leap_month": cal.is_leap_month,
            "is_before_li_chun": cal.is_before_li_chun,
            "jie_qi": cal.jie_qi,
            "used_true_solar": cal.used_true_solar,
        },
        lunar_date=lunar.lunar_text if hasattr(lunar, "lunar_text") else f"{cal.lunar_year}-{cal.lunar_month}-{cal.lunar_day}",
        ganzhi={
            "year": cal.year_ganzhi,
            "month": cal.month_ganzhi,
            "day": cal.day_ganzhi,
            "hour": cal.hour_ganzhi,
        },
        shichen={
            "name": cal.shichen_name,
            "index": cal.shichen_index,
            "branch": EARTHLY_BRANCHES[cal.shichen_index],
        },
        minggong=ming.branch,
        shengong=shen.branch,
        wuxingju=bureau.bureau_name,
        minggong_ganzhi=ming.ganzhi or bureau.ming_gong_ganzhi,
        mingzhu=MING_ZHU_BY_BRANCH.get(ming.branch, ""),
        shenzhu=SHEN_ZHU_BY_YEAR_BRANCH.get(cal.year_branch, ""),
        ziwei_position=zw_branch,
        tianfu_position=tf_branch,
        fourteen_star_positions=fourteen_branches,
        fourteen_star_palaces=fourteen_palaces,
        palaces_main_stars={k: v for k, v in by_palace.items() if v},
        four_transform={
            "yearStem": cal.year_stem,
            "lu": four.hua_lu,
            "quan": four.hua_quan,
            "ke": four.hua_ke,
            "ji": four.hua_ji,
        },
        formula_notes={
            "minggong": (
                f"寅起正月: month_palace=(2+{cal.lunar_month}-1)%12={month_palace}"
                f"({EARTHLY_BRANCHES[month_palace]}); "
                f"命宫=(month-shichen+12)%12=({month_palace}-{cal.shichen_index}+12)%12"
                f"={ming_idx}({ming.branch})"
            ),
            "shengong": (
                f"身宫=(month+shichen)%12=({month_palace}+{cal.shichen_index})%12"
                f"={shen_idx}({shen.branch})"
            ),
            "bureau": f"命宫干支={bureau.ming_gong_ganzhi} 纳音={bureau.nayin} → {bureau.bureau_name}",
            "ziwei": f"calc_ziwei_branch_index(day={cal.lunar_day}, bureau={bureau.bureau_number}) → {zw_branch}",
            "tianfu": f"calc_tianfu_branch_index(ziwei={zw_idx}) mirror → {tf_branch}",
        },
        trace=[
            {"step": "calendar", "output": {"lunar_day": cal.lunar_day, "shichen": cal.shichen_name}},
            {"step": "palace", "output": {"ming": ming.branch, "shen": shen.branch}},
            {"step": "bureau", "output": {"ju": bureau.bureau_name, "n": bureau.bureau_number}},
            {"step": "ziwei", "output": {"branch": zw_branch, "tianfu": tf_branch}},
            {"step": "stars", "output": {"count": sum(1 for v in fourteen_branches.values() if v)}},
            {"step": "four_transform", "output": {"stem": cal.year_stem}},
        ],
    )
    return report


def compare_to_reference(
    audit: ClassicalAuditReport,
    reference: dict[str, Any],
) -> dict[str, Any]:
    """当前引擎 vs reference_data 差异报告。"""
    ref_meta = reference.get("meta") or reference.get("expected") or {}
    ref_birth = reference.get("birth") or {}
    diffs: list[dict[str, Any]] = []

    def _check(field: str, actual: Any, expected: Any) -> None:
        if expected in (None, "", [], {}):
            return
        if actual != expected:
            diffs.append({"field": field, "actual": actual, "expected": expected})

    _check("ganzhi.year", audit.ganzhi.get("year"), (ref_birth.get("ganzhi") or {}).get("year") or ref_meta.get("ganzhi", {}).get("year") if isinstance(ref_meta.get("ganzhi"), dict) else None)
    # meta fields (support both classical fixture and REF-01 shape)
    _check("minggong", audit.minggong, ref_meta.get("minggong") or ref_meta.get("mingGong"))
    _check("shengong", audit.shengong, ref_meta.get("shengong") or ref_meta.get("shenGong"))
    _check("wuxingju", audit.wuxingju, ref_meta.get("wuxingju") or ref_meta.get("wuxingJu"))
    _check("ziwei_position", audit.ziwei_position, ref_meta.get("ziwei_position") or ref_meta.get("ziweiBranch"))

    ref_stars = reference.get("fourteen_stars") or {}
    if not ref_stars and "mainStarsByPalace" in ref_meta:
        # invert palace→stars to star→palace for compare
        for pal, stars in (ref_meta.get("mainStarsByPalace") or {}).items():
            for s in stars:
                ref_stars[s] = pal
        for star, pal in ref_stars.items():
            _check(f"star_palace.{star}", audit.fourteen_star_palaces.get(star), pal)
    else:
        for star, branch in ref_stars.items():
            if isinstance(branch, dict):
                _check(f"star_branch.{star}", audit.fourteen_star_positions.get(star), branch.get("branch"))
                _check(f"star_palace.{star}", audit.fourteen_star_palaces.get(star), branch.get("palace"))
            else:
                # branch string or palace string — prefer branch if in EARTHLY
                if branch in EARTHLY_BRANCHES:
                    _check(f"star_branch.{star}", audit.fourteen_star_positions.get(star), branch)
                else:
                    _check(f"star_palace.{star}", audit.fourteen_star_palaces.get(star), branch)

    ref_ft = reference.get("four_transform") or ref_meta.get("fourTransform") or {}
    if ref_ft:
        for key, label in (("lu", "禄"), ("quan", "权"), ("ke", "科"), ("ji", "忌")):
            exp = ref_ft.get(key) or {}
            act = audit.four_transform.get(key) or {}
            if isinstance(exp, dict) and exp.get("star"):
                _check(f"four_transform.{key}.star", act.get("star"), exp.get("star"))
                if exp.get("palace"):
                    _check(f"four_transform.{key}.palace", act.get("palace"), exp.get("palace"))

    matched = len(diffs) == 0
    return {
        "matched": matched,
        "diff_count": len(diffs),
        "differences": diffs,
        "audit_summary": {
            "minggong": audit.minggong,
            "shengong": audit.shengong,
            "wuxingju": audit.wuxingju,
            "ziwei": audit.ziwei_position,
            "tianfu": audit.tianfu_position,
        },
    }


# 供 formula 文档引用
YIN_BRANCH_INDEX_DOC = 2
