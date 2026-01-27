"""Knowledge Graph module for CORTEX.

Provides abstract graph adapter interface and multiple backend implementations
for storing and querying governance rules, domain entities, and service
relationships in a knowledge graph.

Implementations:
  - MockGraphAdapter: In-memory implementation for testing
  - SQLiteGraphAdapter: SQLite fallback implementation
  - Neo4jGraphAdapter: Neo4j/Neptune backend (future)
"""

from cortex.brain.core.knowledge.graph.interface import (
    IGraphAdapter,
    EntityNode,
    Relationship,
    Path,
    HealthStatus,
    GraphQueryError,
)
from cortex.brain.core.knowledge.graph.mock_adapter import MockGraphAdapter
from cortex.brain.core.knowledge.graph.sqlite_adapter import SQLiteGraphAdapter

__all__ = [
    "IGraphAdapter",
    "EntityNode",
    "Relationship",
    "Path",
    "HealthStatus",
    "GraphQueryError",
    "MockGraphAdapter",
    "SQLiteGraphAdapter",
]
