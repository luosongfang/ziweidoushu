-- 006: 订单表（Sprint 8 商业化）

CREATE TABLE IF NOT EXISTS public.orders (
    id               UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id          UUID        NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    plan_id          TEXT        NOT NULL CHECK (plan_id IN ('basic', 'premium')),
    amount_cents     INTEGER     NOT NULL CHECK (amount_cents > 0),
    currency         TEXT        NOT NULL DEFAULT 'CNY',
    status           TEXT        NOT NULL DEFAULT 'pending'
                                 CHECK (status IN ('pending', 'paid', 'cancelled', 'refunded')),
    payment_provider TEXT,
    payment_ref      TEXT,
    metadata         JSONB       NOT NULL DEFAULT '{}',
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    paid_at          TIMESTAMPTZ
);

COMMENT ON TABLE public.orders IS '会员订阅订单';

CREATE INDEX IF NOT EXISTS idx_orders_user_id    ON public.orders(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_status     ON public.orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_created_at ON public.orders(created_at DESC);

ALTER TABLE public.orders ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "orders_select_own" ON public.orders;
CREATE POLICY "orders_select_own"
    ON public.orders FOR SELECT
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "orders_insert_own" ON public.orders;
CREATE POLICY "orders_insert_own"
    ON public.orders FOR INSERT
    WITH CHECK (auth.uid() = user_id);
