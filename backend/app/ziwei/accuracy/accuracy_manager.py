"""accuracy_manager — 黄金命盘管理（Professional Accuracy Center）。

仅 verification_level=verified_professional 进入自动测试。
不修改排盘算法；复用 classical_reference_charts + reference_manager。
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app.ziwei.debug.classical_audit import run_classical_audit
from app.ziwei.debug.reference_manager import (
    AUTO_TEST_LEVEL,
    VERIFICATION_LEVELS,
    add_reference_chart,
    export_report,
    fixture_dir,
    list_auto_test_charts,
    list_charts,
    load_chart,
    validate_reference,
)
from app.ziwei.accuracy.reference_compare import ReferenceCompare


class AccuracyManager:
    """专业准确率中心：管理黄金盘、跑对比、列出可测案例。"""

    AUTO_TEST_LEVEL = AUTO_TEST_LEVEL
    VERIFICATION_LEVELS = VERIFICATION_LEVELS

    def __init__(self, directory: Path | None = None) -> None:
        self.directory = fixture_dir(directory)
        self._compare = ReferenceCompare()

    def list_golden(
        self,
        *,
        level: str | None = None,
        auto_test_only: bool = False,
    ) -> list[dict[str, Any]]:
        if auto_test_only:
            return list_auto_test_charts(self.directory)
        if level:
            return list_charts(self.directory, level=level)  # type: ignore[arg-type]
        return list_charts(self.directory)

    def list_auto_test_charts(self) -> list[dict[str, Any]]:
        """仅 verified_professional。"""
        return list_auto_test_charts(self.directory)

    def get_chart(self, chart_id: str) -> dict[str, Any]:
        return load_chart(chart_id, self.directory)

    def validate(self, chart: dict[str, Any] | str) -> dict[str, Any]:
        if isinstance(chart, str):
            chart = self.get_chart(chart)
        return validate_reference(chart)

    def add_chart(self, chart: dict[str, Any], *, write: bool = True) -> dict[str, Any]:
        return add_reference_chart(chart, self.directory, write=write)

    def run_engine_for_reference(self, chart: dict[str, Any] | str) -> dict[str, Any]:
        """用现有审计链路生成引擎盘（不改算法）。"""
        if isinstance(chart, str):
            chart = self.get_chart(chart)
        birth = chart.get("birth") or {}
        audit = run_classical_audit(
            birth_date=birth["solar"],
            birth_time=birth["time"],
            gender=chart.get("gender", "male"),
            calendar_type=(chart.get("calendar") or {}).get("type", "solar"),
            location=chart.get("location") or birth.get("location"),
        )
        # 从 audit 重建十二宫主星（按 reference 宫名顺序；地支以引擎十四主星为准）
        branch_to_stars: dict[str, list[str]] = {}
        for star, br in audit.fourteen_star_positions.items():
            branch_to_stars.setdefault(br, []).append(star)

        palace_to_branch = {
            audit.fourteen_star_palaces[s]: audit.fourteen_star_positions[s]
            for s in audit.fourteen_star_positions
            if audit.fourteen_star_palaces.get(s)
        }
        # 命宫/身宫地支
        palace_to_branch.setdefault("命宫", audit.minggong)
        # 其余宫：沿用 reference 地支仅作结构骨架；主星用地支映射覆盖
        rebuilt: list[dict[str, Any]] = []
        ref_palaces = chart.get("palaces") or []
        if ref_palaces:
            for p in ref_palaces:
                name = p.get("name") or ""
                # 引擎侧地支：优先用 reference 同名宫地支（宫序一致时），主星按引擎落支填充
                br = p.get("branch") or palace_to_branch.get(name) or ""
                # 若 reference 地支与引擎命盘不一致，主星仍按引擎该支排列；
                # DiffEngine 会同时比较地支与主星，暴露偏差。
                rebuilt.append(
                    {
                        "name": name,
                        "branch": br,
                        "main_stars": sorted(branch_to_stars.get(br, [])),
                        "transformations": [],
                    }
                )
        else:
            for palace_name, stars in (audit.palaces_main_stars or {}).items():
                br = palace_to_branch.get(palace_name, "")
                rebuilt.append(
                    {
                        "name": palace_name,
                        "branch": br,
                        "main_stars": sorted(stars),
                        "transformations": [],
                    }
                )

        # 生年四化
        ft = audit.four_transform
        four = {
            "yearStem": ft.get("yearStem"),
            "lu": ft.get("lu"),
            "quan": ft.get("quan"),
            "ke": ft.get("ke"),
            "ji": ft.get("ji"),
        }

        return {
            "id": chart.get("id"),
            "birth": birth,
            "calendar": {
                "type": (chart.get("calendar") or {}).get("type", "solar"),
                "lunar": f"{audit.calendar_result.get('lunar_year')}-{audit.calendar_result.get('lunar_month')}-{audit.calendar_result.get('lunar_day')}",
                "ganzhi": dict(audit.ganzhi),
            },
            "meta": {
                "minggong": audit.minggong,
                "shengong": audit.shengong,
                "wuxingju": audit.wuxingju,
                "mingzhu": audit.mingzhu,
                "shenzhu": audit.shenzhu,
                "ziwei_position": audit.ziwei_position,
                "tianfu_position": audit.tianfu_position,
                "minggong_ganzhi": audit.minggong_ganzhi,
            },
            "palaces": rebuilt,
            "fourteen_stars": {
                s: {
                    "branch": audit.fourteen_star_positions.get(s, ""),
                    "palace": audit.fourteen_star_palaces.get(s, ""),
                }
                for s in audit.fourteen_star_positions
            },
            "four_transform": four,
            "fortune": {},  # 运限 reference 未提供时不比较
            "_audit": audit.to_dict(),
        }

    def compare_with_engine(self, chart_id: str) -> dict[str, Any]:
        ref = self.get_chart(chart_id)
        if ref.get("verification_level") != AUTO_TEST_LEVEL:
            return {
                "chart_id": chart_id,
                "skipped": True,
                "reason": f"verification_level={ref.get('verification_level')}，仅 {AUTO_TEST_LEVEL} 进入自动对比",
            }
        engine_chart = self.run_engine_for_reference(ref)
        result = self._compare.compare(engine_chart, ref)
        result["chart_id"] = chart_id
        result["verification_level"] = ref.get("verification_level")
        return result

    def compare_all_professional(self) -> list[dict[str, Any]]:
        out = []
        for c in self.list_auto_test_charts():
            out.append(self.compare_with_engine(c["id"]))
        return out

    def dataset_summary(self) -> dict[str, Any]:
        return export_report(self.directory)
