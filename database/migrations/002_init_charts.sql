-- ===========================================
-- 002: 命盘表
-- 存储用户生成的紫微斗数命盘 JSON
-- ===========================================

CREATE TABLE IF NOT EXISTS public.charts (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name            TEXT NOT NULL DEFAULT '未命名命盘',
    birth_datetime  TIMESTAMPTZ NOT NULL,
    gender          TEXT NOT NULL CHECK (gender IN ('male', 'female')),
    calendar_type   TEXT NOT NULL DEFAULT 'solar' CHECK (calendar_type IN ('solar', 'lunar')),
    timezone        TEXT NOT NULL DEFAULT 'Asia/Shanghai',
    chart_data      JSONB NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_charts_user_id ON public.charts(user_id);
CREATE INDEX idx_charts_birth_datetime ON public.charts(birth_datetime);

ALTER TABLE public.charts ENABLE ROW LEVEL SECURITY;

CREATE POLICY "用户只能查看自己的命盘"
    ON public.charts FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "用户只能创建自己的命盘"
    ON public.charts FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "用户只能更新自己的命盘"
    ON public.charts FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "用户只能删除自己的命盘"
    ON public.charts FOR DELETE
    USING (auth.uid() = user_id);
