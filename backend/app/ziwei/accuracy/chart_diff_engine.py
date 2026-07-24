"""ChartDiffEngine — 专业命盘字段级差异引擎（只读检测）。

比较范围：基础信息 / 十二宫 / 主辅煞杂星 / 四化 / 运限。
不调用、不修改任何排盘算法。
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

Impact = Literal["critical", "major", "minor"]

MAIN_14: tuple[str, ...] = (
    "紫微", "天机", "太阳", "武曲", "天同", "廉贞",
    "天府", "太阴", "贪狼", "巨门", "天相", "天梁", "七杀", "破军",
)
AUX_6: tuple[str, ...] = ("左辅", "右弼", "文昌", "文曲", "天魁", "天钺")
SHA_6: tuple[str, ...] = ("擎羊", "陀罗", "火星", "铃星", "地空", "地劫")
ZA_9: tuple[str, ...] = (
    "天姚", "红鸾", "天喜", "天刑", "孤辰", "寡宿", "华盖", "天哭", "天虚",
)

PALACE_NAMES: tuple[str, ...] = (
    "命宫", "兄弟", "夫妻", "子女", "财帛", "疾厄",
    "迁移", "交友", "官禄", "田宅", "福德", "父母",
)


@dataclass
class DiffItem:
    field: str
    engine: Any
    reference: Any
    impact: Impact
    category: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DiffResult:
    diffs: list[DiffItem] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)  # reference 缺字段时跳过

    def by_impact(self) -> dict[str, list[dict[str, Any]]]:
        out: dict[str, list[dict[str, Any]]] = {
            "critical": [],
            "major": [],
            "minor": [],
        }
        for d in self.diffs:
            out[d.impact].append(d.to_dict())
        return out

    def accuracy_score(self) -> float:
        """0–100：critical 重罚，major 次之，minor 轻罚。"""
        if not self.diffs:
            return 100.0
        penalty = 0.0
        for d in self.diffs:
            if d.impact == "critical":
                penalty += 8.0
            elif d.impact == "major":
                penalty += 3.0
            else:
                penalty += 1.0
        return max(0.0, round(100.0 - penalty, 2))


def _as_dict(obj: Any) -> dict[str, Any]:
    if obj is None:
        return {}
    if isinstance(obj, dict):
        return obj
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    if hasattr(obj, "__dict__"):
        return {k: v for k, v in vars(obj).items() if not k.startswith("_")}
    return {}


def _get(d: dict[str, Any], *keys: str, default: Any = None) -> Any:
    for k in keys:
        if k in d and d[k] not in (None, ""):
            return d[k]
    return default


def _norm_star_map(chart: dict[str, Any]) -> dict[str, dict[str, str]]:
    """统一为 star → {branch, palace}。"""
    out: dict[str, dict[str, str]] = {}

    # fourteen_stars / star maps
    for key in ("fourteen_stars", "stars_by_name", "star_positions"):
        block = chart.get(key)
        if isinstance(block, dict):
            for name, val in block.items():
                if isinstance(val, dict):
                    out[name] = {
                        "branch": str(val.get("branch") or ""),
                        "palace": str(val.get("palace") or ""),
                    }
                elif isinstance(val, str):
                    # 地支或宫名
                    out[name] = {"branch": val, "palace": ""}

    # Professional / V2 stars index
    stars = chart.get("stars") or {}
    for bucket in ("main", "main_stars", "lucky", "six_lucky", "sha", "six_sha", "others", "auxiliary", "all"):
        items = stars.get(bucket) if isinstance(stars, dict) else None
        if not isinstance(items, list):
            continue
        for s in items:
            if not isinstance(s, dict):
                continue
            name = s.get("name") or s.get("star")
            if not name:
                continue
            out[name] = {
                "branch": str(s.get("branch") or out.get(name, {}).get("branch") or ""),
                "palace": str(s.get("palace") or out.get(name, {}).get("palace") or ""),
            }

    # palaces[*].main_stars / lucky / evil / minor
    for p in _iter_palaces(chart):
        pname = p.get("name") or p.get("palace_name") or p.get("palaceName") or ""
        branch = p.get("branch") or ""
        for key in (
            "main_stars",
            "lucky_stars",
            "sha_stars",
            "za_stars",
            "evil_stars",
            "minor_stars",
            "stars",
        ):
            for s in p.get(key) or []:
                if isinstance(s, str):
                    name, br, pal = s, branch, pname
                elif isinstance(s, dict):
                    name = s.get("name") or s.get("star") or ""
                    br = s.get("branch") or branch
                    pal = s.get("palace") or pname
                else:
                    continue
                if name:
                    out[name] = {"branch": str(br), "palace": str(pal)}

    # audit-style flat maps
    for name, br in (chart.get("fourteen_star_positions") or {}).items():
        out.setdefault(name, {"branch": "", "palace": ""})
        out[name]["branch"] = str(br)
    for name, pal in (chart.get("fourteen_star_palaces") or {}).items():
        out.setdefault(name, {"branch": "", "palace": ""})
        out[name]["palace"] = str(pal)

    return out


def _norm_meta(chart: dict[str, Any]) -> dict[str, Any]:
    meta = dict(chart.get("meta") or {})
    return {
        "minggong": _get(meta, "minggong", "mingGong", "ming_gong", default="")
        or _get(chart, "minggong", "mingGong", default=""),
        "shengong": _get(meta, "shengong", "shenGong", "shen_gong", default="")
        or _get(chart, "shengong", "shenGong", default=""),
        "wuxingju": _get(meta, "wuxingju", "wuxingJu", "wuxing_ju", default="")
        or _get(chart, "wuxingju", default=""),
        "mingzhu": _get(meta, "mingzhu", "mingZhu", "ming_zhu", default=""),
        "shenzhu": _get(meta, "shenzhu", "shenZhu", "shen_zhu", default=""),
        "ziwei_position": _get(
            meta, "ziwei_position", "ziweiBranch", "ziwei_branch", default=""
        ),
        "tianfu_position": _get(
            meta, "tianfu_position", "tianfuBranch", "tianfu_branch", default=""
        ),
        "minggong_ganzhi": _get(
            meta, "minggong_ganzhi", "mingGongGanZhi", "ming_gong_ganzhi", default=""
        ),
    }


def _norm_ganzhi(chart: dict[str, Any]) -> dict[str, str]:
    cal = chart.get("calendar") or {}
    birth = chart.get("birth") or {}
    g = (
        cal.get("ganzhi")
        or birth.get("ganzhi")
        or chart.get("ganzhi")
        or chart.get("bazi")
        or {}
    )
    if not isinstance(g, dict):
        g = {}
    # V3 birth fields
    if not g.get("year") and isinstance(birth, dict):
        g = {
            "year": birth.get("ganzhi_year") or g.get("year") or "",
            "month": birth.get("ganzhi_month") or g.get("month") or "",
            "day": birth.get("ganzhi_day") or g.get("day") or "",
            "hour": birth.get("ganzhi_hour") or g.get("hour") or "",
        }
    return {
        "year": str(g.get("year") or ""),
        "month": str(g.get("month") or ""),
        "day": str(g.get("day") or ""),
        "hour": str(g.get("hour") or ""),
    }


def _norm_lunar(chart: dict[str, Any]) -> str:
    cal = chart.get("calendar") or {}
    birth = chart.get("birth") or {}
    lunar = cal.get("lunar") or birth.get("lunar") or birth.get("lunar_date") or chart.get("lunar_date") or ""
    s = str(lunar).replace("/", "-").strip()
    if not s or "-" not in s:
        return s
    parts = s.split("-")
    if len(parts) != 3:
        return s
    try:
        y, m, d = (int(parts[0]), int(parts[1]), int(parts[2]))
        return f"{y}-{m}-{d}"
    except ValueError:
        return s


def _iter_palaces(chart: dict[str, Any]) -> list[dict[str, Any]]:
    palaces = chart.get("palaces") or []
    if isinstance(palaces, dict):
        return [v for v in palaces.values() if isinstance(v, dict)]
    return [p for p in palaces if isinstance(p, dict)]


def _norm_palaces(chart: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for p in _iter_palaces(chart):
        name = p.get("name") or p.get("palace_name") or p.get("palaceName") or ""
        if not name:
            continue
        main = []
        for s in p.get("main_stars") or []:
            if isinstance(s, str):
                main.append(s)
            elif isinstance(s, dict):
                n = s.get("name") or s.get("star")
                if n:
                    main.append(n)
        out[name] = {
            "name": name,
            "branch": p.get("branch") or "",
            "ganzhi": p.get("ganzhi") or p.get("stem_branch") or "",
            "stem": p.get("stem") or p.get("tian_gan") or "",
            "opposite": p.get("opposite") or p.get("dui_gong") or "",
            "sanhe": list(p.get("sanhe") or p.get("triad") or []),
            "main_stars": sorted(main),
            "transformations": p.get("transformations") or [],
            "daxian": p.get("daxian"),
            "liunian": p.get("liunian"),
            "xiaoxian": p.get("xiaoxian"),
        }
    return out


def _norm_four_transform(chart: dict[str, Any]) -> dict[str, Any]:
    ft = chart.get("four_transform") or chart.get("fourTransform") or {}
    if not isinstance(ft, dict):
        ft = {}

    def block(obj: Any) -> dict[str, str]:
        if not isinstance(obj, dict):
            return {}
        out = {}
        for k in ("lu", "quan", "ke", "ji"):
            v = obj.get(k)
            if isinstance(v, dict):
                out[k] = str(v.get("star") or v.get("name") or "")
            elif v:
                out[k] = str(v)
            else:
                out[k] = ""
        return out

    birth = ft.get("birth_transform") or ft.get("year") or ft
    # gold fixture: lu/quan/ke/ji at top of four_transform
    if any(k in ft for k in ("lu", "quan", "ke", "ji")) and "birth_transform" not in ft:
        birth = ft

    # from palace transformations
    if not any(block(birth).values()):
        derived: dict[str, str] = {}
        mapping = {"禄": "lu", "权": "quan", "科": "ke", "忌": "ji"}
        for p in _iter_palaces(chart):
            for t in (p.get("transformations") or []):
                if not isinstance(t, dict):
                    continue
                key = mapping.get(t.get("type") or t.get("hua") or "")
                if key and t.get("star"):
                    derived[key] = t["star"]
        if derived:
            birth = derived

    return {
        "birth": block(birth),
        "daxian": block(ft.get("daxian_transform") or ft.get("daxian") or {}),
        "liunian": block(ft.get("liunian_transform") or ft.get("liunian") or {}),
        "self": ft.get("self_transform") or ft.get("self") or [],
    }


def _norm_fortune(chart: dict[str, Any]) -> dict[str, Any]:
    fortune = chart.get("fortune") or chart.get("yun") or {}
    if not isinstance(fortune, dict):
        fortune = {}
    return {
        "daxian": fortune.get("daxian") or chart.get("daxian") or {},
        "liunian": fortune.get("liuxian") or fortune.get("liunian") or chart.get("liunian") or {},
        "xiaoxian": fortune.get("xiaoxian") or chart.get("xiaoxian") or {},
    }


def normalize_chart(chart: Any) -> dict[str, Any]:
    """将 engine / reference / audit / V2 / V3 / gold fixture 规范为可比对结构。"""
    raw = _as_dict(chart)
    # V1.4.1 expected wrapper
    if raw.get("expected") and isinstance(raw["expected"], dict):
        exp = raw["expected"]
        merged = {
            **raw,
            "meta": exp.get("meta") or raw.get("meta") or {},
            "palaces": exp.get("palaces") or raw.get("palaces") or [],
            "calendar": exp.get("calendar") or raw.get("calendar") or {},
            "four_transform": exp.get("four_transform") or raw.get("four_transform") or {},
            "fortune": exp.get("fortune") or raw.get("fortune") or {},
        }
        raw = merged
    # unwrap reference_data
    if raw.get("reference_data") and not raw.get("meta") and not raw.get("palaces"):
        inner = dict(raw["reference_data"])
        inner["birth"] = raw.get("birth") or inner.get("birth")
        inner["calendar"] = raw.get("calendar") or inner.get("calendar")
        inner["id"] = raw.get("id")
        raw = {**raw, **inner}

    meta = _norm_meta(raw)
    return {
        "id": raw.get("id") or "",
        "lunar": _norm_lunar(raw),
        "ganzhi": _norm_ganzhi(raw),
        "meta": meta,
        "palaces": _norm_palaces(raw),
        "stars": _norm_star_map(raw),
        "four_transform": _norm_four_transform(raw),
        "fortune": _norm_fortune(raw),
        "_raw_keys": sorted(raw.keys()),
    }


class ChartDiffEngine:
    """字段级差异引擎。reference 缺字段 → skip（不记 diff）。"""

    def __init__(self, *, compare_aux: bool = True, compare_fortune: bool = True) -> None:
        self.compare_aux = compare_aux
        self.compare_fortune = compare_fortune

    def compare(self, engine_chart: Any, reference_chart: Any) -> DiffResult:
        eng = normalize_chart(engine_chart)
        ref = normalize_chart(reference_chart)
        result = DiffResult()

        self._compare_basics(eng, ref, result)
        self._compare_palaces(eng, ref, result)
        self._compare_stars(eng, ref, result)
        self._compare_four_transform(eng, ref, result)
        if self.compare_fortune:
            self._compare_fortune(eng, ref, result)
        return result

    def _add(
        self,
        result: DiffResult,
        *,
        field: str,
        engine: Any,
        reference: Any,
        impact: Impact,
        category: str,
        allow_empty_reference: bool = False,
    ) -> None:
        if reference is None:
            result.skipped.append(field)
            return
        if reference in ("", {}, ()) and not allow_empty_reference:
            result.skipped.append(field)
            return
        if isinstance(reference, list) and len(reference) == 0 and not allow_empty_reference:
            result.skipped.append(field)
            return
        if engine != reference:
            if isinstance(engine, list) and isinstance(reference, list):
                if sorted(engine) == sorted(reference):
                    return
            result.diffs.append(
                DiffItem(
                    field=field,
                    engine=engine,
                    reference=reference,
                    impact=impact,
                    category=category,
                )
            )

    def _compare_basics(self, eng: dict, ref: dict, result: DiffResult) -> None:
        cat = "基础信息"
        if ref.get("lunar"):
            self._add(
                result,
                field="农历",
                engine=eng.get("lunar"),
                reference=ref.get("lunar"),
                impact="minor",
                category=cat,
            )
        for k, label in (
            ("year", "四柱.年"),
            ("month", "四柱.月"),
            ("day", "四柱.日"),
            ("hour", "四柱.时"),
        ):
            self._add(
                result,
                field=label,
                engine=(eng.get("ganzhi") or {}).get(k),
                reference=(ref.get("ganzhi") or {}).get(k),
                impact="critical",
                category=cat,
            )
        em, rm = eng.get("meta") or {}, ref.get("meta") or {}
        for key, label, impact in (
            ("wuxingju", "五行局", "critical"),
            ("minggong", "命宫", "critical"),
            ("shengong", "身宫", "critical"),
            ("mingzhu", "命主", "minor"),
            ("shenzhu", "身主", "minor"),
            ("ziwei_position", "紫微位置", "critical"),
            ("tianfu_position", "天府位置", "critical"),
        ):
            self._add(
                result,
                field=label,
                engine=em.get(key),
                reference=rm.get(key),
                impact=impact,  # type: ignore[arg-type]
                category=cat,
            )

    def _compare_palaces(self, eng: dict, ref: dict, result: DiffResult) -> None:
        cat = "十二宫"
        ep, rp = eng.get("palaces") or {}, ref.get("palaces") or {}
        if not rp:
            result.skipped.append("十二宫")
            return
        for name, rp_item in rp.items():
            ep_item = ep.get(name) or {}
            self._add(
                result,
                field=f"宫.{name}.地支",
                engine=ep_item.get("branch"),
                reference=rp_item.get("branch"),
                impact="critical",
                category=cat,
            )
            # 天干：从 ganzhi 首字或 stem
            ref_stem = rp_item.get("stem") or (
                (rp_item.get("ganzhi") or "")[:1] if rp_item.get("ganzhi") else ""
            )
            eng_stem = ep_item.get("stem") or (
                (ep_item.get("ganzhi") or "")[:1] if ep_item.get("ganzhi") else ""
            )
            self._add(
                result,
                field=f"宫.{name}.天干",
                engine=eng_stem,
                reference=ref_stem,
                impact="minor",
                category=cat,
            )
            self._add(
                result,
                field=f"宫.{name}.对宫",
                engine=ep_item.get("opposite"),
                reference=rp_item.get("opposite"),
                impact="minor",
                category=cat,
            )
            self._add(
                result,
                field=f"宫.{name}.三合",
                engine=list(ep_item.get("sanhe") or []),
                reference=list(rp_item.get("sanhe") or []),
                impact="minor",
                category=cat,
            )
            self._add(
                result,
                field=f"宫.{name}.主星",
                engine=list(ep_item.get("main_stars") or []),
                reference=list(rp_item.get("main_stars") or []),
                impact="critical",
                category=cat,
                allow_empty_reference=True,
            )

    def _compare_stars(self, eng: dict, ref: dict, result: DiffResult) -> None:
        es, rs = eng.get("stars") or {}, ref.get("stars") or {}

        def cmp_group(names: tuple[str, ...], impact: Impact, category: str) -> None:
            for name in names:
                r = rs.get(name)
                if not r or (not r.get("branch") and not r.get("palace")):
                    # try derive from ref palaces already in stars map empty
                    result.skipped.append(f"星曜.{name}")
                    continue
                e = es.get(name) or {}
                if r.get("branch"):
                    self._add(
                        result,
                        field=f"星曜.{name}.地支",
                        engine=e.get("branch"),
                        reference=r.get("branch"),
                        impact=impact,
                        category=category,
                    )
                if r.get("palace"):
                    self._add(
                        result,
                        field=f"星曜.{name}.宫位",
                        engine=e.get("palace"),
                        reference=r.get("palace"),
                        impact=impact,
                        category=category,
                    )

        cmp_group(MAIN_14, "critical", "十四主星")
        if self.compare_aux:
            cmp_group(AUX_6, "major", "辅星")
            cmp_group(SHA_6, "major", "煞星")
            cmp_group(ZA_9, "minor", "杂曜")

    def _compare_four_transform(self, eng: dict, ref: dict, result: DiffResult) -> None:
        cat = "四化"
        eft, rft = eng.get("four_transform") or {}, ref.get("four_transform") or {}
        for scope, impact in (
            ("birth", "major"),
            ("daxian", "major"),
            ("liunian", "major"),
        ):
            rb = rft.get(scope) or {}
            eb = eft.get(scope) or {}
            if not any(rb.get(k) for k in ("lu", "quan", "ke", "ji")):
                result.skipped.append(f"四化.{scope}")
                continue
            for k, label in (("lu", "禄"), ("quan", "权"), ("ke", "科"), ("ji", "忌")):
                self._add(
                    result,
                    field=f"四化.{scope}.{label}",
                    engine=eb.get(k),
                    reference=rb.get(k),
                    impact=impact,  # type: ignore[arg-type]
                    category=cat,
                )
        # 自化
        rself = rft.get("self") or []
        if rself:
            eself = eft.get("self") or []
            self._add(
                result,
                field="四化.自化",
                engine=eself,
                reference=rself,
                impact="major",
                category=cat,
            )
        else:
            result.skipped.append("四化.自化")

    def _compare_fortune(self, eng: dict, ref: dict, result: DiffResult) -> None:
        cat = "运限"
        ef, rf = eng.get("fortune") or {}, ref.get("fortune") or {}

        def current_of(block: Any) -> dict[str, Any]:
            if not isinstance(block, dict):
                return {}
            cur = block.get("current") or {}
            if cur:
                return cur
            return block

        # 大限宫位 / 年龄
        rd, ed = current_of(rf.get("daxian")), current_of(ef.get("daxian"))
        self._add(
            result,
            field="运限.大限宫位",
            engine=ed.get("palace") or ed.get("palace_name") or ed.get("branch"),
            reference=(rd.get("palace") or rd.get("palace_name") or rd.get("branch")) or None,
            impact="major",
            category=cat,
        )
        self._add(
            result,
            field="运限.大限年龄",
            engine=ed.get("age") or ed.get("age_range") or ed.get("start_age"),
            reference=(rd.get("age") or rd.get("age_range") or rd.get("start_age")) or None,
            impact="major",
            category=cat,
        )

        rl, el = current_of(rf.get("liunian")), current_of(ef.get("liunian"))
        self._add(
            result,
            field="运限.流年位置",
            engine=el.get("palace") or el.get("branch") or el.get("year"),
            reference=(rl.get("palace") or rl.get("branch") or rl.get("year")) or None,
            impact="major",
            category=cat,
        )

        rx, ex = current_of(rf.get("xiaoxian")), current_of(ef.get("xiaoxian"))
        self._add(
            result,
            field="运限.小限",
            engine=ex.get("palace") or ex.get("branch") or ex or None,
            reference=(rx.get("palace") or rx.get("branch") or (rx if rx else None)),
            impact="minor",
            category=cat,
        )
