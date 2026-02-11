"""SQLite implementation of IGraphAdapter for fallback when KG unavailable.

SQLiteGraphAdapter provides a fallback implementation that stores graph data
in the governance SQLite database. Used when Neo4j/Neptune is unavailable or
disabled, ensuring CORTEX continues operating without KG backend.

Implements the same interface as Neo4j adapter, enabling transparent fallback.
"""

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

from cortex.brain.core.knowledge.graph.interface import (
    EntityNode,
    GraphQueryError,
    HealthStatus,
    IGraphAdapter,
    Relationship,
)
from cortex.brain.core.knowledge.graph.interface import (
    Path as GraphPath,
)


class SQLiteGraphAdapter(IGraphAdapter):
    """SQLite implementation of Knowledge Graph adapter.

    Stores graph data in SQLite with tables for entities and relationships.
    Provides non-breaking fallback when primary KG backend unavailable.

    Uses CORTEX governance database (cortex.governance.db).
    """

    def __init__(self, db_path: Optional[str] = None) -> None:
        """Initialize SQLite adapter.

        Args:
            db_path: Optional path to SQLite database file.
                    If not specified, uses :memory: for in-memory database.
                    For production, set to governance.db path.
        """
        if db_path is None:
            # Use in-memory database by default (for testing)
            db_path = ":memory:"

        self.db_path = db_path
        self._init_schema()

    def _init_schema(self) -> None:
        """Initialize database schema on first connection."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Create entities table if not exists
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS kg_entities (
                        id TEXT PRIMARY KEY,
                        type TEXT NOT NULL,
                        properties TEXT NOT NULL
                    )
                    """
                )

                # Create relationships table if not exists
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS kg_relationships (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        source_id TEXT NOT NULL,
                        rel_type TEXT NOT NULL,
                        target_id TEXT NOT NULL,
                        properties TEXT NOT NULL,
                        FOREIGN KEY (source_id) REFERENCES kg_entities(id),
                        FOREIGN KEY (target_id) REFERENCES kg_entities(id),
                        UNIQUE(source_id, rel_type, target_id)
                    )
                    """
                )

                # Create indexes for query performance
                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS idx_entities_type ON kg_entities(type)"
                )
                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS idx_relationships_source ON kg_relationships(source_id)"
                )
                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS idx_relationships_target ON kg_relationships(target_id)"
                )

                conn.commit()
        except sqlite3.Error as e:
            raise GraphQueryError(f"Failed to initialize SQLite schema: {e}")

    def create_entity(
        self, entity_id: str, entity_type: str, properties: Dict[str, Any]
    ) -> EntityNode:
        """Create an entity in SQLite.

        Args:
            entity_id: Unique identifier for the entity
            entity_type: Type of entity
            properties: Key-value properties

        Returns:
            EntityNode: Created entity

        Raises:
            GraphQueryError: If entity_id already exists
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                properties_json = json.dumps(properties)

                cursor.execute(
                    """
                    INSERT INTO kg_entities (id, type, properties)
                    VALUES (?, ?, ?)
                    """,
                    (entity_id, entity_type, properties_json),
                )

                conn.commit()
                return EntityNode(id=entity_id, type=entity_type, properties=properties)

        except sqlite3.IntegrityError:
            raise GraphQueryError(
                f"Entity with id '{entity_id}' already exists (duplicate)"
            )
        except sqlite3.Error as e:
            raise GraphQueryError(f"Failed to create entity: {e}")

    def create_relationship(
        self,
        source_id: str,
        rel_type: str,
        target_id: str,
        properties: Optional[Dict[str, Any]] = None,
    ) -> Relationship:
        """Create a relationship in SQLite.

        Args:
            source_id: ID of source entity
            rel_type: Type of relationship
            target_id: ID of target entity
            properties: Optional relationship properties

        Returns:
            Relationship: Created relationship

        Raises:
            GraphQueryError: If source/target don't exist
        """
        properties = properties or {}

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Verify source and target exist
                cursor.execute("SELECT id FROM kg_entities WHERE id = ?", (source_id,))
                if not cursor.fetchone():
                    raise GraphQueryError(f"Source entity '{source_id}' not found")

                cursor.execute("SELECT id FROM kg_entities WHERE id = ?", (target_id,))
                if not cursor.fetchone():
                    raise GraphQueryError(f"Target entity '{target_id}' not found")

                properties_json = json.dumps(properties)

                cursor.execute(
                    """
                    INSERT INTO kg_relationships (source_id, rel_type, target_id, properties)
                    VALUES (?, ?, ?, ?)
                    """,
                    (source_id, rel_type, target_id, properties_json),
                )

                conn.commit()

                return Relationship(
                    source_id=source_id,
                    rel_type=rel_type,
                    target_id=target_id,
                    properties=properties,
                )

        except sqlite3.IntegrityError:
            raise GraphQueryError(
                f"Relationship already exists: {source_id} -[{rel_type}]-> {target_id}"
            )
        except sqlite3.Error as e:
            raise GraphQueryError(f"Failed to create relationship: {e}")

    def query_entities(
        self,
        entity_type: str,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[EntityNode]:
        """Query entities by type and optional filters.

        Args:
            entity_type: Type of entities to query
            filters: Optional property filters

        Returns:
            List[EntityNode]: Matching entities

        Raises:
            GraphQueryError: On query failure
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    "SELECT id, type, properties FROM kg_entities WHERE type = ?",
                    (entity_type,),
                )

                results = []
                for row in cursor.fetchall():
                    entity_id, entity_type, properties_json = row
                    properties = json.loads(properties_json)

                    if filters:
                        if not all(
                            properties.get(k) == v for k, v in filters.items()
                        ):
                            continue

                    results.append(
                        EntityNode(id=entity_id, type=entity_type, properties=properties)
                    )

                return results

        except sqlite3.Error as e:
            raise GraphQueryError(f"Failed to query entities: {e}")

    def query_paths(
        self,
        source_id: str,
        rel_types: Optional[List[str]] = None,
        max_hops: int = 1,
    ) -> List[GraphPath]:
        """Query paths from source entity.

        Args:
            source_id: Starting entity ID
            rel_types: Optional relationship types to filter
            max_hops: Maximum hops (1-3)

        Returns:
            List[GraphPath]: Paths from source

        Raises:
            GraphQueryError: If source not found
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Verify source exists
                cursor.execute("SELECT id FROM kg_entities WHERE id = ?", (source_id,))
                if not cursor.fetchone():
                    raise GraphQueryError(f"Source entity '{source_id}' not found")

                # BFS traversal
                paths: List[GraphPath] = []
                visited: Dict[str, int] = {source_id: 0}
                queue: List[tuple[str, List[str], List[str]]] = [
                    (source_id, [source_id], [])
                ]

                while queue:
                    current_id, node_path, rel_path = queue.pop(0)
                    current_depth = len(node_path) - 1

                    if current_depth < max_hops:
                        # Find outgoing relationships
                        rel_query = """
                            SELECT rel_type, target_id FROM kg_relationships
                            WHERE source_id = ?
                        """
                        rel_params = [current_id]

                        if rel_types:
                            placeholders = ",".join("?" * len(rel_types))
                            rel_query += f" AND rel_type IN ({placeholders})"
                            rel_params.extend(rel_types)

                        cursor.execute(rel_query, rel_params)

                        for rel_type, target_id in cursor.fetchall():
                            if target_id not in visited or visited[target_id] > current_depth + 1:
                                visited[target_id] = current_depth + 1
                                new_node_path = node_path + [target_id]
                                new_rel_path = rel_path + [rel_type]
                                queue.append((target_id, new_node_path, new_rel_path))

                                paths.append(
                                    GraphPath(
                                        nodes=new_node_path,
                                        relationships=new_rel_path,
                                        length=len(new_node_path) - 1,
                                    )
                                )

                return paths

        except sqlite3.Error as e:
            raise GraphQueryError(f"Failed to query paths: {e}")

    def delete_entity(self, entity_id: str) -> bool:
        """Delete an entity and its relationships.

        Args:
            entity_id: ID of entity to delete

        Returns:
            bool: True if deleted, False if not found

        Raises:
            GraphQueryError: On deletion failure
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Check if entity exists
                cursor.execute("SELECT id FROM kg_entities WHERE id = ?", (entity_id,))
                if not cursor.fetchone():
                    return False

                # Delete entity
                cursor.execute("DELETE FROM kg_entities WHERE id = ?", (entity_id,))

                # Delete relationships
                cursor.execute(
                    "DELETE FROM kg_relationships WHERE source_id = ? OR target_id = ?",
                    (entity_id, entity_id),
                )

                conn.commit()
                return True

        except sqlite3.Error as e:
            raise GraphQueryError(f"Failed to delete entity: {e}")

    def health_check(self, timeout_seconds: float = 5.0) -> HealthStatus:
        """Check SQLite adapter health.

        Args:
            timeout_seconds: Maximum time to wait (not used in SQLite)

        Returns:
            HealthStatus: HEALTHY if database accessible
        """
        try:
            with sqlite3.connect(self.db_path, timeout=timeout_seconds) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                return HealthStatus.HEALTHY
        except (sqlite3.Error, Exception):
            return HealthStatus.UNHEALTHY
