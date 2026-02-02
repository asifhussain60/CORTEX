"""
Analysis module for CORTEX brain.

NOTE: LENS analyzers have moved to cortex.lens.analyzers (v2.0)
This module re-exports for backward compatibility - will be removed next sprint.

Non-LENS components (VisionAnalyzer, RemoteGitAdapter, CompanyDomainLoader) remain here.
"""

# LENS analyzers - re-export from new location (DEPRECATED)
from cortex.lens.analyzers.git_history_analyzer import (
    GitHistoryAnalyzer,
    GitCommit,
    GitBlame,
    GitHistoryResult,
)
from cortex.lens.analyzers.ast_analyzer import (
    ASTAnalyzer,
    FunctionInfo,
    ClassInfo,
    ImportInfo,
    ASTAnalysisResult,
)
from cortex.lens.analyzers.comment_extractor import (
    CommentExtractor,
    Comment,
    DocstringInfo,
    CommentExtractionResult,
)
from cortex.lens.analyzers.config_analyzer import (
    ConfigAnalyzer,
    ConfigFinding,
    ConfigSeverity,
    ConfigCategory,
    ConfigAnalysisResult,
    get_config_analyzer,
)
from cortex.lens.analyzers.database_analyzer import (
    DatabaseAnalyzer,
    MigrationType,
    ColumnInfo,
    TableInfo,
    MigrationInfo,
    DatabaseAnalysisResult,
    get_database_analyzer,
)
from cortex.lens.analyzers.api_analyzer import (
    APIAnalyzer,
    OpenAPIVersion,
    SecuritySchemeType,
    APISecurityPriority,
    APIEndpoint,
    SecurityScheme,
    APISecurityFinding,
    APIAnalysisResult,
    get_api_analyzer,
)
from cortex.lens.analyzers.dependency_analyzer import (
    DependencyAnalyzer,
    DependencyType,
    VulnerabilitySeverity,
    LicenseCategory,
    PackageInfo,
    Vulnerability,
    DependencyFinding,
    DependencyAnalysisResult,
    get_dependency_analyzer,
)

# Non-LENS components remain in cortex.brain.analysis
from cortex.brain.analysis.vision_analyzer import (
    VisionAnalyzer,
    VisionAnalysisResult,
    UIElement,
    ExtractedURL,
    DetectedIssue,
    ImageType,
    AnalysisDepth,
    analyze_image,
)
from cortex.brain.analysis.company_domain_loader import (
    CompanyDomainLoader,
    DomainKnowledge,
    CompanyDomainResult,
    get_company_domain_loader,
)

__all__ = [
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
    "VisionAnalyzer",
    "VisionAnalysisResult",
    "UIElement",
    "ExtractedURL",
    "DetectedIssue",
    "ImageType",
    "AnalysisDepth",
    "analyze_image",
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
    "CompanyDomainLoader",
    "DomainKnowledge",
    "CompanyDomainResult",
    "get_company_domain_loader",
    "DependencyAnalyzer",
    "DependencyType",
    "VulnerabilitySeverity",
    "LicenseCategory",
    "PackageInfo",
    "Vulnerability",
    "DependencyFinding",
    "DependencyAnalysisResult",
    "get_dependency_analyzer",
]
