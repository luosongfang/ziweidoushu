"""Seed Knowledge Core V2.0 — theory / matrices / scenarios / safety."""

from __future__ import annotations

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

BACKEND = Path(__file__).resolve().parents[1]
ROOT = BACKEND.parent
load_dotenv(BACKEND / ".env", override=True)

VERSION = "2.0.0"


def j(obj) -> str:
    return json.dumps(obj, ensure_ascii=False)


THEORY_RULES = [
    {
        "category": "命宫理论",
        "rule_name": "命宫主星定基",
        "rule_expression": "以命宫主星为自我气质与决策底色的核心参考。",
        "traditional_meaning": "命宫主星象征先天心性与处事倾向。",
        "modern_interpretation": "用于自我认知：了解偏好、决策风格与压力反应，而非命运判决。",
        "application_scope": ["career", "growth", "relationship"],
        "risk_expression": "避免把命宫主星解读为固定人格标签。",
        "safety_level": "low",
    },
    {
        "category": "身宫理论",
        "rule_name": "身宫行为取向",
        "rule_expression": "身宫侧重后天行为习惯与对外呈现方式。",
        "traditional_meaning": "身宫论后天作为与社会显现。",
        "modern_interpretation": "观察工作习惯、对外形象与行动节奏，辅助行为调整。",
        "application_scope": ["career", "growth"],
        "risk_expression": "不做人格病理化描述。",
        "safety_level": "low",
    },
    {
        "category": "三方四正",
        "rule_name": "三方四正互参",
        "rule_expression": "本宫需与对宫、三合宫共同解读，忌单宫断语。",
        "traditional_meaning": "三方四正互为表里，合参方见结构。",
        "modern_interpretation": "事业议题看命宫、官禄、财帛、迁移的联动；关系议题看夫妻、福德等联动。",
        "application_scope": ["career", "wealth", "relationship", "growth"],
        "risk_expression": "禁止只凭单星单宫下结论。",
        "safety_level": "medium",
    },
    {
        "category": "四化理论",
        "rule_name": "四化动态调节",
        "rule_expression": "禄权科忌描述能量流向与压力点，不作吉凶判决。",
        "traditional_meaning": "四化论生年动态与宫位感应。",
        "modern_interpretation": "化禄偏资源流动，化权偏主导，化科偏表达认可，化忌偏压力课题。",
        "application_scope": ["career", "wealth", "relationship", "growth"],
        "risk_expression": "化忌不得表达为灾难、失败、死亡。",
        "safety_level": "high",
    },
    {
        "category": "大限理论",
        "rule_name": "大限阶段主题",
        "rule_expression": "大限描述约十年阶段主题与准备重点。",
        "traditional_meaning": "大限论阶段性运势主题。",
        "modern_interpretation": "用于人生阶段规划：识别主题、准备度与可调整空间。",
        "application_scope": ["growth", "career"],
        "risk_expression": "禁止对未来做灾难恐吓或绝对断言。",
        "safety_level": "high",
    },
    {
        "category": "流年理论",
        "rule_name": "流年节奏提醒",
        "rule_expression": "流年用于短期节奏与注意力分配，不作年度判决。",
        "traditional_meaning": "流年论一年感应。",
        "modern_interpretation": "帮助安排年度重点、风险预案与能量管理。",
        "application_scope": ["growth", "career", "wealth"],
        "risk_expression": "禁止「今年必有灾」类表述。",
        "safety_level": "high",
    },
    {
        "category": "星曜组合",
        "rule_name": "紫府朝垣",
        "rule_expression": "紫微与天府同宫或朝垣形成资源统筹型结构。",
        "traditional_meaning": "紫府朝垣，象征稳重管理与库藏。",
        "modern_interpretation": "资源整合与管理意识较强；需注意责任压力与授权。",
        "application_scope": ["career", "wealth", "growth"],
        "risk_expression": "避免「必成大业」绝对断言。",
        "safety_level": "medium",
    },
    {
        "category": "格局理论",
        "rule_name": "杀破狼",
        "rule_expression": "七杀、破军、贪狼同现，形成变动开创型结构。",
        "traditional_meaning": "杀破狼象征开创、变革与强烈行动欲。",
        "modern_interpretation": "变化适应与突破力强；需配套止损、复盘与节奏管理。",
        "application_scope": ["career", "growth", "wealth"],
        "risk_expression": "禁止「大起大落必败」恐吓。",
        "safety_level": "medium",
    },
    {
        "category": "格局理论",
        "rule_name": "机月同梁",
        "rule_expression": "天机、太阴、天同、天梁形成清誉谋略型结构。",
        "traditional_meaning": "机月同梁，主清贵谋略与协调。",
        "modern_interpretation": "适合研究、咨询、协调类发展；警惕思虑过多与执行拖延。",
        "application_scope": ["career", "growth", "relationship"],
        "risk_expression": "不做「必贵」断言。",
        "safety_level": "medium",
    },
    {
        "category": "星曜组合",
        "rule_name": "府相朝垣",
        "rule_expression": "天府与天相形成辅佐守成型结构。",
        "traditional_meaning": "府相朝垣，主稳重辅弼。",
        "modern_interpretation": "协作规范与流程意识强；需培养独立决断。",
        "application_scope": ["career", "relationship"],
        "risk_expression": "避免依赖权威叙事。",
        "safety_level": "low",
    },
]

