"""Apply & seed Knowledge Core V4.0 Phase1 multi-theory tables."""

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

from app.knowledge.multitheory.theory_dispatcher import _FALLBACK_DISPATCH  # noqa: E402
from app.knowledge.multitheory.theory_registry import FALLBACK_SYSTEMS  # noqa: E402
from app.knowledge.multitheory.synthesis_engine import _FALLBACK_RULES  # noqa: E402


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
    sql_path = ROOT / "database" / "migrations" / "011_multi_theory_engine.sql"
    sql = sql_path.read_text(encoding="utf-8")

    with engine.begin() as conn:
        for stmt in _split_sql(sql):
            conn.execute(text(stmt))
        print("migration 011 applied")

        # systems
        for s in FALLBACK_SYSTEMS:
            conn.execute(
                text(
                    """
                    INSERT INTO public.theory_systems (name, type, description, authority_level, active)
                    VALUES (:name, :type, :description, :authority_level, :active)
                    ON CONFLICT (name) DO UPDATE SET
                        type = EXCLUDED.type,
                        description = EXCLUDED.description,
                        authority_level = EXCLUDED.authority_level,
                        active = EXCLUDED.active
                    """
                ),
                s,
            )

        id_by_type = {
            r["type"]: r["id"]
            for r in conn.execute(
                text("SELECT id::text AS id, type FROM public.theory_systems")
            ).mappings()
        }

        # mappings
        for qtype, rows in _FALLBACK_DISPATCH.items():
            for row in rows:
                tid = id_by_type.get(row["theory_type"])
                if not tid:
                    continue
                conn.execute(
                    text(
                        """
                        INSERT INTO public.theory_rules_mapping
                            (theory_id, question_type, required_palaces, required_stars,
                             required_patterns, priority, example)
                        VALUES
                            (CAST(:tid AS uuid), :qtype, CAST(:palaces AS jsonb),
                             CAST(:stars AS jsonb), CAST(:patterns AS jsonb),
                             :priority, :example)
                        ON CONFLICT (theory_id, question_type) DO UPDATE SET
                            required_palaces = EXCLUDED.required_palaces,
                            required_stars = EXCLUDED.required_stars,
                            required_patterns = EXCLUDED.required_patterns,
                            priority = EXCLUDED.priority,
                            example = EXCLUDED.example
                        """
                    ),
                    {
                        "tid": tid,
                        "qtype": qtype,
                        "palaces": j(row.get("required_palaces") or []),
                        "stars": j(row.get("required_stars") or []),
                        "patterns": j(row.get("required_patterns") or []),
                        "priority": int(row.get("priority") or 100),
                        "example": row.get("example"),
                    },
                )

        # synthesis rules
        for scenario, rule in _FALLBACK_RULES.items():
            if scenario == "default":
                continue
            conn.execute(
                text(
                    """
                    INSERT INTO public.decision_synthesis_rules
                        (scenario, input_theories, synthesis_logic, output_template)
                    VALUES
                        (:scenario, CAST(:theories AS jsonb), :logic, CAST(:tmpl AS jsonb))
                    ON CONFLICT (scenario) DO UPDATE SET
                        input_theories = EXCLUDED.input_theories,
                        synthesis_logic = EXCLUDED.synthesis_logic,
                        output_template = EXCLUDED.output_template
                    """
                ),
                {
                    "scenario": scenario,
                    "theories": j(rule.get("input_theories") or []),
                    "logic": rule.get("synthesis_logic"),
                    "tmpl": j(rule.get("output_template") or {}),
                },
            )

        for t in (
            "theory_systems",
            "theory_rules_mapping",
            "theory_analysis_results",
            "decision_synthesis_rules",
        ):
            n = conn.execute(text(f"SELECT COUNT(*) FROM {t}")).scalar()
            print(f"COUNT {t}={n}")


if __name__ == "__main__":
    main()
