"""Import extracted Ziwei PDF page JSON into Supabase knowledge asset tables."""

from __future__ import annotations

import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.knowledge.importer.knowledge_importer import import_knowledge_books


def main() -> None:
    result = import_knowledge_books()
    print("====================")
    print("Ziwei Knowledge Import")
    print()
    print("Books:")
    print(result.get("books", 0))
    print()
    print("Documents:")
    print(result.get("documents", 0))
    print()
    print("Chunks:")
    print(result.get("chunks", 0))
    print()
    print("Characters:")
    print(result.get("characters", 0))
    print("====================")


if __name__ == "__main__":
    main()
