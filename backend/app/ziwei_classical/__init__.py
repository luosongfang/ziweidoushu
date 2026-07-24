"""Ziwei Classical Rule Engine V1.0 — 传统紫微斗数规则计算内核。

原则：查表优先、步骤可 trace、不因单盘硬改、不改 Knowledge/AI/UI。
"""

from app.ziwei_classical.engine import ClassicalEngine, ClassicalEngineConfig
from app.ziwei_classical.validator.classical_validator import ClassicalAccuracyGate
from app.ziwei_classical.validator.dual_compare import DualEngineCompare

__all__ = [
    "ClassicalAccuracyGate",
    "ClassicalEngine",
    "ClassicalEngineConfig",
    "DualEngineCompare",
]

__version__ = "1.0.0"
