-- ziwei_patterns seed V1.0
DELETE FROM public.ziwei_patterns WHERE version = '1.0.0';

INSERT INTO public.ziwei_patterns
(pattern_name, category, conditions, related_stars, related_palaces,
 traditional_meaning, advantages, challenges, career_analysis, wealth_analysis,
 relationship_analysis, growth_advice, ai_prompt, version)
VALUES
('紫府同宫', 'combo',
 '{"ming_gong_contains":["紫微","天府"]}'::jsonb,
 '["紫微","天府"]'::jsonb, '["命宫"]'::jsonb,
 '传统上常以紫微天府同宫象征稳健统御与府库涵养并存。',
 '["统筹管理","长期主义","资源整合"]'::jsonb,
 '["偏保守","压力内化"]'::jsonb,
 '较适合组织建设、运营管理与需要持续经营的方向。',
 '偏稳健积累，建议保留可控进取仓位。',
 '重视承诺与稳定，需练习情感表达。',
 '用阶段性目标验证管理优势，避免只求稳不进取。',
 '仅依据格局知识解释，禁止阶层承诺。', '1.0.0'),

('杀破狼', 'combo',
 '{"has_stars":["七杀","破军","贪狼"]}'::jsonb,
 '["七杀","破军","贪狼"]'::jsonb, '[]'::jsonb,
 '传统上常称杀破狼，象征变动、开创与强烈行动欲望。',
 '["开创突破","高行动力","适应变化"]'::jsonb,
 '["节奏不稳","风险暴露"]'::jsonb,
 '较适应开拓、转型与高迭代任务，需配套复盘。',
 '机会波动可能更大，建议设置止损与Diversify。',
 '关系节奏可能偏快，需协商边界。',
 '把冲劲变成可管理的实验：小步试错+明确退出条件。',
 '禁止恐吓式大起大落表述。', '1.0.0'),

('机月同梁', 'combo',
 '{"has_stars":["天机","太阴","天同","天梁"]}'::jsonb,
 '["天机","太阴","天同","天梁"]'::jsonb, '[]'::jsonb,
 '传统上常描述为清贵、谋略与顾念并存的象征组合。',
 '["策划分析","顾念他人","学习表达"]'::jsonb,
 '["优柔","情绪内耗"]'::jsonb,
 '较适合研究、咨询、内容与需要细腻沟通的岗位。',
 '偏稳健与长期价值创造。',
 '重视情感安全，需避免过度操心。',
 '用决策清单减少内耗，把体贴转化为清晰边界。',
 '禁止必然清贵成功的断言。', '1.0.0');
