"""Apply & seed Knowledge Core V4.1 life cycle tables."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

BACKEND = Path(__file__).resolve().parents[1]
ROOT = BACKEND.parent
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

load_dotenv(BACKEND / ".env", override=True)

from app.knowledge.lifecycle.annual_engine import _FALLBACK_ANNUAL  # noqa: E402
from app.knowledge.lifecycle.cycle_calculator import _FALLBACK_CYCLE_RULES  # noqa: E402
from app.knowledge.lifecycle.lifecycle_advisor import _FALLBACK_TEMPLATES  # noqa: E402
from app.knowledge.lifecycle.stage_analyzer import _FALLBACK_STAGES  # noqa: E402


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


def main() -> None:
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise SystemExit("DATABASE_URL missing")
    engine = create_engine(url)
    sql = (ROOT / "database" / "migrations" / "012_life_cycle_engine.sql").read_text(
        encoding="utf-8"
    )

    with engine.begin() as conn:
        for stmt in _split_sql(sql):
            conn.execute(text(stmt))
        print("migration 012 applied")

        # clear & reseed (idempotent-ish)
        conn.execute(text("DELETE FROM public.fortune_cycle_rules"))
        for r in _FALLBACK_CYCLE_RULES:
            conn.execute(
                text(
                    """
                    INSERT INTO public.fortune_cycle_rules
                        (theory_system, gender, yin_yang, bureau_number,
                         start_age_formula, direction, description)
                    VALUES
                        (:theory_system, :gender, :yin_yang, :bureau_number,
                         :start_age_formula, :direction, :description)
                    """
                ),
                r,
            )
        # bureau-specific start age notes
        for bureau, start in ((2, 2), (3, 3), (4, 4), (5, 5), (6, 6)):
            conn.execute(
                text(
                    """
                    INSERT INTO public.fortune_cycle_rules
                        (theory_system, gender, yin_yang, bureau_number,
                         start_age_formula, direction, description)
                    VALUES
                        ('sanhe', NULL, NULL, :bureau, 'bureau_number', NULL,
                         :desc)
                    """
                ),
                {
                    "bureau": bureau,
                    "desc": f"五行局起运：{bureau}局自{start}岁起大限，每限十年",
                },
            )

        for s in _FALLBACK_STAGES:
            conn.execute(
                text(
                    """
                    INSERT INTO public.life_stage_models
                        (stage_name, age_range, focus_dimensions, advisor_template)
                    VALUES
                        (:name, CAST(:ar AS jsonb), CAST(:fd AS jsonb), :tmpl)
                    ON CONFLICT (stage_name) DO UPDATE SET
                        age_range = EXCLUDED.age_range,
                        focus_dimensions = EXCLUDED.focus_dimensions,
                        advisor_template = EXCLUDED.advisor_template
                    """
                ),
                {
                    "name": s["stage_name"],
                    "ar": j(s["age_range"]),
                    "fd": j(s["focus_dimensions"]),
                    "tmpl": s["advisor_template"],
                },
            )

        conn.execute(text("DELETE FROM public.annual_influence_rules"))
        for r in _FALLBACK_ANNUAL:
            conn.execute(
                text(
                    """
                    INSERT INTO public.annual_influence_rules
                        (year_type, trigger_rule, influence_dimension, description)
                    VALUES
                        (:year_type, CAST(:trigger AS jsonb), :dim, :desc)
                    """
                ),
                {
                    "year_type": r["year_type"],
                    "trigger": j(r["trigger_rule"]),
                    "dim": r["influence_dimension"],
                    "desc": r["description"],
                },
            )

        for scenario, tmpl in _FALLBACK_TEMPLATES.items():
            if scenario == "default":
                continue
            conn.execute(
                text(
                    """
                    INSERT INTO public.cycle_analysis_templates
                        (scenario, strength_template, risk_template, growth_template)
                    VALUES
                        (:scenario, :strength, :risk, :growth)
                    ON CONFLICT (scenario) DO UPDATE SET
                        strength_template = EXCLUDED.strength_template,
                        risk_template = EXCLUDED.risk_template,
                        growth_template = EXCLUDED.growth_template
                    """
                ),
                {
                    "scenario": scenario,
                    "strength": tmpl["strength_template"],
                    "risk": tmpl["risk_template"],
                    "growth": tmpl["growth_template"],
                },
            )

        for t in (
            "fortune_cycle_rules",
            "life_stage_models",
            "annual_influence_rules",
            "cycle_analysis_templates",
        ):
            n = conn.execute(text(f"SELECT COUNT(*) FROM {t}")).scalar()
            print(f"COUNT {t}={n}")


if __name__ == "__main__":
    main()
