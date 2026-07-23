"""Apply & verify Knowledge Core V5.6 theory optimization tables."""

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

from app.knowledge.multitheory.theory_dispatcher import TheoryDispatcher  # noqa: E402
from app.knowledge.optimization import OptimizationService, WeightOptimizer  # noqa: E402


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
    sql = (ROOT / "database" / "migrations" / "016_theory_optimization.sql").read_text(
        encoding="utf-8"
    )
    with engine.begin() as conn:
        for stmt in _split_sql(sql):
            conn.execute(text(stmt))
        print("migration 016 applied")

    weights = WeightOptimizer.list_weights()
    print(f"dispatch_weights={len(weights)}")
    route = TheoryDispatcher.get_dynamic_theory_route("entrepreneurship")
    print(f"entrepreneurship_route={route}")
    print(f"sample_weights={OptimizationService.list_weights('entrepreneurship')}")

    with engine.connect() as conn:
        for t in (
            "theory_dispatch_weights",
            "theory_route_history",
            "optimization_events",
        ):
            n = conn.execute(text(f"SELECT COUNT(*) FROM {t}")).scalar()
            print(f"COUNT {t}={n}")


if __name__ == "__main__":
    main()
