"""Knowledge Core ORM models — Supabase / PostgreSQL."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from app.database.database import Base


def _uuid() -> uuid.UUID:
    return uuid.uuid4()


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# JSONB on Postgres; JSON fallback for local sqlite tests
JsonType = JSON().with_variant(JSONB(), "postgresql")


class TheoryKnowledge(Base):
    __tablename__ = "theory_knowledge"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    school: Mapped[str] = mapped_column(String(32), default="sanhe")
    source_book: Mapped[str | None] = mapped_column(String(128))
    chapter: Mapped[str | None] = mapped_column(String(128))
    topic: Mapped[str] = mapped_column(String(128))
    content: Mapped[str] = mapped_column(Text)
    summary: Mapped[str | None] = mapped_column(Text)
    keywords: Mapped[list] = mapped_column(JsonType, default=list)
    related_rules: Mapped[list] = mapped_column(JsonType, default=list)
    ai_prompt: Mapped[str | None] = mapped_column(Text)
    version: Mapped[str] = mapped_column(String(32), default="1.0.0")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class StarsKnowledge(Base):
    __tablename__ = "stars_knowledge"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    star_name: Mapped[str] = mapped_column(String(32), unique=True)
    category: Mapped[str] = mapped_column(String(32), default="main")
    five_element: Mapped[str | None] = mapped_column(String(8))
    yin_yang: Mapped[str | None] = mapped_column(String(4))
    basic_meaning: Mapped[str | None] = mapped_column(Text)
    personality_positive: Mapped[list] = mapped_column(JsonType, default=list)
    personality_challenge: Mapped[list] = mapped_column(JsonType, default=list)
    career_strength: Mapped[list] = mapped_column(JsonType, default=list)
    career_risk: Mapped[list] = mapped_column(JsonType, default=list)
    wealth_pattern: Mapped[list] = mapped_column(JsonType, default=list)
    relationship_pattern: Mapped[list] = mapped_column(JsonType, default=list)
    life_stage_expression: Mapped[str | None] = mapped_column(Text)
    traditional_description: Mapped[str | None] = mapped_column(Text)
    growth_advice: Mapped[str | None] = mapped_column(Text)
    ai_prompt: Mapped[str | None] = mapped_column(Text)
    source_reference: Mapped[str | None] = mapped_column(Text)
    version: Mapped[str] = mapped_column(String(32), default="1.0.0")


class PalaceKnowledge(Base):
    __tablename__ = "palace_knowledge"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    palace_name: Mapped[str] = mapped_column(String(32), unique=True)
    basic_meaning: Mapped[str | None] = mapped_column(Text)
    life_area: Mapped[str | None] = mapped_column(String(64))
    psychological_meaning: Mapped[str | None] = mapped_column(Text)
    modern_interpretation: Mapped[str | None] = mapped_column(Text)
    positive_expression: Mapped[str | None] = mapped_column(Text)
    challenge_expression: Mapped[str | None] = mapped_column(Text)
    development_direction: Mapped[str | None] = mapped_column(Text)
    development_advice: Mapped[str | None] = mapped_column(Text)
    common_questions: Mapped[list] = mapped_column(JsonType, default=list)
    common_user_questions: Mapped[list] = mapped_column(JsonType, default=list)
    ai_prompt: Mapped[str | None] = mapped_column(Text)
    version: Mapped[str] = mapped_column(String(32), default="1.0.0")


class ZiweiPattern(Base):
    __tablename__ = "ziwei_patterns"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    pattern_name: Mapped[str] = mapped_column(String(64), unique=True)
    category: Mapped[str] = mapped_column(String(32), default="combo")
    conditions: Mapped[dict] = mapped_column(JsonType, default=dict)
    related_stars: Mapped[list] = mapped_column(JsonType, default=list)
    related_palaces: Mapped[list] = mapped_column(JsonType, default=list)
    traditional_meaning: Mapped[str | None] = mapped_column(Text)
    advantages: Mapped[list] = mapped_column(JsonType, default=list)
    challenges: Mapped[list] = mapped_column(JsonType, default=list)
    career_analysis: Mapped[str | None] = mapped_column(Text)
    wealth_analysis: Mapped[str | None] = mapped_column(Text)
    relationship_analysis: Mapped[str | None] = mapped_column(Text)
    growth_advice: Mapped[str | None] = mapped_column(Text)
    ai_prompt: Mapped[str | None] = mapped_column(Text)
    version: Mapped[str] = mapped_column(String(32), default="1.0.0")


class FourTransformKnowledge(Base):
    __tablename__ = "four_transform_knowledge"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    stem: Mapped[str] = mapped_column(String(8), unique=True)
    lu_star: Mapped[str] = mapped_column(String(16))
    quan_star: Mapped[str] = mapped_column(String(16))
    ke_star: Mapped[str] = mapped_column(String(16))
    ji_star: Mapped[str] = mapped_column(String(16))
    lu_meaning: Mapped[str | None] = mapped_column(Text)
    quan_meaning: Mapped[str | None] = mapped_column(Text)
    ke_meaning: Mapped[str | None] = mapped_column(Text)
    ji_meaning: Mapped[str | None] = mapped_column(Text)
    ai_prompt: Mapped[str | None] = mapped_column(Text)
    version: Mapped[str] = mapped_column(String(32), default="1.0.0")


class LifeQuestionModel(Base):
    __tablename__ = "life_question_models"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    question_type: Mapped[str] = mapped_column(String(32), unique=True)
    display_name: Mapped[str | None] = mapped_column(String(64))
    question_examples: Mapped[list] = mapped_column(JsonType, default=list)
    required_palaces: Mapped[list] = mapped_column(JsonType, default=list)
    required_stars: Mapped[list] = mapped_column(JsonType, default=list)
    required_patterns: Mapped[list] = mapped_column(JsonType, default=list)
    analysis_logic: Mapped[str | None] = mapped_column(Text)
    analysis_steps: Mapped[list] = mapped_column(JsonType, default=list)
    output_structure: Mapped[list] = mapped_column(JsonType, default=list)
    output_template: Mapped[str | None] = mapped_column(Text)
    safety_notice: Mapped[str | None] = mapped_column(Text)
    version: Mapped[str] = mapped_column(String(32), default="1.0.0")


class SafetyExpressionRule(Base):
    __tablename__ = "safety_expression_rules"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    category: Mapped[str] = mapped_column(String(64))
    forbidden_expression: Mapped[str] = mapped_column(Text)
    safe_expression: Mapped[str] = mapped_column(Text)
    reason: Mapped[str | None] = mapped_column(Text)
    risk_level: Mapped[str] = mapped_column(String(16), default="medium")
    version: Mapped[str] = mapped_column(String(32), default="1.0.0")


# ---------- Knowledge Core V2.0 ----------


class ZiweiTheoryRule(Base):
    __tablename__ = "ziwei_theory_rules"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    category: Mapped[str] = mapped_column(String(64))
    rule_name: Mapped[str] = mapped_column(String(128))
    rule_expression: Mapped[str | None] = mapped_column(Text)
    traditional_meaning: Mapped[str | None] = mapped_column(Text)
    modern_interpretation: Mapped[str | None] = mapped_column(Text)
    application_scope: Mapped[list] = mapped_column(JsonType, default=list)
    risk_expression: Mapped[str | None] = mapped_column(Text)
    safety_level: Mapped[str] = mapped_column(String(16), default="medium")
    school: Mapped[str] = mapped_column(String(32), default="sanhe")
    version: Mapped[str] = mapped_column(String(32), default="2.0.0")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class StarCombinationMatrix(Base):
    __tablename__ = "star_combination_matrix"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    star_a: Mapped[str] = mapped_column(String(32))
    star_b: Mapped[str | None] = mapped_column(String(32))
    star_c: Mapped[str | None] = mapped_column(String(32))
    combination_name: Mapped[str] = mapped_column(String(128))
    traditional_pattern: Mapped[str | None] = mapped_column(Text)
    personality_dimension: Mapped[str | None] = mapped_column(Text)
    career_dimension: Mapped[str | None] = mapped_column(Text)
    wealth_dimension: Mapped[str | None] = mapped_column(Text)
    relationship_dimension: Mapped[str | None] = mapped_column(Text)
    challenge_dimension: Mapped[str | None] = mapped_column(Text)
    growth_direction: Mapped[str | None] = mapped_column(Text)
    ai_tags: Mapped[list] = mapped_column(JsonType, default=list)
    version: Mapped[str] = mapped_column(String(32), default="2.0.0")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class PalaceDimensionMatrix(Base):
    __tablename__ = "palace_dimension_matrix"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    palace_name: Mapped[str] = mapped_column(String(32))
    dimension: Mapped[str] = mapped_column(String(32))
    traditional_meaning: Mapped[str | None] = mapped_column(Text)
    modern_meaning: Mapped[str | None] = mapped_column(Text)
    question_mapping: Mapped[list] = mapped_column(JsonType, default=list)
    advice_template: Mapped[str | None] = mapped_column(Text)
    version: Mapped[str] = mapped_column(String(32), default="2.0.0")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class FourTransformMatrix(Base):
    __tablename__ = "four_transform_matrix"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    year_stem: Mapped[str | None] = mapped_column(String(8))
    transform_type: Mapped[str] = mapped_column(String(8))
    star_name: Mapped[str | None] = mapped_column(String(32))
    traditional_effect: Mapped[str | None] = mapped_column(Text)
    modern_effect: Mapped[str | None] = mapped_column(Text)
    positive_expression: Mapped[str | None] = mapped_column(Text)
    challenge_expression: Mapped[str | None] = mapped_column(Text)
    growth_advice: Mapped[str | None] = mapped_column(Text)
    version: Mapped[str] = mapped_column(String(32), default="2.0.0")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class LifeScenarioModel(Base):
    __tablename__ = "life_scenario_models"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    scenario_name: Mapped[str] = mapped_column(String(64), unique=True)
    display_name: Mapped[str | None] = mapped_column(String(64))
    required_palaces: Mapped[list] = mapped_column(JsonType, default=list)
    required_patterns: Mapped[list] = mapped_column(JsonType, default=list)
    analysis_steps: Mapped[list] = mapped_column(JsonType, default=list)
    output_structure: Mapped[list] = mapped_column(JsonType, default=list)
    safety_rules: Mapped[list] = mapped_column(JsonType, default=list)
    related_question_types: Mapped[list] = mapped_column(JsonType, default=list)
    version: Mapped[str] = mapped_column(String(32), default="2.0.0")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class UserQuestionMemory(Base):
    __tablename__ = "user_question_memory"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    user_id: Mapped[str | None] = mapped_column(String(64))
    question: Mapped[str] = mapped_column(Text)
    question_type: Mapped[str | None] = mapped_column(String(64))
    chart_snapshot: Mapped[dict | None] = mapped_column(JsonType)
    analysis_result: Mapped[dict | None] = mapped_column(JsonType)
    feedback: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


# ---------- Knowledge Core V2.1 Advisor ----------


class AdvisorDimensionRule(Base):
    __tablename__ = "advisor_dimension_rules"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    dimension_code: Mapped[str] = mapped_column(Text, unique=True)
    dimension_name: Mapped[str] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    positive_expression: Mapped[str | None] = mapped_column(Text)
    challenge_expression: Mapped[str | None] = mapped_column(Text)
    growth_direction: Mapped[str | None] = mapped_column(Text)
    safety_level: Mapped[str | None] = mapped_column(Text, default="medium")
    version: Mapped[str | None] = mapped_column(Text, default="2.1.0")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class AdvisorQuestionTemplate(Base):
    __tablename__ = "advisor_question_templates"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    question_type: Mapped[str] = mapped_column(Text, unique=True)
    user_question_examples: Mapped[list] = mapped_column(JsonType, default=list)
    required_dimensions: Mapped[list] = mapped_column(JsonType, default=list)
    recommended_focus: Mapped[list] = mapped_column(JsonType, default=list)
    avoid_topics: Mapped[list] = mapped_column(JsonType, default=list)
    version: Mapped[str | None] = mapped_column(Text, default="2.1.0")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class AdvisorActionModel(Base):
    __tablename__ = "advisor_action_models"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    pattern_code: Mapped[str] = mapped_column(Text)
    condition: Mapped[dict] = mapped_column(JsonType, default=dict)
    strength_analysis: Mapped[str | None] = mapped_column(Text)
    risk_reminder: Mapped[str | None] = mapped_column(Text)
    action_suggestions: Mapped[list] = mapped_column(JsonType, default=list)
    growth_path: Mapped[list] = mapped_column(JsonType, default=list)
    version: Mapped[str | None] = mapped_column(Text, default="2.1.0")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


# ---------- Knowledge Core V3.0 asset tables ----------


class KnowledgeBook(Base):
    __tablename__ = "knowledge_books"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    book_name: Mapped[str] = mapped_column(Text, unique=True)
    author: Mapped[str | None] = mapped_column(Text)
    school: Mapped[str | None] = mapped_column(Text, default="sanhe")
    description: Mapped[str | None] = mapped_column(Text)
    file_name: Mapped[str | None] = mapped_column(Text)
    total_pages: Mapped[int | None] = mapped_column(default=0)
    status: Mapped[str | None] = mapped_column(Text, default="imported")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    book_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    title: Mapped[str | None] = mapped_column(Text)
    chapter: Mapped[str | None] = mapped_column(Text)
    source_file: Mapped[str | None] = mapped_column(Text)
    page_start: Mapped[int | None] = mapped_column()
    page_end: Mapped[int | None] = mapped_column()
    content: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class KnowledgeChunk(Base):
    __tablename__ = "knowledge_chunks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    book_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    chunk_index: Mapped[int] = mapped_column(default=0)
    page_number: Mapped[int | None] = mapped_column()
    content: Mapped[str] = mapped_column(Text)
    keywords: Mapped[list] = mapped_column(JsonType, default=list)
    star_tags: Mapped[list] = mapped_column(JsonType, default=list)
    palace_tags: Mapped[list] = mapped_column(JsonType, default=list)
    pattern_tags: Mapped[list] = mapped_column(JsonType, default=list)
    life_question_tags: Mapped[list] = mapped_column(JsonType, default=list)
    source_reference: Mapped[dict] = mapped_column(JsonType, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class KnowledgeRelation(Base):
    __tablename__ = "knowledge_relations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    source_chunk_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    target_chunk_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    relation_type: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class KnowledgeCitation(Base):
    __tablename__ = "knowledge_citations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    chunk_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    citation_text: Mapped[str | None] = mapped_column(Text)
    source_book: Mapped[str | None] = mapped_column(Text)
    page_number: Mapped[int | None] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


# ---------- Knowledge Core V3.1 graph ----------


class KnowledgeEntity(Base):
    __tablename__ = "knowledge_entities"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(Text)
    entity_type: Mapped[str] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    metadata_: Mapped[dict] = mapped_column("metadata", JsonType, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class KnowledgeGraphEdge(Base):
    __tablename__ = "knowledge_graph_edges"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    source_entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    target_entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    relation_type: Mapped[str] = mapped_column(Text)
    weight: Mapped[float | None] = mapped_column(default=1.0)
    source_chunk_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    metadata_: Mapped[dict] = mapped_column("metadata", JsonType, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
