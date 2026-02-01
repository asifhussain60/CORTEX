"""
Analysis module for CORTEX brain.

Provides code and repository analysis capabilities.
"""

from cortex.brain.analysis.git_history_analyzer import (
    GitHistoryAnalyzer,
    GitCommit,
    GitBlame,
    GitHistoryResult,
)
from cortex.brain.analysis.ast_analyzer import (
    ASTAnalyzer,
    FunctionInfo,
    ClassInfo,
    ImportInfo,
    ASTAnalysisResult,
)
from cortex.brain.analysis.comment_extractor import (
    CommentExtractor,
    Comment,
    DocstringInfo,
    CommentExtractionResult,
)
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
from cortex.brain.analysis.config_analyzer import (
    ConfigAnalyzer,
    ConfigFinding,
    ConfigSeverity,
    ConfigCategory,
    ConfigAnalysisResult,
    get_config_analyzer,
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
]
    "VisionAnalyzer",
    "VisionAnalysisResult",
    "UIElement",
    "ExtractedURL",
    "DetectedIssue",
    "ImageType",
    "AnalysisDepth",
    "analyze_image",
]
