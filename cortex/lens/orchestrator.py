"""
cortex.lens.orchestrator — compatibility alias for cortex.lens.lens_orchestrator.

Re-exports all public symbols so that patch targets using
``cortex.lens.orchestrator.*`` resolve correctly.

AC-ID: AC-LENS-COMPAT-001
"""

from cortex.lens.lens_orchestrator import (  # noqa: F401
    LENSOrchestrator,
    LENSContext,
)
from cortex.lens.analyzers.ast_analyzer import ASTAnalyzer  # noqa: F401
from cortex.lens.analyzers.comment_extractor import CommentExtractor  # noqa: F401
from cortex.lens.analyzers.git_history_analyzer import GitHistoryAnalyzer  # noqa: F401

__all__ = [
    "LENSOrchestrator",
    "LENSContext",
    "ASTAnalyzer",
    "CommentExtractor",
    "GitHistoryAnalyzer",
]
