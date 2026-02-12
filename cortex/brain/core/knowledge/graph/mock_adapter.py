"""Mock implementation of IGraphAdapter for testing without external dependencies.

MockGraphAdapter provides an in-memory implementation of the graph adapter
interface using dictionaries. Useful for local development and testing
without requiring Neo4j, Neptune, or any external KG infrastructure.

All methods follow the same semantics as production implementations but
operate on in-memory data structures.
"""

import time
from typing import Any, Dict, List, Optional

from cortex.brain.core.knowledge.graph.interface import (
    EntityNode,
    GraphQueryError,
    HealthStatus,
    IGraphAdapter,
    Path,
    Relationship,
)


class MockGraphAdapter(IGraphAdapter):
    """In-memory mock implementation of Knowledge Graph adapter.

    Stores entities and relationships in memory using dictionaries.
    Supports all IGraphAdapter operations without external dependencies.

    Thread-safe for single-threaded test scenarios. For multi-threaded
    testing, use production adapters or add locking.
    """

    def __init__(self) -> None:
        """Initialize mock graph adapter with empty storage."""
        self._entities: Dict[str, EntityNode] = {}
        self._relationships: List[Relationship] = []
        self._is_healthy: bool = True

    def create_entity(
        self, entity_id: str, entity_type: str, properties: Dict[str, Any]
    ) -> EntityNode:
        """Create an entity in mock graph storage.

        Args:
            entity_id: Unique identifier for the entity
            entity_type: Type of entity (Entity, Rule, Service, API, Domain)
            properties: Key-value properties to store with entity

        Returns:
            EntityNode: Created entity with populated fields

        Raises:
            GraphQueryError: If entity_id already exists (constraint violation)
        """
        if entity_id in self._entities:
            raise GraphQueryError(
                f"Entity with id '{entity_id}' already exists (duplicate)"
            )

        if not entity_type or not isinstance(entity_type, str):
            raise GraphQueryError(f"Invalid entity type: {entity_type}")

        entity = EntityNode(id=entity_id, type=entity_type, properties=properties)
        self._entities[entity_id] = entity
        return entity

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
            rel_type: Type of relationship
            target_id: ID of target entity
            properties: Optional relationship properties

        Returns:
            Relationship: Created relationship

        Raises:
            GraphQueryError: If source or target entity doesn't exist
        """
        if source_id not in self._entities:
            raise GraphQueryError(f"Source entity '{source_id}' not found")

        if target_id not in self._entities:
            raise GraphQueryError(f"Target entity '{target_id}' not found")

        if not rel_type or not isinstance(rel_type, str):
            raise GraphQueryError(f"Invalid relationship type: {rel_type}")

        relationship = Relationship(
            source_id=source_id,
            rel_type=rel_type,
            target_id=target_id,
            properties=properties or {},
        )
        self._relationships.append(relationship)
        return relationship

    def query_entities(
        self,
        entity_type: str,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[EntityNode]:
        """Query entities by type and optional property filters.

        Args:
            entity_type: Type of entities to query
            filters: Optional property filters (AND semantics)

        Returns:
            List[EntityNode]: Matching entities

        Raises:
            GraphQueryError: If entity_type is invalid
        """
        if not entity_type or not isinstance(entity_type, str):
            raise GraphQueryError(f"Invalid entity type: {entity_type}")

        results = [e for e in self._entities.values() if e.type == entity_type]

        if filters:
            results = [
                e
                for e in results
                if all(e.properties.get(k) == v for k, v in filters.items())
            ]

        return results

    def query_paths(
        self,
        source_id: str,
        rel_types: Optional[List[str]] = None,
        max_hops: int = 1,
    ) -> List[Path]:
        """Query paths from source entity through relationships.

        Args:
            source_id: Starting entity ID
            rel_types: Optional relationship types to filter
            max_hops: Maximum hops (1-3)

        Returns:
            List[Path]: Paths from source entity

        Raises:
            GraphQueryError: If source_id doesn't exist
        """
        if source_id not in self._entities:
            raise GraphQueryError(f"Source entity '{source_id}' not found")

        if max_hops < 1 or max_hops > 3:
            raise GraphQueryError(f"max_hops must be 1-3, got {max_hops}")

        paths: List[Path] = []

        # BFS traversal up to max_hops
        visited: Dict[str, int] = {source_id: 0}
        queue: List[tuple[str, List[str], List[str]]] = [(source_id, [source_id], [])]

        while queue:
            current_id, node_path, rel_path = queue.pop(0)
            current_depth = len(node_path) - 1

            if current_depth < max_hops:
                for rel in self._relationships:
                    if rel.source_id == current_id:
                        if rel_types is None or rel.rel_type in rel_types:
                            target_id = rel.target_id
                            if target_id not in visited or visited[target_id] > current_depth + 1:
                                visited[target_id] = current_depth + 1
                                new_node_path = node_path + [target_id]
                                new_rel_path = rel_path + [rel.rel_type]
                                queue.append((target_id, new_node_path, new_rel_path))

                                # Add complete path
                                paths.append(
                                    Path(
                                        nodes=new_node_path,
                                        relationships=new_rel_path,
                                        length=len(new_node_path) - 1,
                                    )
                                )

        return paths

    def delete_entity(self, entity_id: str) -> bool:
        """Delete an entity and its relationships.

        Args:
            entity_id: ID of entity to delete

        Returns:
            bool: True if deleted, False if not found

        Raises:
            GraphQueryError: On deletion failure
        """
        if entity_id not in self._entities:
            return False

        del self._entities[entity_id]

        # Remove relationships involving this entity
        self._relationships = [
            r for r in self._relationships
            if r.source_id != entity_id and r.target_id != entity_id
        ]

        return True

    def health_check(self, timeout_seconds: float = 5.0) -> HealthStatus:
        """Check health of mock adapter.

        Args:
            timeout_seconds: Maximum time to wait (not used in mock)

        Returns:
            HealthStatus: HEALTHY if operational
        """
        if self._is_healthy:
            return HealthStatus.HEALTHY
        return HealthStatus.UNHEALTHY

    def set_health(self, is_healthy: bool) -> None:
        """Set health status for testing (mock-specific method).

        Args:
            is_healthy: True for HEALTHY, False for UNHEALTHY
        """
        self._is_healthy = is_healthy

    def clear(self) -> None:
        """Clear all entities and relationships (mock-specific method)."""
        self._entities.clear()
        self._relationships.clear()