STAR_COMBOS = [
    {
        "star_a": "紫微",
        "star_b": "天府",
        "star_c": None,
        "combination_name": "紫微天府",
        "traditional_pattern": "紫府朝垣 / 紫府同宫",
        "personality_dimension": "统筹意识强，责任感高，偏稳重管理。",
        "career_dimension": "资源整合与组织协调能力突出。",
        "wealth_dimension": "偏稳健经营与长期积累。",
        "relationship_dimension": "重视边界与承诺，可能偏管控。",
        "challenge_dimension": "责任压力过高，授权不足。",
        "growth_direction": "培养授权能力，把统筹落到可验证目标。",
        "ai_tags": ["management", "stability", "career"],
    },
    {
        "star_a": "七杀",
        "star_b": "破军",
        "star_c": "贪狼",
        "combination_name": "杀破狼",
        "traditional_pattern": "杀破狼",
        "personality_dimension": "行动欲强，变革敏感，开拓取向明显。",
        "career_dimension": "适合开创、转型与高压推进场景。",
        "wealth_dimension": "机会导向，波动偏好较高。",
        "relationship_dimension": "节奏变化快，需要清晰沟通。",
        "challenge_dimension": "善始难终、冲动决策、风险过高。",
        "growth_direction": "配套止损线、里程碑与复盘机制。",
        "ai_tags": ["change", "entrepreneurship", "action"],
    },
    {
        "star_a": "天机",
        "star_b": "太阴",
        "star_c": "天梁",
        "combination_name": "机月同梁",
        "traditional_pattern": "机月同梁",
        "personality_dimension": "思辨细腻，清誉与谋略倾向。",
        "career_dimension": "研究、咨询、教育、协调类优势。",
        "wealth_dimension": "细水长流，偏知识与信誉变现。",
        "relationship_dimension": "重视安全感与照顾，或偏操心。",
        "challenge_dimension": "思虑过多、执行拖延、好为人师。",
        "growth_direction": "用最小可行方案把思考落地。",
        "ai_tags": ["analysis", "consulting", "growth"],
    },
    {
        "star_a": "武曲",
        "star_b": "贪狼",
        "star_c": None,
        "combination_name": "武贪",
        "traditional_pattern": "武贪同行",
        "personality_dimension": "执行与开拓并重，专业进取。",
        "career_dimension": "技术变现与商务拓展结合。",
        "wealth_dimension": "技能与机会双通道。",
        "relationship_dimension": "直接坦率，魅力互动。",
        "challenge_dimension": "目标漂移或协作摩擦。",
        "growth_direction": "用优先级清单平衡深耕与拓展。",
        "ai_tags": ["career", "wealth", "execution"],
    },
    {
        "star_a": "太阳",
        "star_b": "太阴",
        "star_c": None,
        "combination_name": "日月并明",
        "traditional_pattern": "日月并明",
        "personality_dimension": "外显与内省并存，表达与滋养兼顾。",
        "career_dimension": "传播教育与研究服务可并重。",
        "wealth_dimension": "分享与细水长流并进。",
        "relationship_dimension": "热情与敏感并存，需边界。",
        "challenge_dimension": "能量消耗与内耗交替。",
        "growth_direction": "建立付出与补给的平衡节奏。",
        "ai_tags": ["relationship", "career", "balance"],
    },
    {
        "star_a": "天同",
        "star_b": "天梁",
        "star_c": None,
        "combination_name": "同梁",
        "traditional_pattern": "同梁嘉会",
        "personality_dimension": "亲和担当，偏协调化解。",
        "career_dimension": "服务、顾问、公益教育取向。",
        "wealth_dimension": "稳健信誉型积累。",
        "relationship_dimension": "照顾他人，温和体贴。",
        "challenge_dimension": "安逸惰性或负担过重。",
        "growth_direction": "舒适区外设小挑战，照顾他人同时设边界。",
        "ai_tags": ["growth", "relationship", "service"],
    },
    {
        "star_a": "廉贞",
        "star_b": "贪狼",
        "star_c": None,
        "combination_name": "廉贪",
        "traditional_pattern": "廉贪同行",
        "personality_dimension": "原则感与欲望拓展并存，魅力与张力明显。",
        "career_dimension": "创意表达、风控与商务拓展。",
        "wealth_dimension": "起伏较大，需纪律。",
        "relationship_dimension": "激情与冲突并存。",
        "challenge_dimension": "情绪振幅与关系消耗。",
        "growth_direction": "用规则与复盘稳定情绪与欲望带宽。",
        "ai_tags": ["relationship", "career", "emotion"],
    },
    {
        "star_a": "文昌",
        "star_b": "文曲",
        "star_c": None,
        "combination_name": "昌曲",
        "traditional_pattern": "昌曲加会",
        "personality_dimension": "学习力与表达力强。",
        "career_dimension": "知识工作、写作考试、创意设计。",
        "wealth_dimension": "知识与才艺变现。",
        "relationship_dimension": "理性与感性表达并存。",
        "challenge_dimension": "纸上谈兵或稳定性不足。",
        "growth_direction": "学以致用，灵感沉淀为可交付作品。",
        "ai_tags": ["study", "career", "expression"],
    },
]

