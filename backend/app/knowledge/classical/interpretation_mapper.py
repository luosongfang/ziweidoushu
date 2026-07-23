"""Map classical quotes to theory systems via keyword tags only (no rewrite)."""

from __future__ import annotations

import json
from typing import Any

from sqlalchemy import text

from app.database.database import SessionLocal
from app.knowledge.classical.quote_models import ClassicalQuote, extract_tags
from app.knowledge.importer.metadata_extractor import infer_relation_types

# book_type / theory_category → theory_system
_BOOK_TYPE_TO_THEORY = {
    "classic_formula": "classic_formula",
    "star_theory": "star",
    "palace_theory": "palace",
    "foundation": "foundation",
    "modern_analysis": "general",
}


class InterpretationMapper:
    """
    Attach theory_system + topic tags to a quote.
    Does NOT create paraphrases or summaries of original_text.
    """

    @classmethod
    def derive_mappings(cls, quote: ClassicalQuote) -> list[dict[str, Any]]:
        tags = extract_tags(quote.original_text)
        relation_types = infer_relation_types(tags)
        systems: list[str] = []

        # From content-derived theory category
        cat = quote.theory_category or "general"
        if cat == "four_transform":
            systems.append("four_transform")
        elif cat in {
            "sanhe",
            "feixing",
            "classic_formula",
            "palace",
            "star",
            "foundation",
            "general",
        }:
            systems.append(cat)

        if tags.get("four_transform_tags") and "four_transform" not in systems:
            systems.append("four_transform")
        if tags.get("star_tags") and "star" not in systems:
            systems.append("star")
        if tags.get("palace_tags") and "palace" not in systems:
            systems.append("palace")
        if tags.get("pattern_tags") and "classic_formula" not in systems:
            systems.append("classic_formula")

        if not systems:
            systems = ["general"]

        out: list[dict[str, Any]] = []
        for theory in systems:
            mapping_type = None
            if theory == "four_transform":
                mapping_type = "four_transform"
            elif theory == "star":
                mapping_type = "star_meaning"
            elif theory == "palace":
                mapping_type = "palace_meaning"
            elif theory == "classic_formula":
                mapping_type = "combination"
            elif relation_types:
                mapping_type = relation_types[0]

            out.append(
                {
                    "theory_system": theory,
                    "mapping_type": mapping_type,
                    "topic_tags": list(
                        dict.fromkeys(
                            (tags.get("life_question_tags") or [])
                            + (tags.get("keywords") or [])[:12]
                        )
                    ),
                    "star_tags": tags.get("star_tags") or [],
                    "palace_tags": tags.get("palace_tags") or [],
                    "pattern_tags": tags.get("pattern_tags") or [],
                }
            )
        return out

    @classmethod
    def map_quote(cls, quote: ClassicalQuote) -> int:
        if not quote.id:
            return 0
        mappings = cls.derive_mappings(quote)
        db = SessionLocal()
        n = 0
        try:
            for m in mappings:
                db.execute(
                    text(
                        """
                        INSERT INTO public.classical_interpretations
                            (quote_id, theory_system, topic_tags, mapping_type,
                             star_tags, palace_tags, pattern_tags)
                        VALUES
                            (CAST(:qid AS uuid), :theory,
                             CAST(:topics AS jsonb), :mtype,
                             CAST(:stars AS jsonb), CAST(:palaces AS jsonb),
                             CAST(:patterns AS jsonb))
                        ON CONFLICT (quote_id, theory_system, mapping_type)
                        DO UPDATE SET
                            topic_tags = EXCLUDED.topic_tags,
                            star_tags = EXCLUDED.star_tags,
                            palace_tags = EXCLUDED.palace_tags,
                            pattern_tags = EXCLUDED.pattern_tags
                        """
                    ),
                    {
                        "qid": quote.id,
                        "theory": m["theory_system"],
                        "topics": json.dumps(m["topic_tags"], ensure_ascii=False),
                        "mtype": m["mapping_type"] or "",
                        "stars": json.dumps(m["star_tags"], ensure_ascii=False),
                        "palaces": json.dumps(m["palace_tags"], ensure_ascii=False),
                        "patterns": json.dumps(m["pattern_tags"], ensure_ascii=False),
                    },
                )
                n += 1
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()
        return n

    @classmethod
    def list_for_quote(cls, quote_id: str) -> list[dict[str, Any]]:
        db = SessionLocal()
        try:
            rows = db.execute(
                text(
                    """
                    SELECT id::text, quote_id::text, theory_system, topic_tags,
                           mapping_type, star_tags, palace_tags, pattern_tags, created_at
                    FROM public.classical_interpretations
                    WHERE quote_id = CAST(:qid AS uuid)
                    ORDER BY theory_system
                    """
                ),
                {"qid": quote_id},
            ).mappings().all()
            out = []
            for r in rows:
                item = dict(r)
                if item.get("created_at"):
                    item["created_at"] = item["created_at"].isoformat()
                out.append(item)
            return out
        finally:
            db.close()
