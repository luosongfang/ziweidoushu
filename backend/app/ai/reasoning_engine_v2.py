"""Reasoning Engine V2.1–V5.1 — Knowledge Core pipeline (no LLM by default)."""

from __future__ import annotations

import json
import uuid
from typing import Any

from app.ai.prompt_builder import KnowledgeCorePromptBuilder
from app.ai.reasoning_engine import ReasoningEngine
from app.database.database import SessionLocal
from app.knowledge.advisor.advisor_engine import AdvisorEngine
from app.knowledge.advisor.advisor_safety import AdvisorSafety
from app.knowledge.intelligence.citation_engine import CitationEngine
from app.knowledge.intelligence.evidence_engine import EvidenceEngine
from app.knowledge.intelligence.interpretation_layer import InterpretationLayer
from app.knowledge.intelligence.knowledge_selector import KnowledgeSelector
from app.knowledge.intelligence.theory_router import TheoryRouter
from app.knowledge.knowledge_models import UserQuestionMemory
from app.knowledge.knowledge_service import KnowledgeService
from app.knowledge.lifecycle import LifeCycleEngine
from app.knowledge.memory.growth_context_builder import GrowthContextBuilder
from app.knowledge.memory.memory_service import MemoryService
from app.knowledge.decision import DecisionEngine
from app.knowledge.decision_feedback import PathSimulator, ReferenceMapper
from app.knowledge.multitheory.synthesis_engine import SynthesisEngine
from app.knowledge.multitheory.theory_analyzer import TheoryAnalyzer
from app.knowledge.multitheory.theory_conflict_checker import TheoryConflictChecker
from app.knowledge.multitheory.theory_dispatcher import TheoryDispatcher
from app.knowledge.multitheory.theory_registry import TheoryRegistry
from app.knowledge.reasoning.life_advisor_engine import LifeAdvisorEngine
from app.knowledge.reasoning.life_reasoning import LifeReasoning
from app.knowledge.reasoning.matrix_engine import MatrixEngine
from app.knowledge.reasoning.question_classifier import QuestionClassifier
from app.knowledge.reasoning.schemas import PipelineResult, ReasoningResult
from app.knowledge.reasoning.theory_engine import TheoryEngine


