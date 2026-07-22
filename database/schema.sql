-- =============================================================================
-- 紫微AI (Ziwei AI) — 完整数据库 Schema
-- 数据库：Supabase PostgreSQL
-- 执行位置：Supabase Dashboard → SQL Editor → 粘贴并 Run
-- =============================================================================
--
-- 依赖：Supabase 项目已创建，内置 auth.users 可用
-- 包含：扩展、表、索引、触发器、RLS 策略
--
-- 表一览：
--   public.profiles          用户扩展信息
--   public.charts            十二宫命盘
--   public.analyses          AI 解读记录
--   public.knowledge_chunks  RAG 向量知识库
-- =============================================================================


-- -----------------------------------------------------------------------------
-- 0. 扩展
-- -----------------------------------------------------------------------------

CREATE EXTENSION IF NOT EXISTS "pgcrypto";   -- gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS "vector";     -- RAG 向量检索


-- -----------------------------------------------------------------------------
-- 1. profiles — 用户扩展表
--    关联 Supabase Auth 内置 auth.users
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS public.profiles (
    id           UUID        PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    display_name TEXT,
    avatar_url   TEXT,
    membership   TEXT        NOT NULL DEFAULT 'free'
                             CHECK (membership IN ('free', 'basic', 'premium')),
    ai_quota     INTEGER     NOT NULL DEFAULT 3,      -- 剩余 AI 解读次数
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE  public.profiles            IS '用户扩展信息，与 auth.users 一对一';
COMMENT ON COLUMN public.profiles.membership IS '会员等级：free / basic / premium';
COMMENT ON COLUMN public.profiles.ai_quota   IS '剩余 AI 解读次数（free 默认 3 次）';


-- -----------------------------------------------------------------------------
-- 2. charts — 命盘表
--    chart_data JSONB 结构与前端 ChartData 类型对齐
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS public.charts (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID        NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name            TEXT        NOT NULL DEFAULT '未命名命盘',
    birth_datetime  TIMESTAMPTZ NOT NULL,
    gender          TEXT        NOT NULL CHECK (gender IN ('male', 'female')),
    calendar_type   TEXT        NOT NULL DEFAULT 'solar'
                                CHECK (calendar_type IN ('solar', 'lunar')),
    timezone        TEXT        NOT NULL DEFAULT 'Asia/Shanghai',
    chart_data      JSONB       NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE  public.charts              IS '紫微斗数十二宫命盘';
COMMENT ON COLUMN public.charts.chart_data   IS '完整命盘 JSON，含 meta + palaces[]';

/*
  chart_data 结构示例：

  {
    "meta": {
      "name": "演示命盘",
      "gender": "male",
      "birthDate": "1990年5月15日",
      "birthTime": "未时 (13:00–15:00)",
      "calendar": "solar",
      "lunarDate": "一九九〇年四月廿一",
      "yearStemBranch": "庚午",
      "monthStemBranch": "辛巳",
      "dayStemBranch": "庚辰",
      "hourStemBranch": "癸未",
      "wuxingJu": "土五局",
      "mingZhu": "贪狼",
      "shenZhu": "天同",
      "mingGong": "午",
      "shenGong": "戌"
    },
    "palaces": [
      {
        "name": "命宫",
        "branch": "午",
        "isMingGong": true,
        "isShenGong": false,
        "mainStars": [
          { "name": "紫微", "brightness": "庙", "isMain": true },
          { "name": "七杀", "brightness": "旺", "sihua": null, "isMain": true }
        ],
        "auxStars": [
          { "name": "左辅", "brightness": "" },
          { "name": "天魁", "brightness": "" }
        ],
        "daxian": { "startAge": 2, "endAge": 11 }
      }
    ]
  }
*/

CREATE INDEX IF NOT EXISTS idx_charts_user_id         ON public.charts(user_id);
CREATE INDEX IF NOT EXISTS idx_charts_birth_datetime  ON public.charts(birth_datetime);
CREATE INDEX IF NOT EXISTS idx_charts_created_at      ON public.charts(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_charts_data_ming_gong  ON public.charts((chart_data->'meta'->>'mingGong'));


-- -----------------------------------------------------------------------------
-- 3. analyses — AI 解读记录表
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS public.analyses (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID        NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    chart_id        UUID        NOT NULL REFERENCES public.charts(id) ON DELETE CASCADE,
    analysis_type   TEXT        NOT NULL DEFAULT 'overall'
                                CHECK (analysis_type IN ('overall', 'palace', 'daxian', 'liunian')),
    palace_name     TEXT,                           -- analysis_type = 'palace' 时指定宫位
    prompt_version  TEXT        NOT NULL DEFAULT 'v1',
    input_context   JSONB,
    result_text     TEXT        NOT NULL,
    tokens_used     INTEGER     NOT NULL DEFAULT 0,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE  public.analyses                IS 'AI 命盘解读历史记录';
COMMENT ON COLUMN public.analyses.analysis_type  IS '解读类型：overall / palace / daxian / liunian';
COMMENT ON COLUMN public.analyses.palace_name    IS '单宫解读时的宫位名称，如「命宫」';

CREATE INDEX IF NOT EXISTS idx_analyses_user_id    ON public.analyses(user_id);
CREATE INDEX IF NOT EXISTS idx_analyses_chart_id   ON public.analyses(chart_id);
CREATE INDEX IF NOT EXISTS idx_analyses_created_at ON public.analyses(created_at DESC);


-- -----------------------------------------------------------------------------
-- 4. knowledge_chunks — RAG 向量知识库
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS public.knowledge_chunks (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    source      TEXT        NOT NULL,               -- 来源古籍或流派
    category    TEXT        NOT NULL,               -- 主星 / 四化 / 宫位 / 大限 等
    title       TEXT,
    content     TEXT        NOT NULL,
    metadata    JSONB       NOT NULL DEFAULT '{}',
    embedding   vector(1536),                       -- OpenAI text-embedding-3-small
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE  public.knowledge_chunks           IS 'RAG 知识库文本片段';
COMMENT ON COLUMN public.knowledge_chunks.source    IS '来源，如「紫微斗数全书」';
COMMENT ON COLUMN public.knowledge_chunks.category  IS '分类：主星 / 四化 / 宫位 / 大限 / 流年';
COMMENT ON COLUMN public.knowledge_chunks.embedding IS '1536 维向量，用于语义检索';

CREATE INDEX IF NOT EXISTS idx_knowledge_category  ON public.knowledge_chunks(category);
CREATE INDEX IF NOT EXISTS idx_knowledge_source    ON public.knowledge_chunks(source);
CREATE INDEX IF NOT EXISTS idx_knowledge_embedding ON public.knowledge_chunks
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);


-- -----------------------------------------------------------------------------
-- 5. 通用函数：自动更新 updated_at
-- -----------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION public.set_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_profiles_updated_at ON public.profiles;
CREATE TRIGGER trg_profiles_updated_at
    BEFORE UPDATE ON public.profiles
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

DROP TRIGGER IF EXISTS trg_charts_updated_at ON public.charts;
CREATE TRIGGER trg_charts_updated_at
    BEFORE UPDATE ON public.charts
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();


-- -----------------------------------------------------------------------------
-- 6. 新用户注册时自动创建 profile
-- -----------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
    INSERT INTO public.profiles (id, display_name, avatar_url)
    VALUES (
        NEW.id,
        COALESCE(NEW.raw_user_meta_data->>'display_name', NEW.email),
        NEW.raw_user_meta_data->>'avatar_url'
    );
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();


-- -----------------------------------------------------------------------------
-- 7. Row Level Security (RLS)
-- -----------------------------------------------------------------------------

-- profiles
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "profiles_select_own" ON public.profiles;
CREATE POLICY "profiles_select_own"
    ON public.profiles FOR SELECT
    USING (auth.uid() = id);

DROP POLICY IF EXISTS "profiles_update_own" ON public.profiles;
CREATE POLICY "profiles_update_own"
    ON public.profiles FOR UPDATE
    USING (auth.uid() = id)
    WITH CHECK (auth.uid() = id);

-- charts
ALTER TABLE public.charts ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "charts_select_own" ON public.charts;
CREATE POLICY "charts_select_own"
    ON public.charts FOR SELECT
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "charts_insert_own" ON public.charts;
CREATE POLICY "charts_insert_own"
    ON public.charts FOR INSERT
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "charts_update_own" ON public.charts;
CREATE POLICY "charts_update_own"
    ON public.charts FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "charts_delete_own" ON public.charts;
CREATE POLICY "charts_delete_own"
    ON public.charts FOR DELETE
    USING (auth.uid() = user_id);

-- analyses
ALTER TABLE public.analyses ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "analyses_select_own" ON public.analyses;
CREATE POLICY "analyses_select_own"
    ON public.analyses FOR SELECT
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "analyses_insert_own" ON public.analyses;
CREATE POLICY "analyses_insert_own"
    ON public.analyses FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- knowledge_chunks（认证用户只读）
ALTER TABLE public.knowledge_chunks ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "knowledge_select_authenticated" ON public.knowledge_chunks;
CREATE POLICY "knowledge_select_authenticated"
    ON public.knowledge_chunks FOR SELECT
    TO authenticated
    USING (true);


-- -----------------------------------------------------------------------------
-- 8. 向量相似度检索函数（RAG 用）
-- -----------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION public.match_knowledge(
    query_embedding  vector(1536),
    match_count      INTEGER DEFAULT 5,
    filter_category  TEXT    DEFAULT NULL
)
RETURNS TABLE (
    id          UUID,
    source      TEXT,
    category    TEXT,
    title       TEXT,
    content     TEXT,
    metadata    JSONB,
    similarity  FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        kc.id,
        kc.source,
        kc.category,
        kc.title,
        kc.content,
        kc.metadata,
        1 - (kc.embedding <=> query_embedding) AS similarity
    FROM public.knowledge_chunks kc
    WHERE
        kc.embedding IS NOT NULL
        AND (filter_category IS NULL OR kc.category = filter_category)
    ORDER BY kc.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

COMMENT ON FUNCTION public.match_knowledge IS 'RAG 语义检索：按向量余弦相似度返回最相关知识片段';


-- -----------------------------------------------------------------------------
-- 9. orders — 会员订阅订单（Sprint 8）
-- -----------------------------------------------------------------------------

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

CREATE INDEX IF NOT EXISTS idx_orders_user_id ON public.orders(user_id);

ALTER TABLE public.orders ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "orders_select_own" ON public.orders;
CREATE POLICY "orders_select_own"
    ON public.orders FOR SELECT
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "orders_insert_own" ON public.orders;
CREATE POLICY "orders_insert_own"
    ON public.orders FOR INSERT
    WITH CHECK (auth.uid() = user_id);


-- =============================================================================
-- 完成。验证：
--   SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';
-- =============================================================================
