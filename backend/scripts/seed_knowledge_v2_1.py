"""Seed Knowledge Core V2.1 — advisor dimension / templates / action models."""

from __future__ import annotations

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

BACKEND = Path(__file__).resolve().parents[1]
ROOT = BACKEND.parent
load_dotenv(BACKEND / ".env", override=True)

VERSION = "2.1.0"


def j(obj) -> str:
    return json.dumps(obj, ensure_ascii=False)


DIMENSIONS = [
    {
        "dimension_code": "career",
        "dimension_name": "事业发展",
        "description": "职业方向、社会角色与长期事业模式。",
        "positive_expression": "领导能力、规划意识、专业深耕与协作推进。",
        "challenge_expression": "目标漂移、责任过载、节奏失衡。",
        "growth_direction": "用可验证里程碑把方向变成阶段行动。",
        "safety_level": "medium",
    },
    {
        "dimension_code": "wealth",
        "dimension_name": "财富规划",
        "description": "资源态度、风险偏好与价值交换方式。",
        "positive_expression": "积累纪律、价值创造、风险识别。",
        "challenge_expression": "冲动投入、忽视安全垫、过度乐观。",
        "growth_direction": "先建立现金流安全垫，再谈进取配置。",
        "safety_level": "high",
    },
    {
        "dimension_code": "relationship",
        "dimension_name": "感情关系",
        "description": "亲密互动、边界与沟通模式。",
        "positive_expression": "连接意愿、同理心、经营意识。",
        "challenge_expression": "投射控制、沟通回避、边界模糊。",
        "growth_direction": "用定期复盘与清晰表达改善关系质量。",
        "safety_level": "high",
    },
    {
        "dimension_code": "family",
        "dimension_name": "家庭关系",
        "description": "长辈、晚辈与家庭角色边界。",
        "positive_expression": "责任感、照顾力、价值传承。",
        "challenge_expression": "权威冲突、过度付出、角色混淆。",
        "growth_direction": "区分可继承价值与需更新规则。",
        "safety_level": "medium",
    },
    {
        "dimension_code": "learning",
        "dimension_name": "学习成长",
        "description": "学习风格、能力建设与知识落地。",
        "positive_expression": "学习力、表达力、迁移应用。",
        "challenge_expression": "纸上谈兵、动力波动。",
        "growth_direction": "学以致用，连接实务反馈。",
        "safety_level": "low",
    },
    {
        "dimension_code": "personality",
        "dimension_name": "自我认知",
        "description": "气质倾向、决策风格与压力反应。",
        "positive_expression": "自我觉察、优势识别。",
        "challenge_expression": "标签化自我、把象征当判决。",
        "growth_direction": "把倾向转为可练习的行为实验。",
        "safety_level": "medium",
    },
    {
        "dimension_code": "decision",
        "dimension_name": "决策质量",
        "description": "选择框架、风险权衡与执行节奏。",
        "positive_expression": "结构化决策、止损意识。",
        "challenge_expression": "冲动或过度犹豫。",
        "growth_direction": "小步验证 + 明确退出条件。",
        "safety_level": "high",
    },
    {
        "dimension_code": "growth",
        "dimension_name": "人生成长",
        "description": "阶段主题、补给系统与长期发展。",
        "positive_expression": "反思力、适应力、持续改进。",
        "challenge_expression": "透支、迷茫、缺乏锚点。",
        "growth_direction": "设定阶段主题并配套能量补给。",
        "safety_level": "medium",
    },
]

