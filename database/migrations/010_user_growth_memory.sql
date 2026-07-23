-- Knowledge Core V3.3 — user growth memory
-- Additive only - no LLM - privacy-first - does not alter V2.1/V3.1/V3.2 tables

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS public.user_question_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    chart_id UUID,
    question TEXT NOT NULL,
    question_type TEXT,
    analysis_result JSONB DEFAULT '{}'::jsonb,
    theory_used JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_uq_history_user
    ON public.user_question_history(user_id);
CREATE INDEX IF NOT EXISTS idx_uq_history_user_created
    ON public.user_question_history(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_uq_history_qtype
    ON public.user_question_history(question_type);

CREATE TABLE IF NOT EXISTS public.user_interest_profile (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE,
    career_interest DOUBLE PRECISION DEFAULT 0,
    wealth_interest DOUBLE PRECISION DEFAULT 0,
    relationship_interest DOUBLE PRECISION DEFAULT 0,
    family_interest DOUBLE PRECISION DEFAULT 0,
    learning_interest DOUBLE PRECISION DEFAULT 0,
    growth_interest DOUBLE PRECISION DEFAULT 0,
    keywords JSONB DEFAULT '[]'::jsonb,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_uip_user
    ON public.user_interest_profile(user_id);

CREATE TABLE IF NOT EXISTS public.user_growth_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    memory_type TEXT NOT NULL,
    content TEXT NOT NULL,
    source_question_id UUID,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_ugm_memory_type CHECK (
        memory_type IN ('goal', 'challenge', 'decision', 'reflection', 'plan')
    )
);

CREATE INDEX IF NOT EXISTS idx_ugm_user
    ON public.user_growth_memory(user_id);
CREATE INDEX IF NOT EXISTS idx_ugm_user_type
    ON public.user_growth_memory(user_id, memory_type);
CREATE INDEX IF NOT EXISTS idx_ugm_source
    ON public.user_growth_memory(source_question_id);

CREATE TABLE IF NOT EXISTS public.advisor_continuity_context (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE,
    summary TEXT,
    important_topics JSONB DEFAULT '[]'::jsonb,
    last_analysis JSONB DEFAULT '{}'::jsonb,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_acc_user
    ON public.advisor_continuity_context(user_id);
