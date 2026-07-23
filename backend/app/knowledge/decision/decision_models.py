"""Decision Intelligence V5.0 — ORM / fallback data models (no LLM)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from app.database.database import Base

JsonType = JSON().with_variant(JSONB(), "postgresql")


def _uuid() -> uuid.UUID:
    return uuid.uuid4()


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# ---------- Fallback seed data (used when DB empty) ----------

DECISION_SCENARIOS: list[dict[str, Any]] = [
    {
        "scenario_name": "career_change",
        "scenario_type": "career",
        "description": "职业转换 / 转型决策",
        "required_palaces": ["命宫", "官禄宫", "迁移宫"],
        "required_stars": ["破军", "七杀"],
        "required_patterns": ["杀破狼"],
        "required_cycles": ["career_build", "career_expand"],
        "decision_dimensions": ["career", "personality", "learning"],
        "risk_dimensions": ["career", "wealth"],
        "growth_dimensions": ["career", "growth"],
        "safety_level": "high",
        "keywords": ["转行", "转型", "换赛道", "跳槽", "职业转换"],
    },
    {
        "scenario_name": "entrepreneurship",
        "scenario_type": "career",
        "description": "创业选择",
        "required_palaces": ["命宫", "官禄宫", "财帛宫", "迁移宫", "福德宫"],
        "required_stars": ["紫微", "天府", "武曲"],
        "required_patterns": ["紫府同宫", "杀破狼"],
        "required_cycles": ["career_build", "career_expand"],
        "decision_dimensions": ["career", "wealth", "decision"],
        "risk_dimensions": ["wealth", "career"],
        "growth_dimensions": ["career", "growth", "learning"],
        "safety_level": "high",
        "keywords": ["创业", "开公司", "自己干", "做老板", "启动项目"],
    },
    {
        "scenario_name": "investment_decision",
        "scenario_type": "wealth",
        "description": "投资与资源配置决策",
        "required_palaces": ["财帛宫", "田宅宫", "官禄宫"],
        "required_stars": ["武曲", "天府", "禄存"],
        "required_patterns": [],
        "required_cycles": ["career_expand"],
        "decision_dimensions": ["wealth", "decision"],
        "risk_dimensions": ["wealth"],
        "growth_dimensions": ["wealth", "learning"],
        "safety_level": "high",
        "keywords": ["投资", "理财", "配置", "资产", "财富"],
    },
    {
        "scenario_name": "relationship_choice",
        "scenario_type": "relationship",
        "description": "感情与关系选择",
        "required_palaces": ["夫妻宫", "福德宫", "命宫"],
        "required_stars": ["贪狼", "天同"],
        "required_patterns": [],
        "required_cycles": ["relationship"],
        "decision_dimensions": ["relationship", "personality"],
        "risk_dimensions": ["relationship"],
        "growth_dimensions": ["relationship", "growth"],
        "safety_level": "high",
        "keywords": ["感情", "恋爱", "分手", "相处", "伴侣", "婚姻选择"],
    },
    {
        "scenario_name": "education_path",
        "scenario_type": "learning",
        "description": "学业与进修路径",
        "required_palaces": ["父母宫", "官禄宫", "命宫"],
        "required_stars": ["文昌", "文曲"],
        "required_patterns": [],
        "required_cycles": ["education", "career_build"],
        "decision_dimensions": ["learning", "career"],
        "risk_dimensions": ["learning"],
        "growth_dimensions": ["learning", "growth"],
        "safety_level": "medium",
        "keywords": ["学习", "考试", "进修", "考证", "学业"],
    },
    {
        "scenario_name": "relocation",
        "scenario_type": "life",
        "description": "迁移与环境选择",
        "required_palaces": ["迁移宫", "命宫", "官禄宫"],
        "required_stars": ["天马"],
        "required_patterns": [],
        "required_cycles": ["career_build", "career_expand", "life_transition"],
        "decision_dimensions": ["career", "decision"],
        "risk_dimensions": ["career", "family"],
        "growth_dimensions": ["growth", "learning"],
        "safety_level": "high",
        "keywords": ["搬家", "迁移", "出国", "换城市", "异地"],
    },
    {
        "scenario_name": "team_cooperation",
        "scenario_type": "career",
        "description": "合作与团队决策",
        "required_palaces": ["交友宫", "官禄宫", "命宫"],
        "required_stars": ["天府", "天相"],
        "required_patterns": ["紫府同宫"],
        "required_cycles": ["career_expand"],
        "decision_dimensions": ["career", "relationship", "decision"],
        "risk_dimensions": ["relationship", "career"],
        "growth_dimensions": ["career", "growth"],
        "safety_level": "medium",
        "keywords": ["合作", "合伙", "团队", "共事", "合伙人"],
    },
    {
        "scenario_name": "life_transition",
        "scenario_type": "life",
        "description": "人生重大选择与阶段转换",
        "required_palaces": ["命宫", "迁移宫", "官禄宫", "福德宫"],
        "required_stars": [],
        "required_patterns": [],
        "required_cycles": ["life_transition", "career_expand", "relationship"],
        "decision_dimensions": ["decision", "personality", "growth"],
        "risk_dimensions": ["decision"],
        "growth_dimensions": ["growth", "learning"],
        "safety_level": "high",
        "keywords": ["重大选择", "人生方向", "何去何从", "抉择", "要不要"],
    },
]

DIMENSION_RULES: list[dict[str, Any]] = [
    {
        "dimension": "career",
        "traditional_factor": "紫微",
        "positive_expression": "具备统筹与主导倾向，适合承担结构化责任",
        "challenge_expression": "需避免过度掌控导致协作摩擦",
        "growth_direction": "把领导力落到可验证的组织与交付机制",
        "source_reference": "星曜知识/紫微",
    },
    {
        "dimension": "career",
        "traditional_factor": "天府",
        "positive_expression": "资源整合与稳健经营能力突出",
        "challenge_expression": "可能偏保守，错失必要试错窗口",
        "growth_direction": "在稳健基础上做小范围试点扩张",
        "source_reference": "星曜知识/天府",
    },
    {
        "dimension": "career",
        "traditional_factor": "紫府同宫",
        "positive_expression": "战略视野与落地经营并存，资源整合优势明显",
        "challenge_expression": "需防止完美主义拖延行动",
        "growth_direction": "用里程碑把资源优势转化为成果",
        "source_reference": "格局/紫府朝垣",
    },
    {
        "dimension": "career",
        "traditional_factor": "杀破狼",
        "positive_expression": "变化适应与开创突破能力强",
        "challenge_expression": "节奏过快时容易透支与波动",
        "growth_direction": "为变化配套复盘与止损机制",
        "source_reference": "格局/杀破狼",
    },
    {
        "dimension": "career",
        "traditional_factor": "七杀",
        "positive_expression": "执行力与攻坚意愿较强",
        "challenge_expression": "压力情境下需注意沟通方式",
        "growth_direction": "把冲劲导向明确目标与协作流程",
        "source_reference": "星曜知识/七杀",
    },
    {
        "dimension": "career",
        "traditional_factor": "破军",
        "positive_expression": "具备打破惯性、推动转型的动能",
        "challenge_expression": "变动过频可能影响积累",
        "growth_direction": "把转型拆成阶段实验而非一次性翻转",
        "source_reference": "星曜知识/破军",
    },
    {
        "dimension": "wealth",
        "traditional_factor": "武曲",
        "positive_expression": "财务纪律与务实配置倾向",
        "challenge_expression": "需避免过度集中单一资产",
        "growth_direction": "先建安全垫，再谈进取配置",
        "source_reference": "星曜知识/武曲",
    },
    {
        "dimension": "wealth",
        "traditional_factor": "禄存",
        "positive_expression": "积累与守成意识较强",
        "challenge_expression": "机会成本意识不足时可能错失优化",
        "growth_direction": "定期复盘现金流与风险敞口",
        "source_reference": "星曜知识/禄存",
    },
    {
        "dimension": "wealth",
        "traditional_factor": "财帛宫",
        "positive_expression": "财富议题适合作为资源配置学习场景",
        "challenge_expression": "传统说法中的波动提醒应转为风险管理",
        "growth_direction": "用可验证预算与止损规则代替结果预测",
        "source_reference": "宫位知识/财帛宫",
    },
    {
        "dimension": "relationship",
        "traditional_factor": "夫妻宫",
        "positive_expression": "关系经营可作为沟通与边界练习场",
        "challenge_expression": "期待不清时容易消耗",
        "growth_direction": "建立定期对齐与清晰表达习惯",
        "source_reference": "宫位知识/夫妻宫",
    },
    {
        "dimension": "relationship",
        "traditional_factor": "贪狼",
        "positive_expression": "人际敏感度与表达力有优势",
        "challenge_expression": "需管理多线投入造成的不稳定感",
        "growth_direction": "把魅力转化为稳定的信任建设",
        "source_reference": "星曜知识/贪狼",
    },
    {
        "dimension": "family",
        "traditional_factor": "父母宫",
        "positive_expression": "可从权威支持与规范中获得学习资源",
        "challenge_expression": "边界模糊时易产生角色压力",
        "growth_direction": "用尊重与清晰边界并行的沟通",
        "source_reference": "宫位知识/父母宫",
    },
    {
        "dimension": "learning",
        "traditional_factor": "文昌",
        "positive_expression": "学习吸收与表达整理能力较好",
        "challenge_expression": "需避免只学不用",
        "growth_direction": "把知识转化成作品与反馈循环",
        "source_reference": "星曜知识/文昌",
    },
    {
        "dimension": "health_lifestyle",
        "traditional_factor": "疾厄宫",
        "positive_expression": "适合建立长期节律与自我照顾意识",
        "challenge_expression": "高压阶段需提前安排恢复机制",
        "growth_direction": "把作息与复盘纳入人生规划清单",
        "source_reference": "宫位知识/疾厄宫",
    },
    {
        "dimension": "personality",
        "traditional_factor": "命宫",
        "positive_expression": "自我认知是决策质量的基础",
        "challenge_expression": "自我标签化可能限制选择空间",
        "growth_direction": "用反馈实验更新自我模型",
        "source_reference": "宫位知识/命宫",
    },
    {
        "dimension": "decision",
        "traditional_factor": "大限",
        "positive_expression": "阶段性主题可帮助对齐中期目标",
        "challenge_expression": "勿把阶段主题误解为命运判决",
        "growth_direction": "把周期主题拆成可验证里程碑",
        "source_reference": "大限规则/生命周期",
    },
    {
        "dimension": "decision",
        "traditional_factor": "官禄宫",
        "positive_expression": "事业路径选择适合对照能力与环境匹配度",
        "challenge_expression": "单一路径依赖可能降低弹性",
        "growth_direction": "保留备选方案与退出机制",
        "source_reference": "宫位知识/官禄宫",
    },
]

PROCESS_STEPS: list[dict[str, Any]] = [
    {
        "step_order": 1,
        "title": "当前状态分析",
        "content_template": "结合命盘结构、人生阶段与提问意图，先描述当下可观察的状态与资源。",
        "safety_expression": "状态描述不等于命运判决。",
    },
    {
        "step_order": 2,
        "title": "传统理论观察",
        "content_template": "从三合、四化与大限等传统视角给出对照观察，并标注知识来源。",
        "safety_expression": "传统观察仅供文化学习与自我认知参考。",
    },
    {
        "step_order": 3,
        "title": "优势资源",
        "content_template": "列出可转化为行动的优势与资源，强调可验证性。",
        "safety_expression": "优势需要实践转化，不作成功保证。",
    },
    {
        "step_order": 4,
        "title": "潜在挑战",
        "content_template": "用风险管理语言提示挑战，避免恐吓与宿命表述。",
        "safety_expression": "挑战是提醒而非灾难预言。",
    },
    {
        "step_order": 5,
        "title": "可行动建议",
        "content_template": "给出小步验证、复盘与资源安排类建议。",
        "safety_expression": "建议需结合现实条件自主判断。",
    },
    {
        "step_order": 6,
        "title": "自我反思问题",
        "content_template": "提出开放式反思问题，帮助用户澄清价值观与约束。",
        "safety_expression": "反思问题不代替专业咨询。",
    },
]

SAFETY_RULES: list[dict[str, str]] = [
    {
        "forbidden_expression": "你一定会失败",
        "safe_expression": "传统理论认为可能存在某些需要提前关注的倾向，建议结合现实条件做小步验证。",
        "reason": "禁止绝对失败预言",
        "risk_level": "high",
    },
    {
        "forbidden_expression": "你命中注定破财",
        "safe_expression": "传统理论认为财富议题上可能存在波动倾向，可以提前关注风险管理与安全垫。",
        "reason": "禁止宿命破财",
        "risk_level": "high",
    },
    {
        "forbidden_expression": "今年必有灾",
        "safe_expression": "传统流年视角提示此阶段宜加强风险意识与复盘，不作绝对灾难预测。",
        "reason": "禁止绝对灾难",
        "risk_level": "high",
    },
    {
        "forbidden_expression": "必须离婚",
        "safe_expression": "关系议题上建议先对齐沟通与边界，重要决定请结合现实条件与专业支持审慎判断。",
        "reason": "禁止强制关系结局",
        "risk_level": "high",
    },
    {
        "forbidden_expression": "一定发财",
        "safe_expression": "传统理论认为可能存在某些积累倾向，最终仍取决于配置纪律与现实执行。",
        "reason": "禁止绝对发财",
        "risk_level": "high",
    },
    {
        "forbidden_expression": "命中注定",
        "safe_expression": "传统理论认为可能存在某些倾向",
        "reason": "禁止宿命论",
        "risk_level": "high",
    },
    {
        "forbidden_expression": "必然会",
        "safe_expression": "传统观察提示可以提前关注",
        "reason": "禁止必然语气",
        "risk_level": "high",
    },
    {
        "forbidden_expression": "一定会",
        "safe_expression": "建议结合现实条件判断",
        "reason": "禁止绝对语气",
        "risk_level": "high",
    },
]


class DecisionModelRow(Base):
    __tablename__ = "decision_models"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    scenario_name: Mapped[str] = mapped_column(String(64), unique=True)
    scenario_type: Mapped[str | None] = mapped_column(String(64))
    description: Mapped[str | None] = mapped_column(Text)
    required_palaces: Mapped[list] = mapped_column(JsonType, default=list)
    required_stars: Mapped[list] = mapped_column(JsonType, default=list)
    required_patterns: Mapped[list] = mapped_column(JsonType, default=list)
    required_cycles: Mapped[list] = mapped_column(JsonType, default=list)
    decision_dimensions: Mapped[list] = mapped_column(JsonType, default=list)
    risk_dimensions: Mapped[list] = mapped_column(JsonType, default=list)
    growth_dimensions: Mapped[list] = mapped_column(JsonType, default=list)
    safety_level: Mapped[str | None] = mapped_column(String(16), default="high")
    version: Mapped[str | None] = mapped_column(String(32), default="5.0.0")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class DecisionDimensionRuleRow(Base):
    __tablename__ = "decision_dimension_rules"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    dimension: Mapped[str] = mapped_column(String(64))
    traditional_factor: Mapped[str] = mapped_column(Text)
    positive_expression: Mapped[str | None] = mapped_column(Text)
    challenge_expression: Mapped[str | None] = mapped_column(Text)
    growth_direction: Mapped[str | None] = mapped_column(Text)
    source_reference: Mapped[str | None] = mapped_column(Text)
    version: Mapped[str | None] = mapped_column(String(32), default="5.0.0")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class DecisionProcessTemplateRow(Base):
    __tablename__ = "decision_process_templates"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    scenario: Mapped[str] = mapped_column(String(64))
    step_order: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(Text)
    content_template: Mapped[str | None] = mapped_column(Text)
    safety_expression: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class DecisionHistoryRow(Base):
    __tablename__ = "decision_history"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    question_type: Mapped[str | None] = mapped_column(String(64))
    question_summary: Mapped[str | None] = mapped_column(Text)
    analysis_summary: Mapped[str | None] = mapped_column(Text)
    suggestions: Mapped[list] = mapped_column(JsonType, default=list)
    user_feedback: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class DecisionSafetyRuleRow(Base):
    __tablename__ = "decision_safety_rules"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    forbidden_expression: Mapped[str] = mapped_column(Text)
    safe_expression: Mapped[str] = mapped_column(Text)
    reason: Mapped[str | None] = mapped_column(Text)
    risk_level: Mapped[str | None] = mapped_column(String(16), default="high")
    version: Mapped[str | None] = mapped_column(String(32), default="5.0.0")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