TEMPLATES = [
    {
        "question_type": "career_choice",
        "user_question_examples": ["事业方向如何？", "适合什么职业？", "如何长期发展？"],
        "required_dimensions": ["career", "personality", "decision"],
        "recommended_focus": ["领导能力", "专业深耕", "阶段目标"],
        "avoid_topics": ["必然成功", "升职保证", "命运判决"],
    },
    {
        "question_type": "entrepreneurship",
        "user_question_examples": ["适合创业吗？", "要不要自己干？", "创业如何评估？"],
        "required_dimensions": ["career", "wealth", "decision", "growth"],
        "recommended_focus": ["变化能力", "风险意识", "试错机制"],
        "avoid_topics": ["一定发财", "适合/不适合二元判决", "稳赚不赔"],
    },
    {
        "question_type": "job_change",
        "user_question_examples": ["要不要转行？", "换赛道怎么做？"],
        "required_dimensions": ["career", "decision", "growth"],
        "recommended_focus": ["可迁移能力", "切换成本", "分阶段过渡"],
        "avoid_topics": ["转行必成", "旧行业必败"],
    },
    {
        "question_type": "relationship",
        "user_question_examples": ["感情模式怎样？", "如何改善关系？"],
        "required_dimensions": ["relationship", "personality", "growth"],
        "recommended_focus": ["沟通", "边界", "成长"],
        "avoid_topics": ["离婚预测", "必然分手", "必婚"],
    },
    {
        "question_type": "marriage",
        "user_question_examples": ["婚姻如何经营？", "婚后相处注意什么？"],
        "required_dimensions": ["relationship", "family", "growth"],
        "recommended_focus": ["沟通", "共同经营", "边界"],
        "avoid_topics": ["必然离婚", "婚姻必失败"],
    },
    {
        "question_type": "investment",
        "user_question_examples": ["如何理财？", "投资要注意什么？"],
        "required_dimensions": ["wealth", "decision"],
        "recommended_focus": ["风险管理", "安全垫", "纪律"],
        "avoid_topics": ["一定发财", "稳赚不赔", "破财断言"],
    },
    {
        "question_type": "life_confusion",
        "user_question_examples": ["人生很迷茫怎么办？", "下一步该怎么走？"],
        "required_dimensions": ["growth", "personality", "decision"],
        "recommended_focus": ["阶段主题", "小步实验", "自我锚点"],
        "avoid_topics": ["命运注定", "灾难恐吓"],
    },
    {
        "question_type": "self_growth",
        "user_question_examples": ["如何认识自己？", "怎样成长？"],
        "required_dimensions": ["personality", "growth", "learning"],
        "recommended_focus": ["优势识别", "行为实验", "补给系统"],
        "avoid_topics": ["病理诊断", "人格判决"],
    },
]

