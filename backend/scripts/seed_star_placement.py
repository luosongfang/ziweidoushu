"""Seed star_placement_rules after quoting reserved columns."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

BACKEND = Path(__file__).resolve().parents[1]
ROOT = BACKEND.parent
sys.path.insert(0, str(BACKEND))
load_dotenv(BACKEND / ".env", override=True)

from scripts.bootstrap_supabase import split_sql  # noqa: E402

seed_path = ROOT / "database" / "rules" / "star_placement_rules.sql"
raw = seed_path.read_text(encoding="utf-8-sig")
raw = raw.replace(
    "(rule_type, star_name, base_star, direction, offset, condition, school, version)",
    '(rule_type, star_name, base_star, direction, "offset", "condition", school, version)',
)
seed_path.write_text(raw, encoding="utf-8")

eng = create_engine(os.environ["DATABASE_URL"], pool_pre_ping=True, isolation_level="AUTOCOMMIT")
ok = fail = 0
with eng.connect() as conn:
    for stmt in split_sql(raw):
        try:
            conn.execute(text(stmt))
            ok += 1
        except Exception as exc:  # noqa: BLE001
            fail += 1
            print("FAIL", type(exc).__name__, repr(str(exc)[:160]))

print("ok=", ok, "fail=", fail)
with eng.connect() as conn:
    n = conn.execute(text("SELECT COUNT(*) FROM public.star_placement_rules")).scalar()
    print("COUNT=", n)
