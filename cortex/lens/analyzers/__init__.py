"""
CORTEX LENS Analyzers Package

Unified code analysis components.

Available Analyzers:
- ASTAnalyzer: Python AST parsing and code structure analysis
- GitHistoryAnalyzer: Git commit history and contributor analysis
- CommentExtractor: Comment, TODO, and documentation extraction
- ConfigAnalyzer: Configuration file security analysis
- DatabaseAnalyzer: Database schema and migration analysis
- APIAnalyzer: API endpoint security analysis
- DependencyAnalyzer: Dependency vulnerability analysis

Authority: CORE-035 (Consolidation)
"""

from cortex.lens.analyzers.ast_analyzer import ASTAnalyzer
from cortex.lens.analyzers.git_history_analyzer import GitHistoryAnalyzer
from cortex.lens.analyzers.comment_extractor import CommentExtractor
from cortex.lens.analyzers.config_analyzer import ConfigAnalyzer, get_config_analyzer
from cortex.lens.analyzers.database_analyzer import (
    DatabaseAnalyzer,
    get_database_analyzer,
)
from cortex.lens.analyzers.api_analyzer import APIAnalyzer, get_api_analyzer
from cortex.lens.analyzers.dependency_analyzer import (
    DependencyAnalyzer,
    get_dependency_analyzer,
)

__all__ = [
    "ASTAnalyzer",
    "GitHistoryAnalyzer",
    "CommentExtractor",
    "ConfigAnalyzer",
    "get_config_analyzer",
    "DatabaseAnalyzer",
    "get_database_analyzer",
    "APIAnalyzer",
    "get_api_analyzer",
    "DependencyAnalyzer",
    "get_dependency_analyzer",
]
