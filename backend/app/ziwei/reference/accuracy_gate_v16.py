"""Accuracy Gate V1.6 — 专业宣称门槛。"""

from __future__ import annotations

from typing import Any

from app.ziwei.reference.diff_report import diff_sample_against_engine, run_calibration_batch
from app.ziwei.reference.importer import ReferenceImporter

MIN_PROFESSIONAL = 30
MIN_FOURTEEN_ACCURACY = 98.0


def evaluate_accuracy_gate_v16(
    samples: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    if samples is None:
        samples = ReferenceImporter().list_samples(professional_only=True)

    professional = [
        s for s in samples if s.get("verification_level") == "verified_professional"
    ]
    n = len(professional)
    reports = [diff_sample_against_engine(s) for s in professional]
    matched = sum(1 for r in reports if r.get("matched"))
    fourteen_acc = round(matched / n * 100, 2) if n else 0.0

    critical_nodes = []
    for r in reports:
        if r.get("critical_count", 0) > 0 and not r.get("matched"):
            critical_nodes.append(
                {"sample": r.get("sample"), "first_offset_step": r.get("first_offset_step")}
            )

    batch = run_calibration_batch(professional)
    claim = (
        n >= MIN_PROFESSIONAL
        and fourteen_acc >= MIN_FOURTEEN_ACCURACY
        and len(critical_nodes) == 0
    )

    return {
        "version": "1.6",
        "verified_professional_count": n,
        "min_professional_required": MIN_PROFESSIONAL,
        "fourteen_star_accuracy": fourteen_acc,
        "min_fourteen_accuracy": MIN_FOURTEEN_ACCURACY,
        "critical_nodes": critical_nodes,
        "has_critical": len(critical_nodes) > 0,
        "accuracy_claim_allowed": claim,
        "statistics": batch.get("statistics"),
        "message": (
            "可宣称专业准确率"
            if claim
            else (
                f"不可宣称：professional={n}/{MIN_PROFESSIONAL}, "
                f"fourteen_acc={fourteen_acc}% (需≥{MIN_FOURTEEN_ACCURACY}%), "
                f"critical={len(critical_nodes)}"
            )
        ),
    }
