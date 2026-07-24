"""Classical Rule Engine — 带 classical_trace 的规则驱动排盘。"""

from __future__ import annotations

from typing import Any

from app.ziwei.constants import EARTHLY_BRANCHES
from app.ziwei_classical.bureau.five_element import calc_five_element_bureau
from app.ziwei_classical.calendar.lunar import convert_calendar
from app.ziwei_classical.config_loader import config_to_engine_config, load_classical_config
from app.ziwei_classical.engine import ClassicalEngine, ClassicalEngineConfig, ClassicalChart
from app.ziwei_classical.palace.twelve_palace import build_twelve_palaces
from app.ziwei_classical.rules.loader import (
    assert_has_source,
    get_fourteen_rules,
    get_tianfu_config,
    get_ziwei_table,
)
from app.ziwei_classical.rules.palace.ming_gong_rule import apply_ming_gong_rule
from app.ziwei_classical.rules.palace.shen_gong_rule import apply_shen_gong_rule
from app.ziwei_classical.rules.rule_conflict_detector import detect_rule_conflicts
from app.ziwei_classical.stars.fourteen_stars import place_fourteen_stars
from app.ziwei_classical.stars.lucky_stars import place_lucky_stars
from app.ziwei_classical.stars.evil_stars import place_evil_stars
from app.ziwei_classical.stars.minor_stars import place_minor_stars
from app.ziwei_classical.transformations.birth_four_hua import birth_four_hua
from app.ziwei_classical.validator.classical_trace import ClassicalTrace
from app.ziwei_classical.validator.rule_trace import RuleTrace


def lookup_ziwei_from_rules_table(bureau_number: int, lunar_day: int) -> tuple[str, str]:
    """查 rules/stars/ziwei_position_table.json，返回 (branch, rule_id)。"""
    table = get_ziwei_table()
    assert_has_source({"id": "ZIWEI_TABLE", "source": table.get("source")})
    for entry in table.get("entries") or []:
        if entry["bureau_number"] == bureau_number and entry["day"] == lunar_day:
            return entry["ziwei"], entry["id"]
    # fallback by bureau name map
    names = {2: "水二局", 3: "木三局", 4: "金四局", 5: "土五局", 6: "火六局"}
    br = table["bureaus"][names[bureau_number]]["days"][str(lunar_day)]
    return br, f"ZIWEI_TABLE_BUREAU_{bureau_number}_DAY_{lunar_day}"


def resolve_tianfu_option(tianfu_rule: str) -> dict[str, Any]:
    cfg = get_tianfu_config()
    options = cfg.get("options") or {}
    key = tianfu_rule
    alias_map = {
        "traditional": "yanshen_mirror",
        "yin_shen_mirror": "yanshen_mirror",
        "yanshen_mirror": "yanshen_mirror",
        "mirror": "yanshen_mirror",  # 本引擎 mirror=寅申；对宫用 opposite
        "opposite": "opposite",
        "dui_gong": "opposite",
    }
    opt_key = alias_map.get(key, key)
    if opt_key not in options:
        raise ValueError(f"tianfu_rule 未在配置中: {tianfu_rule}（冲突项须显式选择）")
    return options[opt_key]


