"""紫微定位 — 传统五局表查表（禁止运行时动态推算替代）。"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from app.ziwei_classical.validator.rule_trace import RuleTrace

_TABLE_PATH = (
    Path(__file__).resolve().parents[1] / "references" / "ziwei_position_table.json"
)


@lru_cache(maxsize=1)
def load_ziwei_table() -> dict:
    return json.loads(_TABLE_PATH.read_text(encoding="utf-8"))


def lookup_ziwei_branch(bureau_number: int, lunar_day: int) -> str:
    table = load_ziwei_table()
    bureau = table["bureaus"].get(str(bureau_number))
    if not bureau:
        raise ValueError(f"未知五行局: {bureau_number}")
    branch = bureau["days"].get(str(lunar_day))
    if not branch:
        raise ValueError(f"紫微表无此日: bureau={bureau_number} day={lunar_day}")
    return branch


def place_ziwei(
    bureau_number: int,
    lunar_day: int,
    trace: RuleTrace | None = None,
) -> dict:
    branch = lookup_ziwei_branch(bureau_number, lunar_day)
    bureau_name = load_ziwei_table()["bureaus"][str(bureau_number)]["name"]
    out = {
        "star": "紫微",
        "branch": branch,
        "bureau_number": bureau_number,
        "bureau_name": bureau_name,
        "lunar_day": lunar_day,
        "method": "table_lookup",
        "table": "ziwei_position_table.json",
    }
    if trace is not None:
        trace.add(
            step="ziwei_position",
            rule="紫微五局传统落宫表查表（非运行时动态推算）",
            inputs={"bureau_number": bureau_number, "lunar_day": lunar_day},
            outputs=out,
            source="ziwei_classical.stars.ziwei_system",
        )
    return out
