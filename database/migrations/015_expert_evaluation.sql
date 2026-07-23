-- Knowledge Core V5.5 — Expert evaluation & case verification
-- Additive only - no LLM - scores analysis process, not life outcomes

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS public.ziwei_case_library (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_name TEXT NOT NULL,
    birth_info_summary TEXT,
    chart_features JSONB DEFAULT '{}'::jsonb,
    main_patterns JSONB DEFAULT '[]'::jsonb,
    life_stage TEXT,
    question_type TEXT,
    analysis_reference JSONB DEFAULT '{}'::jsonb,
    case_source TEXT,
    verification_level TEXT DEFAULT 'classic',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_zcl_verification CHECK (
        verification_level IN ('classic', 'expert_reviewed', 'community_feedback')
    )
);

CREATE INDEX IF NOT EXISTS idx_zcl_qtype
    ON public.ziwei_case_library(question_type);
CREATE INDEX IF NOT EXISTS idx_zcl_level
    ON public.ziwei_case_library(verification_level);
CREATE INDEX IF NOT EXISTS idx_zcl_name
    ON public.ziwei_case_library(case_name);

CREATE TABLE IF NOT EXISTS public.expert_review_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID,
    reviewer_type TEXT DEFAULT 'internal',
    review_score INTEGER,
    logic_score INTEGER,
    safety_score INTEGER,
    value_score INTEGER,
    comments TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_err_scores CHECK (
        (review_score IS NULL OR (review_score BETWEEN 0 AND 100))
        AND (logic_score IS NULL OR (logic_score BETWEEN 0 AND 100))
        AND (safety_score IS NULL OR (safety_score BETWEEN 0 AND 100))
        AND (value_score IS NULL OR (value_score BETWEEN 0 AND 100))
    )
);

CREATE INDEX IF NOT EXISTS idx_err_case
    ON public.expert_review_records(case_id);

CREATE TABLE IF NOT EXISTS public.analysis_quality_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID,
    citation_score INTEGER,
    logic_score INTEGER,
    safety_score INTEGER,
    user_helpful_score INTEGER,
    overall_score INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_aqm_analysis
    ON public.analysis_quality_metrics(analysis_id);
CREATE INDEX IF NOT EXISTS idx_aqm_overall
    ON public.analysis_quality_metrics(overall_score);

CREATE TABLE IF NOT EXISTS public.theory_effectiveness_stats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    theory_system TEXT NOT NULL,
    scenario TEXT NOT NULL,
    usage_count INTEGER DEFAULT 0,
    helpful_count INTEGER DEFAULT 0,
    neutral_count INTEGER DEFAULT 0,
    not_helpful_count INTEGER DEFAULT 0,
    effectiveness_score DOUBLE PRECISION DEFAULT 0,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_tes_theory_scenario
    ON public.theory_effectiveness_stats(theory_system, scenario);
CREATE INDEX IF NOT EXISTS idx_tes_score
    ON public.theory_effectiveness_stats(effectiveness_score DESC);
