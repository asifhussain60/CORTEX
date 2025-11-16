"""CORTEX Tier 2: Knowledge Graph

Backward compatibility layer during Phase 1 modularization.
"""

# Import from legacy file during migration
from .knowledge_graph_legacy import (
    KnowledgeGraph,
    Pattern,
    PatternType,
    RelationshipType
)

__all__ = [
    'KnowledgeGraph',
    'Pattern',
    'PatternType',
    'RelationshipType'
]
