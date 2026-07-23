-- Knowledge Core V1.1 schema upgrades
ALTER TABLE public.stars_knowledge
    ADD COLUMN IF NOT EXISTS life_stage_expression TEXT;

ALTER TABLE public.palace_knowledge
    ADD COLUMN IF NOT EXISTS psychological_meaning TEXT,
    ADD COLUMN IF NOT EXISTS modern_interpretation TEXT,
    ADD COLUMN IF NOT EXISTS development_advice TEXT,
    ADD COLUMN IF NOT EXISTS common_user_questions JSONB DEFAULT '[]'::jsonb;

ALTER TABLE public.life_question_models
    ADD COLUMN IF NOT EXISTS analysis_steps JSONB DEFAULT '[]'::jsonb,
    ADD COLUMN IF NOT EXISTS output_structure JSONB DEFAULT '[]'::jsonb,
    ADD COLUMN IF NOT EXISTS display_name VARCHAR(64);
