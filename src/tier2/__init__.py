"""CORTEX Tier 2: Knowledge Graph

Backward compatibility layer during Phase 1 modularization.
Phase 3: Real brain implementation.
Phase 7.2: Pattern learning activation.
"""

# Phase 3: Real brain implementation (production SQLite backend)
from .knowledge_graph import KnowledgeGraph

# Phase 7.2: Pattern learning components
from . import relationship_mapper
from . import tdd_cycle_logger
from . import relevance_scorer
from . import semantic_search

__all__ = [
    'KnowledgeGraph',
    'relationship_mapper',
    'tdd_cycle_logger',
    'relevance_scorer',
    'semantic_search'
]

