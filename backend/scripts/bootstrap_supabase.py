"""Bootstrap Supabase: rules DDL + seeds (autocommit, dollar-quote safe)."""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text

BACKEND = Path(__file__).resolve().parents[1]
ROOT = BACKEND.parent
load_dotenv(BACKEND / ".env", override=True)
DATABASE_URL = os.environ["DATABASE_URL"]
DB_DIR = ROOT / "database"


def split_sql(sql: str) -> list[str]:
    """Split SQL into statements; respect quotes and $tag$ ... $tag$ blocks."""
    sql = re.sub(r"/\*.*?\*/", "", sql, flags=re.S)
    stmts: list[str] = []
    buf: list[str] = []
    i = 0
    in_single = False
    dollar_tag: str | None = None

    while i < len(sql):
        ch = sql[i]

        if dollar_tag is not None:
            end = sql.find(dollar_tag, i)
            if end < 0:
                buf.append(sql[i:])
                break
            buf.append(sql[i : end + len(dollar_tag)])
            i = end + len(dollar_tag)
            dollar_tag = None
            continue

        if not in_single and ch == "$":
            m = re.match(r"\$[A-Za-z0-9_]*\$", sql[i:])
            if m:
                dollar_tag = m.group(0)
                buf.append(dollar_tag)
                i += len(dollar_tag)
                continue

        if ch == "'" and not in_single:
            in_single = True
            buf.append(ch)
            i += 1
            continue
        if ch == "'" and in_single:
            if i + 1 < len(sql) and sql[i + 1] == "'":
                buf.append("''")
                i += 2
                continue
            in_single = False
            buf.append(ch)
            i += 1
            continue

        if ch == ";" and not in_single:
            raw = "".join(buf)
            cleaned = "\n".join(
                ln
                for ln in raw.splitlines()
                if ln.strip() and not ln.strip().startswith("--")
            ).strip()
            if cleaned:
                stmts.append(cleaned)
            buf = []
            i += 1
            continue

        buf.append(ch)
        i += 1

    raw = "".join(buf)
    cleaned = "\n".join(
        ln for ln in raw.splitlines() if ln.strip() and not ln.strip().startswith("--")
    ).strip()
    if cleaned:
        stmts.append(cleaned)
    return stmts


def run_file(conn, path: Path) -> tuple[int, int]:
    sql = path.read_text(encoding="utf-8")
    stmts = split_sql(sql)
    ok = 0
    fail = 0
    for stmt in stmts:
        try:
            conn.execute(text(stmt))
            ok += 1
        except Exception as exc:  # noqa: BLE001
            msg = str(exc).lower()
            if any(
                k in msg
                for k in (
                    "already exists",
                    "duplicate key",
                    "duplicate",
                )
            ):
                ok += 1
                continue
            fail += 1
            if fail <= 3:
                print(f"  ! {path.name}: {str(exc)[:180]}")
    return ok, fail


def main() -> int:
    # AUTOCOMMIT so one error does not poison the whole batch
    eng = create_engine(DATABASE_URL, pool_pre_ping=True, isolation_level="AUTOCOMMIT")

    with eng.connect() as conn:
        for ext in ("pgcrypto", "uuid-ossp", "vector"):
            try:
                conn.execute(text(f'CREATE EXTENSION IF NOT EXISTS "{ext}"'))
                print("ext OK", ext)
            except Exception as exc:
                print("ext SKIP", ext, str(exc)[:100])

        files: list[Path] = [DB_DIR / "migrations" / "005_rules_tables.sql"]
        for name in [
            "nayin_rules.sql",
            "ziwei_position_rules.sql",
            "star_placement_rules.sql",
            "four_transform_rules.sql",
            "brightness_rules.sql",
            "daxian_rules.sql",
            "stars.sql",
            "star_combination_rules.sql",
            "palace_meaning_rules.sql",
        ]:
            files.append(DB_DIR / "rules" / name)

        for opt in [
            "001_init_users.sql",
            "002_init_charts.sql",
            "003_init_analyses.sql",
        ]:
            files.append(DB_DIR / "migrations" / opt)

        total_fail = 0
        for path in files:
            if not path.exists():
                print("MISSING", path.name)
                continue
            ok, fail = run_file(conn, path)
            total_fail += fail
            print(f"FILE {path.name}: ok={ok} fail={fail}")

        # knowledge_chunks (vector optional)
        try:
            conn.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS public.knowledge_chunks (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        source TEXT NOT NULL,
                        category TEXT NOT NULL,
                        title TEXT,
                        content TEXT NOT NULL,
                        metadata JSONB DEFAULT '{}'::jsonb,
                        embedding vector(1536),
                        created_at TIMESTAMPTZ NOT NULL DEFAULT now()
                    )
                    """
                )
            )
            print("knowledge_chunks OK")
        except Exception as exc:
            print("knowledge_chunks FAIL", str(exc)[:160])

    tables = sorted(inspect(eng).get_table_names(schema="public"))
    print("\nPUBLIC TABLES", len(tables))
    for t in tables:
        print(" -", t)

    # row counts for key rule tables
    with eng.connect() as conn:
        for t in (
            "nayin_rules",
            "ziwei_position_rules",
            "stars",
            "four_transform_rules",
            "users",
            "ziwei_charts",
            "profiles",
            "charts",
            "knowledge_chunks",
        ):
            if t in tables:
                n = conn.execute(text(f'SELECT COUNT(*) FROM public."{t}"')).scalar()
                print(f"COUNT {t}={n}")

    return 1 if total_fail else 0


if __name__ == "__main__":
    sys.exit(main())