PALACE_DIMS = []
_PALACES = [
    ("命宫", "自我气质", "自我认同与选择底色"),
    ("兄弟宫", "同辈协作", "平辈信任与横向关系"),
    ("夫妻宫", "配偶宫", "亲密关系与长期合作"),
    ("子女宫", "子息宫", "创造表达与晚辈互动"),
    ("财帛宫", "财帛", "资源态度与价值交换"),
    ("疾厄宫", "疾厄", "压力负荷与身心节奏"),
    ("迁移宫", "迁移", "外部环境与变动适应"),
    ("仆役宫", "交友", "人际网络与支持系统"),
    ("官禄宫", "官禄", "职业方向与社会角色"),
    ("田宅宫", "田宅", "根据地与生活根基"),
    ("福德宫", "福德", "精神补给与内在安定"),
    ("父母宫", "父母", "长辈关系与学习权威"),
]
_DIMS = {
    "事业": {
        "focus": ["命宫", "官禄宫", "财帛宫", "迁移宫"],
        "advice": "结合人格倾向、事业模式、资源态度与外部环境，给出可验证的阶段性行动。",
    },
    "财富": {
        "focus": ["财帛宫", "田宅宫", "官禄宫"],
        "advice": "匹配风险偏好建立现金流安全垫，再谈进取配置。",
    },
    "关系": {
        "focus": ["夫妻宫", "福德宫", "命宫", "仆役宫"],
        "advice": "用沟通、边界与定期复盘代替宿命化解读。",
    },
    "家庭": {
        "focus": ["父母宫", "子女宫", "田宅宫", "福德宫"],
        "advice": "区分可继承价值与需更新规则，经营互惠关系。",
    },
    "成长": {
        "focus": ["命宫", "福德宫", "官禄宫"],
        "advice": "把传统象征转为可练习的自我模型与补给习惯。",
    },
}
for pname, trad, modern_base in _PALACES:
    for dim, meta in _DIMS.items():
        in_focus = pname in meta["focus"]
        PALACE_DIMS.append(
            {
                "palace_name": pname,
                "dimension": dim,
                "traditional_meaning": f"{trad}在「{dim}」议题中的宫位象征。",
                "modern_meaning": (
                    f"{modern_base}；在{dim}维度中{'为核心参考宫' if in_focus else '作辅助参考'}。"
                ),
                "question_mapping": [
                    f"{dim}相关问题如何理解{pname}？",
                    f"{pname}对{dim}意味着什么？",
                ],
                "advice_template": meta["advice"] if in_focus else f"在{dim}议题中参考{pname}的现代含义，避免单宫断语。",
            }
        )