ACTIONS = [
    {
        "pattern_code": "紫府同宫",
        "condition": {"stars": ["紫微", "天府"]},
        "strength_analysis": "组织能力、资源整合倾向、领导能力与规划意识较强。",
        "risk_reminder": "容易承担过多责任，压力累积。",
        "action_suggestions": ["建立团队分工", "学习授权", "做长期规划并设阶段节点"],
        "growth_path": ["明确核心职责", "授权试点", "复盘压力来源", "扩大可复用流程"],
    },
    {
        "pattern_code": "紫府朝垣",
        "condition": {"stars": ["紫微", "天府"], "alias": "紫府同宫"},
        "strength_analysis": "管理意识强，资源统筹与稳定经营倾向。",
        "risk_reminder": "责任压力过高，可能忽视授权。",
        "action_suggestions": ["建立团队", "学习授权", "长期规划"],
        "growth_path": ["识别可授权事项", "培养二号位", "用仪表盘管理结果"],
    },
    {
        "pattern_code": "杀破狼",
        "condition": {"stars": ["七杀", "破军", "贪狼"]},
        "strength_analysis": "变化适应能力、突破力与行动欲望突出。",
        "risk_reminder": "冲动决策、善始难终、风险暴露过高。",
        "action_suggestions": ["建立试错机制", "控制风险", "设定止损线与复盘节奏"],
        "growth_path": ["小范围验证", "写清退出条件", "里程碑约束变革", "强化风险意识"],
    },
    {
        "pattern_code": "机月同梁",
        "condition": {"stars": ["天机", "太阴", "天梁"]},
        "strength_analysis": "思辨、协调与清誉型解决问题能力。",
        "risk_reminder": "思虑过多、执行拖延。",
        "action_suggestions": ["最小可行方案落地", "设定截止时间", "把建议变成可交付物"],
        "growth_path": ["选题收敛", "原型验证", "对外反馈", "迭代优化"],
    },
    {
        "pattern_code": "武贪",
        "condition": {"stars": ["武曲", "贪狼"]},
        "strength_analysis": "执行力与开拓欲结合，技能变现倾向。",
        "risk_reminder": "目标漂移或协作摩擦。",
        "action_suggestions": ["优先级清单", "深耕一个主赛道", "拓展设配额"],
        "growth_path": ["选定主技能", "量化产出", "有限拓展", "复盘效率"],
    },
    {
        "pattern_code": "昌曲",
        "condition": {"stars": ["文昌", "文曲"]},
        "strength_analysis": "学习力与表达力突出。",
        "risk_reminder": "停留在纸面方案。",
        "action_suggestions": ["学以致用", "作品化输出", "考试/项目双轨"],
        "growth_path": ["输入", "实践", "作品", "反馈"],
    },
    {
        "pattern_code": "七杀入命",
        "condition": {"ming_contains": ["七杀"]},
        "strength_analysis": "行动力、突破性与面对变化的能力。",
        "risk_reminder": "需要学习规划与节奏管理，避免冲动。",
        "action_suggestions": ["行动前设冷静窗口", "配套计划与止损", "高压任务分段推进"],
        "growth_path": ["识别触发冲动的场景", "建立决策清单", "练习节奏管理"],
    },
    {
        "pattern_code": "通用决策",
        "condition": {"always": True},
        "strength_analysis": "可基于宫位与星曜组合识别可迁移优势。",
        "risk_reminder": "避免把传统象征当作确定事件预测。",
        "action_suggestions": ["明确问题维度", "列出可验证下一步", "设定复盘时间"],
        "growth_path": ["觉察", "小实验", "反馈", "调整"],
    },
]

# Map classifier types -> advisor question templates
QTYPE_MAP = {
    "career": "career_choice",
    "entrepreneurship": "entrepreneurship",
    "career_switch": "job_change",
    "wealth": "investment",
    "relationship": "relationship",
    "marriage": "marriage",
    "study": "self_growth",
    "family": "self_growth",
    "personality": "self_growth",
    "life_stage": "life_confusion",
}


