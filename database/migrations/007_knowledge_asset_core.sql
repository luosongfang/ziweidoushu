-- Knowledge Core V3.0 Phase 1 — raw book asset tables
-- Handles conflict with legacy empty RAG knowledge_chunks.

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS public.knowledge_books (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    book_name TEXT NOT NULL,
    author TEXT,
    school TEXT DEFAULT 'sanhe',
    description TEXT,
    file_name TEXT,
    total_pages INTEGER DEFAULT 0,
    status TEXT DEFAULT 'imported',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (book_name)
);

CREATE INDEX IF NOT EXISTS idx_knowledge_books_status
    ON public.knowledge_books(status);

CREATE TABLE IF NOT EXISTS public.knowledge_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    book_id UUID NOT NULL REFERENCES public.knowledge_books(id) ON DELETE CASCADE,
    title TEXT,
    chapter TEXT,
    source_file TEXT,
    page_start INTEGER,
    page_end INTEGER,
    content TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_knowledge_documents_book
    ON public.knowledge_documents(book_id);

-- Legacy RAG table (empty) used the same name. Rename if it has embedding column.
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'knowledge_chunks'
          AND column_name = 'embedding'
    ) THEN
        ALTER TABLE public.knowledge_chunks RENAME TO knowledge_chunks_rag_legacy;
    END IF;
END $$;

CREATE TABLE IF NOT EXISTS public.knowledge_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES public.knowledge_documents(id) ON DELETE CASCADE,
    book_id UUID NOT NULL REFERENCES public.knowledge_books(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL DEFAULT 0,
    page_number INTEGER,
    content TEXT NOT NULL,
    keywords JSONB DEFAULT '[]'::jsonb,
    star_tags JSONB DEFAULT '[]'::jsonb,
    palace_tags JSONB DEFAULT '[]'::jsonb,
    pattern_tags JSONB DEFAULT '[]'::jsonb,
    life_question_tags JSONB DEFAULT '[]'::jsonb,
    source_reference JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_knowledge_chunks_book
    ON public.knowledge_chunks(book_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_chunks_document
    ON public.knowledge_chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_chunks_page
    ON public.knowledge_chunks(page_number);
CREATE INDEX IF NOT EXISTS idx_knowledge_chunks_stars
    ON public.knowledge_chunks USING GIN (star_tags);
CREATE INDEX IF NOT EXISTS idx_knowledge_chunks_palaces
    ON public.knowledge_chunks USING GIN (palace_tags);

CREATE TABLE IF NOT EXISTS public.knowledge_relations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_chunk_id UUID NOT NULL REFERENCES public.knowledge_chunks(id) ON DELETE CASCADE,
    target_chunk_id UUID NOT NULL REFERENCES public.knowledge_chunks(id) ON DELETE CASCADE,
    relation_type TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_knowledge_relations_source
    ON public.knowledge_relations(source_chunk_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_relations_type
    ON public.knowledge_relations(relation_type);

CREATE TABLE IF NOT EXISTS public.knowledge_citations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chunk_id UUID NOT NULL REFERENCES public.knowledge_chunks(id) ON DELETE CASCADE,
    citation_text TEXT,
    source_book TEXT,
    page_number INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_knowledge_citations_chunk
    ON public.knowledge_citations(chunk_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_citations_book
    ON public.knowledge_citations(source_book);
