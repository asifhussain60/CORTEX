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
- VendorDetector: Third-party vendor dependency detection (Phase 19)
- DatabaseCrawlerPlugin: Abstract interface for database schema extraction (Phase 19)
- PolyglotAnalyzer: Multi-language AST analysis (Phase 2 - ENH-017)

Authority: CORE-035 (Consolidation)
Note: Uses lazy imports to prevent circular dependencies
"""

# Lazy imports to prevent circular dependency:
# analyzers/__init__.py → git_history_analyzer → brain.analysis → analyzers/__init__.py
_lazy_imports = {
    "ASTAnalyzer": ("cortex.lens.analyzers.ast_analyzer", "ASTAnalyzer"),
    "GitHistoryAnalyzer": ("cortex.lens.analyzers.git_history_analyzer", "GitHistoryAnalyzer"),
    "CommentExtractor": ("cortex.lens.analyzers.comment_extractor", "CommentExtractor"),
    "ConfigAnalyzer": ("cortex.lens.analyzers.config_analyzer", "ConfigAnalyzer"),
    "get_config_analyzer": ("cortex.lens.analyzers.config_analyzer", "get_config_analyzer"),
    "DatabaseAnalyzer": ("cortex.lens.analyzers.database_analyzer", "DatabaseAnalyzer"),
    "get_database_analyzer": ("cortex.lens.analyzers.database_analyzer", "get_database_analyzer"),
    "APIAnalyzer": ("cortex.lens.analyzers.api_analyzer", "APIAnalyzer"),
    "get_api_analyzer": ("cortex.lens.analyzers.api_analyzer", "get_api_analyzer"),
    "DependencyAnalyzer": ("cortex.lens.analyzers.dependency_analyzer", "DependencyAnalyzer"),
    "get_dependency_analyzer": ("cortex.lens.analyzers.dependency_analyzer", "get_dependency_analyzer"),
    "VendorDetector": ("cortex.lens.analyzers.vendor_detector", "VendorDetector"),
    "get_vendor_detector": ("cortex.lens.analyzers.vendor_detector", "get_vendor_detector"),
    "DatabaseCrawlerPlugin": ("cortex.lens.analyzers.database_crawler_plugin", "DatabaseCrawlerPlugin"),
    "SchemaEntity": ("cortex.lens.analyzers.database_crawler_plugin", "SchemaEntity"),
    "DatabaseConnection": ("cortex.lens.analyzers.database_crawler_plugin", "DatabaseConnection"),
    "get_database_crawler_plugin": ("cortex.lens.analyzers.database_crawler_plugin", "get_database_crawler_plugin"),
    "PolyglotAnalyzer": ("cortex.lens.analyzers.polyglot_analyzer", "PolyglotAnalyzer"),
    "PolyglotAnalysisResult": ("cortex.lens.analyzers.polyglot_analyzer", "PolyglotAnalysisResult"),
}

def __getattr__(name):
    """Lazy import to prevent circular dependencies."""
    if name in _lazy_imports:
        module_path, attr_name = _lazy_imports[name]
        import importlib
        module = importlib.import_module(module_path)
        return getattr(module, attr_name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

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
    "VendorDetector",
    "get_vendor_detector",
    "DatabaseCrawlerPlugin",
    "SchemaEntity",
    "DatabaseConnection",
    "get_database_crawler_plugin",
    "PolyglotAnalyzer",
    "PolyglotAnalysisResult",
]

