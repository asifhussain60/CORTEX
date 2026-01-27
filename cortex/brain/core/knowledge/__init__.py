"""
Knowledge Graph Module Package.

Provides unified knowledge graph representation for CORTEX LENS protocol.
The knowledge graph aggregates intelligence from multiple sources:
- AST analysis
- Git history
- Code comments
- Relationship traversal
- API discovery
- Database schema analysis

Used by Intent Router to build holistic understanding of user requests.
"""

from .knowledge_graph import (
    KnowledgeGraph,
    GraphNode,
    GraphEdge,
    NodeType,
    EdgeType,
    KnowledgeGraphBuilder,
    GraphMetadata,
)

__all__ = [
    "KnowledgeGraph",
    "GraphNode",
    "GraphEdge",
    "NodeType",
    "EdgeType",
    "KnowledgeGraphBuilder",
    "GraphMetadata",
]
