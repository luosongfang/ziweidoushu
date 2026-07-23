"""Knowledge graph package V3.1."""

from app.knowledge.graph.entity_extractor import canonical_entities, detect_in_text
from app.knowledge.graph.graph_models import GraphBuildSummary, GraphEdge, GraphEntity
from app.knowledge.graph.graph_service import GraphService, build_knowledge_graph
from app.knowledge.graph.relation_builder import build_catalog_edges, build_chunk_edges

__all__ = [
    "GraphBuildSummary",
    "GraphEdge",
    "GraphEntity",
    "GraphService",
    "build_catalog_edges",
    "build_chunk_edges",
    "build_knowledge_graph",
    "canonical_entities",
    "detect_in_text",
]
