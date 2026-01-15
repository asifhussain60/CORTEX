# © 2025-2026 Asif Hussain. All rights reserved.
# CORTEX Intelligence Module - Context gathering and analysis
"""
CORTEX Intelligence Module.

This module provides context intelligence capabilities including:
- AST-based code analysis
- Git history intelligence
- Code comment analysis
- Relationship traversal

Part of PHASE-07: Holistic Intent Router Intelligence.
"""

from src.core.intelligence.ast_intelligence import (
    ASTIntelligenceEngine,
    ParseResult,
    FunctionInfo,
    ClassInfo,
    ConstantInfo,
    Parameter,
)
from src.core.intelligence.call_graph import (
    CallGraphBuilder,
    CallGraph,
    CallEdge,
)
from src.core.intelligence.pattern_detector import (
    PatternDetector,
    DetectedPattern,
)
from src.core.intelligence.dependency_mapper import (
    DependencyMapper,
    DependencyMap,
    ImportInfo,
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
]