class ClassicalRuleEngine:
    """16册规则校准引擎：强制来源 + classical_trace。"""

    def __init__(self, config: ClassicalEngineConfig | None = None) -> None:
        self.config = config or config_to_engine_config(load_classical_config())
        self.conflicts = detect_rule_conflicts()

    def compute(
        self,
        *,
        birth_date: str,
        birth_time: str,
        gender: str = "male",
        calendar_type: str = "solar",
        location: str | None = None,
        is_leap_month: bool = False,
    ) -> dict[str, Any]:
        ctr = ClassicalTrace()
        # calendar
        cal = convert_calendar(
            birth_date=birth_date,
            birth_time=birth_time,
            calendar_type=calendar_type,
            location=location,
            is_leap_month=is_leap_month,
            trace=None,
        )
        ctr.add(
            step="calendar",
            rule_id="CAL_LUNAR_001",
            source=["万年历/节气体系", "紫微斗数全书"],
            inputs={"birth_date": birth_date, "birth_time": birth_time, "location": location},
            result={
                "lunar": f"{cal.lunar_year}-{cal.lunar_month}-{cal.lunar_day}",
                "year_ganzhi": cal.year_ganzhi,
                "month_ganzhi": cal.month_ganzhi,
                "day_ganzhi": cal.day_ganzhi,
                "hour_ganzhi": cal.hour_ganzhi,
            },
            formula="公历→农历；节气月令；四柱",
        )

        ming = apply_ming_gong_rule(
            cal.lunar_month, cal.shichen_index, cal.year_stem, trace=ctr
        )
        shen = apply_shen_gong_rule(cal.lunar_month, cal.shichen_index, trace=ctr)

        bureau = calc_five_element_bureau(cal.year_stem, ming["branch_index"], trace=None)
        ctr.add(
            step="five_element",
            rule_id="BUREAU_NAYIN_001",
            source=["紫微斗数全书", "三合派安星诀"],
            inputs={"year_stem": cal.year_stem, "ming_branch": ming["branch"]},
            result=bureau.get("bureau_name"),
            formula="命宫干支纳音→五行局",
        )

        zw_branch, zw_rule_id = lookup_ziwei_from_rules_table(
            bureau["bureau_number"], cal.lunar_day
        )
        ctr.add(
            step="ziwei_position",
            rule_id=zw_rule_id,
            source=["紫微斗数全书", "星曜秘诀", "三合派安星诀"],
            inputs={"bureau": bureau["bureau_name"], "day": cal.lunar_day},
            result=zw_branch,
            formula="紫微五局传统表查表（禁止运行时推算替代）",
        )

        tf_opt = resolve_tianfu_option(self.config.tianfu_rule)
        # place fourteen using existing module but with config
        fourteen = place_fourteen_stars(
            bureau["bureau_number"],
            cal.lunar_day,
            tianfu_rule=self.config.tianfu_rule,
            trace=None,
        )
        # verify table branch matches
        if fourteen["ziwei"]["branch"] != zw_branch:
            raise RuntimeError(
                f"紫微表不一致: rules表={zw_branch} engine={fourteen['ziwei']['branch']}"
            )
        ctr.add(
            step="tianfu_position",
            rule_id=tf_opt["id"],
            source=get_tianfu_config().get("source") or [],
            inputs={"ziwei": zw_branch, "tianfu_rule": self.config.tianfu_rule},
            result=fourteen["tianfu"]["branch"],
            formula=tf_opt.get("formula") or "",
        )

        fr = get_fourteen_rules()
        for series_key in ("ziwei_series", "tianfu_series"):
            for row in fr.get(series_key) or []:
                star = row["star"]
                ctr.add(
                    step=f"star.{star}",
                    rule_id=row.get("rule_id") or star,
                    source=fr.get("source") or [],
                    inputs={"base": row.get("base"), "direction": row.get("direction"), "offset": row.get("offset")},
                    result=fourteen["branches"].get(star),
                    formula=row.get("formula") or "",
                )

        palaces = build_twelve_palaces(
            ming["branch_index"], shen["branch_index"], cal.year_stem, trace=None
        )
        branch_to_palace = {p["branch"]: p["name"] for p in palaces}
        by_palace: dict[str, list[str]] = {p["name"]: [] for p in palaces}
        for star, br in fourteen["branches"].items():
            pn = branch_to_palace.get(br)
            if pn:
                by_palace[pn].append(star)
        for p in palaces:
            p["main_stars"] = sorted(by_palace.get(p["name"], []))

        lucky = place_lucky_stars(
            lunar_month=cal.lunar_month,
            hour_index=cal.shichen_index,
            year_stem=cal.year_stem,
            year_branch=cal.year_branch,
            trace=None,
        )
        evil = place_evil_stars(
            hour_index=cal.shichen_index,
            year_branch=cal.year_branch,
            lu_cun_branch=(lucky.get("禄存") or {}).get("branch", ""),
            trace=None,
        )
        minor = place_minor_stars(
            lunar_month=cal.lunar_month,
            hour_index=cal.shichen_index,
            year_stem=cal.year_stem,
            year_branch=cal.year_branch,
            ming_branch=ming["branch"],
            trace=None,
        )
        for name, info in lucky.items():
            ctr.add(
                step=f"aux.{name}",
                rule_id=f"AUX_{name}",
                source=["紫微斗数全书", "星曜秘诀"],
                inputs={"tier": info.get("tier")},
                result=info.get("branch"),
                formula=info.get("rule") or "",
            )

        star_to_palace = {
            s: branch_to_palace[br]
            for s, br in fourteen["branches"].items()
            if br in branch_to_palace
        }
        for name, info in lucky.items():
            br = info.get("branch")
            if br in branch_to_palace:
                star_to_palace[name] = branch_to_palace[br]
        birth_tf = birth_four_hua(cal.year_stem, star_to_palace, trace=None)
        ctr.add(
            step="birth_four_hua",
            rule_id="HUA_BIRTH_001",
            source=["钦天四化", "紫微斗数全书"],
            inputs={"year_stem": cal.year_stem},
            result={
                "lu": (birth_tf.get("lu") or {}).get("star"),
                "quan": (birth_tf.get("quan") or {}).get("star"),
                "ke": (birth_tf.get("ke") or {}).get("star"),
                "ji": (birth_tf.get("ji") or {}).get("star"),
            },
            formula="年干查禄权科忌",
        )

        return {
            "engine": "classical_rule_engine_v1.6",
            "birth": {
                "solar_date": birth_date,
                "time": birth_time,
                "gender": gender,
                "location": location,
            },
            "calendar": cal.to_dict(),
            "ming_gong": ming,
            "shen_gong": shen,
            "bureau": bureau,
            "ziwei": {"branch": zw_branch, "rule_id": zw_rule_id},
            "tianfu": fourteen["tianfu"],
            "fourteen_stars": fourteen["branches"],
            "fourteen_by_palace": {k: v for k, v in by_palace.items() if v},
            "palaces": palaces,
            "lucky_stars": lucky,
            "evil_stars": evil,
            "minor_stars": minor,
            "transformations": {"birth": birth_tf},
            "classical_trace": ctr.to_list(),
            "rule_conflicts": self.conflicts,
            "config": {
                "tianfu_rule": self.config.tianfu_rule,
                "school": load_classical_config().get("school"),
            },
        }
