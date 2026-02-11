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

Also provides knowledge repository and company override capabilities:
- KnowledgeRepository: Access to CORTEX tier3 knowledge YAMLs
- CompanyKnowledgeLoader: Company-specific knowledge with precedence override

Used by Intent Router to build holistic understanding of user requests.
"""

from .company_knowledge_loader import (
    COMPLIANCE_PATTERNS,
    CompanyKnowledgeLoader,
    ComplianceMatch,
    KnowledgeLayer,
    MergedKnowledgeResult,
    get_company_knowledge_loader,
)
from .knowledge_graph import (
    EdgeType,
    GraphEdge,
    GraphMetadata,
    GraphNode,
    KnowledgeGraph,
    KnowledgeGraphBuilder,
    NodeType,
)
from .knowledge_repository import (
    KnowledgeEntry,
    KnowledgeQueryResult,
    KnowledgeRepository,
    get_knowledge_repository,
)

__all__ = [
    # Knowledge Graph
    "KnowledgeGraph",
    "GraphNode",
    "GraphEdge",
    "NodeType",
    "EdgeType",
    "KnowledgeGraphBuilder",
    "GraphMetadata",
    # Knowledge Repository
    "KnowledgeRepository",
    "KnowledgeEntry",
    "KnowledgeQueryResult",
    "get_knowledge_repository",
    # Company Knowledge Loader
    "CompanyKnowledgeLoader",
    "ComplianceMatch",
    "KnowledgeLayer",
    "MergedKnowledgeResult",
    "get_company_knowledge_loader",
    "COMPLIANCE_PATTERNS",
]
