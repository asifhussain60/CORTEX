"""
CORTEX LENS - Unified Code Intelligence Package

Consolidated LENS analyzers, discovery plugins, and orchestration.

Architecture:
- cortex.lens.analyzers: AST, Git, Config, Database, API, Dependency analyzers
- cortex.lens.discovery: Config and database discovery plugins
- cortex.lens.orchestrator: LENSOrchestrator (unified analysis)

Authority: CORE-035 (Consolidation), ARCH-012 (Standards)

Note: Uses lazy imports via __getattr__ to prevent circular import issues.
      This allows submodules to import from cortex.lens without triggering
      full package initialization.
"""

__version__ = "2.0.0"

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

# Lazy imports via __getattr__ (Python 3.7+)
# This prevents circular import issues by deferring imports until first access
def __getattr__(name):
    """Lazy import mechanism to prevent circular dependencies."""
    if name == "LENSOrchestrator":
        from cortex.lens.orchestrator import LENSOrchestrator
        return LENSOrchestrator
    elif name == "LENSContext":
        from cortex.lens.orchestrator import LENSContext
        return LENSContext
    elif name == "ASTAnalyzer":
        from cortex.lens.analyzers.ast_analyzer import ASTAnalyzer
        return ASTAnalyzer
    elif name == "GitHistoryAnalyzer":
        from cortex.lens.analyzers.git_history_analyzer import GitHistoryAnalyzer
        return GitHistoryAnalyzer
    elif name == "CommentExtractor":
        from cortex.lens.analyzers.comment_extractor import CommentExtractor
        return CommentExtractor
    elif name == "ConfigAnalyzer":
        from cortex.lens.analyzers.config_analyzer import ConfigAnalyzer
        return ConfigAnalyzer
    elif name == "DatabaseAnalyzer":
        from cortex.lens.analyzers.database_analyzer import DatabaseAnalyzer
        return DatabaseAnalyzer
    elif name == "APIAnalyzer":
        from cortex.lens.analyzers.api_analyzer import APIAnalyzer
        return APIAnalyzer
    elif name == "DependencyAnalyzer":
        from cortex.lens.analyzers.dependency_analyzer import DependencyAnalyzer
        return DependencyAnalyzer

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
