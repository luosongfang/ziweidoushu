"""Explainable theory weight optimizer (no ML, no LLM)."""

from __future__ import annotations

import json
from typing import Any

from sqlalchemy import text

from app.database.database import SessionLocal
from app.knowledge.optimization.optimization_models import (
    FEEDBACK_NEUTRAL,
    VERSION,
    TheoryWeight,
    clamp_weight,
    normalize_scenario,
    normalize_theory,
)


class WeightOptimizer:
    """
    dynamic_weight = base_weight + feedback_adjust + quality_adjust + success_adjust
    Clamped to [0.1, 1.0]. Does not invent lore — only reweights dispatch.
    """

    @classmethod
    def compute_dynamic_weight(
        cls,
        *,
        base_weight: float,
        feedback_score: float,
        quality_score: float | None = None,
        success_count: int = 0,
    ) -> float:
        fb_adj = (float(feedback_score) - FEEDBACK_NEUTRAL) / 100.0 * 0.25
        q_adj = 0.0
        if quality_score is not None:
            q_adj = (float(quality_score) - 70.0) / 100.0 * 0.20
        # After ~20 high-quality successes → up to +0.10
        success_adj = min(0.10, max(0, int(success_count)) * 0.005)
        return clamp_weight(float(base_weight) + fb_adj + q_adj + success_adj)

    @classmethod
    def list_weights(cls, scenario: str | None = None) -> list[TheoryWeight]:
        scen = normalize_scenario(scenario) if scenario else None
        db = SessionLocal()
        try:
            if scen:
                rows = db.execute(
                    text(
                        """
                        SELECT id::text, scenario, theory_system, base_weight, dynamic_weight,
                               success_count, feedback_score, version
                        FROM public.theory_dispatch_weights
                        WHERE scenario = :s
                        ORDER BY dynamic_weight DESC, base_weight DESC
                        """
                    ),
                    {"s": scen},
                ).mappings().all()
            else:
                rows = db.execute(
                    text(
                        """
                        SELECT id::text, scenario, theory_system, base_weight, dynamic_weight,
                               success_count, feedback_score, version
                        FROM public.theory_dispatch_weights
                        ORDER BY scenario, dynamic_weight DESC
                        """
                    )
                ).mappings().all()
            return [
                TheoryWeight(
                    id=r["id"],
                    scenario=r["scenario"],
                    theory_system=r["theory_system"],
                    base_weight=float(r["base_weight"]),
                    dynamic_weight=float(r["dynamic_weight"]),
                    success_count=int(r["success_count"] or 0),
                    feedback_score=float(r["feedback_score"] or FEEDBACK_NEUTRAL),
                    version=str(r.get("version") or VERSION),
                )
                for r in rows
            ]
        finally:
            db.close()

    @classmethod
    def get_weight(cls, scenario: str, theory_system: str) -> TheoryWeight | None:
        scen = normalize_scenario(scenario)
        theory = normalize_theory(theory_system)
        db = SessionLocal()
        try:
            row = db.execute(
                text(
                    """
                    SELECT id::text, scenario, theory_system, base_weight, dynamic_weight,
                           success_count, feedback_score, version
                    FROM public.theory_dispatch_weights
                    WHERE scenario = :s AND theory_system = :t
                    """
                ),
                {"s": scen, "t": theory},
            ).mappings().first()
            if not row:
                return None
            return TheoryWeight(
                id=row["id"],
                scenario=row["scenario"],
                theory_system=row["theory_system"],
                base_weight=float(row["base_weight"]),
                dynamic_weight=float(row["dynamic_weight"]),
                success_count=int(row["success_count"] or 0),
                feedback_score=float(row["feedback_score"] or FEEDBACK_NEUTRAL),
                version=str(row.get("version") or VERSION),
            )
        finally:
            db.close()

    @classmethod
    def ensure_weight(
        cls,
        *,
        scenario: str,
        theory_system: str,
        base_weight: float = 0.5,
    ) -> TheoryWeight:
        existing = cls.get_weight(scenario, theory_system)
        if existing:
            return existing
        scen = normalize_scenario(scenario)
        theory = normalize_theory(theory_system)
        bw = clamp_weight(base_weight)
        db = SessionLocal()
        try:
            db.execute(
                text(
                    """
                    INSERT INTO public.theory_dispatch_weights
                        (scenario, theory_system, base_weight, dynamic_weight,
                         success_count, feedback_score, version, last_updated)
                    VALUES
                        (:s, :t, :bw, :bw, 0, :fb, :ver, NOW())
                    ON CONFLICT (scenario, theory_system) DO NOTHING
                    """
                ),
                {"s": scen, "t": theory, "bw": bw, "fb": FEEDBACK_NEUTRAL, "ver": VERSION},
            )
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()
        return cls.get_weight(scen, theory) or TheoryWeight(
            scenario=scen,
            theory_system=theory,
            base_weight=bw,
            dynamic_weight=bw,
        )

    @classmethod
    def _persist_and_log(
        cls,
        *,
        before: TheoryWeight,
        after: TheoryWeight,
        event_type: str,
        reason: str,
        source: str,
    ) -> TheoryWeight:
        db = SessionLocal()
        try:
            db.execute(
                text(
                    """
                    UPDATE public.theory_dispatch_weights
                    SET dynamic_weight = :dw,
                        success_count = :sc,
                        feedback_score = :fs,
                        last_updated = NOW(),
                        version = :ver
                    WHERE scenario = :s AND theory_system = :t
                    """
                ),
                {
                    "dw": after.dynamic_weight,
                    "sc": after.success_count,
                    "fs": after.feedback_score,
                    "ver": VERSION,
                    "s": after.scenario,
                    "t": after.theory_system,
                },
            )
            db.execute(
                text(
                    """
                    INSERT INTO public.optimization_events
                        (event_type, before_value, after_value, reason, source)
                    VALUES
                        (:etype, CAST(:before AS jsonb), CAST(:after AS jsonb), :reason, :source)
                    """
                ),
                {
                    "etype": event_type,
                    "before": json.dumps(before.to_dict(), ensure_ascii=False),
                    "after": json.dumps(after.to_dict(), ensure_ascii=False),
                    "reason": reason,
                    "source": source,
                },
            )
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()
        return after

    @classmethod
    def apply_quality_signal(
        cls,
        *,
        scenario: str,
        theory_system: str,
        overall_score: float,
        source: str = "analysis_quality_metrics",
    ) -> TheoryWeight:
        row = cls.ensure_weight(scenario=scenario, theory_system=theory_system)
        before = TheoryWeight(**{**row.to_dict()})
        score = float(overall_score)
        fb = float(row.feedback_score)
        success = int(row.success_count)

        if score >= 75:
            success += 1
            fb = min(100.0, fb + 1.5)
            reason = f"quality overall_score={score:.1f} high → raise weight"
        elif score < 50:
            success = max(0, success - 1)
            fb = max(0.0, fb - 2.5)
            reason = f"quality overall_score={score:.1f} low → lower weight"
        else:
            fb = min(100.0, max(0.0, fb + (score - 70) * 0.05))
            reason = f"quality overall_score={score:.1f} neutral nudge"

        new_dw = cls.compute_dynamic_weight(
            base_weight=row.base_weight,
            feedback_score=fb,
            quality_score=score,
            success_count=success,
        )
        after = TheoryWeight(
            id=row.id,
            scenario=row.scenario,
            theory_system=row.theory_system,
            base_weight=row.base_weight,
            dynamic_weight=new_dw,
            success_count=success,
            feedback_score=round(fb, 2),
            version=VERSION,
        )
        return cls._persist_and_log(
            before=before,
            after=after,
            event_type="quality_weight_update",
            reason=reason,
            source=source,
        )

    @classmethod
    def apply_feedback_signal(
        cls,
        *,
        scenario: str,
        theory_system: str,
        feedback_type: str,
        source: str = "decision_feedback",
    ) -> TheoryWeight:
        row = cls.ensure_weight(scenario=scenario, theory_system=theory_system)
        before = TheoryWeight(**{**row.to_dict()})
        fb = float(row.feedback_score)
        success = int(row.success_count)
        ftype = (feedback_type or "").strip()

        if ftype == "helpful":
            fb = min(100.0, fb + 5.0)
            success += 1
            reason = "user feedback helpful → raise weight"
        elif ftype == "not_helpful":
            fb = max(0.0, fb - 8.0)
            success = max(0, success - 1)
            reason = "user feedback not_helpful → lower weight"
        elif ftype in {"partially_helpful", "future_check"}:
            fb = min(100.0, fb + 1.0)
            reason = f"user feedback {ftype} → slight raise"
        else:
            reason = f"unknown feedback_type={ftype} — no change"
            return row

        new_dw = cls.compute_dynamic_weight(
            base_weight=row.base_weight,
            feedback_score=fb,
            quality_score=None,
            success_count=success,
        )
        after = TheoryWeight(
            id=row.id,
            scenario=row.scenario,
            theory_system=row.theory_system,
            base_weight=row.base_weight,
            dynamic_weight=new_dw,
            success_count=success,
            feedback_score=round(fb, 2),
            version=VERSION,
        )
        return cls._persist_and_log(
            before=before,
            after=after,
            event_type="feedback_weight_update",
            reason=reason,
            source=source,
        )

    @classmethod
    def reset_dynamic_to_base(cls, scenario: str, theory_system: str) -> TheoryWeight | None:
        row = cls.get_weight(scenario, theory_system)
        if not row:
            return None
        before = TheoryWeight(**{**row.to_dict()})
        after = TheoryWeight(
            id=row.id,
            scenario=row.scenario,
            theory_system=row.theory_system,
            base_weight=row.base_weight,
            dynamic_weight=row.base_weight,
            success_count=0,
            feedback_score=FEEDBACK_NEUTRAL,
            version=VERSION,
        )
        return cls._persist_and_log(
            before=before,
            after=after,
            event_type="weight_reset",
            reason="reset dynamic_weight to base_weight",
            source="manual",
        )
