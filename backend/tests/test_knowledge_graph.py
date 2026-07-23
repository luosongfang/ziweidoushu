"""Knowledge Core V3.1 — knowledge graph tests (no LLM)."""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine, text

from app.config import settings
from app.database.database import is_database_ready
from app.knowledge.graph.entity_extractor import canonical_entities, detect_in_text
from app.knowledge.graph.graph_service import GraphService, apply_migration
from app.knowledge.graph.relation_builder import build_catalog_edges, build_chunk_edges


@pytest.fixture(scope="module")
def require_postgres():
    if not settings.is_postgres:
        pytest.skip("requires PostgreSQL / Supabase")
    if not is_database_ready():
        pytest.skip("database not ready")


@pytest.fixture(scope="module")
def engine(require_postgres):
    url = settings.database_url
    if url.startswith("postgresql") and "sslmode=" not in url:
        url = f"{url}{'&' if '?' in url else '?'}sslmode=require"
    eng = create_engine(url, pool_pre_ping=True)
    apply_migration(eng)
    return eng


def test_canonical_entities_cover_catalog():
    ents = canonical_entities()
    names = {(e.name, e.entity_type) for e in ents}
    assert ("紫微", "star") in names
    assert ("破军", "star") in names
    assert ("命宫", "palace") in names
    assert ("化禄", "four_transform") in names
    assert ("杀破狼", "pattern") in names
    assert ("紫府同宫", "pattern") in names
    assert ("机月同梁", "pattern") in names
    assert ("事业", "life_scene") in names
    assert ("星曜含义", "concept") in names
    assert len(ents) >= 14 + 12 + 4 + 3 + 4 + 5


def test_detect_entities_in_text():
    found = detect_in_text("紫微天府在命宫，化权入官禄，杀破狼主变。")
    assert "紫微" in found["star"]
    assert "天府" in found["star"]
    assert "命宫" in found["palace"]
    assert "官禄宫" in found["palace"]
    assert "化权" in found["four_transform"]
    assert "杀破狼" in found["pattern"]


def test_catalog_relations_exist():
    edges = build_catalog_edges()
    rels = {e.relation_type for e in edges}
    for required in (
        "meaning",
        "combination",
        "belongs",
        "three_harmony",
        "four_transform",
    ):
        assert required in rels
    assert any(e.source_name == "紫微" and e.target_name == "星曜含义" for e in edges)
    assert any(e.source_name == "七杀" and e.target_name == "杀破狼" for e in edges)


def test_chunk_relation_with_citation():
    chunk = {
        "id": "00000000-0000-0000-0000-000000000001",
        "content": "武曲化禄在财帛宫，事业财源相关。",
    }
    edges = build_chunk_edges(chunk)
    assert edges
    assert all(e.source_chunk_id == chunk["id"] for e in edges)
    assert any(e.relation_type in {"belongs", "influence", "four_transform", "career", "wealth"} for e in edges)


def test_graph_tables_exist(engine):
    with engine.connect() as conn:
        for table in ("knowledge_entities", "knowledge_graph_edges"):
            exists = conn.execute(text("SELECT to_regclass(:t)"), {"t": f"public.{table}"}).scalar()
            assert exists is not None


def test_build_graph_integrity(engine):
    # Ensure chunks exist from Phase1
    with engine.connect() as conn:
        n_chunks = conn.execute(text("SELECT COUNT(*) FROM public.knowledge_chunks")).scalar()
        if not n_chunks:
            pytest.skip("knowledge_chunks empty — run Phase1 import first")

    service = GraphService(rebuild=True)
    summary = service.build(max_chunk_edges=800, chunk_limit=100)
    assert summary.entities >= 40
    assert summary.relations >= 50
    assert summary.chunks_scanned >= 1

    counts = service.counts()
    assert counts["entities"] == summary.entities
    assert counts["relations"] >= 50

    with engine.connect() as conn:
        # FK integrity: every edge points to existing entities
        bad = conn.execute(
            text(
                """
                SELECT COUNT(*) FROM public.knowledge_graph_edges e
                LEFT JOIN public.knowledge_entities s ON s.id = e.source_entity_id
                LEFT JOIN public.knowledge_entities t ON t.id = e.target_entity_id
                WHERE s.id IS NULL OR t.id IS NULL
                """
            )
        ).scalar()
        assert bad == 0

        # cited relations reference real chunks when set
        orphan = conn.execute(
            text(
                """
                SELECT COUNT(*) FROM public.knowledge_graph_edges e
                WHERE e.source_chunk_id IS NOT NULL
                  AND NOT EXISTS (
                    SELECT 1 FROM public.knowledge_chunks c WHERE c.id = e.source_chunk_id
                  )
                """
            )
        ).scalar()
        assert orphan == 0
