"""Fix star_placement_rules table (quote reserved offset/condition) + seed."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.bootstrap_supabase import split_sql  # noqa: E402

BACKEND = Path(__file__).resolve().parents[1]
ROOT = BACKEND.parent
load_dotenv(BACKEND / ".env", override=True)

eng = create_engine(os.environ["DATABASE_URL"], pool_pre_ping=True, isolation_level="AUTOCOMMIT")

DDL = """
CREATE TABLE IF NOT EXISTS public.star_placement_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_type TEXT NOT NULL,
    star_name TEXT NOT NULL,
    base_star TEXT NOT NULL DEFAULT '',
    direction TEXT NOT NULL,
    "offset" INTEGER NOT NULL DEFAULT 0,
    "condition" JSONB NOT NULL DEFAULT '{}'::jsonb,
    school TEXT NOT NULL DEFAULT 'sanhe',
    version TEXT NOT NULL DEFAULT '2026.07.22'
)
"""

with eng.connect() as conn:
    conn.execute(text(DDL))
    conn.execute(
        text(
            "CREATE INDEX IF NOT EXISTS idx_star_placement_type "
            "ON public.star_placement_rules(rule_type)"
        )
    )
    try:
        conn.execute(text("ALTER TABLE public.star_placement_rules ENABLE ROW LEVEL SECURITY"))
    except Exception as exc:
        print("RLS:", str(exc)[:120])
    print("table ready")

seed_path = ROOT / "database" / "rules" / "star_placement_rules.sql"
seed = seed_path.read_text(encoding="utf-8")
seed = seed.replace(
    "(rule_type, star_name, base_star, direction, offset, condition, school, version)",
    '(rule_type, star_name, base_star, direction, "offset", "condition", school, version)',
)

ok = fail = 0
with eng.connect() as conn:
    for stmt in split_sql(seed):
        try:
            conn.execute(text(stmt))
            ok += 1
        except Exception as exc:
            fail += 1
            if fail <= 5:
                print("!", str(exc)[:200])

print("seed ok=", ok, "fail=", fail)
with eng.connect() as conn:
    n = conn.execute(text("SELECT COUNT(*) FROM public.star_placement_rules")).scalar()
    print("COUNT star_placement_rules=", n)
