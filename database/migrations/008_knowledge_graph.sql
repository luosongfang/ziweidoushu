-- Knowledge Core V3.1 — knowledge graph layer
-- Additive only - no LLM

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS public.knowledge_entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    description TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (name, entity_type)
);

CREATE INDEX IF NOT EXISTS idx_knowledge_entities_type
    ON public.knowledge_entities(entity_type);
CREATE INDEX IF NOT EXISTS idx_knowledge_entities_name
    ON public.knowledge_entities(name);

CREATE TABLE IF NOT EXISTS public.knowledge_graph_edges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_entity_id UUID NOT NULL REFERENCES public.knowledge_entities(id) ON DELETE CASCADE,
    target_entity_id UUID NOT NULL REFERENCES public.knowledge_entities(id) ON DELETE CASCADE,
    relation_type TEXT NOT NULL,
    weight DOUBLE PRECISION DEFAULT 1.0,
    source_chunk_id UUID,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_kge_source
    ON public.knowledge_graph_edges(source_entity_id);
CREATE INDEX IF NOT EXISTS idx_kge_target
    ON public.knowledge_graph_edges(target_entity_id);
CREATE INDEX IF NOT EXISTS idx_kge_relation
    ON public.knowledge_graph_edges(relation_type);
CREATE INDEX IF NOT EXISTS idx_kge_chunk
    ON public.knowledge_graph_edges(source_chunk_id);
