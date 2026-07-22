"""五行局计算 — 水二/木三/金四/土五/火六。"""

from __future__ import annotations

from dataclasses import dataclass

from app.ziwei.engines.bureau_engine import BureauEngine


@dataclass(frozen=True)
class FiveElementResult:
    """五行局结果。"""

    ming_gong_ganzhi: str
    nayin: str
    element: str
    bureau_number: int
    bureau_name: str

    def to_dict(self) -> dict:
        return {
            "ming_gong_ganzhi": self.ming_gong_ganzhi,
            "nayin": self.nayin,
            "element": self.element,
            "bureau_number": self.bureau_number,
            "bureau_name": self.bureau_name,
        }


class FiveElementCalculator:
    """五行局计算器 — 读纳音规则表。"""

    @staticmethod
    def calculate(year_stem: str, ming_gong_branch_index: int) -> FiveElementResult:
        bureau = BureauEngine.compute(year_stem, ming_gong_branch_index)
        return FiveElementResult(
            ming_gong_ganzhi=bureau.ming_gong_ganzhi,
            nayin=bureau.nayin,
            element=bureau.nayin_element,
            bureau_number=bureau.bureau_number,
            bureau_name=bureau.bureau_name,
        )
