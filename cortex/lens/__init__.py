"""cortex.lens — Compatibility shim. Re-exports LENS components from canonical locations.

Phase 109-D (GAP-109-16): Thin compat shim. IntelligenceFacade is the canonical entry point.
Authority: CORE-035 (single canonical).
"""
# Thin re-export shim — no implementation logic here.
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


def __getattr__(name: str):  # type: ignore[return]
    """Lazy delegate — defers imports to prevent circular imports."""
    _map = {
        "LENSOrchestrator": ("cortex.lens.lens_orchestrator", "LENSOrchestrator"),
        "LENSContext": ("cortex.lens.lens_orchestrator", "LENSContext"),
        "ASTAnalyzer": ("cortex.lens.analyzers.python_structure_analyzer", "ASTAnalyzer"),
        "GitHistoryAnalyzer": ("cortex.lens.analyzers.git_history_analyzer", "GitHistoryAnalyzer"),
        "CommentExtractor": ("cortex.lens.analyzers.comment_extractor", "CommentExtractor"),
        "ConfigAnalyzer": ("cortex.lens.analyzers.config_analyzer", "ConfigAnalyzer"),
        "DatabaseAnalyzer": ("cortex.lens.analyzers.database_analyzer", "DatabaseAnalyzer"),
        "APIAnalyzer": ("cortex.lens.analyzers.api_analyzer", "APIAnalyzer"),
        "DependencyAnalyzer": ("cortex.lens.analyzers.dependency_analyzer", "DependencyAnalyzer"),
    }
    if name in _map:
        module_path, attr = _map[name]
        import importlib
        mod = importlib.import_module(module_path)
        return getattr(mod, attr)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

