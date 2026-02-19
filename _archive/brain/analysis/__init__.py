"""
Analysis module for CORTEX brain.

NOTE: LENS analyzers have moved to cortex.lens.analyzers (v2.0)
This module re-exports for backward compatibility - will be removed next sprint.

Non-LENS components (VisionAnalyzer, RemoteGitAdapter, CompanyDomainLoader) remain here.

Uses lazy imports via __getattr__ to prevent circular dependency:
cortex/brain/analysis/__init__.py → cortex.lens.analyzers → ... → cortex.brain.analysis
"""

# LENS analyzer lazy imports (to prevent circular dependency)
_lazy_lens_imports = {
    # git_history_analyzer
    "GitHistoryAnalyzer": "cortex.lens.analyzers.git_history_analyzer",
    "GitCommit": "cortex.lens.analyzers.git_history_analyzer",
    "GitBlame": "cortex.lens.analyzers.git_history_analyzer",
    "GitHistoryResult": "cortex.lens.analyzers.git_history_analyzer",

    # ast_analyzer
    "ASTAnalyzer": "cortex.lens.analyzers.ast_analyzer",
    "FunctionInfo": "cortex.lens.analyzers.ast_analyzer",
    "ClassInfo": "cortex.lens.analyzers.ast_analyzer",
    "ImportInfo": "cortex.lens.analyzers.ast_analyzer",
    "ASTAnalysisResult": "cortex.lens.analyzers.ast_analyzer",

    # comment_extractor
    "CommentExtractor": "cortex.lens.analyzers.comment_extractor",
    "Comment": "cortex.lens.analyzers.comment_extractor",
    "DocstringInfo": "cortex.lens.analyzers.comment_extractor",
    "CommentExtractionResult": "cortex.lens.analyzers.comment_extractor",

    # config_analyzer
    "ConfigAnalyzer": "cortex.lens.analyzers.config_analyzer",
    "ConfigFinding": "cortex.lens.analyzers.config_analyzer",
    "ConfigSeverity": "cortex.lens.analyzers.config_analyzer",
    "ConfigCategory": "cortex.lens.analyzers.config_analyzer",
    "ConfigAnalysisResult": "cortex.lens.analyzers.config_analyzer",
    "get_config_analyzer": "cortex.lens.analyzers.config_analyzer",

    # database_analyzer
    "DatabaseAnalyzer": "cortex.lens.analyzers.database_analyzer",
    "MigrationType": "cortex.lens.analyzers.database_analyzer",
    "ColumnInfo": "cortex.lens.analyzers.database_analyzer",
    "TableInfo": "cortex.lens.analyzers.database_analyzer",
    "MigrationInfo": "cortex.lens.analyzers.database_analyzer",
    "DatabaseAnalysisResult": "cortex.lens.analyzers.database_analyzer",
    "get_database_analyzer": "cortex.lens.analyzers.database_analyzer",

    # api_analyzer
    "APIAnalyzer": "cortex.lens.analyzers.api_analyzer",
    "OpenAPIVersion": "cortex.lens.analyzers.api_analyzer",
    "SecuritySchemeType": "cortex.lens.analyzers.api_analyzer",
    "APISecurityPriority": "cortex.lens.analyzers.api_analyzer",
    "APIEndpoint": "cortex.lens.analyzers.api_analyzer",
    "SecurityScheme": "cortex.lens.analyzers.api_analyzer",
    "APISecurityFinding": "cortex.lens.analyzers.api_analyzer",
    "APIAnalysisResult": "cortex.lens.analyzers.api_analyzer",
    "get_api_analyzer": "cortex.lens.analyzers.api_analyzer",

    # dependency_analyzer
    "DependencyAnalyzer": "cortex.lens.analyzers.dependency_analyzer",
    "DependencyType": "cortex.lens.analyzers.dependency_analyzer",
    "VulnerabilitySeverity": "cortex.lens.analyzers.dependency_analyzer",
    "LicenseCategory": "cortex.lens.analyzers.dependency_analyzer",
    "PackageInfo": "cortex.lens.analyzers.dependency_analyzer",
    "Vulnerability": "cortex.lens.analyzers.dependency_analyzer",
    "DependencyFinding": "cortex.lens.analyzers.dependency_analyzer",
    "DependencyAnalysisResult": "cortex.lens.analyzers.dependency_analyzer",
    "get_dependency_analyzer": "cortex.lens.analyzers.dependency_analyzer",
}

# Non-LENS components remain in cortex.brain.analysis (no circular dependency)
from cortex.brain.analysis.company_domain_loader import (
    CompanyDomainLoader,
    CompanyDomainResult,
    DomainKnowledge,
    get_company_domain_loader,
)
from cortex.brain.analysis.vision_analyzer import (
    AnalysisDepth,
    DetectedIssue,
    ExtractedURL,
    ImageType,
    UIElement,
    VisionAnalysisResult,
    VisionAnalyzer,
    analyze_image,
)


def __getattr__(name):
    """Lazy import LENS analyzers to prevent circular dependency."""
    if name in _lazy_lens_imports:
        module_path = _lazy_lens_imports[name]
        import importlib
        module = importlib.import_module(module_path)
        return getattr(module, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    # LENS analyzer classes (lazy loaded)
    "GitHistoryAnalyzer",
    "GitCommit",
    "GitBlame",
    "GitHistoryResult",
    "ASTAnalyzer",
    "FunctionInfo",
    "ClassInfo",
    "ImportInfo",
    "ASTAnalysisResult",
    "CommentExtractor",
    "Comment",
    "DocstringInfo",
    "CommentExtractionResult",
    "ConfigAnalyzer",
    "ConfigFinding",
    "ConfigSeverity",
    "ConfigCategory",
    "ConfigAnalysisResult",
    "get_config_analyzer",
    "DatabaseAnalyzer",
    "MigrationType",
    "ColumnInfo",
    "TableInfo",
    "MigrationInfo",
    "DatabaseAnalysisResult",
    "get_database_analyzer",
    "APIAnalyzer",
    "OpenAPIVersion",
    "SecuritySchemeType",
    "APISecurityPriority",
    "APIEndpoint",
    "SecurityScheme",
    "APISecurityFinding",
    "APIAnalysisResult",
    "get_api_analyzer",
    "DependencyAnalyzer",
    "DependencyType",
    "VulnerabilitySeverity",
    "LicenseCategory",
    "PackageInfo",
    "Vulnerability",
    "DependencyFinding",
    "DependencyAnalysisResult",
    "get_dependency_analyzer",

    # Non-LENS components (directly imported above)
    "VisionAnalyzer",
    "VisionAnalysisResult",
    "UIElement",
    "ExtractedURL",
    "DetectedIssue",
    "ImageType",
    "AnalysisDepth",
    "analyze_image",
    "CompanyDomainLoader",
    "DomainKnowledge",
    "CompanyDomainResult",
    "get_company_domain_loader",
]
