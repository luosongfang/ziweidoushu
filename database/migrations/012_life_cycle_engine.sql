-- Knowledge Core V4.1 — Dynamic Life Cycle Engine
-- Additive only - no LLM - preserves V4.0 multi-theory tables

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS public.fortune_cycle_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    theory_system TEXT NOT NULL DEFAULT 'sanhe',
    gender TEXT,
    yin_yang TEXT,
    bureau_number INTEGER,
    start_age_formula TEXT,
    direction TEXT,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_fcr_bureau
    ON public.fortune_cycle_rules(bureau_number);
CREATE INDEX IF NOT EXISTS idx_fcr_gender
    ON public.fortune_cycle_rules(gender, yin_yang);

CREATE TABLE IF NOT EXISTS public.life_stage_models (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    stage_name TEXT NOT NULL UNIQUE,
    age_range JSONB DEFAULT '{}'::jsonb,
    focus_dimensions JSONB DEFAULT '[]'::jsonb,
    advisor_template TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_lsm_stage
    ON public.life_stage_models(stage_name);

CREATE TABLE IF NOT EXISTS public.annual_influence_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    year_type TEXT NOT NULL,
    trigger_rule JSONB DEFAULT '{}'::jsonb,
    influence_dimension TEXT,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_air_year_type
    ON public.annual_influence_rules(year_type);

CREATE TABLE IF NOT EXISTS public.cycle_analysis_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scenario TEXT NOT NULL UNIQUE,
    strength_template TEXT,
    risk_template TEXT,
    growth_template TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_cat_scenario
    ON public.cycle_analysis_templates(scenario);
