"""Graph service — build & persist knowledge graph from chunks (no LLM)."""

from __future__ import annotations

import json
import logging
import os
from collections import Counter
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from app.knowledge.graph.entity_extractor import aggregate_chunk_mentions, canonical_entities
from app.knowledge.graph.graph_models import GraphBuildSummary, GraphEdge, GraphEntity
from app.knowledge.graph.relation_builder import (
    aggregate_edges,
    build_catalog_edges,
    build_chunk_edges,
)

logger = logging.getLogger(__name__)

BACKEND = Path(__file__).resolve().parents[3]
PROJECT_ROOT = BACKEND.parent
MIGRATION_SQL = PROJECT_ROOT / "database" / "migrations" / "008_knowledge_graph.sql"


def _load_env() -> None:
    load_dotenv(BACKEND / ".env", override=True)


def _engine() -> Engine:
    _load_env()
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL missing")
    if url.startswith("postgresql") and "sslmode=" not in url:
        url = f"{url}{'&' if '?' in url else '?'}sslmode=require"
    return create_engine(url, pool_pre_ping=True)


def _j(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False)


def _split_sql(sql: str) -> list[str]:
    out: list[str] = []
    i = 0
    n = len(sql)
    start = 0
    while i < n:
        if sql.startswith("$$", i):
            j = sql.find("$$", i + 2)
            if j < 0:
                break
            i = j + 2
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


def apply_migration(eng: Engine | None = None) -> None:
    eng = eng or _engine()
    sql = MIGRATION_SQL.read_text(encoding="utf-8")
    with eng.connect() as conn:
        conn = conn.execution_options(isolation_level="AUTOCOMMIT")
        for stmt in _split_sql(sql):
            conn.execute(text(stmt))


