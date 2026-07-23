-- theory_knowledge seed (V1.0 minimal)
DELETE FROM public.theory_knowledge WHERE version = '1.0.0';

INSERT INTO public.theory_knowledge
(school, source_book, chapter, topic, content, summary, keywords, related_rules, ai_prompt, version)
VALUES
('sanhe', '紫微斗数概论', '总论', '命盘为自我观察框架',
 '紫微斗数以十二宫与星曜组合描述性格倾向、能力侧重与人生课题，宜作为自我认知与规划参考，而非对具体事件的断定。',
 '命盘用于自我观察与规划参考',
 '["自我认知","人生规划","参考框架"]'::jsonb,
 '["palace_knowledge","stars_knowledge"]'::jsonb,
 '强调文化参考属性，禁止绝对预测。',
 '1.0.0'),
('sanhe', '紫微斗数概论', '表达规范', '谨慎表达原则',
 '涉及未来、疾病、灾难、死亡与重大风险时，应使用谨慎、可行动的表达，引导用户提高准备度而非制造恐惧。',
 '重大风险话题需谨慎表达',
 '["安全表达","风险提示"]'::jsonb,
 '["safety_expression_rules"]'::jsonb,
 '遇到高风险话题必须引用 safety_expression_rules。',
 '1.0.0');
