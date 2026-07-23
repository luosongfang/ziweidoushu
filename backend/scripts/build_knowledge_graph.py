"""Build Ziwei knowledge graph from imported chunks (no LLM)."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.knowledge.graph.graph_service import GraphService


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    service = GraphService(rebuild=True)
    summary = service.build(max_chunk_edges=8000, citation_sample=800)
    print("====================")
    print("Ziwei Knowledge Graph")
    print()
    print("Entities:")
    print(summary.entities)
    print()
    print("Relations:")
    print(summary.relations)
    print()
    print("Chunks scanned:")
    print(summary.chunks_scanned)
    print("====================")


if __name__ == "__main__":
    main()
