-- ===========================================
-- 003: AI 解读记录表
-- 存储每次 AI 分析的结果与用量
-- ===========================================

CREATE TABLE IF NOT EXISTS public.analyses (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    chart_id        UUID NOT NULL REFERENCES public.charts(id) ON DELETE CASCADE,
    analysis_type   TEXT NOT NULL DEFAULT 'overall'
                    CHECK (analysis_type IN ('overall', 'palace', 'daxian', 'liunian')),
    prompt_version  TEXT NOT NULL DEFAULT 'v1',
    input_context   JSONB,
    result_text     TEXT NOT NULL,
    tokens_used     INTEGER DEFAULT 0,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_analyses_user_id ON public.analyses(user_id);
CREATE INDEX idx_analyses_chart_id ON public.analyses(chart_id);

ALTER TABLE public.analyses ENABLE ROW LEVEL SECURITY;

CREATE POLICY "用户只能查看自己的解读"
    ON public.analyses FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "用户只能创建自己的解读"
    ON public.analyses FOR INSERT
    WITH CHECK (auth.uid() = user_id);
