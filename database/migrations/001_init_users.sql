-- ===========================================
-- 001: 用户扩展表
-- 依赖 Supabase Auth 内置 auth.users 表
-- 在 Supabase SQL Editor 中执行
-- ===========================================

CREATE TABLE IF NOT EXISTS public.profiles (
    id          UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    display_name TEXT,
    avatar_url   TEXT,
    membership   TEXT NOT NULL DEFAULT 'free',  -- free / basic / premium
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "用户只能查看自己的 profile"
    ON public.profiles FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "用户只能更新自己的 profile"
    ON public.profiles FOR UPDATE
    USING (auth.uid() = id);