FOUR_TRANSFORM = [
    {
        "year_stem": None,
        "transform_type": "化禄",
        "star_name": None,
        "traditional_effect": "传统以化禄论资禄流动与喜庆感。",
        "modern_effect": "资源更容易流动，机会感增强。",
        "positive_expression": "利于积累、连接与价值交换。",
        "challenge_expression": "可能因机会增多而分心。",
        "growth_advice": "把流动资源沉淀为可复用资产与纪律。",
    },
    {
        "year_stem": None,
        "transform_type": "化权",
        "star_name": None,
        "traditional_effect": "传统以化权论权柄与主导。",
        "modern_effect": "主导欲与决策权重上升。",
        "positive_expression": "利于推进项目与承担责任。",
        "challenge_expression": "可能过度掌控或压迫协作。",
        "growth_advice": "主导同时保留反馈通道与授权空间。",
    },
    {
        "year_stem": None,
        "transform_type": "化科",
        "star_name": None,
        "traditional_effect": "传统以化科论文名、贵人与化解。",
        "modern_effect": "表达认可、专业形象与沟通缓冲增强。",
        "positive_expression": "利于学习、考试、品牌与声誉。",
        "challenge_expression": "可能停留在表面认可。",
        "growth_advice": "把认可转化为可交付成果与专业壁垒。",
    },
    {
        "year_stem": None,
        "transform_type": "化忌",
        "star_name": None,
        "traditional_effect": "传统以化忌论阻滞与牵绊。",
        "modern_effect": "容易形成某方面压力，需要提升认知和调整方式。",
        "positive_expression": "压力可转化为专注与问题意识。",
        "challenge_expression": "该领域更易出现卡住、纠结或消耗感。",
        "growth_advice": "针对压力点做小步实验、边界管理与支持系统建设。",
    },
]
# stem-specific light samples (甲己化)
STEM_MAP = {
    "甲": ("廉贞", "破军", "武曲", "太阳"),
    "乙": ("天机", "天梁", "紫微", "太阴"),
    "丙": ("天同", "天机", "文昌", "廉贞"),
    "丁": ("太阴", "天同", "天机", "巨门"),
    "戊": ("贪狼", "太阴", "右弼", "天机"),
    "己": ("武曲", "贪狼", "天梁", "文曲"),
    "庚": ("太阳", "武曲", "太阴", "天同"),
    "辛": ("巨门", "太阳", "文曲", "文昌"),
    "壬": ("天梁", "紫微", "左辅", "武曲"),
    "癸": ("破军", "巨门", "太阴", "贪狼"),
}
TYPES = ["化禄", "化权", "化科", "化忌"]
for stem, stars in STEM_MAP.items():
    for t, s in zip(TYPES, stars):
        base = next(x for x in FOUR_TRANSFORM if x["transform_type"] == t)
        FOUR_TRANSFORM.append(
            {
                **base,
                "year_stem": stem,
                "star_name": s,
                "traditional_effect": f"{stem}干{t}于{s}。{base['traditional_effect']}",
                "modern_effect": f"当关注{s}所在宫位议题时，{base['modern_effect']}",
            }
        )

