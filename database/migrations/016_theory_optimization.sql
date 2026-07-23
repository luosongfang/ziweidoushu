-- Knowledge Core V5.6 — Theory adaptive optimization loop
-- Additive only - optimizes dispatch weights/order only
-- Does NOT invent lore or rewrite classic interpretations

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS public.theory_dispatch_weights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scenario TEXT NOT NULL,
    theory_system TEXT NOT NULL,
    base_weight DOUBLE PRECISION NOT NULL DEFAULT 0.5,
    dynamic_weight DOUBLE PRECISION NOT NULL DEFAULT 0.5,
    success_count INTEGER NOT NULL DEFAULT 0,
    feedback_score DOUBLE PRECISION NOT NULL DEFAULT 50,
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    version TEXT NOT NULL DEFAULT '5.6.0',
    CONSTRAINT chk_tdw_base CHECK (base_weight >= 0.1 AND base_weight <= 1.0),
    CONSTRAINT chk_tdw_dynamic CHECK (dynamic_weight >= 0.1 AND dynamic_weight <= 1.0),
    CONSTRAINT chk_tdw_feedback CHECK (feedback_score >= 0 AND feedback_score <= 100)
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_tdw_scenario_theory
    ON public.theory_dispatch_weights(scenario, theory_system);
CREATE INDEX IF NOT EXISTS idx_tdw_scenario
    ON public.theory_dispatch_weights(scenario);
CREATE INDEX IF NOT EXISTS idx_tdw_dynamic
    ON public.theory_dispatch_weights(dynamic_weight DESC);

CREATE TABLE IF NOT EXISTS public.theory_route_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID,
    scenario TEXT,
    selected_theories JSONB DEFAULT '[]'::jsonb,
    weights JSONB DEFAULT '{}'::jsonb,
    quality_score DOUBLE PRECISION,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_trh_analysis
    ON public.theory_route_history(analysis_id);
CREATE INDEX IF NOT EXISTS idx_trh_scenario
    ON public.theory_route_history(scenario);
CREATE INDEX IF NOT EXISTS idx_trh_created
    ON public.theory_route_history(created_at DESC);

CREATE TABLE IF NOT EXISTS public.optimization_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type TEXT NOT NULL,
    before_value JSONB DEFAULT '{}'::jsonb,
    after_value JSONB DEFAULT '{}'::jsonb,
    reason TEXT,
    source TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_oe_type
    ON public.optimization_events(event_type);
CREATE INDEX IF NOT EXISTS idx_oe_created
    ON public.optimization_events(created_at DESC);

-- Initial dispatch weights (scenario-specific, explainable defaults)
INSERT INTO public.theory_dispatch_weights
    (scenario, theory_system, base_weight, dynamic_weight, success_count, feedback_score, version)
VALUES
    ('entrepreneurship', 'sanhe', 0.8, 0.8, 0, 50, '5.6.0'),
    ('entrepreneurship', 'four_transform', 0.6, 0.6, 0, 50, '5.6.0'),
    ('entrepreneurship', 'feixing', 0.3, 0.3, 0, 50, '5.6.0'),
    ('wealth', 'four_transform', 0.8, 0.8, 0, 50, '5.6.0'),
    ('wealth', 'sanhe', 0.5, 0.5, 0, 50, '5.6.0'),
    ('relationship', 'four_transform', 0.7, 0.7, 0, 50, '5.6.0'),
    ('relationship', 'sanhe', 0.5, 0.5, 0, 50, '5.6.0'),
    ('career', 'sanhe', 0.75, 0.75, 0, 50, '5.6.0'),
    ('career', 'four_transform', 0.55, 0.55, 0, 50, '5.6.0'),
    ('study', 'sanhe', 0.7, 0.7, 0, 50, '5.6.0'),
    ('life_transition', 'sanhe', 0.65, 0.65, 0, 50, '5.6.0'),
    ('life_transition', 'four_transform', 0.5, 0.5, 0, 50, '5.6.0')
ON CONFLICT (scenario, theory_system) DO NOTHING;
