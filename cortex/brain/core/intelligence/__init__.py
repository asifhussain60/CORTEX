"""
CORTEX Intelligence Module.

This module provides context intelligence capabilities including:
- AST-based code analysis
- Git history intelligence
- Code comment analysis
- Relationship traversal

Part of PHASE-07: Holistic Intent Router Intelligence.
"""

from cortex.brain.core.intelligence.ast_intelligence import (
    ASTIntelligenceEngine,
    ClassInfo,
    ConstantInfo,
    FunctionInfo,
    Parameter,
    ParseResult,
)
from cortex.brain.core.intelligence.author_context import (
    Author,
    AuthorContextBuilder,
    AuthorContribution,
)
from cortex.brain.core.intelligence.call_graph import (
    CallEdge,
    CallGraph,
    CallGraphBuilder,
)
from cortex.brain.core.intelligence.change_frequency import (
    ChangeFrequencyMapper,
    HotSpot,
)
from cortex.brain.core.intelligence.comment_analyzer import (
    ArgInfo,
    CommentAnalysisResult,
    CommentAnalyzer,
    CommentIndex,
    InlineComment,
    ParsedDocstring,
    QualityIssue,
    RaisesInfo,
    TechDebtItem,
)
from cortex.brain.core.intelligence.dependency_mapper import (
    DependencyMap,
    DependencyMapper,
    ImportInfo,
)
from cortex.brain.core.intelligence.pattern_detector import (
    DetectedPattern,
    PatternDetector,
)
from cortex.brain.core.intelligence.relationship_traversal import (
    APIEndpoint,
    ConfigReference,
    DatabaseModel,
    DependencyGraph,
    EnvReference,
    FileDependency,
    ForeignKeyRef,
    ImpactAnalysis,
    ModelGraph,
    ModelRelationship,
    RelationshipAnalysisResult,
    RelationshipEngine,
)
from cortex.lens.analyzers.git_history_analyzer import (
    CommitInfo,
    GitHistoryAnalyzer,
    RenameInfo,
)

__all__ = [
    # AST Intelligence
    "ASTIntelligenceEngine",
    "ParseResult",
    "FunctionInfo",
    "ClassInfo",
    "ConstantInfo",
    "Parameter",
    # Call Graph
    "CallGraphBuilder",
    "CallGraph",
    "CallEdge",
    # Pattern Detection
    "PatternDetector",
    "DetectedPattern",
    # Dependency Mapping
    "DependencyMapper",
    "DependencyMap",
    "ImportInfo",
    # Git History
    "GitHistoryAnalyzer",
    "CommitInfo",
    "RenameInfo",
    # Change Frequency
    "ChangeFrequencyMapper",
    "HotSpot",
    # Author Context
    "AuthorContextBuilder",
    "Author",
    "AuthorContribution",
    # Comment Analysis
    "CommentAnalyzer",
    "CommentAnalysisResult",
    "ParsedDocstring",
    "InlineComment",
    "TechDebtItem",
    "QualityIssue",
    "CommentIndex",
    "ArgInfo",
    "RaisesInfo",
    # Relationship Traversal
    "RelationshipEngine",
    "RelationshipAnalysisResult",
    "APIEndpoint",
    "DatabaseModel",
    "EnvReference",
    "ConfigReference",
    "FileDependency",
    "DependencyGraph",
    "ModelGraph",
    "ImpactAnalysis",
    "ForeignKeyRef",
    "ModelRelationship",
]
