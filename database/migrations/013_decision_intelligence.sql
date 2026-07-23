-- Knowledge Core V5.0 — Decision Intelligence Layer
-- Additive only - no LLM - preserves V4.1 lifecycle and multitheory

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS public.decision_models (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scenario_name TEXT NOT NULL UNIQUE,
    scenario_type TEXT,
    description TEXT,
    required_palaces JSONB DEFAULT '[]'::jsonb,
    required_stars JSONB DEFAULT '[]'::jsonb,
    required_patterns JSONB DEFAULT '[]'::jsonb,
    required_cycles JSONB DEFAULT '[]'::jsonb,
    decision_dimensions JSONB DEFAULT '[]'::jsonb,
    risk_dimensions JSONB DEFAULT '[]'::jsonb,
    growth_dimensions JSONB DEFAULT '[]'::jsonb,
    safety_level TEXT DEFAULT 'high',
    version TEXT DEFAULT '5.0.0',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_dm_scenario
    ON public.decision_models(scenario_name);
CREATE INDEX IF NOT EXISTS idx_dm_type
    ON public.decision_models(scenario_type);

CREATE TABLE IF NOT EXISTS public.decision_dimension_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dimension TEXT NOT NULL,
    traditional_factor TEXT NOT NULL,
    positive_expression TEXT,
    challenge_expression TEXT,
    growth_direction TEXT,
    source_reference TEXT,
    version TEXT DEFAULT '5.0.0',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ddr_dimension
    ON public.decision_dimension_rules(dimension);
CREATE INDEX IF NOT EXISTS idx_ddr_factor
    ON public.decision_dimension_rules(traditional_factor);

CREATE TABLE IF NOT EXISTS public.decision_process_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scenario TEXT NOT NULL,
    step_order INTEGER NOT NULL,
    title TEXT NOT NULL,
    content_template TEXT,
    safety_expression TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_dpt_scenario
    ON public.decision_process_templates(scenario, step_order);

CREATE TABLE IF NOT EXISTS public.decision_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID,
    question_type TEXT,
    question_summary TEXT,
    analysis_summary TEXT,
    suggestions JSONB DEFAULT '[]'::jsonb,
    user_feedback TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_dh_user
    ON public.decision_history(user_id);
CREATE INDEX IF NOT EXISTS idx_dh_created
    ON public.decision_history(created_at DESC);

CREATE TABLE IF NOT EXISTS public.decision_safety_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    forbidden_expression TEXT NOT NULL,
    safe_expression TEXT NOT NULL,
    reason TEXT,
    risk_level TEXT DEFAULT 'high',
    version TEXT DEFAULT '5.0.0',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_dsr_forbidden
    ON public.decision_safety_rules(forbidden_expression);
