"""Apply Knowledge Core schema + seeds to Supabase."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text

BACKEND = Path(__file__).resolve().parents[1]
ROOT = BACKEND.parent
sys.path.insert(0, str(BACKEND))
load_dotenv(BACKEND / ".env", override=True)

from scripts.bootstrap_supabase import split_sql  # noqa: E402

DATABASE_URL = os.environ["DATABASE_URL"]
SCHEMA = ROOT / "database" / "knowledge_schema.sql"
SEED_DIR = ROOT / "database" / "knowledge_seed"


def run_file(conn, path: Path) -> tuple[int, int]:
    sql = path.read_text(encoding="utf-8-sig")
    ok = fail = 0
    for stmt in split_sql(sql):
        try:
            conn.execute(text(stmt))
            ok += 1
        except Exception as exc:  # noqa: BLE001
            msg = str(exc).lower()
            if "already exists" in msg or "duplicate" in msg:
                ok += 1
                continue
            fail += 1
            print("FAIL", path.name, type(exc).__name__, repr(str(exc)[:180]))
    return ok, fail


def main() -> int:
    eng = create_engine(DATABASE_URL, pool_pre_ping=True, isolation_level="AUTOCOMMIT")
    files = [SCHEMA] + [
        SEED_DIR / name
        for name in [
            "theory_knowledge.sql",
            "stars_knowledge.sql",
            "palace_knowledge.sql",
            "ziwei_patterns.sql",
            "four_transform_knowledge.sql",
            "life_question_models.sql",
            "safety_expression_rules.sql",
        ]
    ]
    with eng.connect() as conn:
        for path in files:
            ok, fail = run_file(conn, path)
            print(f"{path.name}: ok={ok} fail={fail}")

    tables = set(inspect(eng).get_table_names(schema="public"))
    needed = [
        "theory_knowledge",
        "stars_knowledge",
        "palace_knowledge",
        "ziwei_patterns",
        "four_transform_knowledge",
        "life_question_models",
        "safety_expression_rules",
    ]
    with eng.connect() as conn:
        for t in needed:
            if t not in tables:
                print(t, "MISSING")
                continue
            n = conn.execute(text(f'SELECT COUNT(*) FROM public."{t}"')).scalar()
            print(f"COUNT {t}={n}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
