"""
LENS Knowledge Graph — Deep intelligence layer.

Authority: Phase 3 Wave 4
Purpose: Graph-based code intelligence and semantic search
"""
from cortex_lens.knowledge_graph.ast_graph_builder import (
    ASTKnowledgeGraph,
    ASTKnowledgeGraphBuilder,
    ASTGraphNode,
    ASTGraphRelationship,
)
from cortex_lens.knowledge_graph.semantic_search import SemanticSearchEngine, SearchResult
from cortex.brain.core.intelligence.pattern_detector import PatternDetector, DetectedPattern

__all__ = [
    "ASTKnowledgeGraph",
    "ASTKnowledgeGraphBuilder",
    "ASTGraphNode",
    "ASTGraphRelationship",
    "SemanticSearchEngine",
    "SearchResult",
    "PatternDetector",
    "DetectedPattern",
]
