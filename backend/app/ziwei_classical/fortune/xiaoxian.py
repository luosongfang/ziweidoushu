"""小限 — V1.0 骨架。"""

from __future__ import annotations

from app.ziwei_classical.validator.rule_trace import RuleTrace


def calc_xiaoxian(trace: RuleTrace | None = None) -> dict:
    out = {"enabled": False, "note": "小限待十四主星专业验证后深化"}
    if trace is not None:
        trace.add(
            step="xiaoxian",
            rule="小限占位",
            inputs={},
            outputs=out,
            source="ziwei_classical.fortune.xiaoxian",
        )
    return out
