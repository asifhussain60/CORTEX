"""
Shim module: cortex.lens.orchestrator

Re-exports everything from cortex.lens.lens_orchestrator so that
``@patch('cortex.lens.orchestrator.XYZ')`` works in tests.

Authority: CORE-035 (single canonical implementation in lens_orchestrator.py)
"""

from cortex.lens.lens_orchestrator import LENSOrchestrator, LENSContext
from cortex.lens.analyzers.git_history_analyzer import GitHistoryAnalyzer
from cortex.lens.analyzers.ast_analyzer import ASTAnalyzer
from cortex.lens.analyzers.comment_extractor import CommentExtractor

__all__ = [
    "LENSOrchestrator",
    "LENSContext",
    "GitHistoryAnalyzer",
    "ASTAnalyzer",
    "CommentExtractor",
]
