"""Query adapter interface for Knowledge Graph queries.

Abstract interface for semantic queries, graph traversal, and rule inference
with fallback mechanisms for non-blocking KG operations.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class QueryNode:
    """Node in graph query result.

    Attributes:
        node_id: Unique node identifier
        entity_type: Type of entity (Service, API, etc.)
        properties: Node properties
    """
    node_id: str
    entity_type: str
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QueryEdge:
    """Edge in graph query result.

    Attributes:
        source_id: Source node ID
        target_id: Target node ID
        relationship_type: Type of relationship
        properties: Edge properties
    """
    source_id: str
    target_id: str
    relationship_type: str
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QueryPath:
    """Path through knowledge graph.

    Attributes:
        nodes: List of nodes in path
        edges: List of edges connecting nodes
    """
    nodes: List[QueryNode]
    edges: List[QueryEdge] = field(default_factory=list)


@dataclass
class QueryResult:
    """Result of a KG query.

    Attributes:
        status: Query status (SUCCESS, FAILED, PARSE_ERROR)
        entities: List of entity nodes returned
        relationships: List of relationship edges returned
        paths: List of paths if path query
        entity_count: Total entity count
        error_message: Error message if failed
        execution_time_ms: Query execution time
    """
    status: str
    entities: List[QueryNode] = field(default_factory=list)
    relationships: List[QueryEdge] = field(default_factory=list)
    paths: List[QueryPath] = field(default_factory=list)
    entity_count: int = 0
    error_message: Optional[str] = None
    execution_time_ms: float = 0.0


class IQueryAdapter(ABC):
    """Abstract interface for Knowledge Graph query operations.

    Supports semantic queries, graph traversal, relationship analysis,
    and rule inference with fallback mechanisms.
    """

    @abstractmethod
    def query(self, query_string: str) -> QueryResult:
        """Execute semantic query on KG.

        Args:
            query_string: Semantic query (e.g., "SELECT * FROM Service WHERE tier=1")

        Returns:
            QueryResult: Query results

        Raises:
            ValueError: If query format is invalid
        """
        pass

    @abstractmethod
    def query_paths(
        self, source_id: str, target_id: str, max_hops: int = 3
    ) -> QueryResult:
        """Query paths between two entities.

        Args:
            source_id: Start entity ID
            target_id: End entity ID
            max_hops: Maximum hops (default 3)

        Returns:
            QueryResult: Paths found
        """
        pass

    @abstractmethod
    def traverse_from(
        self, entity_id: str, max_hops: int = 2, rel_types: Optional[List[str]] = None
    ) -> List[QueryPath]:
        """Traverse graph from starting entity.

        Args:
            entity_id: Start entity ID
            max_hops: Maximum traversal depth
            rel_types: Relationship types to follow (None = all)

        Returns:
            List[QueryPath]: Discovered paths
        """
        pass

    @abstractmethod
    def infer_dependencies(self, entity_id: str) -> List[Dict[str, Any]]:
        """Infer entity dependencies.

        Args:
            entity_id: Entity to analyze

        Returns:
            List[Dict]: Dependency relationships
        """
        pass

    @abstractmethod
    def infer_relationships(self, entity_id: str) -> List[Dict[str, Any]]:
        """Infer relationships for entity.

        Args:
            entity_id: Entity to analyze

        Returns:
            List[Dict]: Inferred relationships
        """
        pass

    @abstractmethod
    def infer_impact(self, entity_id: str) -> List[Dict[str, Any]]:
        """Infer impact of changes to entity.

        Args:
            entity_id: Entity to analyze

        Returns:
            List[Dict]: Impacted entities
        """
        pass

    @abstractmethod
    def health_check(self, timeout: int = 5) -> Dict[str, Any]:
        """Check query layer health.

        Args:
            timeout: Health check timeout in seconds

        Returns:
            Dict: Health status
        """
        pass
