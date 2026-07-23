-- Knowledge Core V5.1 — Decision feedback loop + citation visualization
-- Additive only - no LLM - preserves V5.0 decision tables

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS public.decision_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    decision_history_id UUID,
    feedback_type TEXT NOT NULL,
    feedback_content TEXT,
    result_status TEXT DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_df_feedback_type CHECK (
        feedback_type IN ('helpful', 'not_helpful', 'partially_helpful', 'future_check')
    ),
    CONSTRAINT chk_df_result_status CHECK (
        result_status IN ('pending', 'confirmed', 'changed', 'unknown')
    )
);

CREATE INDEX IF NOT EXISTS idx_df_user
    ON public.decision_feedback(user_id);
CREATE INDEX IF NOT EXISTS idx_df_history
    ON public.decision_feedback(decision_history_id);
CREATE INDEX IF NOT EXISTS idx_df_type
    ON public.decision_feedback(feedback_type);

CREATE TABLE IF NOT EXISTS public.decision_path_models (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scenario TEXT NOT NULL,
    path_type TEXT NOT NULL,
    conditions JSONB DEFAULT '[]'::jsonb,
    advantages JSONB DEFAULT '[]'::jsonb,
    risks JSONB DEFAULT '[]'::jsonb,
    recommended_actions JSONB DEFAULT '[]'::jsonb,
    reflection_questions JSONB DEFAULT '[]'::jsonb,
    version TEXT DEFAULT '5.1.0',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_dpm_path_type CHECK (path_type IN ('stable', 'aggressive'))
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_dpm_scenario_path
    ON public.decision_path_models(scenario, path_type);
CREATE INDEX IF NOT EXISTS idx_dpm_scenario
    ON public.decision_path_models(scenario);

CREATE TABLE IF NOT EXISTS public.knowledge_reference_map (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_type TEXT,
    entity_type TEXT,
    entity_id TEXT,
    source_book TEXT,
    source_page TEXT,
    source_chunk_id UUID,
    relationship TEXT,
    weight DOUBLE PRECISION DEFAULT 1.0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_krm_analysis
    ON public.knowledge_reference_map(analysis_type);
CREATE INDEX IF NOT EXISTS idx_krm_entity
    ON public.knowledge_reference_map(entity_type, entity_id);

CREATE TABLE IF NOT EXISTS public.user_decision_profile (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE,
    decision_style TEXT,
    risk_preference TEXT,
    strength_patterns JSONB DEFAULT '[]'::jsonb,
    challenge_patterns JSONB DEFAULT '[]'::jsonb,
    growth_history JSONB DEFAULT '[]'::jsonb,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_udp_user
    ON public.user_decision_profile(user_id);