LIFE_SCENARIOS = [
    {
        "scenario_name": "career_choice",
        "display_name": "职业选择",
        "required_palaces": ["命宫", "官禄宫", "财帛宫"],
        "required_patterns": ["紫府朝垣", "杀破狼", "机月同梁"],
        "analysis_steps": ["命宫人格", "官禄事业模式", "财帛资源态度", "格局矩阵", "输出优势注意建议"],
        "output_structure": ["traditional_view", "modern_view", "strengths", "challenges", "growth_direction"],
        "safety_rules": ["禁止升职成败绝对预测", "禁止保证成功"],
        "related_question_types": ["career"],
    },
    {
        "scenario_name": "entrepreneurship",
        "display_name": "创业",
        "required_palaces": ["命宫", "官禄宫", "财帛宫", "迁移宫", "福德宫"],
        "required_patterns": ["杀破狼", "紫府朝垣"],
        "analysis_steps": ["人格倾向", "资源能力", "风险偏好", "执行模式", "内在补给"],
        "output_structure": ["strengths", "challenges", "growth_direction", "reflection_questions"],
        "safety_rules": ["禁止是否创业二元判决", "输出优势注意建议"],
        "related_question_types": ["entrepreneurship"],
    },
    {
        "scenario_name": "marriage_relationship",
        "display_name": "婚姻关系",
        "required_palaces": ["夫妻宫", "福德宫", "命宫"],
        "required_patterns": [],
        "analysis_steps": ["互动模式", "内在需求", "自我边界", "沟通建议"],
        "output_structure": ["traditional_view", "modern_view", "strengths", "challenges", "growth_direction"],
        "safety_rules": ["禁止必婚必离", "禁止必然离婚"],
        "related_question_types": ["relationship", "marriage"],
    },
    {
        "scenario_name": "wealth_planning",
        "display_name": "财富规划",
        "required_palaces": ["财帛宫", "田宅宫", "官禄宫"],
        "required_patterns": [],
        "analysis_steps": ["资源态度", "根据地", "事业变现", "风险控制"],
        "output_structure": ["strengths", "challenges", "growth_direction"],
        "safety_rules": ["禁止财富保证", "禁止稳赚不赔"],
        "related_question_types": ["wealth"],
    },
    {
        "scenario_name": "learning_growth",
        "display_name": "学习成长",
        "required_palaces": ["父母宫", "官禄宫", "命宫"],
        "required_patterns": ["昌曲"],
        "analysis_steps": ["学习权威", "能力映射", "自我驱动"],
        "output_structure": ["strengths", "challenges", "growth_direction"],
        "safety_rules": ["禁止考试必过"],
        "related_question_types": ["study", "personality"],
    },
    {
        "scenario_name": "family_relation",
        "display_name": "家庭关系",
        "required_palaces": ["父母宫", "子女宫", "福德宫"],
        "required_patterns": [],
        "analysis_steps": ["长辈关系", "创造养育", "内在补给"],
        "output_structure": ["strengths", "challenges", "growth_direction"],
        "safety_rules": ["不做家庭冲突宿命论"],
        "related_question_types": ["family"],
    },
    {
        "scenario_name": "life_transition",
        "display_name": "人生转折",
        "required_palaces": ["命宫", "迁移宫", "官禄宫"],
        "required_patterns": ["杀破狼"],
        "analysis_steps": ["自我状态", "外部环境", "事业节奏", "准备度"],
        "output_structure": ["traditional_view", "modern_view", "challenges", "growth_direction"],
        "safety_rules": ["禁止灾难恐吓", "涉及未来必须谨慎表达"],
        "related_question_types": ["life_stage", "career_switch"],
    },
    {
        "scenario_name": "personal_strength",
        "display_name": "个人优势",
        "required_palaces": ["命宫", "福德宫", "官禄宫"],
        "required_patterns": [],
        "analysis_steps": ["命宫倾向", "福德补给", "事业表达", "成长建议"],
        "output_structure": ["strengths", "growth_direction", "reflection_questions"],
        "safety_rules": ["不做病理诊断"],
        "related_question_types": ["personality"],
    },
]

