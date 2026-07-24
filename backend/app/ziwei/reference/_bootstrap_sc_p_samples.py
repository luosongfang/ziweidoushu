"""Bootstrap SC-P001~P050 professional reference slots (V1.6)."""

from __future__ import annotations

import json
from pathlib import Path

from app.ziwei.reference.importer import ReferenceImporter
from app.ziwei.reference.metadata import empty_palaces

# Diversity design: 25M/25F, 5 bureaus×hours×stems coverage via birth slots
# Only P001 is verified_professional (from SC-C01); rest pending.

STEM_YEARS = [
    ("甲", "1984-03-15"),  # 甲子附近用具体日
    ("乙", "1985-06-20"),
    ("丙", "1986-09-08"),
    ("丁", "1987-01-12"),
    ("戊", "1988-04-04"),
    ("己", "1989-07-18"),
    ("庚", "1990-05-15"),  # P001
    ("辛", "1991-11-03"),
    ("壬", "1992-02-22"),
    ("癸", "1993-08-09"),
]

HOURS = [
    "00:30", "02:00", "04:00", "06:15", "08:00", "10:00",
    "12:00", "14:00", "14:30", "16:00", "18:45", "20:00", "22:50",
]

LOCATIONS = ["北京", "上海", "深圳", "广州", "杭州", "成都", "武汉", None]


def build_p001() -> dict:
    palaces = empty_palaces()
    mapping = {
        "命宫": [],
        "兄弟": ["廉贞", "破军"],
        "夫妻": [],
        "子女": [],
        "财帛": [],
        "疾厄": ["紫微", "七杀"],
        "迁移": ["天机", "天梁"],
        "交友": ["天相"],
        "官禄": ["太阳", "巨门"],
        "田宅": ["武曲", "贪狼"],
        "福德": ["天同", "太阴"],
        "父母": ["天府"],
    }
    for k, v in mapping.items():
        palaces[k]["main_stars"] = v
    return {
        "id": "SC-P001",
        "source": "wenmo",
        "verification_level": "verified_professional",
        "verified_by": "mapped from SC-C01 / REF-01 cross-check (pending fresh wenmo screenshot)",
        "birth": {
            "date": "1990-05-15",
            "time": "14:30",
            "gender": "male",
            "location": "深圳",
            "true_solar_time": True,
        },
        "settings": {
            "calendar": "solar",
            "school": "sanhe",
            "tianfu_rule": "traditional",
        },
        "chart_reference": {
            "ming_gong": "戌",
            "shen_gong": "子",
            "wuxing": "土五局",
            "ziwei": "巳",
            "tianfu": "亥",
            "palaces": palaces,
        },
        "coverage_tags": {
            "gender": "male",
            "bureau": "earth5",
            "hour": "wei",
            "year_stem": "庚",
        },
    }


def main() -> None:
    imp = ReferenceImporter()
    imp.save(build_p001())

    # 49 pending slots with planned coverage
    idx = 2
    genders = ["male"] * 24 + ["female"] * 25  # +P001 male = 25/25
    for i, gender in enumerate(genders):
        sid = f"SC-P{idx:03d}"
        stem_label, date = STEM_YEARS[i % len(STEM_YEARS)]
        time = HOURS[i % len(HOURS)]
        loc = LOCATIONS[i % len(LOCATIONS)]
        # stagger years for uniqueness
        y, m, d = date.split("-")
        date2 = f"{int(y) + (i // 10)}-{m}-{d}"
        sample = {
            "id": sid,
            "source": "wenmo",
            "verification_level": "pending",
            "birth": {
                "date": date2,
                "time": time,
                "gender": gender,
                "location": loc,
                "true_solar_time": True,
            },
            "settings": {
                "calendar": "solar",
                "school": "sanhe",
                "tianfu_rule": "traditional",
            },
            "chart_reference": {
                "ming_gong": "",
                "shen_gong": "",
                "wuxing": "",
                "ziwei": "",
                "tianfu": "",
                "palaces": empty_palaces(),
            },
            "coverage_tags": {
                "gender": gender,
                "planned_year_stem": stem_label,
                "hour_slot": time,
            },
            "notes": "pending wenmo — 填满 chart_reference 后升 verified_professional",
        }
        imp.save(sample)
        idx += 1

    # rewrite index summary
    cases = imp.list_samples()
    males = sum(1 for s in cases if (s.get("birth") or {}).get("gender") == "male")
    females = sum(1 for s in cases if (s.get("birth") or {}).get("gender") == "female")
    summary = {
        "version": "1.6",
        "total": len(cases),
        "male": males,
        "female": females,
        "verified_professional": sum(
            1 for s in cases if s.get("verification_level") == "verified_professional"
        ),
        "pending": sum(1 for s in cases if s.get("verification_level") == "pending"),
    }
    path = Path(imp.samples_dir) / "coverage_summary.json"
    path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(summary)


if __name__ == "__main__":
    main()
