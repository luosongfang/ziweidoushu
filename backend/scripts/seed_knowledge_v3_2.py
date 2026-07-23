"""Seed / migrate Knowledge Core V3.2 intelligence tables."""

from __future__ import annotations

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

BACKEND = Path(__file__).resolve().parents[1]
ROOT = BACKEND.parent
import sys

if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

load_dotenv(BACKEND / ".env", override=True)

from app.knowledge.intelligence.theory_router import _FALLBACK_ROUTES  # noqa: E402


def j(obj) -> str:
    return json.dumps(obj, ensure_ascii=False)


def _split_sql(sql: str) -> list[str]:
    out: list[str] = []
    start = 0
    i = 0
    n = len(sql)
    while i < n:
        if sql.startswith("$$", i):
            k = sql.find("$$", i + 2)
            if k < 0:
                break
            i = k + 2
            continue
        if sql[i] == ";":
            chunk = sql[start:i].strip()
            body = "\n".join(
                ln for ln in chunk.splitlines() if ln.strip() and not ln.strip().startswith("--")
            ).strip()
            if body:
                out.append(body)
            start = i + 1
        i += 1
    tail = sql[start:].strip()
    body = "\n".join(
        ln for ln in tail.splitlines() if ln.strip() and not ln.strip().startswith("--")
    ).strip()
    if body:
        out.append(body)
    return out


def classify_book(book_name: str) -> tuple[str, int, list[str], list[str], str]:
    n = book_name or ""
    if "全书" in n or "集成" in n:
        return (
            "classic_formula",
            5,
            ["星曜", "宫位", "格局", "基础"],
            ["career", "personality", "life_stage"],
            "经典总论/汇编，适合基础与综合查阅",
        )
    if "原理" in n or "宫位" in n:
        return (
            "palace_theory",
            4,
            ["宫位", "原理"],
            ["career", "relationship", "wealth"],
            "宫位与原理说明类",
        )
    if "结构" in n or "概念" in n or "讲义" in n:
        return (
            "foundation",
            4,
            ["结构", "概念", "基础"],
            ["personality", "study", "career"],
            "结构概念与教学讲义",
        )
    if "命理" in n or "精成" in n or "天纪" in n:
        return (
            "star_theory",
            4,
            ["星曜", "命理"],
            ["career", "personality", "life_stage"],
            "星曜命理深化资料",
        )
    if "股票" in n or "财" in n:
        return (
            "modern_analysis",
            2,
            ["财富", "现代应用"],
            ["wealth"],
            "现代应用向资料，仅作文化参考",
        )
    if "四化" in n:
        return ("four_transform", 4, ["四化"], ["career", "wealth", "relationship"], "四化专题")
    if "大限" in n or "流年" in n:
        return ("fortune", 3, ["大限", "流年"], ["life_stage"], "运限专题")
    return (
        "classic_formula",
        3,
        ["综合"],
        ["career", "personality"],
        "紫微经典资料画像（自动生成）",
    )


INTERP_RULES = [
    ("必有灾难", "high", "传统理论认为此阶段需要更加关注风险管理。", "禁止灾难断言"),
    ("会发生灾难", "high", "不作为确定事件预测，仅作为传统文化角度的反思参考。", "禁止灾难预测"),
    ("你一定会失败", "high", "这个方向可能存在压力与不确定性，建议分阶段验证并准备备选方案。", "禁止绝对失败"),
    ("你一定会发财", "high", "可能具备财富管理优势，需要结合现实行动与风险控制。", "禁止绝对财富"),
    ("必然离婚", "high", "关系模式可能存在需要沟通调整的地方。", "禁止婚姻宿命"),
    ("婚姻必失败", "high", "关系模式中可能存在需要沟通改善的地方。", "禁止婚姻宿命"),
    ("今年必有灾", "high", "这个阶段建议提高风险意识，提前做好心理准备与规划。", "禁止灾年断言"),
    ("破财", "medium", "提示关注资源管理、风险控制和财务规划。", "破财改资源管理"),
    ("有劫难", "high", "传统理论认为某阶段可能存在压力或挑战，可以提前做好心理准备。", "劫难改压力"),
    ("必然成功", "medium", "结果取决于准备度、执行与环境反馈，建议分阶段验证。", "弱化必然成功"),
]


