-- Knowledge Core V3.2 — intelligence routing layer
-- Additive only - no LLM - does not alter V2.1/V3.1 tables

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS public.book_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    book_name TEXT NOT NULL UNIQUE,
    book_type TEXT NOT NULL,
    authority_level INTEGER DEFAULT 3,
    main_topics JSONB DEFAULT '[]'::jsonb,
    suitable_questions JSONB DEFAULT '[]'::jsonb,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_book_profiles_type
    ON public.book_profiles(book_type);

CREATE TABLE IF NOT EXISTS public.theory_routes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question_type TEXT NOT NULL UNIQUE,
    required_palaces JSONB DEFAULT '[]'::jsonb,
    required_stars JSONB DEFAULT '[]'::jsonb,
    required_patterns JSONB DEFAULT '[]'::jsonb,
    required_theories JSONB DEFAULT '[]'::jsonb,
    priority INTEGER DEFAULT 100,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_theory_routes_qtype
    ON public.theory_routes(question_type);

CREATE TABLE IF NOT EXISTS public.knowledge_evidence (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID NOT NULL,
    claim TEXT NOT NULL,
    chunk_id UUID,
    book_name TEXT,
    page_number INTEGER,
    theory_type TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_knowledge_evidence_analysis
    ON public.knowledge_evidence(analysis_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_evidence_chunk
    ON public.knowledge_evidence(chunk_id);

CREATE TABLE IF NOT EXISTS public.interpretation_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    traditional_expression TEXT NOT NULL,
    risk_level TEXT DEFAULT 'medium',
    safe_expression TEXT NOT NULL,
    guidance TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_interpretation_rules_expr
    ON public.interpretation_rules(traditional_expression);
