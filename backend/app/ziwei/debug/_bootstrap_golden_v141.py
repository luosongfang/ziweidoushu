"""Bootstrap Golden Dataset V1.4.1 under debug/classical_reference_charts."""

from __future__ import annotations

import json
from pathlib import Path

from app.ziwei.constants import EARTHLY_BRANCHES
from app.ziwei.debug.classical_audit import run_classical_audit

OUT = Path(__file__).resolve().parent / "classical_reference_charts"
PALACE_ORDER = [
    "命宫", "兄弟", "夫妻", "子女", "财帛", "疾厄",
    "迁移", "交友", "官禄", "田宅", "福德", "父母",
]

BIRTHS = [
    ("SC-C02", "1982-02-22", "14:00", "male", "北京", False),
    ("SC-C03", "1988-11-08", "09:20", "male", "上海", True),
    ("SC-C04", "1975-03-12", "23:40", "female", "北京", False),
    ("SC-C05", "2000-01-01", "00:30", "male", None, False),
    ("SC-C06", "1995-07-20", "16:00", "female", "上海", True),
    ("SC-C07", "1968-09-09", "06:15", "male", "广州", False),
    ("SC-C08", "1985-12-25", "12:00", "female", "广州", True),
    ("SC-C09", "1992-04-04", "03:00", "male", "成都", False),
    ("SC-C10", "1979-08-18", "18:45", "female", "杭州", True),
    ("SC-C11", "1998-06-01", "08:00", "female", "深圳", False),
    ("SC-C12", "1960-01-15", "11:30", "male", "西安", False),
    ("SC-C13", "2005-10-10", "21:00", "female", "武汉", True),
    ("SC-C14", "1972-05-05", "05:00", "male", "南京", False),
    ("SC-C15", "1991-09-30", "19:20", "female", "天津", False),
    ("SC-C16", "1980-03-08", "01:10", "male", "重庆", True),
    ("SC-C17", "1993-12-12", "22:50", "female", "苏州", False),
    ("SC-C18", "1965-07-07", "07:40", "male", "厦门", False),
    ("SC-C19", "2001-02-14", "15:15", "female", "青岛", True),
    ("SC-C20", "1977-11-11", "04:30", "male", "长沙", False),
]


