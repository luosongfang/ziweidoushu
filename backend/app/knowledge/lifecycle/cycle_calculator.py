"""Major-limit (大限) and life-stage calculators — traditional Ziwei rules, no LLM."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from sqlalchemy import text

from app.database.database import SessionLocal

# 十二宫顺行序（自命宫起）
PALACE_ORDER_SHUN = [
    "命宫",
    "父母宫",
    "福德宫",
    "田宅宫",
    "官禄宫",
    "交友宫",
    "迁移宫",
    "疾厄宫",
    "财帛宫",
    "子女宫",
    "夫妻宫",
    "兄弟宫",
]

# 五行局 → 起运年龄（传统：水二木三金四土五火六）
BUREAU_START_AGE: dict[int, int] = {2: 2, 3: 3, 4: 4, 5: 5, 6: 6}
BUREAU_NAME: dict[int, str] = {
    2: "水二局",
    3: "木三局",
    4: "金四局",
    5: "土五局",
    6: "火六局",
}

# Fallback rules when DB empty
_FALLBACK_CYCLE_RULES: list[dict[str, Any]] = [
    {
        "theory_system": "sanhe",
        "gender": "male",
        "yin_yang": "yang",
        "bureau_number": None,
        "start_age_formula": "bureau_number",
        "direction": "shun",
        "description": "阳男顺行：自大限起运年龄起，每限十年，顺十二宫",
    },
    {
        "theory_system": "sanhe",
        "gender": "male",
        "yin_yang": "yin",
        "bureau_number": None,
        "start_age_formula": "bureau_number",
        "direction": "ni",
        "description": "阴男逆行：自大限起运年龄起，每限十年，逆十二宫",
    },
    {
        "theory_system": "sanhe",
        "gender": "female",
        "yin_yang": "yin",
        "bureau_number": None,
        "start_age_formula": "bureau_number",
        "direction": "shun",
        "description": "阴女顺行：自大限起运年龄起，每限十年，顺十二宫",
    },
    {
        "theory_system": "sanhe",
        "gender": "female",
        "yin_yang": "yang",
        "bureau_number": None,
        "start_age_formula": "bureau_number",
        "direction": "ni",
        "description": "阳女逆行：自大限起运年龄起，每限十年，逆十二宫",
    },
]


def normalize_gender(value: str | None) -> str:
    v = (value or "").strip().lower()
    if v in {"m", "male", "男", "阳男", "阴男"}:
        return "male"
    if v in {"f", "female", "女", "阳女", "阴女"}:
        return "female"
    return "male"


def normalize_yin_yang(value: str | None, *, year_stem: str | None = None) -> str:
    v = (value or "").strip().lower()
    if v in {"yang", "阳", "陽"}:
        return "yang"
    if v in {"yin", "阴", "陰"}:
        return "yin"
    # 天干阴阳：甲丙戊庚壬阳，乙丁己辛癸阴
    yang_stems = {"甲", "丙", "戊", "庚", "壬"}
    yin_stems = {"乙", "丁", "己", "辛", "癸"}
    if year_stem in yang_stems:
        return "yang"
    if year_stem in yin_stems:
        return "yin"
    return "yang"


def resolve_bureau_number(chart: dict[str, Any] | None = None, explicit: int | None = None) -> int:
    if explicit in BUREAU_START_AGE:
        return int(explicit)
    meta = (chart or {}).get("meta") if isinstance(chart, dict) else {}
    meta = meta if isinstance(meta, dict) else {}
    for key in ("bureau_number", "wuju", "five_bureau", "bureau"):
        raw = (chart or {}).get(key) if chart else None
        if raw is None:
            raw = meta.get(key)
        if raw is None:
            continue
        if isinstance(raw, int) and raw in BUREAU_START_AGE:
            return raw
        s = str(raw)
        for n, name in BUREAU_NAME.items():
            if str(n) == s or name in s or s in name:
                return n
        for n in BUREAU_START_AGE:
            if f"{n}局" in s:
                return n
    return 4  # default 金四局


class CycleCalculator:
    """Compute 大限 start age, direction, and decade blocks from traditional rules."""

    @classmethod
    @lru_cache(maxsize=1)
    def _load_rules(cls) -> tuple[dict[str, Any], ...]:
        db = SessionLocal()
        try:
            rows = db.execute(
                text(
                    """
                    SELECT theory_system, gender, yin_yang, bureau_number,
                           start_age_formula, direction, description
                    FROM public.fortune_cycle_rules
                    """
                )
            ).mappings().all()
            if rows:
                return tuple(dict(r) for r in rows)
        except Exception:
            pass
        finally:
            db.close()
        return tuple(_FALLBACK_CYCLE_RULES)

    @classmethod
    def refresh(cls) -> None:
        cls._load_rules.cache_clear()

    @classmethod
    def start_age(cls, bureau_number: int) -> int:
        return BUREAU_START_AGE.get(int(bureau_number), int(bureau_number) if 1 <= int(bureau_number) <= 6 else 4)

    @classmethod
    def resolve_direction(
        cls,
        *,
        gender: str | None,
        yin_yang: str | None,
        theory_system: str = "sanhe",
    ) -> dict[str, Any]:
        g = normalize_gender(gender)
        yy = normalize_yin_yang(yin_yang)
        # Traditional: 阳男阴女顺，阴男阳女逆
        default_dir = "shun" if (g == "male" and yy == "yang") or (g == "female" and yy == "yin") else "ni"

        for rule in cls._load_rules():
            if rule.get("gender") and normalize_gender(str(rule["gender"])) != g:
                continue
            if rule.get("yin_yang") and normalize_yin_yang(str(rule["yin_yang"])) != yy:
                continue
            if rule.get("theory_system") and str(rule["theory_system"]) not in {theory_system, "sanhe"}:
                continue
            return {
                "direction": rule.get("direction") or default_dir,
                "description": rule.get("description") or "",
                "start_age_formula": rule.get("start_age_formula") or "bureau_number",
                "theory_system": rule.get("theory_system") or theory_system,
            }
        return {
            "direction": default_dir,
            "description": "阳男阴女顺行，阴男阳女逆行（三合传统）",
            "start_age_formula": "bureau_number",
            "theory_system": theory_system,
        }

    @classmethod
    def palace_sequence(cls, direction: str) -> list[str]:
        if direction == "ni":
            # 逆行：命宫起逆走
            return [PALACE_ORDER_SHUN[0]] + list(reversed(PALACE_ORDER_SHUN[1:]))
        return list(PALACE_ORDER_SHUN)

    @classmethod
    def major_limits(
        cls,
        *,
        bureau_number: int,
        gender: str | None = None,
        yin_yang: str | None = None,
        max_age: int = 112,
        chart: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        bureau = resolve_bureau_number(chart, bureau_number)
        start = cls.start_age(bureau)
        meta = cls.resolve_direction(gender=gender, yin_yang=yin_yang)
        direction = meta["direction"]
        seq = cls.palace_sequence(direction)

        limits: list[dict[str, Any]] = []
        age = start
        idx = 0
        while age <= max_age and idx < 12 * 3:  # up to 3 cycles
            palace = seq[idx % 12]
            end = age + 9
            limits.append(
                {
                    "index": idx,
                    "palace": palace,
                    "age_start": age,
                    "age_end": end,
                    "age_range": f"{age}-{end}",
                    "direction": direction,
                    "bureau_number": bureau,
                    "bureau_name": BUREAU_NAME.get(bureau, f"{bureau}局"),
                    "description": meta.get("description") or "",
                    "source": {
                        "type": "fortune_cycle_rule",
                        "theory_system": meta.get("theory_system") or "sanhe",
                        "rule": "大限十年一宫",
                    },
                }
            )
            age = end + 1
            idx += 1
        return limits

    @classmethod
    def current_major_limit(
        cls,
        age: int,
        *,
        bureau_number: int = 4,
        gender: str | None = None,
        yin_yang: str | None = None,
        chart: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        limits = cls.major_limits(
            bureau_number=bureau_number,
            gender=gender,
            yin_yang=yin_yang,
            chart=chart,
        )
        for lim in limits:
            if lim["age_start"] <= age <= lim["age_end"]:
                return lim
        if age < (limits[0]["age_start"] if limits else 0):
            return {
                "index": -1,
                "palace": "童限/未起运",
                "age_start": 0,
                "age_end": (limits[0]["age_start"] - 1) if limits else 0,
                "age_range": f"0-{(limits[0]['age_start'] - 1) if limits else 0}",
                "direction": limits[0]["direction"] if limits else "shun",
                "bureau_number": resolve_bureau_number(chart, bureau_number),
                "description": "尚未进入大限起运年龄，宜以学习与基础建设为主",
                "source": {"type": "fortune_cycle_rule", "rule": "起运前"},
            }
        return limits[-1] if limits else None

    @classmethod
    def extract_profile(cls, chart: dict[str, Any] | None, user_context: dict[str, Any] | None = None) -> dict[str, Any]:
        chart = chart or {}
        ctx = user_context or {}
        meta = chart.get("meta") if isinstance(chart.get("meta"), dict) else {}
        age = ctx.get("age") or chart.get("age") or meta.get("age")
        if age is None and (ctx.get("birth_year") or chart.get("birth_year") or meta.get("birth_year")):
            try:
                from datetime import datetime

                by = int(ctx.get("birth_year") or chart.get("birth_year") or meta.get("birth_year"))
                age = datetime.now().year - by
            except (TypeError, ValueError):
                age = None
        gender = ctx.get("gender") or chart.get("gender") or meta.get("gender")
        yin_yang = ctx.get("yin_yang") or chart.get("yin_yang") or meta.get("yin_yang")
        year_stem = ctx.get("year_stem") or chart.get("year_stem") or meta.get("year_stem")
        yin_yang = normalize_yin_yang(yin_yang, year_stem=str(year_stem) if year_stem else None)
        bureau = resolve_bureau_number(chart, ctx.get("bureau_number") or chart.get("bureau_number"))
        return {
            "age": int(age) if age is not None else None,
            "gender": normalize_gender(str(gender) if gender else None),
            "yin_yang": yin_yang,
            "bureau_number": bureau,
            "year_stem": year_stem,
        }
