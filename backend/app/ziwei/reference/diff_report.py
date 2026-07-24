"""Reference vs ClassicalEngine 差异报告 + first_offset_step 统计。"""

from __future__ import annotations

from collections import Counter
from typing import Any

from app.ziwei.reference.metadata import MAIN_14
from app.ziwei_classical.config_loader import config_to_engine_config, load_classical_config
from app.ziwei_classical.engine import ClassicalEngine, ClassicalEngineConfig

FORMULA_CHANGE_THRESHOLD = 0.70  # 同节点占全部样本 ≥70% 才允许考虑改公式


def _first_offset(engine: dict[str, Any], ref: dict[str, Any]) -> str | None:
    """按计算链顺序定位首次偏移。"""
    cr = ref.get("chart_reference") or ref
    cal_ref = ref.get("calendar") or (cr.get("calendar") if isinstance(cr, dict) else None)
    if isinstance(cal_ref, dict) and cal_ref.get("ganzhi"):
        eg = (engine.get("calendar") or {}).get("year_ganzhi")
        rg = (cal_ref.get("ganzhi") or {}).get("year")
        if rg and eg and eg != rg:
            return "calendar"

    ming_e = (engine.get("ming_gong") or {}).get("branch")
    ming_r = cr.get("ming_gong") or ""
    if ming_r and ming_e != ming_r:
        return "ming_gong"

    shen_e = (engine.get("shen_gong") or {}).get("branch")
    shen_r = cr.get("shen_gong") or ""
    if shen_r and shen_e != shen_r:
        return "ming_gong"

    wx_e = (engine.get("bureau") or {}).get("bureau_name") or (engine.get("bureau") or {}).get(
        "wuxing"
    )
    wx_r = cr.get("wuxing") or ""
    if wx_r and wx_e != wx_r:
        return "five_element"

    zw_e = (engine.get("ziwei") or {}).get("branch")
    zw_r = cr.get("ziwei") or ""
    if zw_r and zw_e != zw_r:
        return "ziwei"

    tf_e = (engine.get("tianfu") or {}).get("branch")
    tf_r = cr.get("tianfu") or ""
    if tf_r and tf_e != tf_r:
        return "tianfu"

    palaces_r = cr.get("palaces") or {}
    by_palace_e = engine.get("fourteen_by_palace") or {}
    for pname, pdata in palaces_r.items():
        exp = sorted((pdata or {}).get("main_stars") or [])
        act = sorted(by_palace_e.get(pname) or [])
        if exp and exp != act:
            return "fourteen_stars"

    for star in MAIN_14:
        for pname, pdata in palaces_r.items():
            if star in ((pdata or {}).get("main_stars") or []):
                eng_palaces = [p for p, stars in by_palace_e.items() if star in stars]
                if eng_palaces and pname not in eng_palaces:
                    return "fourteen_stars"
                break

    return None


def diff_sample_against_engine(
    sample: dict[str, Any],
    *,
    engine_chart: dict[str, Any] | None = None,
    config: ClassicalEngineConfig | None = None,
) -> dict[str, Any]:
    birth = sample.get("birth") or {}
    settings = sample.get("settings") or {}
    if engine_chart is None:
        cfg = config or config_to_engine_config(load_classical_config())
        if settings.get("tianfu_rule"):
            cfg.tianfu_rule = settings["tianfu_rule"]  # type: ignore[assignment]
        chart = ClassicalEngine(cfg).compute(
            birth_date=birth.get("date") or birth.get("solar_date") or "",
            birth_time=birth.get("time") or "",
            gender=birth.get("gender") or "male",
            location=birth.get("location"),
            calendar_type=settings.get("calendar") or "solar",
        )
        engine_chart = chart.to_dict()

    ref = sample.get("chart_reference") or {}
    differences: list[dict[str, Any]] = []

    def add(field: str, engine: Any, reference: Any, critical: bool = True) -> None:
        if reference in (None, "", [], {}):
            return
        if engine != reference:
            differences.append(
                {
                    "field": field,
                    "engine": engine,
                    "reference": reference,
                    "critical": critical,
                }
            )

    add("ming_gong", (engine_chart.get("ming_gong") or {}).get("branch"), ref.get("ming_gong"))
    add("shen_gong", (engine_chart.get("shen_gong") or {}).get("branch"), ref.get("shen_gong"))
    add("wuxing", (engine_chart.get("bureau") or {}).get("bureau_name"), ref.get("wuxing"))
    add("ziwei", (engine_chart.get("ziwei") or {}).get("branch"), ref.get("ziwei"))
    add("tianfu", (engine_chart.get("tianfu") or {}).get("branch"), ref.get("tianfu"))

    by_palace = engine_chart.get("fourteen_by_palace") or {}
    for pname, pdata in (ref.get("palaces") or {}).items():
        exp = sorted((pdata or {}).get("main_stars") or [])
        act = sorted(by_palace.get(pname) or [])
        if (exp or act) and exp != act:
            differences.append(
                {
                    "field": f"palace.{pname}.main_stars",
                    "engine": act,
                    "reference": exp,
                    "critical": True,
                }
            )

    first = _first_offset(engine_chart, sample)
    critical = [d for d in differences if d.get("critical")]
    return {
        "sample": sample.get("id"),
        "first_offset_step": first,
        "difference": differences,
        "critical_count": len(critical),
        "matched": len(differences) == 0,
        "verification_level": sample.get("verification_level"),
    }


def aggregate_offset_frequency(reports: list[dict[str, Any]]) -> dict[str, Any]:
    """统计 first_offset_step 频率；占全部样本 ≥70% 才允许考虑改公式。"""
    usable = [r for r in reports if r.get("verification_level") == "verified_professional"]
    if not usable:
        usable = [r for r in reports if r.get("first_offset_step") or r.get("matched")]

    counter: Counter[str] = Counter()
    matched = 0
    for r in usable:
        if r.get("matched"):
            matched += 1
            counter["matched"] += 1
        elif r.get("first_offset_step"):
            counter[str(r["first_offset_step"])] += 1

    n = len(usable) or 1
    frequency = {k: round(v / n * 100, 2) for k, v in sorted(counter.items())}
    err_freq = {k: frequency[k] for k in frequency if k != "matched"}

    allow_change_node = None
    for k, pct in err_freq.items():
        if pct >= FORMULA_CHANGE_THRESHOLD * 100:
            allow_change_node = k
            break

    return {
        "sample_count": len(usable),
        "matched_count": matched,
        "first_offset_step_frequency": frequency,
        "error_node_frequency": err_freq,
        "formula_change_threshold": FORMULA_CHANGE_THRESHOLD,
        "formula_change_allowed": allow_change_node is not None,
        "dominant_error_node": allow_change_node,
        "recommendation": (
            f"节点 {allow_change_node} 在全部样本中占比≥70%，允许启动规则审计（仍禁止单盘硬编码）"
            if allow_change_node
            else "无节点达到70%样本频率门槛，禁止修改公式；继续扩充专业样本"
        ),
    }


def run_calibration_batch(samples: list[dict[str, Any]]) -> dict[str, Any]:
    reports = []
    for s in samples:
        if s.get("verification_level") != "verified_professional":
            continue
        reports.append(diff_sample_against_engine(s))
    stats = aggregate_offset_frequency(reports)
    return {"reports": reports, "statistics": stats}
