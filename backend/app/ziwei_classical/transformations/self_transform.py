"""自化 — V1.0 检测占位。"""

from __future__ import annotations

from app.ziwei_classical.validator.rule_trace import RuleTrace


def self_transform(trace: RuleTrace | None = None) -> list:
    out: list = []
    if trace is not None:
        trace.add(
            step="self_transform",
            rule="自化检测（本阶段输出空列表，待专业表）",
            inputs={},
            outputs={"items": out},
            source="ziwei_classical.transformations.self_transform",
        )
    return out
