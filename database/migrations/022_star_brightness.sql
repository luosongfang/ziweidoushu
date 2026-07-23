-- =============================================================================
-- 022: 星曜亮度规则表（V1.2 扩展视图）— 与 brightness_rules 数据一致
-- =============================================================================

CREATE TABLE IF NOT EXISTS public.star_brightness_rules (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    star_name           TEXT NOT NULL,
    branch              TEXT NOT NULL,
    brightness          TEXT NOT NULL CHECK (brightness IN ('庙', '旺', '得', '利', '平', '陷', '不得')),
    source              TEXT NOT NULL DEFAULT 'sanhe_traditional',
    school              TEXT NOT NULL DEFAULT 'sanhe',
    version             TEXT NOT NULL DEFAULT '2026.07.23',
    UNIQUE (star_name, branch, school, version)
);

CREATE INDEX IF NOT EXISTS idx_star_brightness_star
    ON public.star_brightness_rules(star_name);

ALTER TABLE public.star_brightness_rules ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS star_brightness_rules_select ON public.star_brightness_rules;
CREATE POLICY star_brightness_rules_select ON public.star_brightness_rules
    FOR SELECT TO authenticated USING (true);

-- 从既有 brightness_rules 同步十四主星亮度（若存在）
INSERT INTO public.star_brightness_rules (star_name, branch, brightness, source, school, version)
SELECT star_name, branch, brightness, 'sanhe_traditional', school, '2026.07.23'
FROM public.brightness_rules
WHERE school = 'sanhe'
ON CONFLICT (star_name, branch, school, version) DO NOTHING;