def main() -> None:
    eng = create_engine(os.environ["DATABASE_URL"], pool_pre_ping=True, isolation_level="AUTOCOMMIT")
    schema = (ROOT / "database" / "migrations" / "006_advisor_model.sql").read_text(encoding="utf-8")

    with eng.connect() as conn:
        for stmt in [s.strip() for s in schema.split(";") if s.strip()]:
            body = "\n".join(
                ln for ln in stmt.splitlines() if ln.strip() and not ln.strip().startswith("--")
            ).strip()
            if not body:
                continue
            conn.execute(text(body))
        print("migration 006_advisor_model applied")

        for d in DIMENSIONS:
            conn.execute(
                text(
                    """
                    INSERT INTO public.advisor_dimension_rules (
                        dimension_code, dimension_name, description, positive_expression,
                        challenge_expression, growth_direction, safety_level, version
                    ) VALUES (
                        :dimension_code, :dimension_name, :description, :positive_expression,
                        :challenge_expression, :growth_direction, :safety_level, :version
                    )
                    ON CONFLICT (dimension_code) DO UPDATE SET
                        dimension_name=EXCLUDED.dimension_name,
                        description=EXCLUDED.description,
                        positive_expression=EXCLUDED.positive_expression,
                        challenge_expression=EXCLUDED.challenge_expression,
                        growth_direction=EXCLUDED.growth_direction,
                        safety_level=EXCLUDED.safety_level,
                        version=EXCLUDED.version
                    """
                ),
                {**d, "version": VERSION},
            )
        print("dimensions", len(DIMENSIONS))

        for t in TEMPLATES:
            conn.execute(
                text(
                    """
                    INSERT INTO public.advisor_question_templates (
                        question_type, user_question_examples, required_dimensions,
                        recommended_focus, avoid_topics, version
                    ) VALUES (
                        :question_type, CAST(:user_question_examples AS jsonb),
                        CAST(:required_dimensions AS jsonb), CAST(:recommended_focus AS jsonb),
                        CAST(:avoid_topics AS jsonb), :version
                    )
                    ON CONFLICT (question_type) DO UPDATE SET
                        user_question_examples=EXCLUDED.user_question_examples,
                        required_dimensions=EXCLUDED.required_dimensions,
                        recommended_focus=EXCLUDED.recommended_focus,
                        avoid_topics=EXCLUDED.avoid_topics,
                        version=EXCLUDED.version
                    """
                ),
                {
                    **t,
                    "user_question_examples": j(t["user_question_examples"]),
                    "required_dimensions": j(t["required_dimensions"]),
                    "recommended_focus": j(t["recommended_focus"]),
                    "avoid_topics": j(t["avoid_topics"]),
                    "version": VERSION,
                },
            )
        print("templates", len(TEMPLATES))

        for a in ACTIONS:
            conn.execute(
                text(
                    """
                    INSERT INTO public.advisor_action_models (
                        pattern_code, condition, strength_analysis, risk_reminder,
                        action_suggestions, growth_path, version
                    ) VALUES (
                        :pattern_code, CAST(:condition AS jsonb), :strength_analysis,
                        :risk_reminder, CAST(:action_suggestions AS jsonb),
                        CAST(:growth_path AS jsonb), :version
                    )
                    ON CONFLICT (pattern_code, version) DO UPDATE SET
                        condition=EXCLUDED.condition,
                        strength_analysis=EXCLUDED.strength_analysis,
                        risk_reminder=EXCLUDED.risk_reminder,
                        action_suggestions=EXCLUDED.action_suggestions,
                        growth_path=EXCLUDED.growth_path
                    """
                ),
                {
                    **a,
                    "condition": j(a["condition"]),
                    "action_suggestions": j(a["action_suggestions"]),
                    "growth_path": j(a["growth_path"]),
                    "version": VERSION,
                },
            )
        print("actions", len(ACTIONS))

        # V2.1 extra safety rows
        conn.execute(text("DELETE FROM public.safety_expression_rules WHERE version = '2.1.0'"))
        for forbidden, safe, cat in [
            ("你今年一定破财", "传统理论认为该阶段需要更加关注风险管理。", "wealth"),
            ("今年一定破财", "传统理论认为该阶段需要更加关注风险管理。", "wealth"),
            ("你的婚姻必失败", "关系模式中可能存在需要沟通改善的地方。", "relationship"),
            ("婚姻必失败", "关系模式中可能存在需要沟通改善的地方。", "relationship"),
            ("会发生灾难", "不作为确定事件预测，仅作为传统文化角度的反思参考。", "disaster"),
            ("离婚预测", "关系议题请聚焦沟通、边界与共同成长，不做确定性预测。", "relationship"),
            ("必然成功", "结果取决于准备度、执行与环境反馈，建议分阶段验证。", "absolute"),
            ("一定发财", "可能具备财富管理优势，需要结合现实行动与风险控制。", "wealth"),
        ]:
            conn.execute(
                text(
                    """
                    INSERT INTO public.safety_expression_rules
                        (category, forbidden_expression, safe_expression, reason, risk_level, version)
                    VALUES (:c, :f, :s, 'advisor v2.1', 'high', '2.1.0')
                    """
                ),
                {"c": cat, "f": forbidden, "s": safe},
            )
        print("safety 2.1 inserted")

        for t in [
            "advisor_dimension_rules",
            "advisor_question_templates",
            "advisor_action_models",
        ]:
            n = conn.execute(text(f"SELECT COUNT(*) FROM public.{t}")).scalar()
            print(f"COUNT {t}={n}")


if __name__ == "__main__":
    main()
