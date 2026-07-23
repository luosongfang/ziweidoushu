-- =============================================================================
-- Ziwei AI Knowledge Core V1.0 — Schema (PostgreSQL / Supabase)
-- =============================================================================

CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 1. theory_knowledge — 经典理论
CREATE TABLE IF NOT EXISTS public.theory_knowledge (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school          VARCHAR(32)  NOT NULL DEFAULT 'sanhe',
    source_book     VARCHAR(128),
    chapter         VARCHAR(128),
    topic           VARCHAR(128) NOT NULL,
    content         TEXT         NOT NULL,
    summary         TEXT,
    keywords        JSONB        NOT NULL DEFAULT '[]'::jsonb,
    related_rules   JSONB        NOT NULL DEFAULT '[]'::jsonb,
    ai_prompt       TEXT,
    version         VARCHAR(32)  NOT NULL DEFAULT '1.0.0',
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_theory_topic ON public.theory_knowledge(topic);
CREATE INDEX IF NOT EXISTS idx_theory_school ON public.theory_knowledge(school);

-- 2. stars_knowledge — 星曜 AI 知识模型
CREATE TABLE IF NOT EXISTS public.stars_knowledge (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    star_name               VARCHAR(32)  NOT NULL UNIQUE,
    category                VARCHAR(32)  NOT NULL DEFAULT 'main',
    five_element            VARCHAR(8),
    yin_yang                VARCHAR(4),
    basic_meaning           TEXT,
    personality_positive    JSONB NOT NULL DEFAULT '[]'::jsonb,
    personality_challenge   JSONB NOT NULL DEFAULT '[]'::jsonb,
    career_strength         JSONB NOT NULL DEFAULT '[]'::jsonb,
    career_risk             JSONB NOT NULL DEFAULT '[]'::jsonb,
    wealth_pattern          JSONB NOT NULL DEFAULT '[]'::jsonb,
    relationship_pattern    JSONB NOT NULL DEFAULT '[]'::jsonb,
    traditional_description TEXT,
    growth_advice           TEXT,
    ai_prompt               TEXT,
    source_reference        TEXT,
    version                 VARCHAR(32) NOT NULL DEFAULT '1.0.0'
);
CREATE INDEX IF NOT EXISTS idx_stars_knowledge_category ON public.stars_knowledge(category);

-- 3. palace_knowledge — 十二宫
CREATE TABLE IF NOT EXISTS public.palace_knowledge (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    palace_name             VARCHAR(32) NOT NULL UNIQUE,
    basic_meaning           TEXT,
    life_area               VARCHAR(64),
    positive_expression     TEXT,
    challenge_expression    TEXT,
    development_direction   TEXT,
    common_questions        JSONB NOT NULL DEFAULT '[]'::jsonb,
    ai_prompt               TEXT,
    version                 VARCHAR(32) NOT NULL DEFAULT '1.0.0'
);

-- 4. ziwei_patterns — 组合格局
CREATE TABLE IF NOT EXISTS public.ziwei_patterns (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pattern_name            VARCHAR(64) NOT NULL UNIQUE,
    category                VARCHAR(32) NOT NULL DEFAULT 'combo',
    conditions              JSONB NOT NULL DEFAULT '{}'::jsonb,
    related_stars           JSONB NOT NULL DEFAULT '[]'::jsonb,
    related_palaces         JSONB NOT NULL DEFAULT '[]'::jsonb,
    traditional_meaning     TEXT,
    advantages              JSONB NOT NULL DEFAULT '[]'::jsonb,
    challenges              JSONB NOT NULL DEFAULT '[]'::jsonb,
    career_analysis         TEXT,
    wealth_analysis         TEXT,
    relationship_analysis   TEXT,
    growth_advice           TEXT,
    ai_prompt               TEXT,
    version                 VARCHAR(32) NOT NULL DEFAULT '1.0.0'
);
CREATE INDEX IF NOT EXISTS idx_ziwei_patterns_category ON public.ziwei_patterns(category);

-- 5. four_transform_knowledge — 四化知识
CREATE TABLE IF NOT EXISTS public.four_transform_knowledge (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    stem        VARCHAR(8)  NOT NULL UNIQUE,
    lu_star     VARCHAR(16) NOT NULL,
    quan_star   VARCHAR(16) NOT NULL,
    ke_star     VARCHAR(16) NOT NULL,
    ji_star     VARCHAR(16) NOT NULL,
    lu_meaning  TEXT,
    quan_meaning TEXT,
    ke_meaning  TEXT,
    ji_meaning  TEXT,
    ai_prompt   TEXT,
    version     VARCHAR(32) NOT NULL DEFAULT '1.0.0'
);

-- 6. life_question_models — 人生问题模型
CREATE TABLE IF NOT EXISTS public.life_question_models (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question_type       VARCHAR(32) NOT NULL UNIQUE,
    question_examples   JSONB NOT NULL DEFAULT '[]'::jsonb,
    required_palaces    JSONB NOT NULL DEFAULT '[]'::jsonb,
    required_stars      JSONB NOT NULL DEFAULT '[]'::jsonb,
    required_patterns   JSONB NOT NULL DEFAULT '[]'::jsonb,
    analysis_logic      TEXT,
    output_template     TEXT,
    safety_notice       TEXT,
    version             VARCHAR(32) NOT NULL DEFAULT '1.0.0'
);

-- 7. safety_expression_rules — AI 安全表达
CREATE TABLE IF NOT EXISTS public.safety_expression_rules (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category                VARCHAR(64) NOT NULL,
    forbidden_expression    TEXT NOT NULL,
    safe_expression         TEXT NOT NULL,
    reason                  TEXT,
    risk_level              VARCHAR(16) NOT NULL DEFAULT 'medium',
    version                 VARCHAR(32) NOT NULL DEFAULT '1.0.0'
);
CREATE INDEX IF NOT EXISTS idx_safety_category ON public.safety_expression_rules(category);
CREATE INDEX IF NOT EXISTS idx_safety_forbidden ON public.safety_expression_rules(forbidden_expression);
