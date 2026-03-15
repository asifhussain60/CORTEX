"""
cortex.lens.lens_orchestrator — LENS Orchestrator package.

Decomposed from lens_orchestrator.py (2,045L) in Phase 103-d (GAP-103-04).
Re-exports all public symbols for backward compatibility.

Authority: CORE-035 (single canonical), SWEEP-103-GOD-OBJECT-DECOMPOSITION
"""
from cortex.lens.lens_orchestrator.lens_models import LENSContext
from cortex.lens.lens_orchestrator.lens_analysis_mixin import LensFileAnalysisMixin
from cortex.lens.lens_orchestrator.lens_remote_mixin import LensRemoteMixin
from cortex.lens.lens_orchestrator.lens_holistic_mixin import LensHolisticMixin
from cortex.lens.lens_orchestrator.lens_company_mixin import LensCompanyMixin
from cortex.lens.lens_orchestrator.lens_vision_mixin import LensVisionMixin
from cortex.lens.lens_orchestrator._coordinator import (
    LENSOrchestrator,
    get_lens_orchestrator,
)
# Re-exported for test patching at cortex.lens.lens_orchestrator.* namespace
from cortex.lens.analyzers.python_structure_analyzer import ASTAnalyzer
from cortex.lens.analyzers.comment_extractor import CommentExtractor
from cortex.lens.analyzers.git_history_analyzer import GitHistoryAnalyzer

__all__ = [
    "LENSContext",
    "LensFileAnalysisMixin",
    "LensRemoteMixin",
    "LensHolisticMixin",
    "LensCompanyMixin",
    "LensVisionMixin",
    "LENSOrchestrator",
    "get_lens_orchestrator",
    "ASTAnalyzer",
    "CommentExtractor",
    "GitHistoryAnalyzer",
]
