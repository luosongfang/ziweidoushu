"""Unified optimization service — closes quality/feedback → weight loop."""

from __future__ import annotations

import json
import uuid
from typing import Any

from sqlalchemy import text

from app.database.database import SessionLocal
from app.knowledge.evaluation.theory_statistics import TheoryStatistics
from app.knowledge.optimization.optimization_models import (
    VERSION,
    from_dispatch_type,
    normalize_scenario,
    normalize_theory,
)
from app.knowledge.optimization.route_optimizer import RouteOptimizer
from app.knowledge.optimization.weight_optimizer import WeightOptimizer


class OptimizationService:
    """
    After analysis quality scoring or user feedback:
    update theory_effectiveness_stats + theory_dispatch_weights,
    record theory_route_history / optimization_events.
    """

    @classmethod
    def get_route(cls, scenario: str, *, use_chinese_label: bool = False) -> dict[str, Any]:
        route = RouteOptimizer.build_route(scenario, use_chinese_label=use_chinese_label)
        return route.to_dict()

    @classmethod
    def list_weights(cls, scenario: str | None = None) -> list[dict[str, Any]]:
        return [w.to_dict() for w in WeightOptimizer.list_weights(scenario)]

    @classmethod
    def record_route(
        cls,
        *,
        scenario: str,
        analysis_id: str | None = None,
        quality_score: float | None = None,
    ) -> dict[str, Any]:
        scen = normalize_scenario(scenario)
        theories = RouteOptimizer.get_ordered_theories(scen)
        selected = [t["name"] for t in theories]
        weights = {t["name"]: t["weight"] for t in theories}
        aid = None
        if analysis_id:
            try:
                aid = str(uuid.UUID(str(analysis_id)))
            except Exception:
                aid = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"ziwei.analysis:{analysis_id}"))

        db = SessionLocal()
        try:
            row = db.execute(
                text(
                    """
                    INSERT INTO public.theory_route_history
                        (analysis_id, scenario, selected_theories, weights, quality_score)
                    VALUES
                        (
                          CASE WHEN :aid IS NULL THEN NULL ELSE CAST(:aid AS uuid) END,
                          :scen,
                          CAST(:theories AS jsonb),
                          CAST(:weights AS jsonb),
                          :q
                        )
                    RETURNING id::text, created_at
                    """
                ),
                {
                    "aid": aid,
                    "scen": scen,
                    "theories": json.dumps(selected, ensure_ascii=False),
                    "weights": json.dumps(weights, ensure_ascii=False),
                    "q": quality_score,
                },
            ).mappings().first()
            db.commit()
            return {
                "id": row["id"] if row else None,
                "scenario": scen,
                "selected_theories": selected,
                "weights": weights,
                "quality_score": quality_score,
                "saved": True,
            }
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    @classmethod
    def update(
        cls,
        *,
        scenario: str,
        theory_used: list[str] | None = None,
        overall_score: float | None = None,
        feedback_type: str | None = None,
        analysis_id: str | None = None,
        source: str = "evaluation",
        update_effectiveness: bool = False,
    ) -> dict[str, Any]:
        """
        Primary hook after POST /evaluation/analysis.
        Adjusts dynamic weights from quality (+ optional feedback).
        """
        scen = normalize_scenario(scenario)
        theories = cls._resolve_theories(scen, theory_used)
        updated_weights: list[dict[str, Any]] = []
        stats_rows: list[dict[str, Any]] = []

        for theory in theories:
            if overall_score is not None:
                w = WeightOptimizer.apply_quality_signal(
                    scenario=scen,
                    theory_system=theory,
                    overall_score=float(overall_score),
                    source=source,
                )
                updated_weights.append(w.to_dict())
            if feedback_type:
                w = WeightOptimizer.apply_feedback_signal(
                    scenario=scen,
                    theory_system=theory,
                    feedback_type=feedback_type,
                    source=source,
                )
                updated_weights.append(w.to_dict())
                if update_effectiveness:
                    stats_rows.append(
                        TheoryStatistics.record_usage(
                            theory_system=theory,
                            scenario=scen,
                            feedback_type=feedback_type,
                        )
                    )

        route_hist = cls.record_route(
            scenario=scen,
            analysis_id=analysis_id,
            quality_score=overall_score,
        )
        route = cls.get_route(scen)

        return {
            "scenario": scen,
            "theories_updated": theories,
            "weights": updated_weights,
            "route": route,
            "route_history": route_hist,
            "effectiveness_updated": stats_rows,
            "engine_version": VERSION,
        }

    @classmethod
    def update_from_feedback(
        cls,
        *,
        feedback_type: str,
        scenario: str | None = None,
        theory_used: list[str] | None = None,
        decision_history_id: str | None = None,
        source: str = "decision_feedback",
    ) -> dict[str, Any]:
        """
        Hook after POST /decision/feedback.
        Syncs theory_effectiveness_stats + theory_dispatch_weights.
        """
        scen = scenario
        if not scen and decision_history_id:
            scen = cls._scenario_from_history(decision_history_id)
        if not scen and not theory_used:
            return {
                "skipped": True,
                "reason": "scenario_or_theory_used_required",
                "engine_version": VERSION,
            }
        scen = normalize_scenario(scen or "career")
        theories = cls._resolve_theories(scen, theory_used)

        stats_rows = []
        weight_rows = []
        for theory in theories:
            stats_rows.append(
                TheoryStatistics.record_usage(
                    theory_system=theory,
                    scenario=scen,
                    feedback_type=feedback_type,
                )
            )
            w = WeightOptimizer.apply_feedback_signal(
                scenario=scen,
                theory_system=theory,
                feedback_type=feedback_type,
                source=source,
            )
            weight_rows.append(w.to_dict())

        db = SessionLocal()
        try:
            db.execute(
                text(
                    """
                    INSERT INTO public.optimization_events
                        (event_type, before_value, after_value, reason, source)
                    VALUES
                        ('feedback_sync',
                         CAST(:before AS jsonb),
                         CAST(:after AS jsonb),
                         :reason,
                         :source)
                    """
                ),
                {
                    "before": json.dumps({"feedback_type": feedback_type}, ensure_ascii=False),
                    "after": json.dumps(
                        {"scenario": scen, "theories": theories, "weights": weight_rows},
                        ensure_ascii=False,
                    ),
                    "reason": f"decision feedback {feedback_type} synced to weights+stats",
                    "source": source,
                },
            )
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

        return {
            "scenario": scen,
            "theories_updated": theories,
            "effectiveness_updated": stats_rows,
            "weights": weight_rows,
            "route": cls.get_route(scen),
            "engine_version": VERSION,
        }

    @classmethod
    def _resolve_theories(
        cls,
        scenario: str,
        theory_used: list[str] | None,
    ) -> list[str]:
        if theory_used:
            seen: list[str] = []
            for t in theory_used:
                name = normalize_theory(str(t))
                # map stats names (sihua) → weight names
                name = from_dispatch_type(name) if name == "sihua" else name
                name = normalize_theory(name)
                if name not in seen:
                    seen.append(name)
            return seen or ["sanhe"]

        ordered = RouteOptimizer.get_ordered_theories(scenario)
        if ordered:
            return [t["name"] for t in ordered]
        return ["sanhe"]

    @classmethod
    def _scenario_from_history(cls, decision_history_id: str) -> str | None:
        try:
            hid = str(uuid.UUID(str(decision_history_id)))
        except Exception:
            return None
        db = SessionLocal()
        try:
            row = db.execute(
                text(
                    """
                    SELECT question_type
                    FROM public.decision_history
                    WHERE id = CAST(:id AS uuid)
                    """
                ),
                {"id": hid},
            ).mappings().first()
            if not row:
                return None
            return normalize_scenario(str(row.get("question_type") or "career"))
        except Exception:
            return None
        finally:
            db.close()
