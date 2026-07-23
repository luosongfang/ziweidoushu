"""Apply migration 017 + seed classical authority + sample/full quote import."""

from __future__ import annotations

import argparse
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

from app.knowledge.classical import AuthorityRanker, EvidenceService, QuoteImporter  # noqa: E402


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
    parser = argparse.ArgumentParser(description="Seed Classical Evidence Layer V6.0 Phase1")
    parser.add_argument("--full", action="store_true", help="Import all extracted pages")
    parser.add_argument("--max-pages", type=int, default=3, help="Pages per book when not --full")
    parser.add_argument("--max-total", type=int, default=None, help="Cap total imported pages")
    args = parser.parse_args()

    url = os.environ.get("DATABASE_URL")
    if not url:
        raise SystemExit("DATABASE_URL missing")
    engine = create_engine(url)
    sql = (ROOT / "database" / "migrations" / "017_classical_evidence_layer.sql").read_text(
        encoding="utf-8"
    )
    with engine.begin() as conn:
        for stmt in _split_sql(sql):
            conn.execute(text(stmt))
        print("migration 017 applied")

    auth_n = AuthorityRanker.seed_from_profiles()
    print(f"authority_scores_seeded={auth_n}")

    importer = QuoteImporter()
    if args.full:
        result = importer.import_books(
            map_interpretations=True,
            seed_authority=False,
            max_total=args.max_total,
        )
    else:
        result = importer.import_books(
            max_pages_per_book=args.max_pages,
            max_total=args.max_total,
            map_interpretations=True,
            seed_authority=False,
        )
    print(f"import_result books={result.get('book_count')} imported={result.get('imported')}")
    print(f"stats={EvidenceService.stats()}")


if __name__ == "__main__":
    main()
