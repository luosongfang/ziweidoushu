"""Per-theory analyzers wrapping Theory/Matrix/Graph engines (no LLM)."""

from __future__ import annotations

import json
import uuid
from typing import Any

from sqlalchemy import text

from app.database.database import SessionLocal
from app.knowledge.knowledge_service import KnowledgeService
from app.knowledge.multitheory.theory_registry import TheoryRegistry
from app.knowledge.reasoning.matrix_engine import MatrixEngine
from app.knowledge.reasoning.theory_engine import TheoryEngine


def _uniq(items: list[str], limit: int = 8) -> list[str]:
    return list(dict.fromkeys([x for x in items if x]))[:limit]


def _source(kind: str, **kwargs: Any) -> dict[str, Any]:
    return {"type": kind, **kwargs}


class TheoryAnalyzer:
    """Run each dispatched theory against Knowledge Core engines."""

    @classmethod
    def analyze_one(
        cls,
        *,
        theory_type: str,
        chart: dict[str, Any],
        question_type: str,
        mapping: dict[str, Any],
        selected_chunks: list[dict[str, Any]] | None = None,
        precomputed_theory: Any | None = None,
        precomputed_matrix: Any | None = None,
    ) -> dict[str, Any]:
        t = TheoryRegistry.normalize_type(theory_type)
        if t == "sanhe":
            return cls._sanhe(
                chart, question_type, mapping, precomputed_theory, precomputed_matrix
            )
        if t == "sihua":
            return cls._sihua(chart, question_type, mapping)
        if t == "feixing":
            return cls._feixing(chart, question_type, mapping)
        if t == "classic_formula":
            return cls._classic(chart, question_type, mapping, selected_chunks)
        return cls._sanhe(
            chart, question_type, mapping, precomputed_theory, precomputed_matrix
        )

    @classmethod
    def analyze_all(
        cls,
        *,
        chart: dict[str, Any],
        question_type: str,
        dispatch: list[dict[str, Any]],
        selected_chunks: list[dict[str, Any]] | None = None,
        precomputed_theory: Any | None = None,
        precomputed_matrix: Any | None = None,
        analysis_id: str | None = None,
        persist: bool = False,
    ) -> dict[str, dict[str, Any]]:
        results: dict[str, dict[str, Any]] = {}
        for mapping in dispatch:
            t = TheoryRegistry.normalize_type(str(mapping.get("theory_type") or "sanhe"))
            result = cls.analyze_one(
                theory_type=t,
                chart=chart,
                question_type=question_type,
                mapping=mapping,
                selected_chunks=selected_chunks,
                precomputed_theory=precomputed_theory,
                precomputed_matrix=precomputed_matrix,
            )
            results[t] = result

        if persist and analysis_id:
            cls.persist_results(analysis_id, results)
        return results

    @classmethod
    def persist_results(cls, analysis_id: str, results: dict[str, dict[str, Any]]) -> int:
        db = SessionLocal()
        try:
            aid = uuid.UUID(str(analysis_id))
            n = 0
            for theory_type, payload in results.items():
                db.execute(
                    text(
                        """
                        INSERT INTO public.theory_analysis_results
                            (analysis_id, theory_name, result, evidence, confidence_level)
                        VALUES
                            (:aid, :name, CAST(:result AS jsonb), CAST(:evidence AS jsonb), :conf)
                        """
                    ),
                    {
                        "aid": str(aid),
                        "name": TheoryRegistry.display(theory_type),
                        "result": json.dumps(payload, ensure_ascii=False),
                        "evidence": json.dumps(
                            payload.get("evidence") or payload.get("sources") or [],
                            ensure_ascii=False,
                        ),
                        "conf": payload.get("confidence_level") or "medium",
                    },
                )
                n += 1
            db.commit()
            return n
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    @classmethod
    def _pack(
        cls,
        theory_type: str,
        *,
        summary: str,
        strengths: list[str],
        challenges: list[str],
        suggestions: list[str],
        sources: list[dict[str, Any]],
        traditional: list[str] | None = None,
        required_palaces: list[str] | None = None,
        confidence_level: str = "medium",
    ) -> dict[str, Any]:
        sources = sources or []
        # every theory result must carry at least one source citation
        if not sources:
            sources = [
                _source(
                    "theory_system",
                    book=TheoryRegistry.display(theory_type),
                    note="Knowledge Core theory registry",
                )
            ]
        evidence = [
            {
                "claim": summary,
                "source": sources[0],
                "theory": TheoryRegistry.display(theory_type),
            }
        ]
        for s in strengths[:2]:
            evidence.append(
                {
                    "claim": s,
                    "source": sources[min(1, len(sources) - 1)],
                    "theory": TheoryRegistry.display(theory_type),
                }
            )
        return {
            "theory_type": theory_type,
            "theory_name": TheoryRegistry.display(theory_type),
            "summary": summary,
            "strengths": _uniq(strengths),
            "challenges": _uniq(challenges),
            "suggestions": _uniq(suggestions),
            "traditional_basis": _uniq(traditional or [], 10),
            "sources": sources[:12],
            "evidence": evidence[:8],
            "required_palaces": list(required_palaces or []),
            "confidence_level": confidence_level,
        }

    @classmethod
    def _sanhe(
        cls,
        chart: dict[str, Any],
        question_type: str,
        mapping: dict[str, Any],
        precomputed_theory: Any | None,
        precomputed_matrix: Any | None,
    ) -> dict[str, Any]:
        palaces = list(mapping.get("required_palaces") or ["命宫", "官禄宫"])
        theory = precomputed_theory or TheoryEngine.match_for_question(question_type)
        matrix = precomputed_matrix
        if matrix is None:
            matrix, _ = MatrixEngine.analyze(
                chart, question_type, required_palaces=palaces
            )

        strengths = list(theory.strengths or []) + list(matrix.strengths or [])
        challenges = list(theory.challenges or []) + list(matrix.challenges or [])
        suggestions = list(theory.suggestions or []) + list(matrix.suggestions or [])
        trad = list(theory.traditional_basis or []) + list(matrix.traditional_basis or [])
        sources = [
            _source("theory_engine", school="三合派", rule=r.get("rule_name") or r.get("name"))
            for r in (theory.sources or [])[:4]
            if isinstance(r, dict)
        ] + [
            _source("palace_dimension", palace=p, school="三合派")
            for p in palaces[:4]
        ]
        for s in matrix.sources or []:
            if isinstance(s, dict) and s.get("type") == "palace_dimension":
                sources.append({**s, "school": "三合派"})

        summary = (
            f"三合派视角：围绕{'、'.join(palaces[:4])}做结构协同分析。"
            + (f"传统依据：{trad[0]}" if trad else "强调宫位协同与资源配置，不作绝对预测。")
        )
        return cls._pack(
            "sanhe",
            summary=summary[:280],
            strengths=strengths,
            challenges=challenges,
            suggestions=suggestions,
            sources=sources,
            traditional=trad,
            required_palaces=palaces,
            confidence_level="high" if trad else "medium",
        )

    @classmethod
    def _sihua(
        cls,
        chart: dict[str, Any],
        question_type: str,
        mapping: dict[str, Any],
    ) -> dict[str, Any]:
        palaces = list(mapping.get("required_palaces") or ["官禄宫", "财帛宫"])
        year_stem = None
        if isinstance(chart.get("year_stem"), str):
            year_stem = chart["year_stem"]
        elif isinstance(chart.get("meta"), dict):
            year_stem = chart["meta"].get("year_stem") or chart["meta"].get("stem")

        transforms = MatrixEngine.four_transforms(year_stem=year_stem)
        strengths: list[str] = []
        challenges: list[str] = []
        suggestions: list[str] = []
        trad: list[str] = []
        sources: list[dict[str, Any]] = []

        for t in transforms[:8]:
            sources.append(
                _source(
                    "four_transform_matrix",
                    transform=t.get("transform_type"),
                    star=t.get("star_name"),
                    stem=t.get("year_stem"),
                    book="四化矩阵",
                )
            )
            if t.get("traditional_effect"):
                trad.append(str(t["traditional_effect"]))
            if t.get("positive_expression"):
                strengths.append(str(t["positive_expression"]))
            if t.get("challenge_expression"):
                challenges.append(str(t["challenge_expression"]))
            if t.get("growth_advice"):
                suggestions.append(str(t["growth_advice"]))

        # also pull theory rules tagged 四化
        for r in TheoryEngine.list_rules(categories=["四化理论"])[:4]:
            sources.append(
                _source(
                    "theory_rule",
                    rule=r.get("rule_name"),
                    school="四化",
                    book=r.get("source_book") or "四化理论",
                )
            )
            if r.get("traditional_meaning"):
                trad.append(str(r["traditional_meaning"]))
            if r.get("modern_interpretation"):
                strengths.append(str(r["modern_interpretation"]))

        focus = "、".join(palaces[:3])
        summary = (
            f"四化视角：结合{focus}观察禄权科忌的阶段性节奏。"
            + (f"依据：{trad[0]}" if trad else "强调动态变化与风险管理，不作绝对预测。")
        )
        return cls._pack(
            "sihua",
            summary=summary[:280],
            strengths=strengths,
            challenges=challenges or ["需关注资源波动与节奏管理"],
            suggestions=suggestions or ["用阶段复盘代替一次性押注"],
            sources=sources,
            traditional=trad,
            required_palaces=palaces,
            confidence_level="high" if transforms else "medium",
        )

    @classmethod
    def _feixing(
        cls,
        chart: dict[str, Any],
        question_type: str,
        mapping: dict[str, Any],
    ) -> dict[str, Any]:
        palaces = list(mapping.get("required_palaces") or ["命宫"])
        stars = KnowledgeService.extract_stars_from_chart(chart)
        combos = MatrixEngine.match_star_combinations(stars)
        strengths: list[str] = []
        challenges: list[str] = []
        suggestions: list[str] = []
        trad: list[str] = []
        sources: list[dict[str, Any]] = []

        for c in combos[:6]:
            sources.append(
                _source(
                    "star_combination",
                    name=c.get("combination_name"),
                    pattern=c.get("traditional_pattern"),
                    school="飞星",
                )
            )
            if c.get("traditional_pattern"):
                trad.append(str(c["traditional_pattern"]))
            dim_key = {
                "career": "career_dimension",
                "entrepreneurship": "career_dimension",
                "wealth": "wealth_dimension",
                "relationship": "relationship_dimension",
                "marriage": "relationship_dimension",
            }.get(question_type, "personality_dimension")
            if c.get(dim_key):
                strengths.append(str(c[dim_key]))
            if c.get("challenge_dimension"):
                challenges.append(str(c["challenge_dimension"]))
            if c.get("growth_direction"):
                suggestions.append(str(c["growth_direction"]))

        # light graph citation (optional, non-fatal)
        graph_sources = cls._graph_star_sources(stars[:4])
        sources.extend(graph_sources)

        summary = (
            f"飞星视角：对照命盘星曜组合（{','.join(stars[:4]) or '星曜'}）观察互动关系。"
            + (f"依据：{trad[0]}" if trad else "强调组合关系与互动张力，不作绝对预测。")
        )
        return cls._pack(
            "feixing",
            summary=summary[:280],
            strengths=strengths or ["星曜互动可提供差异化表达空间"],
            challenges=challenges or ["组合张力需通过沟通与节奏管理消化"],
            suggestions=suggestions or ["把星曜组合理解为能力组合，而非吉凶判决"],
            sources=sources,
            traditional=trad,
            required_palaces=palaces,
            confidence_level="medium",
        )

    @classmethod
    def _classic(
        cls,
        chart: dict[str, Any],
        question_type: str,
        mapping: dict[str, Any],
        selected_chunks: list[dict[str, Any]] | None,
    ) -> dict[str, Any]:
        palaces = list(mapping.get("required_palaces") or ["命宫"])
        stars = KnowledgeService.extract_stars_from_chart(chart)
        patterns = KnowledgeService.match_patterns(stars)
        wanted = set(mapping.get("required_patterns") or [])
        strengths: list[str] = []
        challenges: list[str] = []
        suggestions: list[str] = []
        trad: list[str] = []
        sources: list[dict[str, Any]] = []

        for p in patterns:
            pname = p.get("pattern_name") or ""
            if wanted and pname not in wanted and not any(w in pname for w in wanted):
                # still include if no explicit match filter saturation
                if len(sources) >= 3:
                    continue
            sources.append(
                _source(
                    "pattern",
                    name=pname,
                    school="古诀格局",
                    book=p.get("source_reference") or "格局知识",
                )
            )
            if p.get("traditional_meaning"):
                trad.append(str(p["traditional_meaning"]))
            for a in p.get("advantages") or []:
                strengths.append(str(a))
            for c in p.get("challenges") or []:
                challenges.append(str(c))
            if p.get("growth_advice"):
                suggestions.append(str(p["growth_advice"]))

        for chunk in (selected_chunks or [])[:5]:
            book = chunk.get("book_name") or chunk.get("book") or "Knowledge Core"
            page = chunk.get("page_number") or chunk.get("page")
            sources.append(
                _source(
                    "knowledge_chunk",
                    book=book,
                    page=page,
                    chapter=chunk.get("chapter"),
                    school="古诀",
                )
            )
            snippet = (chunk.get("content") or chunk.get("summary") or "")[:120]
            if snippet:
                trad.append(snippet)

        # theory rules for 格局
        for r in TheoryEngine.list_rules(categories=["格局理论"])[:3]:
            sources.append(
                _source("theory_rule", rule=r.get("rule_name"), school="古诀格局")
            )
            if r.get("traditional_meaning"):
                trad.append(str(r["traditional_meaning"]))

        summary = (
            f"古诀格局视角：对照{'、'.join([p.get('pattern_name') for p in patterns[:3] if p.get('pattern_name')]) or '经典格局'}。"
            + (f"依据：{trad[0][:80]}" if trad else "强调条件对照与学习视角，不作绝对预测。")
        )
        return cls._pack(
            "classic_formula",
            summary=summary[:280],
            strengths=strengths,
            challenges=challenges,
            suggestions=suggestions or ["把格局当作能力结构参考，落到可验证行动"],
            sources=sources,
            traditional=trad,
            required_palaces=palaces,
            confidence_level="medium" if patterns or selected_chunks else "low",
        )

    @classmethod
    def _graph_star_sources(cls, stars: list[str]) -> list[dict[str, Any]]:
        if not stars:
            return []
        db = SessionLocal()
        try:
            rows = db.execute(
                text(
                    """
                    SELECT name, entity_type, COALESCE(mention_count, 0) AS mention_count
                    FROM public.knowledge_entities
                    WHERE name = ANY(:names)
                    LIMIT 8
                    """
                ),
                {"names": stars},
            ).mappings().all()
            return [
                _source(
                    "knowledge_graph",
                    entity=r["name"],
                    entity_type=r["entity_type"],
                    mentions=r["mention_count"],
                    book="知识图谱",
                )
                for r in rows
            ]
        except Exception:
            return []
        finally:
            db.close()

    @classmethod
    def to_api_payload(
        cls,
        results: dict[str, dict[str, Any]],
        synthesis: dict[str, Any] | None = None,
        conflicts: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        for theory_type, result in results.items():
            key = TheoryRegistry.api_key(theory_type)
            payload[key] = {
                "summary": result.get("summary") or "",
                "sources": result.get("sources") or [],
                "strengths": result.get("strengths") or [],
                "challenges": result.get("challenges") or [],
                "suggestions": result.get("suggestions") or [],
                "confidence_level": result.get("confidence_level") or "medium",
                "theory_name": result.get("theory_name"),
            }
        if conflicts is not None:
            payload["conflicts"] = conflicts
        if synthesis is not None:
            payload["synthesis"] = {
                "common": synthesis.get("common") or synthesis.get("common_points") or "",
                "difference": synthesis.get("difference")
                or synthesis.get("different_views")
                or "",
                "advice": synthesis.get("advice") or synthesis.get("decision_advice") or "",
            }
        return payload
