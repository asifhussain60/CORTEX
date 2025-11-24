"""
CORTEX Tier 2: Knowledge Graph (Modular Architecture)

Long-term memory with FTS5 semantic search and pattern relationships.

PHASE 1 MIGRATION: This package is under active development.
For backward compatibility, we re-export from the legacy monolithic file.

New Structure (in progress):
- types.py: Shared data types (Pattern, PatternType, etc.) ✅
- database/: Database schema and connections ✅
- patterns/: Pattern storage, search, and decay logic (TODO)
- relationships/: Pattern relationship management (TODO)
- tags/: Tag-based organization (TODO)

Once modularization is complete, this will import from the new coordinator.
"""

# Import from modular types
from .types import (
    Pattern,
    PatternType,
    RelationshipType
)

# Import KnowledgeGraph facade
from .knowledge_graph import KnowledgeGraph

# New modular components (partially complete)
from .database import DatabaseSchema, ConnectionManager
from .patterns.pattern_store import PatternStore

__all__ = [
    # Legacy exports (for backward compatibility)
    'KnowledgeGraph',
    'Pattern',
    'PatternType',
    'RelationshipType',
    # New modular exports
    'DatabaseSchema',
    'ConnectionManager',
    'PatternStore',
]

__version__ = "2.0.0-modular-in-progress"
