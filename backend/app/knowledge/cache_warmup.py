"""启动时预热 Knowledge Core 缓存，缩短首次分析等待。"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

_MAIN_STARS = (
    "紫微",
    "天府",
    "天机",
    "太阳",
    "武曲",
    "天同",
    "廉贞",
    "太阴",
    "贪狼",
    "巨门",
    "天相",
    "天梁",
    "七杀",
    "破军",
)


def warm_knowledge_caches() -> None:
    """幂等预热：失败不影响服务启动。"""
    try:
        from app.database.database import is_database_ready

        if not is_database_ready():
            return

        from app.knowledge.advisor.advisor_engine import (
            AdvisorEngine,
            _cached_actions,
            _cached_dimensions,
        )
        from app.knowledge.decision.decision_context_builder import DecisionContextBuilder
        from app.knowledge.intelligence.knowledge_selector import KnowledgeSelector
        from app.knowledge.knowledge_loader import KnowledgeLoader, cached_safety_rules
        from app.knowledge.multitheory.theory_registry import TheoryRegistry
        from app.knowledge.reasoning.life_advisor_engine import LifeAdvisorEngine
        from app.knowledge.reasoning.matrix_engine import MatrixEngine
        from app.knowledge.reasoning.theory_engine import TheoryEngine

        _cached_dimensions()
        _cached_actions()
        KnowledgeSelector.warm_cache()
        KnowledgeLoader.list_patterns()
        KnowledgeLoader.list_theory()
        KnowledgeLoader.list_safety_rules()
        cached_safety_rules()
        TheoryRegistry.list_systems()
        DecisionContextBuilder.list_scenarios()
        DecisionContextBuilder.list_dimension_rules()
        DecisionContextBuilder.list_process_steps()
        TheoryEngine.list_rules()
        MatrixEngine.list_star_combos()
        for dim in ("事业", "财富", "关系", "成长", "家庭"):
            MatrixEngine.palace_dimensions(["命宫"], dim)
        MatrixEngine.four_transforms()

        for star in _MAIN_STARS:
            KnowledgeLoader.get_star(star)
        for qtype in (
            "personality",
            "career",
            "wealth",
            "relationship",
            "life_stage",
            "self_growth",
        ):
            KnowledgeLoader.get_question_model(qtype)
            AdvisorEngine.get_template(qtype)
            LifeAdvisorEngine.get_scenario(
                LifeAdvisorEngine.resolve_scenario(qtype).get("scenario_name") or "personal_strength"
            )

        logger.info("Knowledge Core 缓存预热完成")
    except Exception as exc:  # noqa: BLE001
        logger.warning("Knowledge Core 缓存预热跳过：%s", exc)
