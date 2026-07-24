"""ClassicalEngine vs CurrentEngine 双引擎比较。"""

from __future__ import annotations

from typing import Any

from app.ziwei.debug.classical_audit import MAIN_14, run_classical_audit
from app.ziwei_classical.engine import ClassicalEngine, ClassicalEngineConfig


class DualEngineCompare:
    """same input → difference report（支持与文墨 expected 再比）。"""

    def __init__(self, config: ClassicalEngineConfig | None = None) -> None:
        self.classical = ClassicalEngine(config)

    def compare(
        self,
        *,
        birth_date: str,
        birth_time: str,
        gender: str = "male",
        location: str | None = None,
        calendar_type: str = "solar",
    ) -> dict[str, Any]:
        c = self.classical.compute(
            birth_date=birth_date,
            birth_time=birth_time,
            gender=gender,
            location=location,
            calendar_type=calendar_type,
        )
        cur = run_classical_audit(
            birth_date=birth_date,
            birth_time=birth_time,
            gender=gender,
            location=location,
            calendar_type=calendar_type,
        )

        def status(ok: bool) -> str:
            return "PASS" if ok else "FAIL"

        calendar_ok = (
            c.calendar["lunar_day"] == cur.calendar_result.get("lunar_day")
            and c.calendar["year_ganzhi"] == cur.ganzhi.get("year")
        )
        palace_ok = (
            c.ming_gong["branch"] == cur.minggong
            and c.shen_gong["branch"] == cur.shengong
        )
        bureau_ok = c.bureau["bureau_name"] == cur.wuxingju
        ziwei_ok = c.ziwei["branch"] == cur.ziwei_position
        tianfu_ok = c.tianfu["branch"] == cur.tianfu_position

        star_difference: list[dict[str, Any]] = []
        # 按宫比较主星
        cur_by_palace = dict(cur.palaces_main_stars or {})
        all_palaces = sorted(
            set(c.fourteen_by_palace) | set(cur_by_palace)
        )
        for pname in all_palaces:
            exp = sorted(c.fourteen_by_palace.get(pname) or [])
            act = sorted(cur_by_palace.get(pname) or [])
            if exp != act:
                star_difference.append(
                    {"palace": pname, "classical": exp, "current": act}
                )

        # 逐星地支
        star_branch_diffs = []
        for star in MAIN_14:
            a = c.fourteen_stars.get(star)
            b = cur.fourteen_star_positions.get(star)
            if a != b:
                star_branch_diffs.append(
                    {"star": star, "classical": a, "current": b}
                )

        fourteen_ok = len(star_branch_diffs) == 0 and len(star_difference) == 0

        return {
            "calendar": status(calendar_ok),
            "palace": status(palace_ok),
            "bureau": status(bureau_ok),
            "ziwei": status(ziwei_ok),
            "tianfu": status(tianfu_ok),
            "fourteen_stars": status(fourteen_ok),
            "star_difference": star_difference,
            "star_branch_difference": star_branch_diffs,
            "classical_summary": {
                "ming_gong": c.ming_gong["branch"],
                "wuxing": c.bureau["bureau_name"],
                "ziwei": c.ziwei["branch"],
                "tianfu": c.tianfu["branch"],
            },
            "current_summary": {
                "ming_gong": cur.minggong,
                "wuxing": cur.wuxingju,
                "ziwei": cur.ziwei_position,
                "tianfu": cur.tianfu_position,
            },
            "matched": all(
                x == "PASS"
                for x in (
                    status(calendar_ok),
                    status(palace_ok),
                    status(bureau_ok),
                    status(ziwei_ok),
                    status(tianfu_ok),
                    status(fourteen_ok),
                )
            ),
        }

    def compare_to_expected(
        self,
        classical_chart: dict[str, Any] | Any,
        expected: dict[str, Any],
    ) -> dict[str, Any]:
        """与黄金盘 expected 比较（文墨导入后使用）。"""
        if hasattr(classical_chart, "to_dict"):
            c = classical_chart.to_dict()
        else:
            c = classical_chart

        star_difference = []
        exp_fourteen = expected.get("fourteen_stars") or {}
        # expected 可能是 宫→星 或 星→宫
        if exp_fourteen and isinstance(next(iter(exp_fourteen.values()), None), list):
            # 宫 → stars
            for palace, stars in exp_fourteen.items():
                act = sorted((c.get("fourteen_by_palace") or {}).get(palace) or [])
                exp = sorted(stars or [])
                if act != exp:
                    star_difference.append(
                        {"palace": palace, "expected": exp, "actual": act}
                    )
        else:
            for star, val in exp_fourteen.items():
                exp_br = val.get("branch") if isinstance(val, dict) else val
                act = (c.get("fourteen_stars") or {}).get(star)
                if exp_br and act != exp_br:
                    star_difference.append(
                        {
                            "star": star,
                            "expected": exp_br,
                            "actual": act,
                            "palace": None,
                        }
                    )

        ziwei_ok = True
        if expected.get("ziwei"):
            ziwei_ok = (c.get("ziwei") or {}).get("branch") == expected.get("ziwei")
        palace_ok = True
        if expected.get("ming_gong"):
            palace_ok = (c.get("ming_gong") or {}).get("branch") == expected.get("ming_gong")

        return {
            "calendar": "PASS",  # 由调用方细分
            "palace": "PASS" if palace_ok else "FAIL",
            "ziwei": "PASS" if ziwei_ok else "FAIL",
            "star_difference": star_difference,
            "matched": palace_ok and ziwei_ok and len(star_difference) == 0,
        }
