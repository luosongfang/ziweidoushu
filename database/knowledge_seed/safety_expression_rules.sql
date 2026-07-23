-- safety_expression_rules seed V1.0
DELETE FROM public.safety_expression_rules WHERE version = '1.0.0';

INSERT INTO public.safety_expression_rules
(category, forbidden_expression, safe_expression, reason, risk_level, version)
VALUES
('absolute', '一定会', '比较可能 / 倾向于', '禁止绝对预测', 'high', '1.0.0'),
('absolute', '必然', '较可能', '禁止绝对预测', 'high', '1.0.0'),
('absolute', '注定', '倾向于', '禁止宿命论', 'high', '1.0.0'),
('absolute', '百分百', '在一定程度上', '禁止绝对化', 'high', '1.0.0'),
('wealth', '一定会发财', '可能具备财富管理优势，需要结合现实行动。', '禁止财富保证', 'critical', '1.0.0'),
('wealth', '稳赚不赔', '财务结果存在不确定性，建议控制风险。', '禁止收益保证', 'critical', '1.0.0'),
('disaster', '今年有灾', '这个阶段建议提高风险意识，做好规划。', '禁止灾难恐吓', 'critical', '1.0.0'),
('disaster', '必有灾难', '建议提高准备度并制定预案。', '禁止灾难恐吓', 'critical', '1.0.0'),
('health', '疾病诊断', '健康议题请咨询专业医疗机构，这里只提供生活与压力管理建议。', '禁止医疗诊断', 'critical', '1.0.0'),
('death', '死亡预测', '关于寿命与重大健康风险，请以专业医疗建议为准。', '禁止死亡预测', 'critical', '1.0.0');
