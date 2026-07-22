#!/usr/bin/env python3
"""导出规则种子 SQL — 与 app.ziwei.rules.seed_generator 保持一致。"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))

from app.ziwei.rules.seed_generator import build_all_rules  # noqa: E402

OUT = ROOT / "database" / "rules"
DATA = OUT / "data"


def sql_str(v: str) -> str:
    return "'" + v.replace("'", "''") + "'"


def sql_json(v) -> str:
    return sql_str(json.dumps(v, ensure_ascii=False))


def write_nayin(rules: list[dict]) -> None:
    lines = ["-- nayin_rules 六十甲子纳音", "DELETE FROM public.nayin_rules WHERE school = 'sanhe';", ""]
    for r in rules:
        lines.append(
            "INSERT INTO public.nayin_rules (heavenly_stem, earthly_branch, nayin, element, bureau_number, school, version) "
            f"VALUES ({sql_str(r['heavenly_stem'])}, {sql_str(r['earthly_branch'])}, {sql_str(r['nayin'])}, "
            f"{sql_str(r['element'])}, {r['bureau_number']}, 'sanhe', '2026.07.22');"
        )
    (OUT / "nayin_rules.sql").write_text("\n".join(lines), encoding="utf-8")


def write_four_transform(rules: list[dict]) -> None:
    lines = ["-- four_transform_rules 十天干四化", "DELETE FROM public.four_transform_rules WHERE school = 'sanhe';", ""]
    for r in rules:
        lines.append(
            "INSERT INTO public.four_transform_rules (heavenly_stem, lu_star, quan_star, ke_star, ji_star, school, version) "
            f"VALUES ({sql_str(r['heavenly_stem'])}, {sql_str(r['lu'])}, {sql_str(r['quan'])}, "
            f"{sql_str(r['ke'])}, {sql_str(r['ji'])}, 'sanhe', '2026.07.22');"
        )
    (OUT / "four_transform_rules.sql").write_text("\n".join(lines), encoding="utf-8")


def write_daxian(rules: list[dict]) -> None:
    lines = ["-- daxian_rules 大限顺逆", "DELETE FROM public.daxian_rules WHERE school = 'sanhe';", ""]
    for r in rules:
        lines.append(
            "INSERT INTO public.daxian_rules (gender, year_yinyang, direction, start_age_formula, school, version) "
            f"VALUES ({sql_str(r['gender'])}, {sql_str(r['year_yinyang'])}, {sql_str(r['direction'])}, "
            f"'bureau_number', 'sanhe', '2026.07.22');"
        )
    (OUT / "daxian_rules.sql").write_text("\n".join(lines), encoding="utf-8")


def write_ziwei(rules: list[dict]) -> None:
    lines = ["-- ziwei_position_rules 6局×30日", "DELETE FROM public.ziwei_position_rules WHERE school = 'sanhe';", ""]
    for r in rules:
        lines.append(
            "INSERT INTO public.ziwei_position_rules (bureau, lunar_day, ziwei_branch, school, version) "
            f"VALUES ({r['bureau']}, {r['lunar_day']}, {sql_str(r['ziwei_branch'])}, 'sanhe', '2026.07.22');"
        )
    (OUT / "ziwei_position_rules.sql").write_text("\n".join(lines), encoding="utf-8")


def write_brightness(rules: list[dict]) -> None:
    lines = ["-- brightness_rules 十四主星亮度", "DELETE FROM public.brightness_rules WHERE school = 'sanhe';", ""]
    for r in rules:
        lines.append(
            "INSERT INTO public.brightness_rules (star_name, branch, brightness, school, version) "
            f"VALUES ({sql_str(r['star_name'])}, {sql_str(r['branch'])}, {sql_str(r['brightness'])}, 'sanhe', '2026.07.22');"
        )
    (OUT / "brightness_rules.sql").write_text("\n".join(lines), encoding="utf-8")


def write_star_placement(rules: list[dict]) -> None:
    lines = ["-- star_placement_rules 安星规则", "DELETE FROM public.star_placement_rules WHERE school = 'sanhe';", ""]
    for r in rules:
        lines.append(
            "INSERT INTO public.star_placement_rules (rule_type, star_name, base_star, direction, offset, condition, school, version) "
            f"VALUES ({sql_str(r['rule_type'])}, {sql_str(r['star_name'])}, {sql_str(r['base_star'])}, "
            f"{sql_str(r['direction'])}, {r['offset']}, {sql_json(r['condition'])}, 'sanhe', '2026.07.22');"
        )
    (OUT / "star_placement_rules.sql").write_text("\n".join(lines), encoding="utf-8")


def write_stars(rules: list[dict]) -> None:
    lines = ["-- stars 星曜元数据", "DELETE FROM public.stars WHERE school = 'sanhe';", ""]
    for r in rules:
        lines.append(
            "INSERT INTO public.stars (name, element, yin_yang, category, keywords, personality_tags, "
            "career_tags, wealth_tags, relationship_tags, description, ai_prompt, school, is_active) "
            f"VALUES ({sql_str(r['name'])}, {sql_str(r['element'])}, {sql_str(r['yin_yang'])}, "
            f"{sql_str(r['category'])}, {sql_json(r['keywords'])}, {sql_json(r['personality_tags'])}, "
            f"{sql_json(r['career_tags'])}, {sql_json(r['wealth_tags'])}, {sql_json(r['relationship_tags'])}, "
            f"{sql_str(r['description'])}, {sql_str(r['ai_prompt'])}, 'sanhe', true);"
        )
    (OUT / "stars.sql").write_text("\n".join(lines), encoding="utf-8")


def write_combinations(rules: list[dict]) -> None:
    lines = ["-- star_combination_rules", "DELETE FROM public.star_combination_rules WHERE school = 'sanhe';", ""]
    for r in rules:
        lines.append(
            "INSERT INTO public.star_combination_rules (combination_name, stars, category, personality, career, wealth, relationship, ai_prompt, school, version) "
            f"VALUES ({sql_str(r['combination_name'])}, {sql_json(r['stars'])}, {sql_str(r['category'])}, "
            f"{sql_str(r['personality'])}, {sql_str(r['career'])}, {sql_str(r['wealth'])}, "
            f"{sql_str(r['relationship'])}, {sql_str(r['ai_prompt'])}, 'sanhe', '2026.07.22');"
        )
    (OUT / "star_combination_rules.sql").write_text("\n".join(lines), encoding="utf-8")


def write_palace_meanings(rules: list[dict]) -> None:
    lines = ["-- palace_meaning_rules", "DELETE FROM public.palace_meaning_rules WHERE school = 'sanhe';", ""]
    for r in rules:
        lines.append(
            "INSERT INTO public.palace_meaning_rules (palace_name, keyword, meaning, career, wealth, relationship, health, ai_prompt, school, version) "
            f"VALUES ({sql_str(r['palace_name'])}, {sql_str(r['keyword'])}, {sql_str(r['meaning'])}, "
            f"{sql_str(r['career'])}, {sql_str(r['wealth'])}, {sql_str(r['relationship'])}, "
            f"{sql_str(r['health'])}, {sql_str(r['ai_prompt'])}, 'sanhe', '2026.07.22');"
        )
    (OUT / "palace_meaning_rules.sql").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    rules = build_all_rules()
    DATA.joinpath("rules_cache.json").write_text(
        json.dumps(rules, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    write_nayin(rules["nayin_rules"])
    write_four_transform(rules["four_transform_rules"])
    write_daxian(rules["daxian_rules"])
    write_ziwei(rules["ziwei_position_rules"])
    write_brightness(rules["brightness_rules"])
    write_star_placement(rules["star_placement_rules"])
    write_stars(rules["stars"])
    write_combinations(rules["star_combination_rules"])
    write_palace_meanings(rules["palace_meaning_rules"])
    print(f"Exported rules to {OUT}")


if __name__ == "__main__":
    main()
