-- Knowledge Core V2 safety expression rules
-- Additive inserts into existing safety_expression_rules (V1.1 preserved).

DELETE FROM public.safety_expression_rules WHERE version = '2.0.0';

INSERT INTO public.safety_expression_rules
    (category, forbidden_expression, safe_expression, reason, risk_level, version)
VALUES
('absolute_failure', '你一定会失败', '这个方向可能存在压力与不确定性，建议分阶段验证并准备备选方案。', '禁止绝对失败断言', 'high', '2.0.0'),
('absolute_wealth', '你一定会发财', '可能具备财富管理优势，需要结合现实行动与风险管理。', '禁止绝对财富保证', 'high', '2.0.0'),
('disaster', '今年必有灾', '这个阶段建议提高风险意识，提前做好心理准备与规划。', '禁止灾难恐吓', 'high', '2.0.0'),
('disaster', '今年有灾', '这个阶段建议提高风险意识，做好规划。', '禁止灾难恐吓', 'high', '2.0.0'),
('divorce', '必然离婚', '关系模式可能存在需要沟通调整的地方，建议以经营视角看待。', '禁止婚姻宿命断言', 'high', '2.0.0'),
('divorce', '一定会离婚', '关系中或有需要沟通与边界调整的议题，可主动经营。', '禁止婚姻宿命断言', 'high', '2.0.0'),
('lifespan', '寿命', '关于寿命与重大健康议题，请以专业医疗建议为准；此处仅提供生活与压力管理参考。', '禁止寿命讨论', 'critical', '2.0.0'),
('death_time', '死亡时间', '关于寿命与重大健康风险，请以专业医疗建议为准。', '禁止死亡时间预测', 'critical', '2.0.0'),
('death', '死亡预测', '关于寿命与重大健康风险，请以专业医疗建议为准。', '禁止死亡预测', 'critical', '2.0.0'),
('medical', '疾病诊断', '健康议题请咨询专业医疗机构，这里只提供生活与压力管理建议。', '禁止医学诊断', 'critical', '2.0.0'),
('calamity', '有劫难', '传统理论认为某阶段可能存在压力或挑战，可以提前做好心理准备。', '劫难改压力表达', 'high', '2.0.0'),
('calamity', '必有灾难', '建议提高准备度并制定预案。', '禁止灾难断言', 'high', '2.0.0'),
('wealth_loss', '破财', '提示关注资源管理、风险控制和财务规划。', '破财改资源管理', 'medium', '2.0.0'),
('marriage', '婚姻不顺', '关系模式可能存在需要沟通调整的地方。', '婚姻不顺改沟通调整', 'medium', '2.0.0'),
('absolute', '一定会', '比较可能', '弱化绝对措辞', 'medium', '2.0.0'),
('absolute', '必然', '较可能', '弱化绝对措辞', 'medium', '2.0.0'),
('absolute', '注定', '倾向于', '弱化宿命措辞', 'medium', '2.0.0'),
('absolute', '百分百', '在一定程度上', '弱化绝对措辞', 'medium', '2.0.0'),
('guarantee', '稳赚不赔', '财务结果存在不确定性，建议控制风险。', '禁止收益保证', 'high', '2.0.0');
