"""
CORTEX LENS - Unified Code Intelligence Package

Consolidated LENS analyzers, discovery plugins, and orchestration.

Architecture:
- cortex.lens.analyzers: AST, Git, Config, Database, API, Dependency analyzers
- cortex.lens.discovery: Config and database discovery plugins
- cortex.lens.orchestrator: LENSOrchestrator (unified analysis)

Authority: CORE-035 (Consolidation), ARCH-012 (Standards)
"""

from cortex.lens.orchestrator import LENSOrchestrator, LENSContext

# Convenience imports for common analyzers
from cortex.lens.analyzers.ast_analyzer import ASTAnalyzer
from cortex.lens.analyzers.git_history_analyzer import GitHistoryAnalyzer
from cortex.lens.analyzers.comment_extractor import CommentExtractor
from cortex.lens.analyzers.config_analyzer import ConfigAnalyzer
from cortex.lens.analyzers.database_analyzer import DatabaseAnalyzer
from cortex.lens.analyzers.api_analyzer import APIAnalyzer
from cortex.lens.analyzers.dependency_analyzer import DependencyAnalyzer

__all__ = [
    "LENSOrchestrator",
    "LENSContext",
    "ASTAnalyzer",
    "GitHistoryAnalyzer",
    "CommentExtractor",
    "ConfigAnalyzer",
    "DatabaseAnalyzer",
    "APIAnalyzer",
    "DependencyAnalyzer",
]

__version__ = "2.0.0"
