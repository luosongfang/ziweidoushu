"""算法差异检测 — Sprint 6 完整实现。"""

from __future__ import annotations

from typing import Any


def detect_diff(expected: dict[str, Any], actual: dict[str, Any], prefix: str = "") -> list[str]:
    diffs: list[str] = []
    for key, exp_val in expected.items():
        path = f"{prefix}.{key}" if prefix else key
        if key not in actual:
            diffs.append(f"{path}: missing in actual")
            continue
        act_val = actual[key]
        if isinstance(exp_val, dict) and isinstance(act_val, dict):
            diffs.extend(detect_diff(exp_val, act_val, path))
        elif exp_val != act_val:
            diffs.append(f"{path}: expected={exp_val!r}, actual={act_val!r}")
    return diffs
