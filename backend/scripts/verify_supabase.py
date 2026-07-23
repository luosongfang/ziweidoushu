"""Verify Supabase schema counts."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text

load_dotenv(Path(__file__).resolve().parents[1] / ".env", override=True)
eng = create_engine(os.environ["DATABASE_URL"], pool_pre_ping=True)
tables = sorted(inspect(eng).get_table_names(schema="public"))
print("tables", len(tables))
print(", ".join(tables))
checks = [
    "nayin_rules",
    "ziwei_position_rules",
    "star_placement_rules",
    "stars",
    "four_transform_rules",
    "brightness_rules",
    "daxian_rules",
    "star_combination_rules",
    "palace_meaning_rules",
    "users",
    "ziwei_charts",
    "profiles",
    "charts",
    "analyses",
    "knowledge_chunks",
]
with eng.connect() as conn:
    for t in checks:
        if t in tables:
            n = conn.execute(text(f'SELECT COUNT(*) FROM public."{t}"')).scalar()
            print(f"{t}={n}")
        else:
            print(f"{t}=MISSING")
