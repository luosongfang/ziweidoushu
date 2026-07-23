"""Apply Knowledge Core V3.3 growth memory migration."""

from __future__ import annotations

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
    sql_path = ROOT / "database" / "migrations" / "010_user_growth_memory.sql"
    sql = sql_path.read_text(encoding="utf-8")
    with engine.begin() as conn:
        for stmt in _split_sql(sql):
            conn.execute(text(stmt))
        print("migration 010 applied")
        for t in (
            "user_question_history",
            "user_interest_profile",
            "user_growth_memory",
            "advisor_continuity_context",
        ):
            n = conn.execute(text(f"SELECT COUNT(*) FROM {t}")).scalar()
            print(f"COUNT {t}={n}")


if __name__ == "__main__":
    main()
