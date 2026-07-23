"""Knowledge graph models — entities and edges (no LLM)."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class GraphEntity(BaseModel):
    name: str
    entity_type: str
    description: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class GraphEdge(BaseModel):
    source_name: str
    source_type: str
    target_name: str
    target_type: str
    relation_type: str
    weight: float = 1.0
    source_chunk_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class GraphBuildSummary(BaseModel):
    entities: int = 0
    relations: int = 0
    chunks_scanned: int = 0
    entity_types: dict[str, int] = Field(default_factory=dict)
    relation_types: dict[str, int] = Field(default_factory=dict)
