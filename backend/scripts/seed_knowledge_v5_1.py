"""Apply & seed Knowledge Core V5.1 decision feedback tables."""

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

from app.knowledge.decision_feedback.path_simulator import _FALLBACK_PATHS  # noqa: E402


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
    sql = (ROOT / "database" / "migrations" / "014_decision_feedback.sql").read_text(
        encoding="utf-8"
    )

    with engine.begin() as conn:
        for stmt in _split_sql(sql):
            conn.execute(text(stmt))
        print("migration 014 applied")

        for scenario, paths in _FALLBACK_PATHS.items():
            for path_type, data in paths.items():
                conn.execute(
                    text(
                        """
                        INSERT INTO public.decision_path_models
                            (scenario, path_type, conditions, advantages, risks,
                             recommended_actions, reflection_questions, version)
                        VALUES
                            (:scenario, :ptype, CAST(:cond AS jsonb), CAST(:adv AS jsonb),
                             CAST(:risks AS jsonb), CAST(:acts AS jsonb),
                             CAST(:refl AS jsonb), '5.1.0')
                        ON CONFLICT (scenario, path_type) DO UPDATE SET
                            conditions = EXCLUDED.conditions,
                            advantages = EXCLUDED.advantages,
                            risks = EXCLUDED.risks,
                            recommended_actions = EXCLUDED.recommended_actions,
                            reflection_questions = EXCLUDED.reflection_questions,
                            version = EXCLUDED.version
                        """
                    ),
                    {
                        "scenario": scenario,
                        "ptype": path_type,
                        "cond": j(data.get("conditions") or []),
                        "adv": j(data.get("advantages") or []),
                        "risks": j(data.get("risks") or []),
                        "acts": j(data.get("recommended_actions") or []),
                        "refl": j(data.get("reflection_questions") or []),
                    },
                )

        for t in (
            "decision_feedback",
            "decision_path_models",
            "knowledge_reference_map",
            "user_decision_profile",
        ):
            n = conn.execute(text(f"SELECT COUNT(*) FROM {t}")).scalar()
            print(f"COUNT {t}={n}")


if __name__ == "__main__":
    main()
