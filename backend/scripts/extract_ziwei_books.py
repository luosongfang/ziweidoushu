"""Run Ziwei classic PDF raw text extraction (no AI rewrite)."""

from __future__ import annotations

import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.knowledge.pdf_processor.extract_service import extract_all_books


def main() -> None:
    result = extract_all_books()
    print("=====================")
    print("Ziwei PDF Extract")
    print()
    print("Books:")
    print(result.get("books", 0))
    print()
    print("Pages:")
    print(result.get("pages", 0))
    print()
    print("Characters:")
    print(result.get("characters", 0))
    print()
    print("Output:")
    print(result.get("output_dir", ""))
    print("=====================")


if __name__ == "__main__":
    main()
