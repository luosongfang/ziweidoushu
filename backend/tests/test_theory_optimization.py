"""Knowledge Core V5.6 — theory adaptive optimization tests (no LLM)."""

from __future__ import annotations

import pytest

from app.config import settings
from app.database.database import is_database_ready
from app.knowledge.multitheory.theory_dispatcher import TheoryDispatcher
from app.knowledge.optimization import (
    OptimizationService,
    RouteOptimizer,
    WeightOptimizer,
)
from app.knowledge.optimization.optimization_models import clamp_weight


@pytest.fixture(scope="module")
def require_postgres():
    if not settings.is_postgres:
        pytest.skip("requires PostgreSQL")
    if not is_database_ready():
        pytest.skip("database not ready")


@pytest.fixture()
def reset_entrepreneurship_sanhe(require_postgres):
    WeightOptimizer.reset_dynamic_to_base("entrepreneurship", "sanhe")
    WeightOptimizer.reset_dynamic_to_base("entrepreneurship", "four_transform")
    yield
    WeightOptimizer.reset_dynamic_to_base("entrepreneurship", "sanhe")
    WeightOptimizer.reset_dynamic_to_base("entrepreneurship", "four_transform")


def test_initial_weight_read(require_postgres):
    weights = WeightOptimizer.list_weights("entrepreneurship")
    assert weights, "expected seeded theory_dispatch_weights"
    by_name = {w.theory_system: w for w in weights}
    assert "sanhe" in by_name
    assert "four_transform" in by_name
    assert "feixing" in by_name
    assert abs(by_name["sanhe"].base_weight - 0.8) < 1e-6
    assert abs(by_name["four_transform"].base_weight - 0.6) < 1e-6
    assert abs(by_name["feixing"].base_weight - 0.3) < 1e-6
    assert 0.1 <= by_name["sanhe"].dynamic_weight <= 1.0

    route = TheoryDispatcher.get_dynamic_theory_route("entrepreneurship")
    assert route["scenario"] in {"创业", "entrepreneurship"}
    names = [t["name"] for t in route["theories"]]
    assert "sanhe" in names
    assert route["theories"][0]["weight"] >= route["theories"][-1]["weight"]


def test_quality_raises_weight(require_postgres, reset_entrepreneurship_sanhe):
    before = WeightOptimizer.get_weight("entrepreneurship", "sanhe")
    assert before is not None
    before_w = before.dynamic_weight

    # Simulate consecutive high-quality analyses
    for _ in range(20):
        WeightOptimizer.apply_quality_signal(
            scenario="entrepreneurship",
            theory_system="sanhe",
            overall_score=88.0,
            source="unit_test_quality",
        )

    after = WeightOptimizer.get_weight("entrepreneurship", "sanhe")
    assert after is not None
    assert after.dynamic_weight > before_w
    assert after.success_count >= 20
    assert after.dynamic_weight <= 1.0
    assert after.dynamic_weight == clamp_weight(after.dynamic_weight)


def test_negative_feedback_lowers_weight(require_postgres, reset_entrepreneurship_sanhe):
    # First boost so there is room to drop
    for _ in range(5):
        WeightOptimizer.apply_quality_signal(
            scenario="entrepreneurship",
            theory_system="four_transform",
            overall_score=90.0,
            source="unit_test_prep",
        )
    before = WeightOptimizer.get_weight("entrepreneurship", "four_transform")
    assert before is not None
    before_w = before.dynamic_weight

    for _ in range(8):
        WeightOptimizer.apply_feedback_signal(
            scenario="entrepreneurship",
            theory_system="four_transform",
            feedback_type="not_helpful",
            source="unit_test_feedback",
        )

    after = WeightOptimizer.get_weight("entrepreneurship", "four_transform")
    assert after is not None
    assert after.dynamic_weight < before_w
    assert after.dynamic_weight >= 0.1


def test_theory_route_changes(require_postgres, reset_entrepreneurship_sanhe):
    # Make four_transform clearly outrank sanhe via quality+helpful
    WeightOptimizer.reset_dynamic_to_base("entrepreneurship", "sanhe")
    WeightOptimizer.reset_dynamic_to_base("entrepreneurship", "four_transform")

    for _ in range(25):
        WeightOptimizer.apply_quality_signal(
            scenario="entrepreneurship",
            theory_system="four_transform",
            overall_score=95.0,
        )
        WeightOptimizer.apply_feedback_signal(
            scenario="entrepreneurship",
            theory_system="four_transform",
            feedback_type="helpful",
        )
        WeightOptimizer.apply_feedback_signal(
            scenario="entrepreneurship",
            theory_system="sanhe",
            feedback_type="not_helpful",
        )

    route = OptimizationService.get_route("entrepreneurship")
    assert route["theories"]
    top = route["theories"][0]["name"]
    assert top == "four_transform"

    # Dispatcher dispatch order should follow weights
    rows = TheoryDispatcher.dispatch("entrepreneurship")
    assert rows
    # first theory among sanhe/sihua should prefer sihua (four_transform)
    theory_order = [r["theory_type"] for r in rows]
    if "sihua" in theory_order and "sanhe" in theory_order:
        assert theory_order.index("sihua") < theory_order.index("sanhe")


def test_scenario_weights_independent(require_postgres):
    WeightOptimizer.reset_dynamic_to_base("wealth", "four_transform")
    WeightOptimizer.reset_dynamic_to_base("relationship", "four_transform")
    WeightOptimizer.reset_dynamic_to_base("entrepreneurship", "sanhe")

    wealth = WeightOptimizer.get_weight("wealth", "four_transform")
    rel = WeightOptimizer.get_weight("relationship", "four_transform")
    ent = WeightOptimizer.get_weight("entrepreneurship", "sanhe")
    assert wealth is not None and rel is not None and ent is not None

    # Boost wealth only
    for _ in range(15):
        WeightOptimizer.apply_quality_signal(
            scenario="wealth",
            theory_system="four_transform",
            overall_score=92.0,
        )

    wealth_after = WeightOptimizer.get_weight("wealth", "four_transform")
    rel_after = WeightOptimizer.get_weight("relationship", "four_transform")
    assert wealth_after is not None and rel_after is not None
    assert wealth_after.dynamic_weight > wealth.dynamic_weight
    # relationship unchanged (independent scenario)
    assert abs(rel_after.dynamic_weight - rel.dynamic_weight) < 1e-6

    wealth_route = RouteOptimizer.get_ordered_theories("wealth")
    rel_route = RouteOptimizer.get_ordered_theories("relationship")
    assert wealth_route[0]["name"] == "four_transform"
    assert any(t["name"] == "sanhe" for t in rel_route)

    # Service update end-to-end
    result = OptimizationService.update(
        scenario="wealth",
        theory_used=["four_transform"],
        overall_score=85.0,
        analysis_id=None,
        source="unit_test_service",
    )
    assert result["route"]["theories"]
    assert result["engine_version"].startswith("5.6")
