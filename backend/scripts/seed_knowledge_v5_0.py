"""Apply & seed Knowledge Core V5.0 decision intelligence tables."""

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

from app.knowledge.decision.decision_models import (  # noqa: E402
    DECISION_SCENARIOS,
    DIMENSION_RULES,
    PROCESS_STEPS,
    SAFETY_RULES,
)


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
    sql = (ROOT / "database" / "migrations" / "013_decision_intelligence.sql").read_text(
        encoding="utf-8"
    )

    with engine.begin() as conn:
        for stmt in _split_sql(sql):
            conn.execute(text(stmt))
        print("migration 013 applied")

        for sc in DECISION_SCENARIOS:
            conn.execute(
                text(
                    """
                    INSERT INTO public.decision_models
                        (scenario_name, scenario_type, description,
                         required_palaces, required_stars, required_patterns,
                         required_cycles, decision_dimensions, risk_dimensions,
                         growth_dimensions, safety_level, version)
                    VALUES
                        (:name, :stype, :desc,
                         CAST(:palaces AS jsonb), CAST(:stars AS jsonb), CAST(:patterns AS jsonb),
                         CAST(:cycles AS jsonb), CAST(:ddim AS jsonb), CAST(:rdim AS jsonb),
                         CAST(:gdim AS jsonb), :safety, '5.0.0')
                    ON CONFLICT (scenario_name) DO UPDATE SET
                        scenario_type = EXCLUDED.scenario_type,
                        description = EXCLUDED.description,
                        required_palaces = EXCLUDED.required_palaces,
                        required_stars = EXCLUDED.required_stars,
                        required_patterns = EXCLUDED.required_patterns,
                        required_cycles = EXCLUDED.required_cycles,
                        decision_dimensions = EXCLUDED.decision_dimensions,
                        risk_dimensions = EXCLUDED.risk_dimensions,
                        growth_dimensions = EXCLUDED.growth_dimensions,
                        safety_level = EXCLUDED.safety_level
                    """
                ),
                {
                    "name": sc["scenario_name"],
                    "stype": sc.get("scenario_type"),
                    "desc": sc.get("description"),
                    "palaces": j(sc.get("required_palaces") or []),
                    "stars": j(sc.get("required_stars") or []),
                    "patterns": j(sc.get("required_patterns") or []),
                    "cycles": j(sc.get("required_cycles") or []),
                    "ddim": j(sc.get("decision_dimensions") or []),
                    "rdim": j(sc.get("risk_dimensions") or []),
                    "gdim": j(sc.get("growth_dimensions") or []),
                    "safety": sc.get("safety_level") or "high",
                },
            )

        conn.execute(text("DELETE FROM public.decision_dimension_rules"))
        for r in DIMENSION_RULES:
            conn.execute(
                text(
                    """
                    INSERT INTO public.decision_dimension_rules
                        (dimension, traditional_factor, positive_expression,
                         challenge_expression, growth_direction, source_reference, version)
                    VALUES
                        (:dimension, :factor, :pos, :chal, :growth, :src, '5.0.0')
                    """
                ),
                {
                    "dimension": r["dimension"],
                    "factor": r["traditional_factor"],
                    "pos": r.get("positive_expression"),
                    "chal": r.get("challenge_expression"),
                    "growth": r.get("growth_direction"),
                    "src": r.get("source_reference"),
                },
            )

        conn.execute(text("DELETE FROM public.decision_process_templates"))
        scenarios = [s["scenario_name"] for s in DECISION_SCENARIOS] + ["default"]
        for scen in scenarios:
            for step in PROCESS_STEPS:
                conn.execute(
                    text(
                        """
                        INSERT INTO public.decision_process_templates
                            (scenario, step_order, title, content_template, safety_expression)
                        VALUES
                            (:scenario, :ord, :title, :content, :safety)
                        """
                    ),
                    {
                        "scenario": scen,
                        "ord": step["step_order"],
                        "title": step["title"],
                        "content": step["content_template"],
                        "safety": step["safety_expression"],
                    },
                )

        conn.execute(text("DELETE FROM public.decision_safety_rules"))
        for r in SAFETY_RULES:
            conn.execute(
                text(
                    """
                    INSERT INTO public.decision_safety_rules
                        (forbidden_expression, safe_expression, reason, risk_level, version)
                    VALUES
                        (:bad, :good, :reason, :level, '5.0.0')
                    """
                ),
                {
                    "bad": r["forbidden_expression"],
                    "good": r["safe_expression"],
                    "reason": r.get("reason"),
                    "level": r.get("risk_level") or "high",
                },
            )

        for t in (
            "decision_models",
            "decision_dimension_rules",
            "decision_process_templates",
            "decision_history",
            "decision_safety_rules",
        ):
            n = conn.execute(text(f"SELECT COUNT(*) FROM {t}")).scalar()
            print(f"COUNT {t}={n}")


if __name__ == "__main__":
    main()
