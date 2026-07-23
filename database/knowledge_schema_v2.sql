-- Knowledge Core V2.0 schema
-- Additive only — does not alter V1.1 tables.

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 1. ziwei_theory_rules — 传统紫微核心规则
CREATE TABLE IF NOT EXISTS public.ziwei_theory_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category VARCHAR(64) NOT NULL,
    rule_name VARCHAR(128) NOT NULL,
    rule_expression TEXT,
    traditional_meaning TEXT,
    modern_interpretation TEXT,
    application_scope JSONB DEFAULT '[]'::jsonb,
    risk_expression TEXT,
    safety_level VARCHAR(16) DEFAULT 'medium',
    school VARCHAR(32) DEFAULT 'sanhe',
    version VARCHAR(32) DEFAULT '2.0.0',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (rule_name, school, version)
);

CREATE INDEX IF NOT EXISTS idx_ziwei_theory_rules_category
    ON public.ziwei_theory_rules(category);
CREATE INDEX IF NOT EXISTS idx_ziwei_theory_rules_scope
    ON public.ziwei_theory_rules USING GIN (application_scope);

-- 2. star_combination_matrix — 星曜组合推理矩阵
CREATE TABLE IF NOT EXISTS public.star_combination_matrix (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    star_a VARCHAR(32) NOT NULL,
    star_b VARCHAR(32),
    star_c VARCHAR(32),
    combination_name VARCHAR(128) NOT NULL,
    traditional_pattern TEXT,
    personality_dimension TEXT,
    career_dimension TEXT,
    wealth_dimension TEXT,
    relationship_dimension TEXT,
    challenge_dimension TEXT,
    growth_direction TEXT,
    ai_tags JSONB DEFAULT '[]'::jsonb,
    version VARCHAR(32) DEFAULT '2.0.0',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (combination_name, version)
);

CREATE INDEX IF NOT EXISTS idx_star_combo_stars
    ON public.star_combination_matrix(star_a, star_b);

-- 3. palace_dimension_matrix — 十二宫多维解释
CREATE TABLE IF NOT EXISTS public.palace_dimension_matrix (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    palace_name VARCHAR(32) NOT NULL,
    dimension VARCHAR(32) NOT NULL,
    traditional_meaning TEXT,
    modern_meaning TEXT,
    question_mapping JSONB DEFAULT '[]'::jsonb,
    advice_template TEXT,
    version VARCHAR(32) DEFAULT '2.0.0',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (palace_name, dimension, version)
);

CREATE INDEX IF NOT EXISTS idx_palace_dim_palace
    ON public.palace_dimension_matrix(palace_name);
CREATE INDEX IF NOT EXISTS idx_palace_dim_dimension
    ON public.palace_dimension_matrix(dimension);

-- 4. four_transform_matrix — 四化深度分析
CREATE TABLE IF NOT EXISTS public.four_transform_matrix (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    year_stem VARCHAR(8),
    transform_type VARCHAR(8) NOT NULL,
    star_name VARCHAR(32),
    traditional_effect TEXT,
    modern_effect TEXT,
    positive_expression TEXT,
    challenge_expression TEXT,
    growth_advice TEXT,
    version VARCHAR(32) DEFAULT '2.0.0',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_four_tf_type
    ON public.four_transform_matrix(transform_type);
CREATE INDEX IF NOT EXISTS idx_four_tf_stem
    ON public.four_transform_matrix(year_stem);

-- 5. life_scenario_models — 人生场景模型
CREATE TABLE IF NOT EXISTS public.life_scenario_models (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scenario_name VARCHAR(64) NOT NULL UNIQUE,
    display_name VARCHAR(64),
    required_palaces JSONB DEFAULT '[]'::jsonb,
    required_patterns JSONB DEFAULT '[]'::jsonb,
    analysis_steps JSONB DEFAULT '[]'::jsonb,
    output_structure JSONB DEFAULT '[]'::jsonb,
    safety_rules JSONB DEFAULT '[]'::jsonb,
    related_question_types JSONB DEFAULT '[]'::jsonb,
    version VARCHAR(32) DEFAULT '2.0.0',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_life_scenario_name
    ON public.life_scenario_models(scenario_name);

-- 6. user_question_memory — 用户真实问题收集（未来训练）
CREATE TABLE IF NOT EXISTS public.user_question_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(64),
    question TEXT NOT NULL,
    question_type VARCHAR(64),
    chart_snapshot JSONB,
    analysis_result JSONB,
    feedback TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_uqm_user ON public.user_question_memory(user_id);
CREATE INDEX IF NOT EXISTS idx_uqm_qtype ON public.user_question_memory(question_type);
CREATE INDEX IF NOT EXISTS idx_uqm_created ON public.user_question_memory(created_at DESC);