QUESTION_TYPE_TO_SCENARIO = {
    "career": "career_choice",
    "entrepreneurship": "entrepreneurship",
    "career_switch": "life_transition",
    "wealth": "wealth_planning",
    "relationship": "marriage_relationship",
    "marriage": "marriage_relationship",
    "study": "learning_growth",
    "family": "family_relation",
    "personality": "personal_strength",
    "life_stage": "life_transition",
}


def main() -> None:
    eng = create_engine(os.environ["DATABASE_URL"], pool_pre_ping=True, isolation_level="AUTOCOMMIT")
    schema = (ROOT / "database" / "knowledge_schema_v2.sql").read_text(encoding="utf-8")
    safety = (ROOT / "database" / "safety_expression_v2.sql").read_text(encoding="utf-8")

    with eng.connect() as conn:
        for stmt in [s.strip() for s in schema.split(";") if s.strip()]:
            conn.execute(text(stmt))
        print("schema v2 applied")

        for stmt in [s.strip() for s in safety.split(";") if s.strip()]:
            conn.execute(text(stmt))
        print("safety v2 applied")

        for r in THEORY_RULES:
            conn.execute(
                text(
                    """
                    INSERT INTO public.ziwei_theory_rules (
                        category, rule_name, rule_expression, traditional_meaning,
                        modern_interpretation, application_scope, risk_expression,
                        safety_level, school, version
                    ) VALUES (
                        :category, :rule_name, :rule_expression, :traditional_meaning,
                        :modern_interpretation, CAST(:application_scope AS jsonb),
                        :risk_expression, :safety_level, 'sanhe', :version
                    )
                    ON CONFLICT (rule_name, school, version) DO UPDATE SET
                        category=EXCLUDED.category,
                        rule_expression=EXCLUDED.rule_expression,
                        traditional_meaning=EXCLUDED.traditional_meaning,
                        modern_interpretation=EXCLUDED.modern_interpretation,
                        application_scope=EXCLUDED.application_scope,
                        risk_expression=EXCLUDED.risk_expression,
                        safety_level=EXCLUDED.safety_level
                    """
                ),
                {**r, "application_scope": j(r["application_scope"]), "version": VERSION},
            )
        print("theory_rules", len(THEORY_RULES))

        for c in STAR_COMBOS:
            conn.execute(
                text(
                    """
                    INSERT INTO public.star_combination_matrix (
                        star_a, star_b, star_c, combination_name, traditional_pattern,
                        personality_dimension, career_dimension, wealth_dimension,
                        relationship_dimension, challenge_dimension, growth_direction,
                        ai_tags, version
                    ) VALUES (
                        :star_a, :star_b, :star_c, :combination_name, :traditional_pattern,
                        :personality_dimension, :career_dimension, :wealth_dimension,
                        :relationship_dimension, :challenge_dimension, :growth_direction,
                        CAST(:ai_tags AS jsonb), :version
                    )
                    ON CONFLICT (combination_name, version) DO UPDATE SET
                        star_a=EXCLUDED.star_a, star_b=EXCLUDED.star_b, star_c=EXCLUDED.star_c,
                        traditional_pattern=EXCLUDED.traditional_pattern,
                        personality_dimension=EXCLUDED.personality_dimension,
                        career_dimension=EXCLUDED.career_dimension,
                        wealth_dimension=EXCLUDED.wealth_dimension,
                        relationship_dimension=EXCLUDED.relationship_dimension,
                        challenge_dimension=EXCLUDED.challenge_dimension,
                        growth_direction=EXCLUDED.growth_direction,
                        ai_tags=EXCLUDED.ai_tags
                    """
                ),
                {**c, "ai_tags": j(c["ai_tags"]), "version": VERSION},
            )
        print("star_combos", len(STAR_COMBOS))

        for p in PALACE_DIMS:
            conn.execute(
                text(
                    """
                    INSERT INTO public.palace_dimension_matrix (
                        palace_name, dimension, traditional_meaning, modern_meaning,
                        question_mapping, advice_template, version
                    ) VALUES (
                        :palace_name, :dimension, :traditional_meaning, :modern_meaning,
                        CAST(:question_mapping AS jsonb), :advice_template, :version
                    )
                    ON CONFLICT (palace_name, dimension, version) DO UPDATE SET
                        traditional_meaning=EXCLUDED.traditional_meaning,
                        modern_meaning=EXCLUDED.modern_meaning,
                        question_mapping=EXCLUDED.question_mapping,
                        advice_template=EXCLUDED.advice_template
                    """
                ),
                {**p, "question_mapping": j(p["question_mapping"]), "version": VERSION},
            )
        print("palace_dims", len(PALACE_DIMS))

        conn.execute(text("DELETE FROM public.four_transform_matrix WHERE version = :v"), {"v": VERSION})
        for f in FOUR_TRANSFORM:
            conn.execute(
                text(
                    """
                    INSERT INTO public.four_transform_matrix (
                        year_stem, transform_type, star_name, traditional_effect,
                        modern_effect, positive_expression, challenge_expression,
                        growth_advice, version
                    ) VALUES (
                        :year_stem, :transform_type, :star_name, :traditional_effect,
                        :modern_effect, :positive_expression, :challenge_expression,
                        :growth_advice, :version
                    )
                    """
                ),
                {**f, "version": VERSION},
            )
        print("four_transform", len(FOUR_TRANSFORM))

        for s in LIFE_SCENARIOS:
            conn.execute(
                text(
                    """
                    INSERT INTO public.life_scenario_models (
                        scenario_name, display_name, required_palaces, required_patterns,
                        analysis_steps, output_structure, safety_rules,
                        related_question_types, version
                    ) VALUES (
                        :scenario_name, :display_name,
                        CAST(:required_palaces AS jsonb), CAST(:required_patterns AS jsonb),
                        CAST(:analysis_steps AS jsonb), CAST(:output_structure AS jsonb),
                        CAST(:safety_rules AS jsonb), CAST(:related_question_types AS jsonb),
                        :version
                    )
                    ON CONFLICT (scenario_name) DO UPDATE SET
                        display_name=EXCLUDED.display_name,
                        required_palaces=EXCLUDED.required_palaces,
                        required_patterns=EXCLUDED.required_patterns,
                        analysis_steps=EXCLUDED.analysis_steps,
                        output_structure=EXCLUDED.output_structure,
                        safety_rules=EXCLUDED.safety_rules,
                        related_question_types=EXCLUDED.related_question_types,
                        version=EXCLUDED.version
                    """
                ),
                {
                    **s,
                    "required_palaces": j(s["required_palaces"]),
                    "required_patterns": j(s["required_patterns"]),
                    "analysis_steps": j(s["analysis_steps"]),
                    "output_structure": j(s["output_structure"]),
                    "safety_rules": j(s["safety_rules"]),
                    "related_question_types": j(s["related_question_types"]),
                    "version": VERSION,
                },
            )
        print("life_scenarios", len(LIFE_SCENARIOS))

        for t in [
            "ziwei_theory_rules",
            "star_combination_matrix",
            "palace_dimension_matrix",
            "four_transform_matrix",
            "life_scenario_models",
            "user_question_memory",
            "safety_expression_rules",
        ]:
            n = conn.execute(text(f"SELECT COUNT(*) FROM public.{t}")).scalar()
            print(f"COUNT {t}={n}")


if __name__ == "__main__":
    main()
