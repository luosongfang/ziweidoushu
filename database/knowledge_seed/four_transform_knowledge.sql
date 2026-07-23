-- four_transform_knowledge seed V1.0 (sample stems)
DELETE FROM public.four_transform_knowledge WHERE version = '1.0.0';

INSERT INTO public.four_transform_knowledge
(stem, lu_star, quan_star, ke_star, ji_star, lu_meaning, quan_meaning, ke_meaning, ji_meaning, ai_prompt, version)
VALUES
('甲', '廉贞', '破军', '武曲', '太阳',
 '化禄常象征资源流动与展开机会，需主动兑现。',
 '化权常象征主导与推进力增强，需搭配倾听。',
 '化科常象征信誉、方法与学习表达。',
 '化忌提示需要复盘与边界管理的课题，不是灾难断言。',
 '四化解释必须基于本表含义，禁止恐吓。', '1.0.0'),
('庚', '太阳', '武曲', '太阴', '天同',
 '太阳化禄：外显机会与付出回报的流动可能增强。',
 '武曲化权：专业决断与执行主导可能被强化。',
 '太阴化科：细腻表达与信誉积累可能被强调。',
 '天同化忌：安稳需求与情绪课题需要整理，非灾祸断言。',
 '仅作倾向参考。', '1.0.0');
