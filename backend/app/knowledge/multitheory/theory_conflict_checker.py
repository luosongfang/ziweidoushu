"""Detect disagreements across multi-theory results (no LLM)."""

from __future__ import annotations

from typing import Any

from app.knowledge.multitheory.theory_registry import TheoryRegistry


def _tokens(text: str) -> set[str]:
    # coarse Chinese bigrams + keyword hits
    t = text or ""
    toks: set[str] = set()
    for i in range(len(t) - 1):
        pair = t[i : i + 2]
        if pair.strip():
            toks.add(pair)
    for kw in ("优势", "风险", "稳定", "进取", "资源", "关系", "沟通", "节奏", "格局", "四化", "三合"):
        if kw in t:
            toks.add(kw)
    return toks


class TheoryConflictChecker:
    """Compare theory outputs for complementary vs conflicting signals."""

    RISK_MARKERS = ("风险", "挑战", "波动", "压力", "谨慎", "张力", "忌")
    OPPORTUNITY_MARKERS = ("优势", "机会", "稳健", "进取", "资源", "禄", "权", "科")

    @classmethod
    def check(cls, results: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
        items = list(results.items())
        conflicts: list[dict[str, Any]] = []
        if len(items) < 2:
            return conflicts

        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                t_a, a = items[i]
                t_b, b = items[j]
                conflict = cls._pair_conflict(t_a, a, t_b, b)
                if conflict:
                    conflicts.append(conflict)
        return conflicts

    @classmethod
    def _pair_conflict(
        cls,
        type_a: str,
        a: dict[str, Any],
        type_b: str,
        b: dict[str, Any],
    ) -> dict[str, Any] | None:
        name_a = TheoryRegistry.display(type_a)
        name_b = TheoryRegistry.display(type_b)

        # polarity: one emphasizes opportunity, other risk on overlapping topic
        a_opp = cls._score(a, cls.OPPORTUNITY_MARKERS)
        a_risk = cls._score(a, cls.RISK_MARKERS)
        b_opp = cls._score(b, cls.OPPORTUNITY_MARKERS)
        b_risk = cls._score(b, cls.RISK_MARKERS)

        polarity_gap = (a_opp - a_risk) - (b_opp - b_risk)

        # textual divergence of summaries
        sa = str(a.get("summary") or "")
        sb = str(b.get("summary") or "")
        ta, tb = _tokens(sa), _tokens(sb)
        overlap = len(ta & tb) / max(1, min(len(ta), len(tb))) if ta and tb else 0.0

        # strength vs challenge contradiction: A's strength similar to B's challenge
        strength_challenge_hits = 0
        for s in a.get("strengths") or []:
            for c in b.get("challenges") or []:
                if cls._similar(str(s), str(c)):
                    strength_challenge_hits += 1
        for s in b.get("strengths") or []:
            for c in a.get("challenges") or []:
                if cls._similar(str(s), str(c)):
                    strength_challenge_hits += 1

        palace_a = set(a.get("required_palaces") or [])
        palace_b = set(b.get("required_palaces") or [])
        palace_diff = sorted(palace_a.symmetric_difference(palace_b))

        is_conflict = abs(polarity_gap) >= 2 or strength_challenge_hits > 0 or (
            overlap < 0.15 and (a.get("challenges") or b.get("challenges"))
        )
        if not is_conflict and not palace_diff:
            return None
        if not is_conflict and palace_diff:
            # soft difference, not hard conflict
            return {
                "theory_a": name_a,
                "theory_b": name_b,
                "level": "difference",
                "reason": f"关注宫位侧重不同：{('、'.join(palace_diff[:6]))}",
                "polarity_gap": polarity_gap,
                "overlap": round(overlap, 3),
            }

        reason_parts = []
        if abs(polarity_gap) >= 2:
            lean_a = "偏机会" if (a_opp - a_risk) > (b_opp - b_risk) else "偏风险"
            lean_b = "偏风险" if lean_a == "偏机会" else "偏机会"
            reason_parts.append(f"{name_a}{lean_a}，{name_b}{lean_b}")
        if strength_challenge_hits:
            reason_parts.append("一方优势表述与另一方挑战表述存在张力")
        if overlap < 0.15:
            reason_parts.append("摘要主题重合度较低，宜对照阅读")

        return {
            "theory_a": name_a,
            "theory_b": name_b,
            "level": "conflict" if strength_challenge_hits or abs(polarity_gap) >= 3 else "difference",
            "reason": "；".join(reason_parts) or "理论视角存在差异",
            "polarity_gap": polarity_gap,
            "overlap": round(overlap, 3),
            "guidance": "差异反映观察角度不同，应综合对照而非二选一判决。",
        }

    @classmethod
    def _score(cls, result: dict[str, Any], markers: tuple[str, ...]) -> int:
        blob = " ".join(
            [
                str(result.get("summary") or ""),
                " ".join(result.get("strengths") or []),
                " ".join(result.get("challenges") or []),
                " ".join(result.get("suggestions") or []),
            ]
        )
        return sum(1 for m in markers if m in blob)

    @classmethod
    def _similar(cls, a: str, b: str) -> bool:
        if not a or not b:
            return False
        if a in b or b in a:
            return True
        ta, tb = _tokens(a), _tokens(b)
        if not ta or not tb:
            return False
        return len(ta & tb) / max(1, min(len(ta), len(tb))) >= 0.4
