"""KnowledgeLoader — 从数据库加载 Knowledge Core。"""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.database import SessionLocal, is_database_ready
from app.knowledge.knowledge_models import (
    FourTransformKnowledge,
    LifeQuestionModel,
    PalaceKnowledge,
    SafetyExpressionRule,
    StarsKnowledge,
    TheoryKnowledge,
    ZiweiPattern,
)


def _row_to_dict(obj: Any) -> dict[str, Any]:
    data: dict[str, Any] = {}
    for col in obj.__table__.columns:
        val = getattr(obj, col.name)
        if hasattr(val, "hex"):
            val = str(val)
        data[col.name] = val
    return data


@lru_cache(maxsize=256)
def _cached_star(star_name: str) -> dict[str, Any] | None:
    db = SessionLocal()
    try:
        row = db.scalar(select(StarsKnowledge).where(StarsKnowledge.star_name == star_name))
        return _row_to_dict(row) if row else None
    finally:
        db.close()


@lru_cache(maxsize=64)
def _cached_palace(palace_name: str) -> dict[str, Any] | None:
    db = SessionLocal()
    try:
        row = db.scalar(
            select(PalaceKnowledge).where(PalaceKnowledge.palace_name == palace_name)
        )
        return _row_to_dict(row) if row else None
    finally:
        db.close()


@lru_cache(maxsize=1)
def _cached_patterns() -> tuple[dict[str, Any], ...]:
    db = SessionLocal()
    try:
        rows = db.scalars(select(ZiweiPattern).order_by(ZiweiPattern.pattern_name)).all()
        return tuple(_row_to_dict(r) for r in rows)
    finally:
        db.close()


class KnowledgeLoader:
    """负责加载数据库知识（可缓存）。"""

    @classmethod
    def session(cls) -> Session:
        return SessionLocal()

    @classmethod
    def ensure_ready(cls) -> bool:
        return is_database_ready()

    @classmethod
    def get_star(cls, star_name: str, db: Session | None = None) -> dict[str, Any] | None:
        if db is not None:
            row = db.scalar(select(StarsKnowledge).where(StarsKnowledge.star_name == star_name))
            return _row_to_dict(row) if row else None
        return _cached_star(star_name)

    @classmethod
    def list_stars(cls, db: Session | None = None) -> list[dict[str, Any]]:
        own = db is None
        db = db or cls.session()
        try:
            rows = db.scalars(select(StarsKnowledge).order_by(StarsKnowledge.star_name)).all()
            return [_row_to_dict(r) for r in rows]
        finally:
            if own:
                db.close()

    @classmethod
    def get_palace(cls, palace_name: str, db: Session | None = None) -> dict[str, Any] | None:
        if db is not None:
            row = db.scalar(
                select(PalaceKnowledge).where(PalaceKnowledge.palace_name == palace_name)
            )
            return _row_to_dict(row) if row else None
        return _cached_palace(palace_name)

    @classmethod
    def get_pattern(cls, pattern_name: str, db: Session | None = None) -> dict[str, Any] | None:
        own = db is None
        db = db or cls.session()
        try:
            row = db.scalar(
                select(ZiweiPattern).where(ZiweiPattern.pattern_name == pattern_name)
            )
            return _row_to_dict(row) if row else None
        finally:
            if own:
                db.close()

    @classmethod
    def list_patterns(cls, db: Session | None = None) -> list[dict[str, Any]]:
        if db is not None:
            rows = db.scalars(select(ZiweiPattern).order_by(ZiweiPattern.pattern_name)).all()
            return [_row_to_dict(r) for r in rows]
        return list(_cached_patterns())

    @classmethod
    def get_question_model(
        cls, question_type: str, db: Session | None = None
    ) -> dict[str, Any] | None:
        if db is not None:
            row = db.scalar(
                select(LifeQuestionModel).where(LifeQuestionModel.question_type == question_type)
            )
            return _row_to_dict(row) if row else None
        return _cached_question_model(question_type)

    @classmethod
    def list_question_models(cls, db: Session | None = None) -> list[dict[str, Any]]:
        own = db is None
        db = db or cls.session()
        try:
            rows = db.scalars(select(LifeQuestionModel)).all()
            return [_row_to_dict(r) for r in rows]
        finally:
            if own:
                db.close()

    @classmethod
    def list_safety_rules(cls, db: Session | None = None) -> list[dict[str, Any]]:
        if db is not None:
            rows = db.scalars(select(SafetyExpressionRule)).all()
            return [_row_to_dict(r) for r in rows]
        return list(_cached_safety_rules_rows())

    @classmethod
    def get_four_transform(cls, stem: str, db: Session | None = None) -> dict[str, Any] | None:
        own = db is None
        db = db or cls.session()
        try:
            row = db.scalar(
                select(FourTransformKnowledge).where(FourTransformKnowledge.stem == stem)
            )
            return _row_to_dict(row) if row else None
        finally:
            if own:
                db.close()

    @classmethod
    def list_theory(cls, db: Session | None = None) -> list[dict[str, Any]]:
        if db is not None:
            rows = db.scalars(select(TheoryKnowledge)).all()
            return [_row_to_dict(r) for r in rows]
        return list(_cached_theory_rows())


@lru_cache(maxsize=1)
def _cached_safety_rules_rows() -> tuple[dict[str, Any], ...]:
    db = SessionLocal()
    try:
        rows = db.scalars(select(SafetyExpressionRule)).all()
        return tuple(_row_to_dict(r) for r in rows)
    finally:
        db.close()


@lru_cache(maxsize=1)
def _cached_theory_rows() -> tuple[dict[str, Any], ...]:
    db = SessionLocal()
    try:
        rows = db.scalars(select(TheoryKnowledge)).all()
        return tuple(_row_to_dict(r) for r in rows)
    finally:
        db.close()


@lru_cache(maxsize=32)
def _cached_question_model(question_type: str) -> dict[str, Any] | None:
    db = SessionLocal()
    try:
        row = db.scalar(
            select(LifeQuestionModel).where(LifeQuestionModel.question_type == question_type)
        )
        return _row_to_dict(row) if row else None
    finally:
        db.close()


@lru_cache(maxsize=1)
def cached_safety_rules() -> tuple[tuple[str, str], ...]:
    """返回 (forbidden, safe) 元组缓存，供过滤器快速使用。"""
    rules = KnowledgeLoader.list_safety_rules()
    return tuple((r["forbidden_expression"], r["safe_expression"]) for r in rules)
