-- Knowledge Core V6.0 Phase 1 — Classical Knowledge Evidence Layer
-- Additive only - stores original quotes with citations
-- Does NOT rewrite classical text or invent lore
-- Does NOT alter V5.6 dispatch / evaluation / optimization flows

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS public.classical_quotes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    book TEXT NOT NULL,
    chapter TEXT,
    page INTEGER NOT NULL,
    original_text TEXT NOT NULL,
    keywords JSONB DEFAULT '[]'::jsonb,
    source_reference JSONB DEFAULT '{}'::jsonb,
    theory_category TEXT,
    source_file TEXT,
    content_hash TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_cq_page CHECK (page >= 0)
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_cq_book_page_hash
    ON public.classical_quotes(book, page, content_hash);
CREATE INDEX IF NOT EXISTS idx_cq_book
    ON public.classical_quotes(book);
CREATE INDEX IF NOT EXISTS idx_cq_page
    ON public.classical_quotes(book, page);
CREATE INDEX IF NOT EXISTS idx_cq_theory
    ON public.classical_quotes(theory_category);
CREATE INDEX IF NOT EXISTS idx_cq_keywords_gin
    ON public.classical_quotes USING gin (keywords);
CREATE INDEX IF NOT EXISTS idx_cq_source_gin
    ON public.classical_quotes USING gin (source_reference);

CREATE TABLE IF NOT EXISTS public.classical_interpretations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    quote_id UUID NOT NULL REFERENCES public.classical_quotes(id) ON DELETE CASCADE,
    theory_system TEXT NOT NULL,
    topic_tags JSONB DEFAULT '[]'::jsonb,
    mapping_type TEXT NOT NULL DEFAULT '',
    star_tags JSONB DEFAULT '[]'::jsonb,
    palace_tags JSONB DEFAULT '[]'::jsonb,
    pattern_tags JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_ci_theory CHECK (
        theory_system IN (
            'sanhe', 'four_transform', 'feixing', 'classic_formula',
            'palace', 'star', 'foundation', 'general'
        )
    )
);

CREATE INDEX IF NOT EXISTS idx_ci_quote
    ON public.classical_interpretations(quote_id);
CREATE INDEX IF NOT EXISTS idx_ci_theory
    ON public.classical_interpretations(theory_system);
CREATE UNIQUE INDEX IF NOT EXISTS uq_ci_quote_theory_map
    ON public.classical_interpretations(quote_id, theory_system, mapping_type);

CREATE TABLE IF NOT EXISTS public.classical_authority_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    book TEXT NOT NULL,
    authority_level INTEGER NOT NULL DEFAULT 3,
    book_type TEXT,
    main_topics JSONB DEFAULT '[]'::jsonb,
    suitable_questions JSONB DEFAULT '[]'::jsonb,
    description TEXT,
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_cas_level CHECK (authority_level BETWEEN 1 AND 5)
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_cas_book
    ON public.classical_authority_scores(book);
CREATE INDEX IF NOT EXISTS idx_cas_level
    ON public.classical_authority_scores(authority_level DESC);
