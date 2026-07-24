"""规则库加载与生产门禁：无来源规则禁止进入生产。"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

RULES_ROOT = Path(__file__).resolve().parent


@lru_cache(maxsize=1)
def load_catalog() -> dict[str, Any]:
    return json.loads((RULES_ROOT / "rule_catalog.json").read_text(encoding="utf-8"))


def load_json(rel: str) -> dict[str, Any]:
    path = RULES_ROOT / rel
    return json.loads(path.read_text(encoding="utf-8"))


@lru_cache(maxsize=32)
def load_rule_file(rel: str) -> dict[str, Any]:
    return load_json(rel)


def get_ming_rule() -> dict[str, Any]:
    data = load_rule_file("palace/ming_gong_rules.json")
    return data["rules"][0]


def get_shen_rule() -> dict[str, Any]:
    data = load_rule_file("palace/shen_gong_rules.json")
    return data["rules"][0]


def get_ziwei_table() -> dict[str, Any]:
    return load_rule_file("stars/ziwei_position_table.json")


def get_tianfu_config() -> dict[str, Any]:
    return load_rule_file("stars/tianfu_rule_config.json")


def get_fourteen_rules() -> dict[str, Any]:
    return load_rule_file("stars/fourteen_star_rule.json")


def get_five_element_table() -> dict[str, Any]:
    return load_rule_file("bureau/five_element_table.json")


def get_aux_catalog() -> dict[str, Any]:
    return load_rule_file("stars/traditional_aux/aux_catalog.json")


def assert_has_source(rule: dict[str, Any]) -> None:
    src = rule.get("source") or rule.get("sources")
    if not src:
        raise PermissionError(
            f"规则 {rule.get('id')} 无来源，禁止进入生产（production_requires_source）"
        )


def list_sourced_rules() -> list[dict[str, Any]]:
    """汇总已编目且带 source 的规则条目。"""
    out: list[dict[str, Any]] = []
    catalog = load_catalog()
    for item in catalog.get("rules", []):
        rel = item["file"]
        data = load_rule_file(rel)
        if "rules" in data:
            for r in data["rules"]:
                assert_has_source(r) if r.get("validation") == "required" else None
                out.append(r)
        elif data.get("source") or data.get("star_rules"):
            if data.get("source"):
                out.append(
                    {
                        "id": data.get("rule_id") or item["id"],
                        "name": data.get("name") or item["id"],
                        "source": data.get("source"),
                        "category": item["id"],
                    }
                )
            for sr in data.get("star_rules") or []:
                out.append(sr)
        elif data.get("entries"):
            out.append(
                {
                    "id": "ZIWEI_TABLE",
                    "name": "紫微五局表",
                    "source": data.get("source"),
                    "count": len(data["entries"]),
                }
            )
        elif data.get("ganzhi_table"):
            out.append(
                {
                    "id": "BUREAU_NAYIN_001",
                    "name": "纳音五行局表",
                    "source": data.get("source"),
                    "count": len(data["ganzhi_table"]),
                }
            )
    return out
