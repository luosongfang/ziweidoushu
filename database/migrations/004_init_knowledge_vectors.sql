-- ===========================================
-- 004: RAG 知识库向量表
-- 需要先启用 pgvector 扩展
-- ===========================================

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS public.knowledge_chunks (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source      TEXT NOT NULL,           -- 来源古籍或流派
    category    TEXT NOT NULL,           -- 如：主星、四化、宫位
    title       TEXT,
    content     TEXT NOT NULL,
    metadata    JSONB DEFAULT '{}',
    embedding   vector(1536),            -- OpenAI text-embedding-3-small 维度
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_knowledge_category ON public.knowledge_chunks(category);
CREATE INDEX idx_knowledge_embedding ON public.knowledge_chunks
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- 知识库为只读公共数据，所有认证用户可读
ALTER TABLE public.knowledge_chunks ENABLE ROW LEVEL SECURITY;

CREATE POLICY "认证用户可读取知识库"
    ON public.knowledge_chunks FOR SELECT
    TO authenticated
    USING (true);
