"""流年 — V1.0 骨架。"""

from __future__ import annotations

from app.ziwei_classical.validator.rule_trace import RuleTrace


def calc_liunian(trace: RuleTrace | None = None) -> dict:
    out = {"enabled": False, "note": "流年待专业盘批量校验"}
    if trace is not None:
        trace.add(
            step="liunian",
            rule="流年占位",
            inputs={},
            outputs=out,
            source="ziwei_classical.fortune.liunian",
        )
    return out
