-- =============================================================================
-- 005: 紫微AI 规则表（V1.0 Final）
-- 执行顺序：在 schema.sql 业务表之后执行
-- 然后依次执行 database/rules/*.sql 种子数据
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. stars — 星曜元数据
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS public.stars (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name                TEXT NOT NULL UNIQUE,
    element             TEXT,
    yin_yang            TEXT CHECK (yin_yang IN ('阴', '阳')),
    category            TEXT NOT NULL CHECK (category IN ('main', 'aux', 'sha', 'za', 'special')),
    keywords            JSONB NOT NULL DEFAULT '[]',
    personality_tags    JSONB NOT NULL DEFAULT '[]',
    career_tags         JSONB NOT NULL DEFAULT '[]',
    wealth_tags         JSONB NOT NULL DEFAULT '[]',
    relationship_tags   JSONB NOT NULL DEFAULT '[]',
    description         TEXT,
    ai_prompt           TEXT,
    school              TEXT NOT NULL DEFAULT 'sanhe',
    is_active           BOOLEAN NOT NULL DEFAULT true,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_stars_category ON public.stars(category);
CREATE INDEX IF NOT EXISTS idx_stars_school ON public.stars(school);


-- -----------------------------------------------------------------------------
-- 2. nayin_rules — 纳音五行局
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS public.nayin_rules (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    heavenly_stem       TEXT NOT NULL,
    earthly_branch      TEXT NOT NULL,
    nayin               TEXT NOT NULL,
    element             TEXT NOT NULL CHECK (element IN ('水', '木', '金', '土', '火')),
    bureau_number       INTEGER NOT NULL CHECK (bureau_number BETWEEN 2 AND 6),
    school              TEXT NOT NULL DEFAULT 'sanhe',
    version             TEXT NOT NULL DEFAULT '2026.07.22',
    UNIQUE (heavenly_stem, earthly_branch, school, version)
);


-- -----------------------------------------------------------------------------
-- 3. ziwei_position_rules — 紫微星定位
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS public.ziwei_position_rules (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bureau              INTEGER NOT NULL CHECK (bureau BETWEEN 2 AND 6),
    lunar_day           INTEGER NOT NULL CHECK (lunar_day BETWEEN 1 AND 30),
    ziwei_branch        TEXT NOT NULL,
    school              TEXT NOT NULL DEFAULT 'sanhe',
    version             TEXT NOT NULL DEFAULT '2026.07.22',
    UNIQUE (bureau, lunar_day, school, version)
);


-- -----------------------------------------------------------------------------
-- 4. star_placement_rules — 安星规则
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS public.star_placement_rules (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_type           TEXT NOT NULL CHECK (rule_type IN ('main_star', 'aux_star', 'sha_star', 'za_star')),
    star_name           TEXT NOT NULL,
    base_star           TEXT NOT NULL DEFAULT '',
    direction           TEXT NOT NULL,
    offset              INTEGER NOT NULL DEFAULT 0,
    condition           JSONB NOT NULL DEFAULT '{}',
    school              TEXT NOT NULL DEFAULT 'sanhe',
    version             TEXT NOT NULL DEFAULT '2026.07.22'
);

CREATE INDEX IF NOT EXISTS idx_star_placement_type ON public.star_placement_rules(rule_type);


-- -----------------------------------------------------------------------------
-- 5. four_transform_rules — 生年四化
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS public.four_transform_rules (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    heavenly_stem       TEXT NOT NULL,
    lu_star             TEXT NOT NULL,
    quan_star           TEXT NOT NULL,
    ke_star             TEXT NOT NULL,
    ji_star             TEXT NOT NULL,
    school              TEXT NOT NULL DEFAULT 'sanhe',
    version             TEXT NOT NULL DEFAULT '2026.07.22',
    UNIQUE (heavenly_stem, school, version)
);


-- -----------------------------------------------------------------------------
-- 6. brightness_rules — 星曜亮度
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS public.brightness_rules (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    star_name           TEXT NOT NULL,
    branch              TEXT NOT NULL,
    brightness          TEXT NOT NULL,
    school              TEXT NOT NULL DEFAULT 'sanhe',
    version             TEXT NOT NULL DEFAULT '2026.07.22',
    UNIQUE (star_name, branch, school, version)
);


-- -----------------------------------------------------------------------------
-- 7. daxian_rules — 大限顺逆
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS public.daxian_rules (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    gender              TEXT NOT NULL CHECK (gender IN ('male', 'female')),
    year_yinyang        TEXT NOT NULL CHECK (year_yinyang IN ('yang', 'yin')),
    direction           TEXT NOT NULL CHECK (direction IN ('forward', 'backward')),
    start_age_formula   TEXT NOT NULL DEFAULT 'bureau_number',
    school              TEXT NOT NULL DEFAULT 'sanhe',
    version             TEXT NOT NULL DEFAULT '2026.07.22',
    UNIQUE (gender, year_yinyang, school, version)
);


-- -----------------------------------------------------------------------------
-- 8. star_combination_rules — 星曜组合（AI 核心）
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS public.star_combination_rules (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    combination_name    TEXT NOT NULL,
    stars               JSONB NOT NULL,
    category            TEXT NOT NULL,
    personality         TEXT,
    career              TEXT,
    wealth              TEXT,
    relationship        TEXT,
    ai_prompt           TEXT,
    school              TEXT NOT NULL DEFAULT 'sanhe',
    version             TEXT NOT NULL DEFAULT '2026.07.22'
);

CREATE INDEX IF NOT EXISTS idx_combination_category ON public.star_combination_rules(category);


-- -----------------------------------------------------------------------------
-- 9. palace_meaning_rules — 十二宫语义（AI 核心）
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS public.palace_meaning_rules (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    palace_name         TEXT NOT NULL,
    keyword             TEXT NOT NULL,
    meaning             TEXT NOT NULL,
    career              TEXT,
    wealth              TEXT,
    relationship        TEXT,
    health              TEXT,
    ai_prompt           TEXT,
    school              TEXT NOT NULL DEFAULT 'sanhe',
    version             TEXT NOT NULL DEFAULT '2026.07.22',
    UNIQUE (palace_name, school, version)
);


-- -----------------------------------------------------------------------------
-- RLS：规则表为只读公共数据
-- -----------------------------------------------------------------------------

ALTER TABLE public.stars ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.nayin_rules ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ziwei_position_rules ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.star_placement_rules ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.four_transform_rules ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.brightness_rules ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.daxian_rules ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.star_combination_rules ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.palace_meaning_rules ENABLE ROW LEVEL SECURITY;

DO $$
DECLARE
    t TEXT;
BEGIN
    FOREACH t IN ARRAY ARRAY[
        'stars', 'nayin_rules', 'ziwei_position_rules', 'star_placement_rules',
        'four_transform_rules', 'brightness_rules', 'daxian_rules',
        'star_combination_rules', 'palace_meaning_rules'
    ] LOOP
        EXECUTE format(
            'DROP POLICY IF EXISTS %I ON public.%I; CREATE POLICY %I ON public.%I FOR SELECT TO authenticated USING (true);',
            t || '_select', t, t || '_select', t
        );
    END LOOP;
END $$;
