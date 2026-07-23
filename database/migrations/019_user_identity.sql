-- ===========================================
-- 019: ZiweiX AI V1.2 用户身份与成长档案
-- 依赖: auth.users (Supabase) 或应用层 UUID
-- 说明: 扩展 legacy profiles (001)，新增命盘/分析/成长画像
-- ===========================================

-- ── 1. profiles（扩展 001，对齐 V1.2 字段） ──
ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS auth_user_id UUID;
ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS nickname TEXT;

UPDATE public.profiles
SET auth_user_id = id
WHERE auth_user_id IS NULL;

UPDATE public.profiles
SET nickname = display_name
WHERE nickname IS NULL AND display_name IS NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS idx_profiles_auth_user_id ON public.profiles(auth_user_id);

-- ── 2. user_charts（V1.2 结构化命盘存档） ──
CREATE TABLE IF NOT EXISTS public.user_charts (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL,
    chart_name      TEXT NOT NULL DEFAULT '未命名命盘',
    birth_date      TEXT,
    birth_time      TEXT,
    birth_place     TEXT,
    gender          TEXT CHECK (gender IN ('male', 'female')),
    chart_data      JSONB NOT NULL DEFAULT '{}',
    birth_info      JSONB DEFAULT '{}',
    is_default      BOOLEAN NOT NULL DEFAULT false,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE public.user_charts ADD COLUMN IF NOT EXISTS chart_name TEXT NOT NULL DEFAULT '未命名命盘';
ALTER TABLE public.user_charts ADD COLUMN IF NOT EXISTS birth_date TEXT;
ALTER TABLE public.user_charts ADD COLUMN IF NOT EXISTS birth_time TEXT;
ALTER TABLE public.user_charts ADD COLUMN IF NOT EXISTS birth_place TEXT;
ALTER TABLE public.user_charts ADD COLUMN IF NOT EXISTS gender TEXT;
ALTER TABLE public.user_charts ADD COLUMN IF NOT EXISTS birth_info JSONB DEFAULT '{}';
ALTER TABLE public.user_charts ADD COLUMN IF NOT EXISTS is_default BOOLEAN NOT NULL DEFAULT false;
ALTER TABLE public.user_charts ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT now();

-- 兼容旧列 name → chart_name
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'user_charts' AND column_name = 'name'
    ) THEN
        UPDATE public.user_charts SET chart_name = name WHERE chart_name IS NULL OR chart_name = '未命名命盘';
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_user_charts_user_id ON public.user_charts(user_id);
CREATE INDEX IF NOT EXISTS idx_user_charts_user_default ON public.user_charts(user_id, is_default);

-- ── 3. analysis_history ──
CREATE TABLE IF NOT EXISTS public.analysis_history (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL,
    chart_id        UUID,
    question        TEXT NOT NULL DEFAULT '',
    analysis_type   TEXT NOT NULL DEFAULT 'overview',
    summary         TEXT NOT NULL DEFAULT '',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_analysis_history_user_id ON public.analysis_history(user_id);
CREATE INDEX IF NOT EXISTS idx_analysis_history_chart_id ON public.analysis_history(chart_id);
CREATE INDEX IF NOT EXISTS idx_analysis_history_created ON public.analysis_history(user_id, created_at DESC);

-- ── 4. growth_profile ──
CREATE TABLE IF NOT EXISTS public.growth_profile (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL UNIQUE,
    interest_tags   JSONB NOT NULL DEFAULT '[]',
    career_focus    TEXT,
    decision_style  TEXT,
    growth_notes    TEXT,
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_growth_profile_user_id ON public.growth_profile(user_id);

-- ── RLS ──
ALTER TABLE public.user_charts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.analysis_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.growth_profile ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "user_charts_select_own" ON public.user_charts;
CREATE POLICY "user_charts_select_own" ON public.user_charts FOR SELECT
    USING (auth.uid() = user_id);
DROP POLICY IF EXISTS "user_charts_insert_own" ON public.user_charts;
CREATE POLICY "user_charts_insert_own" ON public.user_charts FOR INSERT
    WITH CHECK (auth.uid() = user_id);
DROP POLICY IF EXISTS "user_charts_update_own" ON public.user_charts;
CREATE POLICY "user_charts_update_own" ON public.user_charts FOR UPDATE
    USING (auth.uid() = user_id);
DROP POLICY IF EXISTS "user_charts_delete_own" ON public.user_charts;
CREATE POLICY "user_charts_delete_own" ON public.user_charts FOR DELETE
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "analysis_history_select_own" ON public.analysis_history;
CREATE POLICY "analysis_history_select_own" ON public.analysis_history FOR SELECT
    USING (auth.uid() = user_id);
DROP POLICY IF EXISTS "analysis_history_insert_own" ON public.analysis_history;
CREATE POLICY "analysis_history_insert_own" ON public.analysis_history FOR INSERT
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "growth_profile_select_own" ON public.growth_profile;
CREATE POLICY "growth_profile_select_own" ON public.growth_profile FOR SELECT
    USING (auth.uid() = user_id);
DROP POLICY IF EXISTS "growth_profile_upsert_own" ON public.growth_profile;
CREATE POLICY "growth_profile_upsert_own" ON public.growth_profile FOR INSERT
    WITH CHECK (auth.uid() = user_id);
DROP POLICY IF EXISTS "growth_profile_update_own" ON public.growth_profile;
CREATE POLICY "growth_profile_update_own" ON public.growth_profile FOR UPDATE
    USING (auth.uid() = user_id);

COMMENT ON TABLE public.user_charts IS 'V1.2 用户云端命盘';
COMMENT ON TABLE public.analysis_history IS 'V1.2 用户分析记录';
COMMENT ON TABLE public.growth_profile IS 'V1.2 用户成长画像';
