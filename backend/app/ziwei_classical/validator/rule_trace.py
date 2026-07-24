"""规则步骤 trace 记录。"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class RuleStep:
    step: str
    rule: str
    inputs: dict[str, Any] = field(default_factory=dict)
    outputs: dict[str, Any] = field(default_factory=dict)
    source: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RuleTrace:
    steps: list[RuleStep] = field(default_factory=list)

    def add(
        self,
        step: str,
        rule: str,
        inputs: dict[str, Any] | None = None,
        outputs: dict[str, Any] | None = None,
        source: str = "",
    ) -> None:
        self.steps.append(
            RuleStep(
                step=step,
                rule=rule,
                inputs=inputs or {},
                outputs=outputs or {},
                source=source,
            )
        )

    def to_list(self) -> list[dict[str, Any]]:
        return [s.to_dict() for s in self.steps]
