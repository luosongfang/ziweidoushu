"""Classical Trace — 规则 id + 来源 + 输入输出。"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class ClassicalTraceStep:
    step: str
    rule_id: str
    source: list[str] | str
    input: dict[str, Any] = field(default_factory=dict)
    result: Any = None
    formula: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "step": self.step,
            "rule_id": self.rule_id,
            "source": self.source,
            "input": self.input,
            "result": self.result,
            "formula": self.formula,
        }


@dataclass
class ClassicalTrace:
    steps: list[ClassicalTraceStep] = field(default_factory=list)

    def add(
        self,
        *,
        step: str,
        rule_id: str,
        source: list[str] | str,
        inputs: dict[str, Any] | None = None,
        result: Any = None,
        formula: str = "",
    ) -> None:
        self.steps.append(
            ClassicalTraceStep(
                step=step,
                rule_id=rule_id,
                source=source,
                input=inputs or {},
                result=result,
                formula=formula,
            )
        )

    def to_list(self) -> list[dict[str, Any]]:
        return [s.to_dict() for s in self.steps]
