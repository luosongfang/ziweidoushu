"""ClassicalEngine — 传统排盘计算链编排。"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

from app.ziwei_classical.bureau.five_element import calc_five_element_bureau
from app.ziwei_classical.calendar.lunar import convert_calendar
from app.ziwei_classical.fortune.daxian import calc_daxian
from app.ziwei_classical.fortune.liunian import calc_liunian
from app.ziwei_classical.fortune.xiaoxian import calc_xiaoxian
from app.ziwei_classical.palace.ming_gong import calc_ming_gong
from app.ziwei_classical.palace.shen_gong import calc_shen_gong
from app.ziwei_classical.palace.twelve_palace import build_twelve_palaces
from app.ziwei_classical.stars.evil_stars import place_evil_stars
from app.ziwei_classical.stars.fourteen_stars import MAIN_14, place_fourteen_stars
from app.ziwei_classical.stars.lucky_stars import place_lucky_stars
from app.ziwei_classical.stars.minor_stars import place_minor_stars
from app.ziwei_classical.transformations.birth_four_hua import birth_four_hua
from app.ziwei_classical.transformations.decade_four_hua import decade_four_hua
from app.ziwei_classical.transformations.self_transform import self_transform
from app.ziwei_classical.transformations.year_four_hua import year_four_hua
from app.ziwei_classical.validator.rule_trace import RuleTrace

TianfuRule = Literal["traditional", "yin_shen_mirror", "opposite"]


@dataclass
class ClassicalEngineConfig:
    tianfu_rule: TianfuRule = "traditional"
    include_aux: bool = True
    include_minor: bool = True
    include_fortune_skeleton: bool = True


@dataclass
class ClassicalChart:
    birth: dict[str, Any]
    calendar: dict[str, Any]
    ming_gong: dict[str, Any]
    shen_gong: dict[str, Any]
    bureau: dict[str, Any]
    ziwei: dict[str, Any]
    tianfu: dict[str, Any]
    fourteen_stars: dict[str, str]
    fourteen_by_palace: dict[str, list[str]]
    palaces: list[dict[str, Any]]
    lucky_stars: dict[str, dict] = field(default_factory=dict)
    evil_stars: dict[str, dict] = field(default_factory=dict)
    minor_stars: dict[str, dict] = field(default_factory=dict)
    transformations: dict[str, Any] = field(default_factory=dict)
    fortune: dict[str, Any] = field(default_factory=dict)
    trace: list[dict[str, Any]] = field(default_factory=list)
    config: dict[str, Any] = field(default_factory=dict)
    engine: str = "classical_v1.0"

    def to_dict(self) -> dict[str, Any]:
        return {
            "engine": self.engine,
            "config": self.config,
            "birth": self.birth,
            "calendar": self.calendar,
            "ming_gong": self.ming_gong,
            "shen_gong": self.shen_gong,
            "bureau": self.bureau,
            "ziwei": self.ziwei,
            "tianfu": self.tianfu,
            "fourteen_stars": self.fourteen_stars,
            "fourteen_by_palace": self.fourteen_by_palace,
            "palaces": self.palaces,
            "lucky_stars": self.lucky_stars,
            "evil_stars": self.evil_stars,
            "minor_stars": self.minor_stars,
            "transformations": self.transformations,
            "fortune": self.fortune,
            "trace": self.trace,
        }


class ClassicalEngine:
    """严格顺序：历法 → 命身宫 → 五行局 → 紫微表 → 天府 → 十四主星 → 辅煞杂 → 四化。"""

    def __init__(self, config: ClassicalEngineConfig | None = None) -> None:
        self.config = config or ClassicalEngineConfig()

    def compute(
        self,
        *,
        birth_date: str,
        birth_time: str,
        gender: str = "male",
        calendar_type: str = "solar",
        location: str | None = None,
        is_leap_month: bool = False,
    ) -> ClassicalChart:
        trace = RuleTrace()
        cal = convert_calendar(
            birth_date=birth_date,
            birth_time=birth_time,
            calendar_type=calendar_type,
            location=location,
            is_leap_month=is_leap_month,
            trace=trace,
        )
        ming = calc_ming_gong(
            cal.lunar_month, cal.shichen_index, cal.year_stem, trace=trace
        )
        shen = calc_shen_gong(cal.lunar_month, cal.shichen_index, trace=trace)
        bureau = calc_five_element_bureau(
            cal.year_stem, ming["branch_index"], trace=trace
        )
        fourteen = place_fourteen_stars(
            bureau["bureau_number"],
            cal.lunar_day,
            tianfu_rule=self.config.tianfu_rule,
            trace=trace,
        )
        palaces = build_twelve_palaces(
            ming["branch_index"], shen["branch_index"], cal.year_stem, trace=trace
        )
        branch_to_palace = {p["branch"]: p["name"] for p in palaces}
        by_palace: dict[str, list[str]] = {p["name"]: [] for p in palaces}
        for star, br in fourteen["branches"].items():
            pname = branch_to_palace.get(br)
            if pname:
                by_palace[pname].append(star)
        for p in palaces:
            p["main_stars"] = sorted(by_palace.get(p["name"], []))

        lucky: dict[str, dict] = {}
        evil: dict[str, dict] = {}
        minor: dict[str, dict] = {}
        if self.config.include_aux:
            lucky = place_lucky_stars(
                lunar_month=cal.lunar_month,
                hour_index=cal.shichen_index,
                year_stem=cal.year_stem,
                year_branch=cal.year_branch,
                trace=trace,
            )
            lu = (lucky.get("禄存") or {}).get("branch", "")
            evil = place_evil_stars(
                hour_index=cal.shichen_index,
                year_branch=cal.year_branch,
                lu_cun_branch=lu,
                trace=trace,
            )
            for bucket, stars in (("lucky_stars", lucky), ("evil_stars", evil)):
                for name, info in stars.items():
                    br = info.get("branch")
                    if not br:
                        continue
                    pname = branch_to_palace.get(br)
                    if not pname:
                        continue
                    for p in palaces:
                        if p["name"] == pname:
                            p[bucket].append(name)

        if self.config.include_minor:
            minor = place_minor_stars(
                lunar_month=cal.lunar_month,
                hour_index=cal.shichen_index,
                year_stem=cal.year_stem,
                year_branch=cal.year_branch,
                ming_branch=ming["branch"],
                trace=trace,
            )
            for name, info in minor.items():
                br = info.get("branch")
                pname = branch_to_palace.get(br or "")
                if not pname:
                    continue
                for p in palaces:
                    if p["name"] == pname:
                        p["minor_stars"].append(name)

        star_to_palace = {
            s: branch_to_palace[br]
            for s, br in fourteen["branches"].items()
            if br in branch_to_palace
        }
        # 辅星也加入四化目标（文昌等）
        for name, info in {**lucky}.items():
            br = info.get("branch")
            if br in branch_to_palace:
                star_to_palace[name] = branch_to_palace[br]

        birth_tf = birth_four_hua(cal.year_stem, star_to_palace, trace=trace)
        transforms = {
            "birth": birth_tf,
            "decade": decade_four_hua(trace=trace),
            "year": year_four_hua(trace=trace),
            "self": self_transform(trace=trace),
        }

        fortune: dict[str, Any] = {}
        if self.config.include_fortune_skeleton:
            fortune = {
                "daxian": calc_daxian(
                    gender=gender,
                    year_branch=cal.year_branch,
                    bureau_number=bureau["bureau_number"],
                    ming_branch=ming["branch"],
                    trace=trace,
                ),
                "xiaoxian": calc_xiaoxian(trace=trace),
                "liunian": calc_liunian(trace=trace),
            }

        return ClassicalChart(
            birth={
                "solar_date": birth_date,
                "time": birth_time,
                "gender": gender,
                "location": location,
                "calendar_type": calendar_type,
            },
            calendar=cal.to_dict(),
            ming_gong=ming,
            shen_gong=shen,
            bureau=bureau,
            ziwei=fourteen["ziwei"],
            tianfu=fourteen["tianfu"],
            fourteen_stars=fourteen["branches"],
            fourteen_by_palace={k: v for k, v in by_palace.items() if v},
            palaces=palaces,
            lucky_stars=lucky,
            evil_stars=evil,
            minor_stars=minor,
            transformations=transforms,
            fortune=fortune,
            trace=trace.to_list(),
            config={
                "tianfu_rule": self.config.tianfu_rule,
                "include_aux": self.config.include_aux,
                "include_minor": self.config.include_minor,
            },
        )


# 供测试引用
__all__ = ["ClassicalEngine", "ClassicalEngineConfig", "ClassicalChart", "MAIN_14"]
