-- Knowledge Core / Product V1.0 — membership & points (no payment)
-- Additive only — does not alter Knowledge Core V5.6 / V6.0 tables

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS public.membership_plan_catalog (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    price_cents INTEGER NOT NULL,
    billing_period TEXT NOT NULL DEFAULT 'month',
    analysis_quota INTEGER,
    ai_unlimited BOOLEAN DEFAULT FALSE,
    advisor_enabled BOOLEAN DEFAULT FALSE,
    monthly_points INTEGER DEFAULT 0,
    knowledge_access TEXT DEFAULT 'partial',
    features JSONB DEFAULT '[]'::jsonb,
    recommended BOOLEAN DEFAULT FALSE,
    sort_order INTEGER DEFAULT 0,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.user_membership (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    plan_id TEXT NOT NULL DEFAULT 'free',
    status TEXT NOT NULL DEFAULT 'active',
    started_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    analysis_used INTEGER DEFAULT 0,
    analysis_quota INTEGER,
    advisor_enabled BOOLEAN DEFAULT FALSE,
    knowledge_access TEXT DEFAULT 'none',
    metadata JSONB DEFAULT '{}'::jsonb,
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_um_status CHECK (status IN ('active', 'expired', 'cancelled')),
    CONSTRAINT chk_um_plan CHECK (
        plan_id IN ('free', 'basic', 'vip', 'svip')
    )
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_um_user_active
    ON public.user_membership(user_id)
    WHERE status = 'active';
CREATE INDEX IF NOT EXISTS idx_um_user
    ON public.user_membership(user_id);
CREATE INDEX IF NOT EXISTS idx_um_plan
    ON public.user_membership(plan_id);

CREATE TABLE IF NOT EXISTS public.user_points (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    balance INTEGER NOT NULL DEFAULT 0,
    lifetime_earned INTEGER NOT NULL DEFAULT 0,
    lifetime_spent INTEGER NOT NULL DEFAULT 0,
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_up_balance CHECK (balance >= 0)
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_up_user
    ON public.user_points(user_id);

CREATE TABLE IF NOT EXISTS public.user_points_ledger (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    delta INTEGER NOT NULL,
    balance_after INTEGER NOT NULL,
    reason TEXT NOT NULL,
    ref_type TEXT,
    ref_id UUID,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_upl_user
    ON public.user_points_ledger(user_id, created_at DESC);

CREATE TABLE IF NOT EXISTS public.membership_orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    plan_id TEXT NOT NULL,
    amount_cents INTEGER NOT NULL,
    currency TEXT NOT NULL DEFAULT 'CNY',
    status TEXT NOT NULL DEFAULT 'pending',
    payment_provider TEXT,
    payment_ref TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    paid_at TIMESTAMPTZ,
    CONSTRAINT chk_mo_status CHECK (
        status IN ('pending', 'paid', 'cancelled', 'refunded')
    ),
    CONSTRAINT chk_mo_plan CHECK (
        plan_id IN ('basic', 'vip', 'svip')
    )
);

CREATE INDEX IF NOT EXISTS idx_mo_user
    ON public.membership_orders(user_id);
CREATE INDEX IF NOT EXISTS idx_mo_status
    ON public.membership_orders(status);

INSERT INTO public.membership_plan_catalog
    (id, name, price_cents, billing_period, analysis_quota, ai_unlimited,
     advisor_enabled, monthly_points, knowledge_access, features, recommended, sort_order)
VALUES
    ('free', '免费用户', 0, 'once', 1, FALSE, FALSE, 0, 'none',
     '["一次完整排盘","一次专业解盘"]'::jsonb, FALSE, 0),
    ('basic', '普通会员', 2990, 'month', 10, FALSE, FALSE, 0, 'partial',
     '["每月10次专家级解盘","事业/财富/关系/阶段分析","部分知识来源"]'::jsonb, FALSE, 1),
    ('vip', 'VIP会员', 29900, 'year', NULL, FALSE, TRUE, 300, 'partial',
     '["不限次数解盘","AI人生导师","300积分/月","连续上下文记忆","成长档案"]'::jsonb, TRUE, 2),
    ('svip', 'SVIP会员', 69900, 'year', NULL, TRUE, TRUE, 0, 'full',
     '["不限解盘","不限AI交流","高级模型优先","完整知识引用","人生成长报告"]'::jsonb, FALSE, 3)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    price_cents = EXCLUDED.price_cents,
    features = EXCLUDED.features,
    recommended = EXCLUDED.recommended;
