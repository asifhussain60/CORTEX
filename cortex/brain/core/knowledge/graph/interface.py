"""Abstract graph adapter interface for Knowledge Graph backend.

Defines the IGraphAdapter contract that all KG implementations must follow.
This enables multiple backend implementations (Neo4j, Neptune, SQLite) while
maintaining a consistent interface throughout CORTEX.

Design Principles:
  - Abstract interface allows mock implementation for local testing
  - Multiple backends can be swapped without code changes
  - Timeout/error handling ensures non-breaking fallback semantics
  - Type hints and docstrings enforce governance compliance (CORE-011, CORE-012)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from cortex.api.health_endpoints import HealthStatus


class GraphQueryError(Exception):
    """Exception raised on graph query or constraint violation.

    Raised when:
      - Entity or relationship creation violates schema constraints
      - Invalid entity type or relationship type specified
      - Query execution fails in adapter backend
      - Constraint violations occur (duplicate IDs, cardinality)
    """

    pass


@dataclass
class EntityNode:
    """Represents an entity node in the knowledge graph.

    Attributes:
        id: Unique identifier for entity
        type: Entity type (Entity, Rule, Service, API, Domain)
        properties: Key-value properties stored with entity
    """

    id: str
    type: str
    properties: Dict[str, Any]


@dataclass
class Relationship:
    """Represents a relationship between two entities.

    Attributes:
        source_id: ID of source entity
        rel_type: Relationship type (CALLS, DEPENDS_ON, IMPLEMENTS, HAS_RULE, BELONGS_TO)
        target_id: ID of target entity
        properties: Key-value properties stored with relationship
    """

    source_id: str
    rel_type: str
    target_id: str
    properties: Dict[str, Any]


@dataclass
class Path:
    """Represents a traversal path through relationships.

    Attributes:
        nodes: List of EntityNode IDs in the path
        relationships: List of Relationship types traversed
        length: Number of hops in the path
    """

    nodes: List[str]
    relationships: List[str]
    length: int


class IGraphAdapter(ABC):
    """Abstract interface for Knowledge Graph backends.

    Implementations must support entity and relationship management,
    querying with filters and path traversal up to 3 hops, and
    health checking with explicit timeout handling.

    All implementations must comply with CORE-011 (type hints),
    CORE-012 (docstrings), and CORE-013 (exception handling).
    """

    @abstractmethod
    def create_entity(
        self, entity_id: str, entity_type: str, properties: Dict[str, Any]
    ) -> EntityNode:
        """Create an entity in the graph.

        Args:
            entity_id: Unique identifier for the entity
            entity_type: Type of entity (Entity, Rule, Service, API, Domain)
            properties: Key-value properties to store with entity

        Returns:
            EntityNode: Created entity with populated id, type, properties

        Raises:
            GraphQueryError: If entity_id already exists or type is invalid
        """

        pass

    @abstractmethod
    def create_relationship(
        self,
        source_id: str,
        rel_type: str,
        target_id: str,
        properties: Optional[Dict[str, Any]] = None,
    ) -> Relationship:
        """Create a relationship between two entities.

        Args:
            source_id: ID of source entity
            rel_type: Type of relationship (CALLS, DEPENDS_ON, IMPLEMENTS, HAS_RULE, BELONGS_TO)
            target_id: ID of target entity
            properties: Optional key-value properties for relationship

        Returns:
            Relationship: Created relationship with populated fields

        Raises:
            GraphQueryError: If source or target entity doesn't exist,
                           or relationship type is invalid
        """

        pass

    @abstractmethod
    def query_entities(
        self,
        entity_type: str,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[EntityNode]:
        """Query entities by type and optional filters.

        Args:
            entity_type: Type of entities to query
            filters: Optional property filters (AND semantics)

        Returns:
            List[EntityNode]: Matching entities (empty list if none found)

        Raises:
            GraphQueryError: If entity_type is invalid
        """

        pass

    @abstractmethod
    def query_paths(
        self,
        source_id: str,
        rel_types: Optional[List[str]] = None,
        max_hops: int = 1,
    ) -> List[Path]:
        """Query paths from source entity through relationships.

        Args:
            source_id: Starting entity ID
            rel_types: Optional relationship types to follow (any if None)
            max_hops: Maximum hops to traverse (1-3, default 1)

        Returns:
            List[Path]: Paths from source up to max_hops away

        Raises:
            GraphQueryError: If source_id doesn't exist or max_hops invalid
        """

        pass

    @abstractmethod
    def delete_entity(self, entity_id: str) -> bool:
        """Delete an entity and its relationships.

        Args:
            entity_id: ID of entity to delete

        Returns:
            bool: True if entity was deleted, False if not found

        Raises:
            GraphQueryError: On deletion failure
        """

        pass

    @abstractmethod
    def health_check(self, timeout_seconds: float = 5.0) -> HealthStatus:
        """Check health and responsiveness of adapter.

        Args:
            timeout_seconds: Maximum time to wait for response (default 5.0s)

        Returns:
            HealthStatus: HEALTHY, DEGRADED, or UNHEALTHY

        Note:
            Must not raise exceptions; returns UNHEALTHY on timeout/error
        """

        pass
