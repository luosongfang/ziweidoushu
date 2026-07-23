"""Knowledge Core V4.0 Phase 1 — Multi-Theory Decision Engine."""

from app.knowledge.multitheory.synthesis_engine import SynthesisEngine
from app.knowledge.multitheory.theory_analyzer import TheoryAnalyzer
from app.knowledge.multitheory.theory_conflict_checker import TheoryConflictChecker
from app.knowledge.multitheory.theory_dispatcher import TheoryDispatcher
from app.knowledge.multitheory.theory_registry import TheoryRegistry

__all__ = [
    "TheoryRegistry",
    "TheoryDispatcher",
    "TheoryAnalyzer",
    "TheoryConflictChecker",
    "SynthesisEngine",
]
