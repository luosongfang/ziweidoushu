"""黄金标准命盘管理 — Ziwei Core Engine V1.3.1。

不修改排盘算法；仅管理 / 校验 / 对比 reference 数据集。
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from app.ziwei.debug.classical_audit import MAIN_14, ClassicalAuditReport, run_classical_audit

VerificationLevel = Literal["pending", "verified_manual", "verified_professional"]
ImpactLevel = Literal["critical", "major", "minor"]

VERIFICATION_LEVELS = ("pending", "verified_manual", "verified_professional")
AUTO_TEST_LEVEL = "verified_professional"

REQUIRED_META = ("minggong", "shengong", "wuxingju", "mingzhu", "shenzhu")
CRITICAL_META = ("minggong", "shengong", "wuxingju", "ziwei_position")
MAJOR_FOUR = ("lu", "quan", "ke", "ji")

# V1.4.1 权威黄金盘目录（debug）；旧 tests/fixtures 仅作兼容回退
DEFAULT_FIXTURE_DIR = Path(__file__).resolve().parent / "classical_reference_charts"
_LEGACY_FIXTURE_DIR = (
    Path(__file__).resolve().parents[3] / "tests" / "fixtures" / "classical_reference_charts"
)


@dataclass
class ChartReferenceDiff:
    field: str
    engine: Any
    reference: Any
    impact: ImpactLevel

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CompareReport:
    chart_id: str
    matched: bool
    diffs: list[ChartReferenceDiff] = field(default_factory=list)
    verification_level: str = ""
    summary: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "chart_id": self.chart_id,
            "matched": self.matched,
            "verification_level": self.verification_level,
            "diff_count": len(self.diffs),
            "diffs": [d.to_dict() for d in self.diffs],
            "summary": self.summary,
            "by_impact": {
                "critical": sum(1 for d in self.diffs if d.impact == "critical"),
                "major": sum(1 for d in self.diffs if d.impact == "major"),
                "minor": sum(1 for d in self.diffs if d.impact == "minor"),
            },
        }


def fixture_dir(path: Path | None = None) -> Path:
    if path is not None:
        return path
    if DEFAULT_FIXTURE_DIR.exists() and (DEFAULT_FIXTURE_DIR / "index.json").exists():
        return DEFAULT_FIXTURE_DIR
    return _LEGACY_FIXTURE_DIR


def _impact_for_field(field_name: str) -> ImpactLevel:
    if field_name.startswith("十四主星") or field_name in (
        "紫微位置",
        "天府位置",
        "命宫",
        "身宫",
        "五行局",
    ):
        return "critical"
    if field_name.startswith("四化") or "transformations" in field_name:
        return "major"
    return "minor"


def _normalize_legacy(raw: dict[str, Any]) -> dict[str, Any]:
    """将 V1.4.1 expected / 旧版 reference_data / 扁平 schema 统一。"""
    level = raw.get("verification_level")
    if not level:
        status = raw.get("status") or ""
        if status in ("verified", "verified_professional"):
            level = "verified_professional"
        elif status in ("verified_manual",):
            level = "verified_manual"
        else:
            level = "pending"

    birth_in = dict(raw.get("birth") or {})
    # V1.4.1: birth.solar_date
    if birth_in.get("solar_date") and not birth_in.get("solar"):
        birth_in["solar"] = birth_in["solar_date"]

    expected = raw.get("expected") or {}
    ref = raw.get("reference_data") or {}

    meta_src = dict(raw.get("meta") or expected.get("meta") or ref.get("meta") or {})
    # alias ming_gong → minggong
    meta = {
        "minggong": meta_src.get("minggong") or meta_src.get("ming_gong") or meta_src.get("mingGong") or "",
        "shengong": meta_src.get("shengong") or meta_src.get("shen_gong") or meta_src.get("shenGong") or "",
        "wuxingju": meta_src.get("wuxingju") or meta_src.get("wuxing_ju") or meta_src.get("wuxingJu") or "",
        "mingzhu": meta_src.get("mingzhu") or meta_src.get("ming_zhu") or meta_src.get("mingZhu") or "",
        "shenzhu": meta_src.get("shenzhu") or meta_src.get("shen_zhu") or meta_src.get("shenZhu") or "",
        "ziwei_position": meta_src.get("ziwei_position") or meta_src.get("ziwei_branch") or "",
        "tianfu_position": meta_src.get("tianfu_position") or meta_src.get("tianfu_branch") or "",
        "minggong_ganzhi": meta_src.get("minggong_ganzhi") or meta_src.get("ming_gong_ganzhi") or "",
    }

    palaces = list(
        raw.get("palaces") or expected.get("palaces") or ref.get("palaces") or []
    )

    calendar_block = raw.get("calendar")
    if expected.get("calendar"):
        calendar_block = expected.get("calendar")
    if isinstance(calendar_block, str):
        calendar_type = calendar_block
        calendar_block = {
            "type": calendar_type,
            "lunar": birth_in.get("lunar") or "",
            "ganzhi": birth_in.get("ganzhi") or {},
        }
    elif not isinstance(calendar_block, dict):
        calendar_block = {
            "type": "solar",
            "lunar": birth_in.get("lunar") or "",
            "ganzhi": birth_in.get("ganzhi") or {},
        }
    else:
        calendar_block = dict(calendar_block)
        calendar_block.setdefault("type", "solar")
        calendar_block.setdefault("lunar", birth_in.get("lunar") or "")
        calendar_block.setdefault("ganzhi", birth_in.get("ganzhi") or {})

    location = raw.get("location")
    if location is None:
        location = birth_in.get("location")

    gender = birth_in.get("gender") or raw.get("gender") or "male"
    true_solar = birth_in.get("true_solar_time")
    if true_solar is None:
        true_solar = bool(raw.get("true_solar_time", False))

    source = raw.get("source", "")
    if isinstance(source, dict):
        source_name = source.get("name") or ""
        source_type = source.get("type") or ""
    else:
        source_name = str(source or "")
        source_type = ""

    # four_transform: V1.4.1 strings or legacy objects
    ft_src = raw.get("four_transform") or expected.get("four_transform") or ref.get("four_transform") or {}
    four_transform: dict[str, Any] = {}
    if isinstance(ft_src, dict):
        for k in ("lu", "quan", "ke", "ji"):
            v = ft_src.get(k)
            if isinstance(v, dict):
                four_transform[k] = v
            elif v:
                four_transform[k] = {"star": str(v)}
            else:
                four_transform[k] = {"star": ""}
        if ft_src.get("yearStem"):
            four_transform["yearStem"] = ft_src["yearStem"]

    # fourteen_stars from palaces if missing
    fourteen = raw.get("fourteen_stars") or ref.get("fourteen_stars") or expected.get("fourteen_stars")
    if not fourteen and palaces:
        fourteen = {}
        for p in palaces:
            for s in p.get("main_stars") or []:
                name = s if isinstance(s, str) else (s.get("name") if isinstance(s, dict) else None)
                if name:
                    fourteen[name] = {
                        "branch": p.get("branch", ""),
                        "palace": p.get("name", ""),
                    }

    fortune = raw.get("fortune") or expected.get("fortune") or {}

    out: dict[str, Any] = {
        "id": raw.get("id", ""),
        "source": source_name,
        "source_detail": source if isinstance(source, dict) else {"name": source_name, "type": source_type},
        "verified_by": raw.get("verified_by", ""),
        "verification_level": level,
        "gender": gender,
        "true_solar_time": bool(true_solar),
        "location": location,
        "birth": {
            "solar": birth_in.get("solar") or birth_in.get("solar_date") or "",
            "solar_date": birth_in.get("solar_date") or birth_in.get("solar") or "",
            "time": birth_in.get("time", ""),
            "location": birth_in.get("location"),
            "longitude": birth_in.get("longitude"),
            "shichen": birth_in.get("shichen"),
            "gender": gender,
            "true_solar_time": bool(true_solar),
        },
        "calendar": calendar_block,
        "meta": meta,
        "palaces": palaces,
        "four_transform": four_transform,
        "fortune": fortune,
        "expected": expected,
    }
    if fourteen:
        out["fourteen_stars"] = fourteen
    if raw.get("notes"):
        out["notes"] = raw["notes"]
    return out


def load_chart(chart_id: str, directory: Path | None = None) -> dict[str, Any]:
    d = fixture_dir(directory)
    path = d / f"{chart_id}.json"
    if not path.exists():
        index = json.loads((d / "index.json").read_text(encoding="utf-8"))
        for row in index.get("cases", []):
            if row.get("id") == chart_id:
                path = d / row["file"]
                break
    raw = json.loads(path.read_text(encoding="utf-8"))
    return _normalize_legacy(raw)


def list_charts(
    directory: Path | None = None,
    *,
    level: VerificationLevel | None = None,
) -> list[dict[str, Any]]:
    d = fixture_dir(directory)
    index = json.loads((d / "index.json").read_text(encoding="utf-8"))
    out: list[dict[str, Any]] = []
    for row in index.get("cases", []):
        chart = load_chart(row["id"], d)
        if level and chart.get("verification_level") != level:
            continue
        out.append(chart)
    return out


def list_auto_test_charts(directory: Path | None = None) -> list[dict[str, Any]]:
    """仅 verified_professional 进入自动测试。"""
    return list_charts(directory, level=AUTO_TEST_LEVEL)


def validate_reference(chart: dict[str, Any]) -> dict[str, Any]:
    """校验 reference 结构完整性；不跑引擎。"""
    errors: list[str] = []
    warnings: list[str] = []
    level = chart.get("verification_level") or "pending"

    if level not in VERIFICATION_LEVELS:
        errors.append(f"verification_level 非法: {level}")

    if not chart.get("id"):
        errors.append("缺少 id")
    birth = chart.get("birth") or {}
    if not birth.get("solar"):
        errors.append("缺少 birth.solar")
    if not birth.get("time"):
        errors.append("缺少 birth.time")

    if level == "pending":
        return {
            "ok": len(errors) == 0,
            "errors": errors,
            "warnings": warnings + ["pending：不要求 meta/palaces，禁止入测"],
            "eligible_for_auto_test": False,
        }

    meta = chart.get("meta") or {}
    for k in REQUIRED_META:
        if not meta.get(k):
            errors.append(f"meta.{k} 缺失")

    palaces = chart.get("palaces") or []
    if len(palaces) != 12:
        errors.append(f"palaces 数量={len(palaces)}，需要 12")
    else:
        names = [p.get("name") for p in palaces]
        if len(set(names)) != 12:
            errors.append("十二宫 name 不唯一")
        stars: list[str] = []
        for p in palaces:
            for s in p.get("main_stars") or []:
                stars.append(s)
        missing = [s for s in MAIN_14 if s not in stars]
        if missing:
            errors.append(f"十四主星缺失: {missing}")
        dup = sorted({s for s in stars if stars.count(s) > 1})
        if dup:
            errors.append(f"主星重复: {dup}")

    if level == "verified_professional" and not chart.get("verified_by"):
        warnings.append("verified_professional 建议填写 verified_by")

    if not chart.get("source"):
        warnings.append("缺少 source")

    return {
        "ok": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "eligible_for_auto_test": level == AUTO_TEST_LEVEL and len(errors) == 0,
    }


def _fourteen_from_palaces(palaces: list[dict[str, Any]]) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for p in palaces:
        for star in p.get("main_stars") or []:
            out[star] = {"branch": p.get("branch", ""), "palace": p.get("name", "")}
    return out


def _four_from_palaces(palaces: list[dict[str, Any]]) -> dict[str, dict[str, str]]:
    mapping = {"禄": "lu", "权": "quan", "科": "ke", "忌": "ji"}
    out: dict[str, dict[str, str]] = {}
    for p in palaces:
        for t in p.get("transformations") or []:
            typ = t.get("type") or t.get("hua") or ""
            key = mapping.get(typ)
            if key and t.get("star"):
                out[key] = {"star": t["star"], "palace": p.get("name", "")}
    return out


def compare_chart(
    chart: dict[str, Any] | None = None,
    *,
    chart_id: str | None = None,
    directory: Path | None = None,
    audit: ClassicalAuditReport | None = None,
) -> CompareReport:
    """引擎结果 vs reference → ChartReferenceDiff 列表。"""
    if chart is None:
        if not chart_id:
            raise ValueError("需要 chart 或 chart_id")
        chart = load_chart(chart_id, directory)
    chart = _normalize_legacy(chart)
    cid = chart.get("id") or chart_id or ""

    birth = chart.get("birth") or {}
    if audit is None:
        audit = run_classical_audit(
            birth_date=birth["solar"],
            birth_time=birth["time"],
            gender=chart.get("gender", "male"),
            calendar_type=(chart.get("calendar") or {}).get("type", "solar"),
            location=chart.get("location") or birth.get("location"),
        )

    diffs: list[ChartReferenceDiff] = []

    def add(field: str, engine: Any, reference: Any) -> None:
        if reference in (None, "", [], {}):
            return
        if engine != reference:
            diffs.append(
                ChartReferenceDiff(
                    field=field,
                    engine=engine,
                    reference=reference,
                    impact=_impact_for_field(field),
                )
            )

    cal = chart.get("calendar") or {}
    ganzhi_ref = cal.get("ganzhi") or {}
    if isinstance(ganzhi_ref, dict):
        for k in ("year", "month", "day", "hour"):
            add(f"干支.{k}", audit.ganzhi.get(k), ganzhi_ref.get(k))
    if cal.get("lunar"):
        # 仅当引擎能产出可比对的 y-m-d 时比较；中文农历文案跳过
        eng_lunar = f"{audit.calendar_result.get('lunar_year')}-{audit.calendar_result.get('lunar_month'):02d}-{audit.calendar_result.get('lunar_day'):02d}" if audit.calendar_result.get("lunar_year") else ""
        ref_lunar = str(cal.get("lunar") or "").replace("/", "-")
        if eng_lunar and ref_lunar and "-" in ref_lunar:
            # 归一：1990-4-21 vs 1990-04-21
            def _norm_ymd(s: str) -> str:
                parts = s.split("-")
                if len(parts) != 3:
                    return s
                y, m, d = parts
                return f"{int(y)}-{int(m)}-{int(d)}"

            add("农历", _norm_ymd(eng_lunar), _norm_ymd(ref_lunar))

    meta = chart.get("meta") or {}
    add("命宫", audit.minggong, meta.get("minggong"))
    add("身宫", audit.shengong, meta.get("shengong"))
    add("五行局", audit.wuxingju, meta.get("wuxingju"))
    add("命主", audit.mingzhu, meta.get("mingzhu"))
    add("身主", audit.shenzhu, meta.get("shenzhu"))
    add("紫微位置", audit.ziwei_position, meta.get("ziwei_position"))
    add("天府位置", audit.tianfu_position, meta.get("tianfu_position"))

    fourteen = chart.get("fourteen_stars") or _fourteen_from_palaces(chart.get("palaces") or [])
    for star in MAIN_14:
        exp = fourteen.get(star)
        if not exp:
            continue
        if isinstance(exp, dict):
            add(f"十四主星.{star}.地支", audit.fourteen_star_positions.get(star), exp.get("branch"))
            add(f"十四主星.{star}.宫位", audit.fourteen_star_palaces.get(star), exp.get("palace"))
        elif exp in (
            "子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥",
        ):
            add(f"十四主星.{star}.地支", audit.fourteen_star_positions.get(star), exp)
        else:
            add(f"十四主星.{star}.宫位", audit.fourteen_star_palaces.get(star), exp)

    # palace main_stars sets
    for p in chart.get("palaces") or []:
        name = p.get("name")
        if not name:
            continue
        eng = sorted(audit.palaces_main_stars.get(name) or [])
        ref_stars = sorted(p.get("main_stars") or [])
        if ref_stars or eng:
            add(f"宫位主星.{name}", eng, ref_stars)

    ft = chart.get("four_transform") or _four_from_palaces(chart.get("palaces") or [])
    for key, label in (("lu", "禄"), ("quan", "权"), ("ke", "科"), ("ji", "忌")):
        exp = ft.get(key) or {}
        act = audit.four_transform.get(key) or {}
        if isinstance(exp, dict) and exp.get("star"):
            add(f"四化.{label}.星", act.get("star"), exp.get("star"))
            if exp.get("palace"):
                add(f"四化.{label}.宫", act.get("palace"), exp.get("palace"))

    return CompareReport(
        chart_id=cid,
        matched=len(diffs) == 0,
        diffs=diffs,
        verification_level=chart.get("verification_level", ""),
        summary={
            "minggong": audit.minggong,
            "shengong": audit.shengong,
            "wuxingju": audit.wuxingju,
            "ziwei": audit.ziwei_position,
            "critical_diffs": sum(1 for d in diffs if d.impact == "critical"),
        },
    )


def add_reference_chart(
    chart: dict[str, Any],
    directory: Path | None = None,
    *,
    write: bool = True,
) -> dict[str, Any]:
    """校验并写入新 reference（默认不自动升为 verified_professional）。"""
    d = fixture_dir(directory)
    normalized = _normalize_legacy(chart)
    if not normalized.get("verification_level"):
        normalized["verification_level"] = "pending"

    validation = validate_reference(normalized)
    if normalized["verification_level"] != "pending" and not validation["ok"]:
        raise ValueError(f"reference 校验失败: {validation['errors']}")

    cid = normalized["id"]
    if not cid:
        raise ValueError("缺少 id")

    # 写出时使用扁平 schema（保留 fourteen/four 便于对比）
    payload = {
        "id": cid,
        "source": normalized.get("source", ""),
        "verified_by": normalized.get("verified_by", ""),
        "verification_level": normalized["verification_level"],
        "gender": normalized.get("gender", "male"),
        "true_solar_time": normalized.get("true_solar_time", False),
        "location": normalized.get("location"),
        "birth": normalized.get("birth"),
        "calendar": normalized.get("calendar"),
        "meta": normalized.get("meta") or {},
        "palaces": normalized.get("palaces") or [],
    }
    if normalized.get("fourteen_stars"):
        payload["fourteen_stars"] = normalized["fourteen_stars"]
    if normalized.get("four_transform"):
        payload["four_transform"] = normalized["four_transform"]
    if normalized.get("notes"):
        payload["notes"] = normalized["notes"]

    if write:
        path = d / f"{cid}.json"
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        _upsert_index(d, payload)

    return {"path": str(d / f"{cid}.json"), "validation": validation, "chart": payload}


def _upsert_index(directory: Path, chart: dict[str, Any]) -> None:
    index_path = directory / "index.json"
    if index_path.exists():
        index = json.loads(index_path.read_text(encoding="utf-8"))
    else:
        index = {"version": "1.3.1", "description": "专业黄金验证数据集", "cases": []}

    cases = index.setdefault("cases", [])
    entry = {
        "id": chart["id"],
        "source": chart.get("source", ""),
        "verification_level": chart.get("verification_level", "pending"),
        "verified_by": chart.get("verified_by", ""),
        "birth": {
            "solar": (chart.get("birth") or {}).get("solar"),
            "time": (chart.get("birth") or {}).get("time"),
            "location": chart.get("location") or (chart.get("birth") or {}).get("location"),
        },
        "gender": chart.get("gender"),
        "calendar": (chart.get("calendar") or {}).get("type", "solar"),
        "true_solar_time": chart.get("true_solar_time", False),
        "file": f"{chart['id']}.json",
    }
    replaced = False
    for i, row in enumerate(cases):
        if row.get("id") == chart["id"]:
            cases[i] = entry
            replaced = True
            break
    if not replaced:
        cases.append(entry)
    index["version"] = "1.3.1"
    index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def export_report(directory: Path | None = None) -> dict[str, Any]:
    """汇总黄金数据集状态 + 对 verified_professional 的引擎对比。"""
    d = fixture_dir(directory)
    all_charts = list_charts(d)
    counts = {lv: 0 for lv in VERIFICATION_LEVELS}
    missing: list[str] = []
    compares: list[dict[str, Any]] = []

    for c in all_charts:
        lv = c.get("verification_level", "pending")
        counts[lv] = counts.get(lv, 0) + 1
        if lv == "pending":
            missing.append(c["id"])
            continue
        v = validate_reference(c)
        if not v["ok"]:
            missing.append(f"{c['id']}:invalid:{','.join(v['errors'])}")
            continue
        if lv == AUTO_TEST_LEVEL:
            rep = compare_chart(c)
            compares.append(rep.to_dict())

    matched = sum(1 for r in compares if r["matched"])
    total_prof = counts.get(AUTO_TEST_LEVEL, 0)
    accuracy = (matched / total_prof * 100.0) if total_prof else None

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "version": "1.3.1",
        "counts": {
            "total": len(all_charts),
            "pending": counts.get("pending", 0),
            "verified_manual": counts.get("verified_manual", 0),
            "verified_professional": total_prof,
            "verified": total_prof + counts.get("verified_manual", 0),
        },
        "accuracy": {
            "professional_match_rate": accuracy,
            "matched": matched,
            "tested": total_prof,
        },
        "missing": missing,
        "compares": compares,
        "policy": {
            "auto_test_level": AUTO_TEST_LEVEL,
            "algorithm_change_forbidden_without_multi_case_proof": True,
        },
    }


def export_report_markdown(directory: Path | None = None) -> str:
    report = export_report(directory)
    c = report["counts"]
    acc = report["accuracy"]
    rate = acc["professional_match_rate"]
    rate_s = f"{rate:.1f}%" if rate is not None else "N/A（无 verified_professional）"
    lines = [
        "# ZIWEI Golden Dataset Report",
        "",
        f"> 生成时间：{report['generated_at']}",
        f"> 版本：{report['version']}",
        "",
        "## 当前验证数量",
        "",
        f"- **verified_professional**: {c['verified_professional']}",
        f"- **verified_manual**: {c['verified_manual']}",
        f"- **pending**: {c['pending']}",
        f"- **verified (合计)**: {c['verified']}",
        f"- **total**: {c['total']}",
        "",
        "## Accuracy",
        "",
        f"- professional_match_rate: **{rate_s}**",
        f"- matched / tested: {acc['matched']} / {acc['tested']}",
        "",
        "## Missing",
        "",
    ]
    if report["missing"]:
        for m in report["missing"]:
            lines.append(f"- {m}")
    else:
        lines.append("- （无）")
    lines.extend(
        [
            "",
            "## Policy",
            "",
            "- 仅 `verified_professional` 进入自动测试",
            "- **禁止**为通过测试修改排盘公式",
            "- 仅当多个专业案例证明公式错误时才允许改算法",
            "",
        ]
    )
    return "\n".join(lines)
