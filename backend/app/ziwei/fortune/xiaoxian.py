"""小限计算 — V1.2 Phase 2。"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from app.ziwei.engines.palace_engine import PalaceResult
from app.ziwei.rules.loader import RulesLoader


@dataclass
class XiaoxianCycleItem:
    age: int
    palace: str
    branch: str = ""


@dataclass
class XiaoxianResult:
    enabled: bool = True
    current_age: int = 0
    current_palace: str = ""
    current_branch: str = ""
    direction: str = "forward"
    yearly_cycle: list[XiaoxianCycleItem] = field(default_factory=list)
    trace: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "enabled": self.enabled,
            "current_age": self.current_age,
            "current_palace": self.current_palace,
            "current_branch": self.current_branch,
            "direction": self.direction,
            "yearly_cycle": [
                {"age": item.age, "palace": item.palace, "branch": item.branch}
                for item in self.yearly_cycle
            ],
            "trace": self.trace,
        }


class XiaoxianCalculator:
    """小限计算器 — 阳男阴女顺，阴男阳女逆，从命宫起 1 岁。"""

    @staticmethod
    def _calc_virtual_age(birth: datetime, reference: datetime) -> int:
        age = reference.year - birth.year + 1
        if (reference.month, reference.day) < (birth.month, birth.day):
            age -= 1
        return max(age, 1)

    @classmethod
    def compute(
        cls,
        palaces: list[PalaceResult],
        gender: str,
        year_stem: str,
        birth: datetime,
        reference: datetime | None = None,
        max_age: int = 120,
    ) -> XiaoxianResult:
        reference = reference or datetime.now()
        rule = RulesLoader.get_daxian_rule(gender, year_stem)
        forward = rule.direction == "forward"
        ming = next(p for p in palaces if p.is_ming_gong)
        ming_order = next(i for i, p in enumerate(palaces) if p.name == ming.name)
        current_age = cls._calc_virtual_age(birth, reference)

        cycle: list[XiaoxianCycleItem] = []
        for age in range(1, max_age + 1):
            if forward:
                idx = (ming_order + age - 1) % len(palaces)
            else:
                idx = (ming_order - (age - 1) + len(palaces)) % len(palaces)
            palace = palaces[idx]
            cycle.append(XiaoxianCycleItem(age=age, palace=palace.name, branch=palace.branch))

        current = cycle[current_age - 1] if 1 <= current_age <= len(cycle) else cycle[0]
        return XiaoxianResult(
            enabled=True,
            current_age=current_age,
            current_palace=current.palace,
            current_branch=current.branch,
            direction=rule.direction,
            yearly_cycle=cycle,
            trace={
                "engine": "xiaoxian",
                "source": "daxian_rules",
                "rule": "阳男阴女顺，阴男阳女逆；命宫起 1 岁",
                "ming_palace": ming.name,
                "gender": gender,
                "year_stem": year_stem,
            },
        )
