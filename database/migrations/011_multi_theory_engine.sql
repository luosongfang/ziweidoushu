-- Knowledge Core V4.0 Phase 1 — Multi-Theory Decision Engine
-- Additive only - no LLM - preserves V3.3 tables and pipeline

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS public.theory_systems (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    type TEXT NOT NULL,
    description TEXT,
    authority_level INTEGER DEFAULT 3,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_theory_systems_type
    ON public.theory_systems(type);
CREATE INDEX IF NOT EXISTS idx_theory_systems_active
    ON public.theory_systems(active);

CREATE TABLE IF NOT EXISTS public.theory_rules_mapping (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    theory_id UUID NOT NULL REFERENCES public.theory_systems(id) ON DELETE CASCADE,
    question_type TEXT NOT NULL,
    required_palaces JSONB DEFAULT '[]'::jsonb,
    required_stars JSONB DEFAULT '[]'::jsonb,
    required_patterns JSONB DEFAULT '[]'::jsonb,
    priority INTEGER DEFAULT 100,
    example TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_trm_theory
    ON public.theory_rules_mapping(theory_id);
CREATE INDEX IF NOT EXISTS idx_trm_qtype
    ON public.theory_rules_mapping(question_type);
CREATE UNIQUE INDEX IF NOT EXISTS uq_trm_theory_qtype
    ON public.theory_rules_mapping(theory_id, question_type);

CREATE TABLE IF NOT EXISTS public.theory_analysis_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID NOT NULL,
    theory_name TEXT NOT NULL,
    result JSONB DEFAULT '{}'::jsonb,
    evidence JSONB DEFAULT '[]'::jsonb,
    confidence_level TEXT DEFAULT 'medium',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_tar_analysis
    ON public.theory_analysis_results(analysis_id);
CREATE INDEX IF NOT EXISTS idx_tar_theory
    ON public.theory_analysis_results(theory_name);

CREATE TABLE IF NOT EXISTS public.decision_synthesis_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scenario TEXT NOT NULL UNIQUE,
    input_theories JSONB DEFAULT '[]'::jsonb,
    synthesis_logic TEXT,
    output_template JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_dsr_scenario
    ON public.decision_synthesis_rules(scenario);
