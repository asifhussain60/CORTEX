"""CORTEX Tier 2: Knowledge Graph

Backward compatibility layer during Phase 1 modularization.
Phase 3: Real brain implementation.
"""

# Import types from modular implementation
from .knowledge_graph.types import (
    Pattern,
    PatternType,
    RelationshipType
)

# Phase 3: Real brain implementation (production SQLite backend)
from .knowledge_graph import KnowledgeGraph

__all__ = [
    'KnowledgeGraph',
    'Pattern',
    'PatternType',
    'RelationshipType'
]
