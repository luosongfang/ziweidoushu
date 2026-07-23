-- Knowledge Core V2.1 — Advisor decision model layer
-- Additive only — does not alter V2.0 tables

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS public.advisor_dimension_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dimension_code TEXT NOT NULL UNIQUE,
    dimension_name TEXT NOT NULL,
    description TEXT,
    positive_expression TEXT,
    challenge_expression TEXT,
    growth_direction TEXT,
    safety_level TEXT DEFAULT 'medium',
    version TEXT DEFAULT '2.1.0',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_advisor_dim_code
    ON public.advisor_dimension_rules(dimension_code);

CREATE TABLE IF NOT EXISTS public.advisor_question_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question_type TEXT NOT NULL UNIQUE,
    user_question_examples JSONB DEFAULT '[]'::jsonb,
    required_dimensions JSONB DEFAULT '[]'::jsonb,
    recommended_focus JSONB DEFAULT '[]'::jsonb,
    avoid_topics JSONB DEFAULT '[]'::jsonb,
    version TEXT DEFAULT '2.1.0',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_advisor_qtype
    ON public.advisor_question_templates(question_type);

CREATE TABLE IF NOT EXISTS public.advisor_action_models (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pattern_code TEXT NOT NULL,
    condition JSONB DEFAULT '{}'::jsonb,
    strength_analysis TEXT,
    risk_reminder TEXT,
    action_suggestions JSONB DEFAULT '[]'::jsonb,
    growth_path JSONB DEFAULT '[]'::jsonb,
    version TEXT DEFAULT '2.1.0',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (pattern_code, version)
);

CREATE INDEX IF NOT EXISTS idx_advisor_action_pattern
    ON public.advisor_action_models(pattern_code);
