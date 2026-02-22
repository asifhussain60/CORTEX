"""
CORTEX LENS - Multi-language Code Analysis Framework.

Unified code analysis engine supporting:
- Python AST analysis and semantic understanding
- .NET (C#) Roslyn-based code analysis
- Knowledge graph construction and traversal
- Domain-driven inference and pattern detection
- Runtime correlation with execution traces

Authority: Phase 3 - Package Consolidation (formerly cortex.lens)
"""

try:
    from cortex.intelligence.lens.knowledge_graph import (
        ASTKnowledgeGraph,
        SemanticSearchEngine,
    )
    __all__ = [
        "ASTKnowledgeGraph",
        "SemanticSearchEngine",
    ]
except ImportError:
    __all__ = []