class GraphService:
    """Orchestrate entity extraction + relation build + DB persist."""

    def __init__(self, *, rebuild: bool = True) -> None:
        self.engine = _engine()
        self.rebuild = rebuild

    def ensure_schema(self) -> None:
        apply_migration(self.engine)

    def load_chunks(self, limit: int | None = None) -> list[dict[str, Any]]:
        """Load chunk tag rows only (fast path)."""
        lim = int(limit) if limit is not None else 5000
        with self.engine.connect() as conn:
            conn.execute(text("SET statement_timeout = '180s'"))
            rows = conn.execute(
                text(
                    """
                    SELECT id, star_tags, palace_tags, pattern_tags, life_question_tags
                    FROM public.knowledge_chunks
                    LIMIT :lim
                    """
                ),
                {"lim": lim},
            ).mappings().all()
            return [{**dict(r), "content": ""} for r in rows]

    def build(
        self,
        *,
        max_chunk_edges: int | None = None,
        chunk_limit: int | None = None,
        citation_sample: int = 1000,
    ) -> GraphBuildSummary:
        logger.info("ensure schema")
        self.ensure_schema()
        logger.info("load chunks limit=%s", chunk_limit)
        chunks = self.load_chunks(limit=chunk_limit)
        logger.info("chunks loaded=%s", len(chunks))

        entities = canonical_entities()
        mentions = aggregate_chunk_mentions(chunks)
        mention_map: dict[tuple[str, str], int] = {}
        for etype, counter in mentions.items():
            for name, cnt in counter.items():
                mention_map[(name, etype)] = cnt
        for ent in entities:
            key = (ent.name, ent.entity_type)
            if key in mention_map:
                ent.metadata = {**ent.metadata, "mention_count": mention_map[key]}

        # Catalog edges + aggregated chunk co-occurrence (+ citation samples)
        edges: list[GraphEdge] = build_catalog_edges()
        aggregated_pool: list[GraphEdge] = []
        cited_sample: list[GraphEdge] = []
        produced = 0
        for ch in chunks:
            ce = build_chunk_edges(ch)
            for e in ce:
                if max_chunk_edges is not None and produced >= max_chunk_edges:
                    break
                produced += 1
                if len(cited_sample) < citation_sample and e.source_chunk_id:
                    cited_sample.append(e)
                # aggregate without chunk id
                aggregated_pool.append(
                    e.model_copy(update={"source_chunk_id": None, "weight": 1.0})
                )
            if max_chunk_edges is not None and produced >= max_chunk_edges:
                break

        edges.extend(aggregate_edges(aggregated_pool, keep_chunk_edges=False))
        edges.extend(cited_sample)
        logger.info("persist entities=%s edges=%s", len(entities), len(edges))
        self._persist(entities, edges)

        etypes = Counter(e.entity_type for e in entities)
        rtypes = Counter(e.relation_type for e in edges)
        return GraphBuildSummary(
            entities=len(entities),
            relations=len(edges),
            chunks_scanned=len(chunks),
            entity_types=dict(etypes),
            relation_types=dict(rtypes),
        )

    def _persist(self, entities: list[GraphEntity], edges: list[GraphEdge]) -> None:
        with self.engine.begin() as conn:
            conn.execute(text("SET LOCAL statement_timeout = '300s'"))
            if self.rebuild:
                conn.execute(text("DELETE FROM public.knowledge_graph_edges"))
                conn.execute(text("DELETE FROM public.knowledge_entities"))

            id_map: dict[tuple[str, str], Any] = {}
            for ent in entities:
                row_id = conn.execute(
                    text(
                        """
                        INSERT INTO public.knowledge_entities
                            (name, entity_type, description, metadata)
                        VALUES
                            (:name, :entity_type, :description, CAST(:metadata AS jsonb))
                        ON CONFLICT (name, entity_type) DO UPDATE SET
                            description = EXCLUDED.description,
                            metadata = EXCLUDED.metadata
                        RETURNING id
                        """
                    ),
                    {
                        "name": ent.name,
                        "entity_type": ent.entity_type,
                        "description": ent.description,
                        "metadata": _j(ent.metadata),
                    },
                ).scalar_one()
                id_map[(ent.name, ent.entity_type)] = row_id

            edge_rows: list[dict[str, Any]] = []
            for e in edges:
                sid = id_map.get((e.source_name, e.source_type))
                tid = id_map.get((e.target_name, e.target_type))
                if not sid or not tid:
                    continue
                edge_rows.append(
                    {
                        "source_entity_id": sid,
                        "target_entity_id": tid,
                        "relation_type": e.relation_type,
                        "weight": float(e.weight),
                        "source_chunk_id": e.source_chunk_id,
                        "metadata": _j(e.metadata),
                    }
                )

            sql = text(
                """
                INSERT INTO public.knowledge_graph_edges
                    (source_entity_id, target_entity_id, relation_type, weight,
                     source_chunk_id, metadata)
                VALUES
                    (:source_entity_id, :target_entity_id, :relation_type, :weight,
                     :source_chunk_id, CAST(:metadata AS jsonb))
                """
            )
            batch = 300
            for i in range(0, len(edge_rows), batch):
                conn.execute(sql, edge_rows[i : i + batch])
                logger.info("inserted edges %s/%s", min(i + batch, len(edge_rows)), len(edge_rows))

    def counts(self) -> dict[str, int]:
        with self.engine.connect() as conn:
            entities = conn.execute(text("SELECT COUNT(*) FROM public.knowledge_entities")).scalar()
            relations = conn.execute(
                text("SELECT COUNT(*) FROM public.knowledge_graph_edges")
            ).scalar()
            cited = conn.execute(
                text(
                    "SELECT COUNT(*) FROM public.knowledge_graph_edges "
                    "WHERE source_chunk_id IS NOT NULL"
                )
            ).scalar()
            return {
                "entities": int(entities or 0),
                "relations": int(relations or 0),
                "cited_relations": int(cited or 0),
            }


def build_knowledge_graph(**kwargs: Any) -> dict[str, Any]:
    service = GraphService(rebuild=True)
    summary = service.build(**kwargs)
    return summary.model_dump()
