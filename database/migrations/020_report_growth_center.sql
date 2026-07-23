-- ===========================================
-- 020: ZiweiX AI V1.3 人生报告 + 成长中心
-- 依赖: profiles (001), user_charts (019)
-- ===========================================

-- ── 1. user_reports ──
CREATE TABLE IF NOT EXISTS public.user_reports (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL,
    chart_id        UUID,
    report_type     VARCHAR(32) NOT NULL DEFAULT 'life_profile',
    engine_version  VARCHAR(16) NOT NULL DEFAULT '5.6',
    report_json     JSONB NOT NULL DEFAULT '{}'::jsonb,
    summary         TEXT NOT NULL DEFAULT '',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_user_reports_user_id ON public.user_reports(user_id);
CREATE INDEX IF NOT EXISTS idx_user_reports_chart_id ON public.user_reports(chart_id);
CREATE INDEX IF NOT EXISTS idx_user_reports_created ON public.user_reports(user_id, created_at DESC);

-- ── 2. user_growth_goals ──
CREATE TABLE IF NOT EXISTS public.user_growth_goals (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL,
    goal_type       VARCHAR(32) NOT NULL CHECK (
        goal_type IN ('career', 'wealth', 'relationship', 'learning', 'growth')
    ),
    goal_content    TEXT NOT NULL DEFAULT '',
    progress        VARCHAR(32) NOT NULL DEFAULT 'planned',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_user_growth_goals_user_id ON public.user_growth_goals(user_id);

-- ── 3. report_feedback ──
CREATE TABLE IF NOT EXISTS public.report_feedback (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL,
    report_id       UUID NOT NULL,
    helpful         BOOLEAN NOT NULL DEFAULT true,
    feedback_type   VARCHAR(32) NOT NULL DEFAULT 'general',
    comment         TEXT NOT NULL DEFAULT '',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_report_feedback_user_id ON public.report_feedback(user_id);
CREATE INDEX IF NOT EXISTS idx_report_feedback_report_id ON public.report_feedback(report_id);

-- ── RLS ──
ALTER TABLE public.user_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_growth_goals ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.report_feedback ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "user_reports_select_own" ON public.user_reports;
CREATE POLICY "user_reports_select_own" ON public.user_reports FOR SELECT
    USING (auth.uid() = user_id);
DROP POLICY IF EXISTS "user_reports_insert_own" ON public.user_reports;
CREATE POLICY "user_reports_insert_own" ON public.user_reports FOR INSERT
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "user_growth_goals_select_own" ON public.user_growth_goals;
CREATE POLICY "user_growth_goals_select_own" ON public.user_growth_goals FOR SELECT
    USING (auth.uid() = user_id);
DROP POLICY IF EXISTS "user_growth_goals_insert_own" ON public.user_growth_goals;
CREATE POLICY "user_growth_goals_insert_own" ON public.user_growth_goals FOR INSERT
    WITH CHECK (auth.uid() = user_id);
DROP POLICY IF EXISTS "user_growth_goals_update_own" ON public.user_growth_goals;
CREATE POLICY "user_growth_goals_update_own" ON public.user_growth_goals FOR UPDATE
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "report_feedback_select_own" ON public.report_feedback;
CREATE POLICY "report_feedback_select_own" ON public.report_feedback FOR SELECT
    USING (auth.uid() = user_id);
DROP POLICY IF EXISTS "report_feedback_insert_own" ON public.report_feedback;
CREATE POLICY "report_feedback_insert_own" ON public.report_feedback FOR INSERT
    WITH CHECK (auth.uid() = user_id);

COMMENT ON TABLE public.user_reports IS 'V1.3 用户人生分析报告';
COMMENT ON TABLE public.user_growth_goals IS 'V1.3 用户长期成长目标';
COMMENT ON TABLE public.report_feedback IS 'V1.3 报告质量反馈';