def build_pending(cid: str, solar: str, time: str, gender: str, loc, tst: bool) -> dict:
    audit = run_classical_audit(
        birth_date=solar, birth_time=time, gender=gender, location=loc
    )
    branch_to_main: dict[str, list[str]] = {}
    for star, br in audit.fourteen_star_positions.items():
        branch_to_main.setdefault(br, []).append(star)

    ming_idx = EARTHLY_BRANCHES.index(audit.minggong)
    palaces = []
    for i, name in enumerate(PALACE_ORDER):
        br = EARTHLY_BRANCHES[(ming_idx - i) % 12]
        palaces.append(
            {
                "name": name,
                "branch": br,
                "main_stars": sorted(branch_to_main.get(br, [])),
                "lucky_stars": [],
                "sha_stars": [],
                "za_stars": [],
            }
        )
    ft = audit.four_transform
    return {
        "id": cid,
        "verification_level": "pending",
        "source": {"name": f"birth slot {cid}", "type": "manual"},
        "birth": {
            "solar_date": solar,
            "time": time,
            "gender": gender,
            "location": loc,
            "true_solar_time": tst,
        },
        "expected": {
            "_note": "engine_snapshot_for_coverage_only_not_professional",
            "calendar": {
                "lunar": (
                    f"{audit.calendar_result.get('lunar_year')}-"
                    f"{audit.calendar_result.get('lunar_month')}-"
                    f"{audit.calendar_result.get('lunar_day')}"
                ),
                "ganzhi": dict(audit.ganzhi),
                "shichen": audit.shichen,
            },
            "meta": {
                "ming_gong": audit.minggong,
                "shen_gong": audit.shengong,
                "wuxing_ju": audit.wuxingju,
                "ming_zhu": audit.mingzhu,
                "shen_zhu": audit.shenzhu,
                "ziwei_position": audit.ziwei_position,
                "tianfu_position": audit.tianfu_position,
            },
            "palaces": palaces,
            "four_transform": {
                "lu": (ft.get("lu") or {}).get("star", ""),
                "quan": (ft.get("quan") or {}).get("star", ""),
                "ke": (ft.get("ke") or {}).get("star", ""),
                "ji": (ft.get("ji") or {}).get("star", ""),
            },
            "fortune": {"daxian": "", "liunian": ""},
        },
        "notes": "禁止入测直至 verification_level=verified_professional 且经专业软件确认",
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    c01_palaces = [
        {"name": "命宫", "branch": "戌", "main_stars": [], "lucky_stars": [], "sha_stars": [], "za_stars": []},
        {"name": "兄弟", "branch": "酉", "main_stars": ["廉贞", "破军"], "lucky_stars": [], "sha_stars": [], "za_stars": []},
        {"name": "夫妻", "branch": "申", "main_stars": [], "lucky_stars": [], "sha_stars": [], "za_stars": []},
        {"name": "子女", "branch": "未", "main_stars": [], "lucky_stars": [], "sha_stars": [], "za_stars": []},
        {"name": "财帛", "branch": "午", "main_stars": [], "lucky_stars": [], "sha_stars": [], "za_stars": []},
        {"name": "疾厄", "branch": "巳", "main_stars": ["紫微", "七杀"], "lucky_stars": [], "sha_stars": [], "za_stars": []},
        {"name": "迁移", "branch": "辰", "main_stars": ["天机", "天梁"], "lucky_stars": [], "sha_stars": [], "za_stars": []},
        {"name": "交友", "branch": "卯", "main_stars": ["天相"], "lucky_stars": [], "sha_stars": [], "za_stars": []},
        {"name": "官禄", "branch": "寅", "main_stars": ["太阳", "巨门"], "lucky_stars": [], "sha_stars": [], "za_stars": []},
        {"name": "田宅", "branch": "丑", "main_stars": ["武曲", "贪狼"], "lucky_stars": [], "sha_stars": [], "za_stars": []},
        {"name": "福德", "branch": "子", "main_stars": ["天同", "太阴"], "lucky_stars": [], "sha_stars": [], "za_stars": []},
        {"name": "父母", "branch": "亥", "main_stars": ["天府"], "lucky_stars": [], "sha_stars": [], "za_stars": []},
    ]
    c01 = {
        "id": "SC-C01",
        "verification_level": "verified_professional",
        "source": {"name": "REF-01 / lunar_python / Sprint6 cross-check", "type": "manual"},
        "verified_by": "internal REF-01",
        "birth": {
            "solar_date": "1990-05-15",
            "time": "14:30",
            "gender": "male",
            "location": "深圳",
            "true_solar_time": True,
            "longitude": 114.0579,
        },
        "expected": {
            "calendar": {
                "lunar": "1990-4-21",
                "ganzhi": {"year": "庚午", "month": "辛巳", "day": "庚辰", "hour": "癸未"},
                "shichen": {"name": "未时", "branch": "未"},
            },
            "meta": {
                "ming_gong": "戌",
                "shen_gong": "子",
                "wuxing_ju": "土五局",
                "ming_zhu": "禄存",
                "shen_zhu": "火星",
                "ziwei_position": "巳",
                "tianfu_position": "亥",
            },
            "palaces": c01_palaces,
            "four_transform": {"lu": "太阳", "quan": "武曲", "ke": "太阴", "ji": "天同"},
            "fortune": {"daxian": "", "liunian": ""},
        },
    }
    (OUT / "SC-C01.json").write_text(
        json.dumps(c01, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    index_cases = [
        {
            "id": "SC-C01",
            "verification_level": "verified_professional",
            "file": "SC-C01.json",
            "birth": c01["birth"],
        }
    ]
    for cid, solar, time, gender, loc, tst in BIRTHS:
        chart = build_pending(cid, solar, time, gender, loc, tst)
        (OUT / f"{cid}.json").write_text(
            json.dumps(chart, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        index_cases.append(
            {
                "id": cid,
                "verification_level": "pending",
                "file": f"{cid}.json",
                "birth": chart["birth"],
            }
        )
        meta = chart["expected"]["meta"]
        print(cid, meta["wuxing_ju"], meta["ming_gong"], gender, time)

    index = {
        "version": "1.4.1",
        "description": "Golden Dataset V1.4.1 — only verified_professional enters auto tests",
        "cases": index_cases,
    }
    (OUT / "index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("done", len(index_cases), "->", OUT)


if __name__ == "__main__":
    main()
