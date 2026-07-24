"""Classical 流派配置加载。"""

from __future__ import annotations

import json
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from typing import Any

from app.ziwei_classical.engine import ClassicalEngineConfig

_CONFIG_PATH = Path(__file__).resolve().parent / "references" / "classical_config.json"

_TIANFU_ALIAS = {
    "mirror": "yin_shen_mirror",
    "traditional": "traditional",
    "yin_shen_mirror": "yin_shen_mirror",
    "opposite": "opposite",
}


@lru_cache(maxsize=1)
def load_classical_config() -> dict[str, Any]:
    return json.loads(_CONFIG_PATH.read_text(encoding="utf-8"))


def resolve_school_config(school: str | None = None) -> dict[str, Any]:
    cfg = deepcopy(load_classical_config())
    name = school or cfg.get("school") or "sanhe"
    school_cfg = (cfg.get("schools") or {}).get(name) or {}
    merged = {**cfg, **school_cfg, "school": name}
    tr = merged.get("tianfu_rule") or "traditional"
    merged["tianfu_rule"] = _TIANFU_ALIAS.get(tr, tr)
    return merged


def config_to_engine_config(cfg: dict[str, Any] | None = None) -> ClassicalEngineConfig:
    c = cfg or load_classical_config()
    if c.get("school") and "tianfu_rule" not in (cfg or {}):
        c = resolve_school_config(c.get("school"))
    tr = c.get("tianfu_rule") or "traditional"
    tr = _TIANFU_ALIAS.get(tr, tr)
    if tr not in ("traditional", "yin_shen_mirror", "opposite"):
        tr = "traditional"
    return ClassicalEngineConfig(tianfu_rule=tr)  # type: ignore[arg-type]


def switch_school(school: str) -> ClassicalEngineConfig:
    return config_to_engine_config(resolve_school_config(school))