def main() -> None:
    url = os.environ["DATABASE_URL"]
    if "sslmode=" not in url:
        url += "?sslmode=require"
    eng = create_engine(url, pool_pre_ping=True, isolation_level="AUTOCOMMIT")
    sql = (ROOT / "database" / "migrations" / "009_knowledge_intelligence_v3_2.sql").read_text(
        encoding="utf-8"
    )
    with eng.connect() as conn:
        for stmt in _split_sql(sql):
            conn.execute(text(stmt))
        print("migration 009 applied")

        # theory routes
        for qtype, route in _FALLBACK_ROUTES.items():
            conn.execute(
                text(
                    """
                    INSERT INTO public.theory_routes
                        (question_type, required_palaces, required_stars, required_patterns,
                         required_theories, priority, description)
                    VALUES
                        (:question_type, CAST(:required_palaces AS jsonb),
                         CAST(:required_stars AS jsonb), CAST(:required_patterns AS jsonb),
                         CAST(:required_theories AS jsonb), :priority, :description)
                    ON CONFLICT (question_type) DO UPDATE SET
                        required_palaces=EXCLUDED.required_palaces,
                        required_stars=EXCLUDED.required_stars,
                        required_patterns=EXCLUDED.required_patterns,
                        required_theories=EXCLUDED.required_theories,
                        priority=EXCLUDED.priority,
                        description=EXCLUDED.description
                    """
                ),
                {
                    "question_type": qtype,
                    "required_palaces": j(route["required_palaces"]),
                    "required_stars": j(route["required_stars"]),
                    "required_patterns": j(route["required_patterns"]),
                    "required_theories": j(route["required_theories"]),
                    "priority": route["priority"],
                    "description": route["description"],
                },
            )
        print("theory_routes", len(_FALLBACK_ROUTES))

        # interpretation rules
        conn.execute(text("DELETE FROM public.interpretation_rules"))
        for trad, risk, safe, guidance in INTERP_RULES:
            conn.execute(
                text(
                    """
                    INSERT INTO public.interpretation_rules
                        (traditional_expression, risk_level, safe_expression, guidance)
                    VALUES (:t, :r, :s, :g)
                    """
                ),
                {"t": trad, "r": risk, "s": safe, "g": guidance},
            )
        print("interpretation_rules", len(INTERP_RULES))

        # book profiles from knowledge_books / extract_summary
        book_names: list[str] = []
        try:
            book_names = [
                str(r[0])
                for r in conn.execute(text("SELECT book_name FROM public.knowledge_books")).all()
            ]
        except Exception:
            book_names = []
        if not book_names:
            summary_path = ROOT / "knowledge" / "metadata" / "extract_summary.json"
            if summary_path.exists():
                data = json.loads(summary_path.read_text(encoding="utf-8"))
                book_names = [b["book_name"] for b in data.get("books_detail") or []]

        # also write metadata/book_profiles.json without touching PDFs
        meta_dir = ROOT / "knowledge" / "books" / "metadata"
        meta_dir.mkdir(parents=True, exist_ok=True)
        profiles_json = []

        for name in book_names:
            btype, auth, topics, qs, desc = classify_book(name)
            conn.execute(
                text(
                    """
                    INSERT INTO public.book_profiles
                        (book_name, book_type, authority_level, main_topics,
                         suitable_questions, description)
                    VALUES
                        (:book_name, :book_type, :authority_level,
                         CAST(:main_topics AS jsonb), CAST(:suitable_questions AS jsonb),
                         :description)
                    ON CONFLICT (book_name) DO UPDATE SET
                        book_type=EXCLUDED.book_type,
                        authority_level=EXCLUDED.authority_level,
                        main_topics=EXCLUDED.main_topics,
                        suitable_questions=EXCLUDED.suitable_questions,
                        description=EXCLUDED.description
                    """
                ),
                {
                    "book_name": name,
                    "book_type": btype,
                    "authority_level": auth,
                    "main_topics": j(topics),
                    "suitable_questions": j(qs),
                    "description": desc,
                },
            )
            profiles_json.append(
                {
                    "book_name": name,
                    "book_type": btype,
                    "authority_level": auth,
                    "main_topics": topics,
                    "suitable_questions": qs,
                    "description": desc,
                }
            )
        (meta_dir / "book_profiles.json").write_text(
            json.dumps(profiles_json, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print("book_profiles", len(book_names))

        for t in ("book_profiles", "theory_routes", "interpretation_rules", "knowledge_evidence"):
            n = conn.execute(text(f"SELECT COUNT(*) FROM public.{t}")).scalar()
            print(f"COUNT {t}={n}")


if __name__ == "__main__":
    main()
