"""天府定位 — 支持流派配置。"""

from __future__ import annotations

from typing import Literal

from app.ziwei.constants import EARTHLY_BRANCHES
from app.ziwei_classical.validator.rule_trace import RuleTrace

TianfuRule = Literal["yin_shen_mirror", "opposite", "traditional"]

# traditional 默认对齐三合寅申镜像
DEFAULT_TIANFU_RULE: TianfuRule = "traditional"

RULE_DOCS = {
    "yin_shen_mirror": "寅–申轴镜像 index=(4-ziwei_index)%12",
    "opposite": "对宫 index=(ziwei_index+6)%12",
    "traditional": "传统三合默认=寅申镜像（同 yin_shen_mirror）",
}


def resolve_tianfu_rule(rule: str | None) -> str:
    r = rule or DEFAULT_TIANFU_RULE
    if r == "traditional":
        return "yin_shen_mirror"
    if r not in ("yin_shen_mirror", "opposite"):
        raise ValueError(f"未知 tianfu_rule: {rule}")
    return r


def calc_tianfu_branch(ziwei_branch: str, tianfu_rule: str = "traditional") -> str:
    z = EARTHLY_BRANCHES.index(ziwei_branch)
    mode = resolve_tianfu_rule(tianfu_rule)
    if mode == "opposite":
        return EARTHLY_BRANCHES[(z + 6) % 12]
    return EARTHLY_BRANCHES[(4 - z) % 12]


def place_tianfu(
    ziwei_branch: str,
    tianfu_rule: str = "traditional",
    trace: RuleTrace | None = None,
) -> dict:
    mode = resolve_tianfu_rule(tianfu_rule)
    branch = calc_tianfu_branch(ziwei_branch, tianfu_rule)
    out = {
        "star": "天府",
        "branch": branch,
        "ziwei_branch": ziwei_branch,
        "tianfu_rule": tianfu_rule,
        "resolved_mode": mode,
        "rule_doc": RULE_DOCS.get(tianfu_rule, RULE_DOCS[mode]),
    }
    if trace is not None:
        trace.add(
            step="tianfu_position",
            rule=out["rule_doc"],
            inputs={"ziwei_branch": ziwei_branch, "tianfu_rule": tianfu_rule},
            outputs=out,
            source="ziwei_classical.stars.tianfu_system",
        )
    return out
