-- =============================================================================
-- 021: 辅助杂曜规则表 — Ziwei Core Engine V1.2
-- =============================================================================

CREATE TABLE IF NOT EXISTS public.auxiliary_star_rules (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    star_name           TEXT NOT NULL,
    category            TEXT NOT NULL DEFAULT 'auxiliary',
    rule_type           TEXT NOT NULL,
    rule_expression     JSONB NOT NULL DEFAULT '{}',
    source              TEXT NOT NULL DEFAULT 'sanhe_traditional',
    enabled             BOOLEAN NOT NULL DEFAULT true,
    school              TEXT NOT NULL DEFAULT 'sanhe',
    version             TEXT NOT NULL DEFAULT '2026.07.23'
);

CREATE INDEX IF NOT EXISTS idx_auxiliary_star_rules_star
    ON public.auxiliary_star_rules(star_name);
CREATE INDEX IF NOT EXISTS idx_auxiliary_star_rules_enabled
    ON public.auxiliary_star_rules(enabled);

ALTER TABLE public.auxiliary_star_rules ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS auxiliary_star_rules_select ON public.auxiliary_star_rules;
CREATE POLICY auxiliary_star_rules_select ON public.auxiliary_star_rules
    FOR SELECT TO authenticated USING (true);

-- 种子：九颗辅助杂曜（与 app.ziwei.rules.auxiliary_star_rules 一致）
DELETE FROM public.auxiliary_star_rules WHERE school = 'sanhe' AND version = '2026.07.23';

INSERT INTO public.auxiliary_star_rules (star_name, category, rule_type, rule_expression, source, enabled, school, version) VALUES
('红鸾', 'auxiliary', 'branch_offset', '{"base_branch":"卯","direction":"backward","offset":0,"by":"year_branch"}', 'sanhe_traditional', true, 'sanhe', '2026.07.23'),
('天喜', 'auxiliary', 'opposite_branch', '{"base_star":"红鸾","offset":6}', 'sanhe_traditional', true, 'sanhe', '2026.07.23'),
('天姚', 'auxiliary', 'branch_offset', '{"base_branch":"丑","direction":"forward","offset":0,"by":"lunar_month"}', 'sanhe_traditional', true, 'sanhe', '2026.07.23'),
('天刑', 'auxiliary', 'branch_offset', '{"base_branch":"酉","direction":"backward","offset":0,"by":"year_branch"}', 'sanhe_traditional', true, 'sanhe', '2026.07.23'),
('天虚', 'auxiliary', 'branch_offset', '{"base_branch":"午","direction":"backward","offset":0,"by":"year_branch"}', 'sanhe_traditional', true, 'sanhe', '2026.07.23'),
('天哭', 'auxiliary', 'branch_offset', '{"base_branch":"午","direction":"forward","offset":0,"by":"year_branch"}', 'sanhe_traditional', true, 'sanhe', '2026.07.23'),
('孤辰', 'auxiliary', 'branch_group', '{"by":"year_branch","mapping":{"寅卯辰":"巳","巳午未":"申","申酉戌":"亥","亥子丑":"寅"}}', 'sanhe_traditional', true, 'sanhe', '2026.07.23'),
('寡宿', 'auxiliary', 'branch_group', '{"by":"year_branch","mapping":{"寅卯辰":"丑","巳午未":"辰","申酉戌":"未","亥子丑":"戌"}}', 'sanhe_traditional', true, 'sanhe', '2026.07.23'),
('华盖', 'auxiliary', 'branch_group', '{"by":"year_branch","mapping":{"寅午戌":"戌","申子辰":"辰","巳酉丑":"丑","亥卯未":"未"}}', 'sanhe_traditional', true, 'sanhe', '2026.07.23');