class ReasoningEngineV2:
    """
    V5.1 pipeline:
    Question → Memory → Classifier → Theory Dispatcher → Multi Theory
    → Life Cycle → Conflict → Synthesis → Decision Engine
    → Path Simulator → Knowledge Trace → Advisor → Safety → Memory
    """

    @classmethod
    def run(
        cls,
        question: str,
        chart_id: str | None = None,
        chart_data: dict[str, Any] | None = None,
        user_context: dict[str, Any] | None = None,
        *,
        persist_memory: bool = False,
        user_id: str | None = None,
        call_llm: bool = False,
        persist_evidence: bool = False,
        persist_growth_memory: bool | None = None,
        persist_theory_results: bool = False,
    ) -> PipelineResult:
        del call_llm
        analysis_id = str(uuid.uuid4())
        trace: list[str] = ["engine:v5.1"]

        resolved_user_id = user_id or (user_context or {}).get("user_id")
        if persist_growth_memory is None:
            persist_growth_memory = bool(resolved_user_id)

        qtype = QuestionClassifier.classify(question)
        trace.append(f"classify:{qtype}")

        growth_user_context: dict[str, Any] = {
            "main_interests": [],
            "previous_topics": [],
            "continuity_message": "",
        }
        advisor_memory_ctx: dict[str, Any] = {}
        if resolved_user_id:
            try:
                growth_user_context = MemoryService.get_user_context(
                    resolved_user_id,
                    question_type=qtype,
                )
                advisor_memory_ctx = GrowthContextBuilder.advisor_context(
                    growth_user_context, qtype
                )
                trace.append("growth_memory:loaded")
            except Exception as exc:  # noqa: BLE001
                trace.append(f"growth_memory:load_error:{type(exc).__name__}")

        # Keep Theory Router for backward-compatible route metadata
        route = TheoryRouter.route(qtype)
        # V4.0 Theory Dispatcher selects multi-theory set
        dispatch = TheoryDispatcher.dispatch(qtype)
        dispatched_types = [d["theory_type"] for d in dispatch]
        theory_used = list(
            dict.fromkeys(
                [TheoryRegistry.display(t) for t in dispatched_types]
                + list(route.get("required_theories") or [])
            )
        )
        trace.append(f"theory_router:{qtype}")
        trace.append(f"theory_dispatcher:{','.join(dispatched_types)}")
        trace.append(f"theories:{','.join(theory_used)}")

        scenario = LifeAdvisorEngine.resolve_scenario(qtype)
        required_palaces = list(
            TheoryDispatcher.union_palaces(qtype)
            or route.get("required_palaces")
            or scenario.get("required_palaces")
            or []
        )
        trace.append(f"life_scenario:{scenario.get('scenario_name')}")

        chart = ReasoningEngine.load_chart(chart_id=chart_id, chart_data=chart_data)
        trace.append("chart_loaded")

        context = KnowledgeService.build_context(chart, question)
        stars = KnowledgeService.extract_stars_from_chart(chart)
        trace.append("knowledge_retrieved")

        selected = KnowledgeSelector.select(route, limit=12, chart_stars=stars)
        trace.append(f"knowledge_selector:chunks={len(selected)}")

        patterns = KnowledgeService.match_patterns(stars)
        pattern_names = [p.get("pattern_name") for p in patterns if p.get("pattern_name")]
        pattern_names = list(
            dict.fromkeys(pattern_names + list(route.get("required_patterns") or []))
        )

        # Legacy single-pass engines (preserved)
        theory = TheoryEngine.match_for_question(qtype, pattern_names=pattern_names)
        trace.extend(theory.call_trace)

        matrix, matrix_summary = MatrixEngine.analyze(
            chart,
            qtype,
            required_palaces=required_palaces,
        )
        trace.extend(matrix.call_trace)

        # V4.0 multi-theory branch
        multi_results = TheoryAnalyzer.analyze_all(
            chart=chart,
            question_type=qtype,
            dispatch=dispatch,
            selected_chunks=selected,
            precomputed_theory=theory,
            precomputed_matrix=matrix,
            analysis_id=analysis_id,
            persist=persist_theory_results,
        )
        trace.append(f"multitheory:analyzed={','.join(multi_results.keys())}")
        if persist_theory_results:
            trace.append(f"multitheory:persisted={len(multi_results)}")

        # V4.1 Life Cycle Engine (after multi-theory, before conflict/synthesis)
        lifecycle = LifeCycleEngine.analyze(
            chart,
            question_type=qtype,
            user_context={
                **(user_context or {}),
                "age": (user_context or {}).get("age") or chart.get("age"),
                "gender": (user_context or {}).get("gender") or chart.get("gender"),
                "bureau_number": (user_context or {}).get("bureau_number")
                or chart.get("bureau_number"),
                "yin_yang": (user_context or {}).get("yin_yang") or chart.get("yin_yang"),
                "year_stem": (user_context or {}).get("year_stem") or chart.get("year_stem"),
            },
        )
        life_timeline = lifecycle.get("life_timeline")
        trace.extend(list(lifecycle.get("call_trace") or ["lifecycle:engine"]))

        conflicts = TheoryConflictChecker.check(multi_results)
        trace.append(f"multitheory:conflicts={len(conflicts)}")

        synthesis = SynthesisEngine.synthesize(
            multi_results,
            question_type=qtype,
            conflicts=conflicts,
        )
        # enrich synthesis advice with lifecycle growth hint
        if life_timeline and life_timeline.get("growth_advice"):
            synthesis["advice"] = (
                str(synthesis.get("advice") or "")
                + " 周期建议："
                + str(life_timeline["growth_advice"])
            ).strip()
        trace.append("multitheory:synthesis")

        theory_analysis = TheoryAnalyzer.to_api_payload(
            multi_results, synthesis=synthesis, conflicts=conflicts
        )

        # V5.0 Decision Intelligence Layer
        decision_bundle = DecisionEngine.analyze(
            question=question,
            chart_data=chart if isinstance(chart, dict) else {},
            question_type=qtype,
            user_context=user_context,
            theory_analysis=theory_analysis,
            life_timeline=life_timeline,
            user_memory=growth_user_context,
            selected_knowledge=selected,
            persist_history=bool(resolved_user_id),
            user_id=resolved_user_id,
        )
        decision_analysis = decision_bundle.get("decision_analysis")
        decision_history_id = decision_bundle.get("decision_history_id")
        decision_paths = PathSimulator.simulate(
            decision_analysis,
            scenario_code=(decision_analysis or {}).get("scenario_code"),
        )
        knowledge_trace = ReferenceMapper.build_trace(
            decision_analysis=decision_analysis,
            theory_analysis=theory_analysis,
            sources=None,  # filled after citations built; refreshed later
            stars=list(decision_bundle.get("stars") or stars),
            theory_used=theory_used,
            selected_knowledge=selected,
            persist=False,
        )
        trace.extend(list(decision_bundle.get("call_trace") or ["decision:engine:v5.0"]))
        trace.append("decision:paths")
        trace.append("decision:knowledge_trace")

        v1_parts = LifeReasoning.analyze(chart, qtype)
        for r in v1_parts:
            trace.extend(r.call_trace)

        life_advisor = LifeAdvisorEngine.build(qtype, theory, matrix, v1_parts=v1_parts)
        trace.extend(life_advisor.call_trace)

        advisor_question = question
        if advisor_memory_ctx.get("continuity_message"):
            advisor_question = (
                f"{question}\n[导师连续上下文]{advisor_memory_ctx['continuity_message']}"
            )
        if synthesis.get("advice"):
            advisor_question = (
                f"{advisor_question}\n[多理论综合]{str(synthesis['advice'])[:240]}"
            )
        if life_timeline and life_timeline.get("growth_advice"):
            advisor_question = (
                f"{advisor_question}\n[人生周期]{str(life_timeline['growth_advice'])[:200]}"
            )
        if decision_analysis:
            advisor_question = (
                f"{advisor_question}\n[决策场景]{decision_analysis.get('scenario')}"
                f"\n[行动建议]{'；'.join((decision_analysis.get('action_suggestions') or [])[:3])}"
            )

        advisor_v21 = AdvisorEngine.analyze(
            chart_data=chart,
            question=advisor_question,
            question_type=qtype,
            reasoning_result=[theory, matrix, *v1_parts],
            matrix_summary=matrix_summary,
            life_advisor=life_advisor.model_dump(),
        )
        trace.extend(advisor_v21.call_trace)
        if advisor_memory_ctx:
            trace.append("advisor:continuity_applied")
        trace.append("advisor:multitheory_applied")

        claims = list(
            dict.fromkeys(
                (advisor_v21.strengths or [])
                + (advisor_v21.challenges or [])
                + (advisor_v21.suggestions or [])[:3]
                + (theory.traditional_basis or [])[:3]
                + list((synthesis.get("sections") or {}).get("建议") or [])[:2]
            )
        )
        evidence = EvidenceEngine.build(
            analysis_id=analysis_id,
            claims=claims[:12],
            selected_chunks=selected,
            theory_type="、".join(theory_used) if theory_used else "三合派",
        )
        if persist_evidence:
            EvidenceEngine.persist(evidence)
            trace.append(f"evidence_persisted:{len(evidence)}")
        else:
            trace.append(f"evidence:{len(evidence)}")

        sources = CitationEngine.from_chunks(selected, limit=8)
        if not sources:
            sources = CitationEngine.from_evidence(evidence, limit=8)
        for t_result in multi_results.values():
            for s in (t_result.get("sources") or [])[:2]:
                if s not in sources:
                    sources.append(s)
        citation_lines = CitationEngine.render_lines(sources)
        trace.append(f"citations:{len(sources)}")

        # refresh knowledge_trace with final sources
        knowledge_trace = ReferenceMapper.build_trace(
            decision_analysis=decision_analysis,
            theory_analysis=theory_analysis,
            sources=sources,
            stars=list(decision_bundle.get("stars") or stars),
            theory_used=theory_used,
            selected_knowledge=selected,
            persist=False,
        )

        reasoning: list[ReasoningResult] = [theory, matrix, *v1_parts]
        reasoning.append(
            ReasoningResult(
                dimension="life_advisor",
                observations=[life_advisor.modern_view] if life_advisor.modern_view else [],
                traditional_basis=[life_advisor.traditional_view]
                if life_advisor.traditional_view
                else [],
                strengths=life_advisor.strengths,
                challenges=life_advisor.challenges,
                suggestions=life_advisor.growth_direction,
                sources=life_advisor.sources,
                call_trace=life_advisor.call_trace,
            )
        )
        reasoning.append(
            ReasoningResult(
                dimension="advisor_v2.1",
                observations=[advisor_v21.life_dimension],
                traditional_basis=[],
                strengths=advisor_v21.strengths,
                challenges=advisor_v21.challenges,
                suggestions=advisor_v21.suggestions,
                sources=advisor_v21.sources,
                call_trace=advisor_v21.call_trace,
            )
        )
        reasoning.append(
            ReasoningResult(
                dimension="multitheory_v4.0",
                observations=[synthesis.get("common") or ""]
                + [f"理论数 {len(multi_results)}", f"差异/冲突 {len(conflicts)}"],
                traditional_basis=[r.get("summary") or "" for r in multi_results.values()],
                strengths=list((synthesis.get("sections") or {}).get("优势") or []),
                challenges=list((synthesis.get("sections") or {}).get("风险") or []),
                suggestions=list((synthesis.get("sections") or {}).get("建议") or []),
                sources=[{"type": "theory_dispatch", "theories": dispatched_types}],
                call_trace=[t for t in trace if t.startswith("multitheory")],
            )
        )

        reasoning.append(
            ReasoningResult(
                dimension="lifecycle_v4.1",
                observations=[
                    f"阶段 {(life_timeline or {}).get('current_stage')}",
                    f"年龄区间 {(life_timeline or {}).get('age_range')}",
                ],
                traditional_basis=[(life_timeline or {}).get("traditional_view") or ""],
                strengths=[(life_timeline or {}).get("strength") or ""],
                challenges=[(life_timeline or {}).get("risk") or ""],
                suggestions=[(life_timeline or {}).get("growth_advice") or ""],
                sources=list((life_timeline or {}).get("sources") or []),
                call_trace=[t for t in trace if t.startswith("lifecycle")],
            )
        )

        reasoning.append(
            ReasoningResult(
                dimension="decision_v5.0",
                observations=[
                    f"场景 {(decision_analysis or {}).get('scenario')}",
                    (decision_analysis or {}).get("current_state") or "",
                ],
                traditional_basis=list(
                    ((decision_analysis or {}).get("traditional_view") or {}).values()
                ),
                strengths=list((decision_analysis or {}).get("strengths") or []),
                challenges=list((decision_analysis or {}).get("challenges") or []),
                suggestions=list((decision_analysis or {}).get("action_suggestions") or []),
                sources=list((decision_analysis or {}).get("sources") or []),
                call_trace=[t for t in trace if t.startswith("decision")],
            )
        )

        traditional = list(
            dict.fromkeys(
                theory.traditional_basis
                + matrix.traditional_basis
                + ([life_advisor.traditional_view] if life_advisor.traditional_view else [])
                + citation_lines
                + [r.get("summary") or "" for r in multi_results.values()]
                + ([(life_timeline or {}).get("traditional_view") or ""] if life_timeline else [])
                + (
                    [str(v) for v in ((decision_analysis or {}).get("traditional_view") or {}).values()]
                    if decision_analysis
                    else []
                )
            )
        )
        suggestions = list(
            dict.fromkeys(
                advisor_v21.suggestions
                + advisor_v21.action_plan
                + life_advisor.growth_direction
                + matrix.suggestions
                + list((synthesis.get("sections") or {}).get("建议") or [])
                + (
                    [(life_timeline or {}).get("growth_advice") or ""]
                    if life_timeline and life_timeline.get("growth_advice")
                    else []
                )
                + list((decision_analysis or {}).get("action_suggestions") or [])
            )
        )

        safety = (
            (decision_analysis or {}).get("safety_notice")
            or advisor_v21.safety_notice
            or "本分析仅供传统文化学习、自我认知辅助与人生规划参考。"
        )
        reflection_questions = list(
            (decision_analysis or {}).get("reflection_questions")
            or advisor_v21.reflection_questions
        )

        traditional = InterpretationLayer.apply_list(traditional)
        suggestions = InterpretationLayer.apply_list(suggestions)
        for r in reasoning:
            r.observations = InterpretationLayer.apply_list(r.observations)
            r.traditional_basis = InterpretationLayer.apply_list(r.traditional_basis)
            r.strengths = InterpretationLayer.apply_list(r.strengths)
            r.challenges = InterpretationLayer.apply_list(r.challenges)
            r.suggestions = InterpretationLayer.apply_list(r.suggestions)
        for e in evidence:
            e["claim"] = InterpretationLayer.apply(e.get("claim") or "")

        # safety on lifecycle timeline
        if isinstance(life_timeline, dict):
            for k in ("traditional_view", "growth_advice", "strength", "risk"):
                if life_timeline.get(k):
                    life_timeline[k] = InterpretationLayer.apply(str(life_timeline[k]))
        for _t_key, t_val in list(theory_analysis.items()):
            if isinstance(t_val, dict) and "summary" in t_val:
                t_val["summary"] = InterpretationLayer.apply(str(t_val.get("summary") or ""))
        if isinstance(theory_analysis.get("synthesis"), dict):
            syn = theory_analysis["synthesis"]
            for k in ("common", "difference", "advice"):
                if syn.get(k):
                    syn[k] = InterpretationLayer.apply(str(syn[k]))

        advisor_analysis = advisor_v21.as_advisor_analysis()
        for key in ("strengths", "challenges", "growth_direction", "action_plan"):
            if isinstance(advisor_analysis.get(key), list):
                advisor_analysis[key] = InterpretationLayer.apply_list(advisor_analysis[key])
        if advisor_analysis.get("safety_notice"):
            advisor_analysis["safety_notice"] = InterpretationLayer.apply(
                str(advisor_analysis["safety_notice"])
            )

        traditional_structured = {
            "theory": theory.traditional_basis[:8],
            "matrix": matrix.traditional_basis[:8],
            "summary": traditional[:12],
            "theory_used": theory_used,
            "text": "；".join(traditional[:6]),
            "multitheory": {
                k: (v.get("summary") if isinstance(v, dict) else v)
                for k, v in theory_analysis.items()
                if k not in {"conflicts", "synthesis"}
            },
            "decision_scenario": (decision_analysis or {}).get("scenario"),
        }

        context = {
            **context,
            "engine_version": "5.1",
            "life_scenario": scenario,
            "theory_route": route,
            "theory_dispatch": dispatch,
            "theory_used": theory_used,
            "selected_knowledge": selected,
            "sources": sources,
            "evidence": evidence,
            "matrix_summary": matrix_summary,
            "advisor_analysis": advisor_analysis,
            "growth_memory": growth_user_context,
            "theory_analysis": theory_analysis,
            "theory_synthesis": synthesis,
            "life_timeline": life_timeline,
            "lifecycle": lifecycle,
            "decision_analysis": decision_analysis,
            "decision_paths": decision_paths,
            "knowledge_trace": knowledge_trace,
        }
        prompt_messages = KnowledgeCorePromptBuilder.build(question, context)
        prompt_preview = json.dumps(prompt_messages, ensure_ascii=False)[:2000]
        trace.append("prompt_built_no_llm")

        if user_context:
            trace.append(f"user_context_keys:{','.join(user_context.keys())}")

        result = PipelineResult(
            question_type=qtype,
            traditional_analysis=traditional[:12],
            reasoning=reasoning,
            suggestions=suggestions[:12],
            safety_notice=safety if "定位" in safety else AdvisorSafety.notice(safety),
            prompt_preview=prompt_preview,
            call_trace=trace,
            scenario_name=scenario.get("scenario_name"),
            life_advisor=life_advisor.model_dump(),
            matrix_summary=matrix_summary,
            engine_version="5.1",
            advisor_analysis=advisor_analysis,
            reflection_questions=reflection_questions,
            traditional_analysis_structured=traditional_structured,
            theory_used=theory_used,
            sources=sources,
            evidence=evidence,
            theory_route={**route, "dispatch": dispatch},
            selected_knowledge=selected,
            user_context=growth_user_context,
            theory_analysis=theory_analysis,
            theory_conflicts=conflicts,
            theory_synthesis=synthesis,
            life_timeline=life_timeline,
            decision_analysis=decision_analysis,
            decision_paths=decision_paths,
            knowledge_trace=knowledge_trace,
            decision_history_id=decision_history_id,
        )

        if persist_growth_memory and resolved_user_id:
            try:
                MemoryService.save_memory(
                    user_id=resolved_user_id,
                    question=question,
                    question_type=qtype,
                    chart_id=chart_id,
                    theory_used=theory_used,
                    analysis_result=result.model_dump(),
                )
                growth_user_context = MemoryService.get_user_context(
                    resolved_user_id,
                    question_type=qtype,
                )
                result.user_context = growth_user_context
                trace.append("growth_memory:saved")
            except Exception as exc:  # noqa: BLE001
                trace.append(f"growth_memory:save_error:{type(exc).__name__}")
            result.call_trace = trace

        if persist_memory:
            cls._save_memory(
                user_id=resolved_user_id,
                question=question,
                question_type=qtype,
                chart_snapshot=chart if isinstance(chart, dict) else None,
                analysis_result=result.model_dump(),
            )
            trace.append("user_question_memory:saved")
            result.call_trace = trace

        return result

    @classmethod
    def _save_memory(
        cls,
        *,
        user_id: str | None,
        question: str,
        question_type: str,
        chart_snapshot: dict[str, Any] | None,
        analysis_result: dict[str, Any],
    ) -> None:
        db = SessionLocal()
        try:
            row = UserQuestionMemory(
                user_id=str(user_id) if user_id else None,
                question=question,
                question_type=question_type,
                chart_snapshot=chart_snapshot,
                analysis_result=analysis_result,
            )
            db.add(row)
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()
