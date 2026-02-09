"""
Phase 66 Stage 2: Knowledge Graph Storage

SQLite-based storage backend for property graph model.

AC_START: AC-PHASE66-S2-003
"""

import sqlite3
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from cortex_lens.knowledge_graph.graph_schema import Node, Edge, SCHEMA_SQL

logger = logging.getLogger(__name__)


class GraphStorage:
    """
    SQLite-based storage for knowledge graph.
    
    Implements property graph model with nodes and directed edges.
    Optimized for fast queries (<100ms for 2-hop traversals).
    
    Example:
        >>> storage = GraphStorage(Path("graph.db"))
        >>> storage.initialize_schema()
        >>> node_id = storage.insert_node("File", "test.py", {"lines": 50})
        >>> neighbors = storage.query_neighbors(node_id, "imports", depth=1)
    """
    
    def __init__(self, db_path: Path):
        """
        Initialize graph storage.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection (lazy initialization)."""
        if self.conn is None:
            self.conn = sqlite3.connect(str(self.db_path))
            self.conn.row_factory = sqlite3.Row  # Enable column access by name
            # Enable foreign keys
            self.conn.execute("PRAGMA foreign_keys = ON")
        return self.conn
    
    def initialize_schema(self) -> None:
        """
        Create database schema if not exists.
        
        Creates nodes and edges tables with indexes.
        """
        conn = self._get_connection()
        conn.executescript(SCHEMA_SQL)
        conn.commit()
        logger.info(f"Initialized knowledge graph schema at {self.db_path}")
    
    def insert_node(
        self,
        node_type: str,
        name: str,
        properties: Dict[str, Any]
    ) -> int:
        """
        Insert a new node into the graph.
        
        Args:
            node_type: Type of node (File, Class, Function, etc.)
            name: Node name
            properties: Additional metadata (JSON-serializable)
        
        Returns:
            Node ID
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        properties_json = json.dumps(properties)
        
        cursor.execute(
            """
            INSERT INTO nodes (node_type, name, properties)
            VALUES (?, ?, ?)
            """,
            (node_type, name, properties_json)
        )
        
        conn.commit()
        node_id = cursor.lastrowid
        
        if node_id is None:
            raise RuntimeError("Failed to get node ID after insertion")
        
        logger.debug(f"Inserted node: id={node_id}, type={node_type}, name={name}")
        return node_id
    
    def insert_edge(
        self,
        source_id: int,
        target_id: int,
        edge_type: str,
        properties: Dict[str, Any]
    ) -> int:
        """
        Insert a new edge between nodes.
        
        Args:
            source_id: Source node ID
            target_id: Target node ID
            edge_type: Type of relationship (imports, calls, etc.)
            properties: Additional metadata (JSON-serializable)
        
        Returns:
            Edge ID
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        properties_json = json.dumps(properties)
        
        cursor.execute(
            """
            INSERT INTO edges (source_id, target_id, edge_type, properties)
            VALUES (?, ?, ?, ?)
            """,
            (source_id, target_id, edge_type, properties_json)
        )
        
        conn.commit()
        edge_id = cursor.lastrowid
        
        if edge_id is None:
            raise RuntimeError("Failed to get edge ID after insertion")
        
        logger.debug(f"Inserted edge: id={edge_id}, {source_id} → {target_id} ({edge_type})")
        return edge_id
    
    def get_node(self, node_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve node by ID.
        
        Args:
            node_id: Node ID to retrieve
        
        Returns:
            Node dictionary or None if not found
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            SELECT id, node_type, name, properties
            FROM nodes
            WHERE id = ?
            """,
            (node_id,)
        )
        
        row = cursor.fetchone()
        if row is None:
            return None
        
        return {
            "id": row[0],
            "node_type": row[1],
            "name": row[2],
            "properties": json.loads(row[3]) if row[3] else {}
        }
    
    def get_edge(self, edge_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve edge by ID.
        
        Args:
            edge_id: Edge ID to retrieve
        
        Returns:
            Edge dictionary or None if not found
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            SELECT id, source_id, target_id, edge_type, properties
            FROM edges
            WHERE id = ?
            """,
            (edge_id,)
        )
        
        row = cursor.fetchone()
        if row is None:
            return None
        
        return {
            "id": row[0],
            "source_id": row[1],
            "target_id": row[2],
            "edge_type": row[3],
            "properties": json.loads(row[4]) if row[4] else {}
        }
    
    def update_node(self, node_id: int, properties: Dict[str, Any]) -> bool:
        """
        Update node properties.
        
        Args:
            node_id: Node ID to update
            properties: New properties (replaces existing)
        
        Returns:
            True if updated, False if node not found
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        properties_json = json.dumps(properties)
        
        cursor.execute(
            """
            UPDATE nodes
            SET properties = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (properties_json, node_id)
        )
        
        conn.commit()
        updated = cursor.rowcount > 0
        
        if updated:
            logger.debug(f"Updated node: id={node_id}")
        
        return updated
    
    def delete_node(self, node_id: int) -> bool:
        """
        Delete node (cascades to edges).
        
        Args:
            node_id: Node ID to delete
        
        Returns:
            True if deleted, False if node not found
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM nodes WHERE id = ?", (node_id,))
        
        conn.commit()
        deleted = cursor.rowcount > 0
        
        if deleted:
            logger.debug(f"Deleted node: id={node_id}")
        
        return deleted
    
    def query_neighbors(
        self,
        node_id: int,
        edge_type: Optional[str] = None,
        depth: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Query neighbors of a node up to specified depth.
        
        Args:
            node_id: Starting node ID
            edge_type: Filter by edge type (None = all types)
            depth: Maximum traversal depth (1 = direct neighbors)
        
        Returns:
            List of neighbor nodes (includes transitive neighbors up to depth)
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        visited = set()
        neighbors = []
        current_level = [node_id]
        
        for _ in range(depth):
            next_level = []
            
            for current_id in current_level:
                if current_id in visited:
                    continue
                visited.add(current_id)
                
                # Query outgoing edges
                if edge_type:
                    cursor.execute(
                        """
                        SELECT n.id, n.node_type, n.name, n.properties
                        FROM edges e
                        JOIN nodes n ON e.target_id = n.id
                        WHERE e.source_id = ? AND e.edge_type = ?
                        """,
                        (current_id, edge_type)
                    )
                else:
                    cursor.execute(
                        """
                        SELECT n.id, n.node_type, n.name, n.properties
                        FROM edges e
                        JOIN nodes n ON e.target_id = n.id
                        WHERE e.source_id = ?
                        """,
                        (current_id,)
                    )
                
                for row in cursor.fetchall():
                    neighbor_id = row[0]
                    if neighbor_id not in visited and neighbor_id != node_id:
                        neighbors.append({
                            "id": neighbor_id,
                            "node_type": row[1],
                            "name": row[2],
                            "properties": json.loads(row[3]) if row[3] else {}
                        })
                        next_level.append(neighbor_id)
            
            current_level = next_level
            if not current_level:
                break
        
        return neighbors
    
    def query_nodes_by_type(self, node_type: str) -> List[Dict[str, Any]]:
        """
        Query all nodes of a specific type.
        
        Args:
            node_type: Node type to filter by
        
        Returns:
            List of nodes matching type
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            SELECT id, node_type, name, properties
            FROM nodes
            WHERE node_type = ?
            """,
            (node_type,)
        )
        
        nodes = []
        for row in cursor.fetchall():
            nodes.append({
                "id": row[0],
                "node_type": row[1],
                "name": row[2],
                "properties": json.loads(row[3]) if row[3] else {}
            })
        
        return nodes
    
    def bulk_insert_nodes(
        self,
        nodes_data: List[Tuple[str, str, Dict[str, Any]]]
    ) -> List[int]:
        """
        Bulk insert multiple nodes efficiently.
        
        Args:
            nodes_data: List of (node_type, name, properties) tuples
        
        Returns:
            List of inserted node IDs
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Prepare data with JSON-serialized properties
        prepared_data = [
            (node_type, name, json.dumps(properties))
            for node_type, name, properties in nodes_data
        ]
        
        cursor.executemany(
            """
            INSERT INTO nodes (node_type, name, properties)
            VALUES (?, ?, ?)
            """,
            prepared_data
        )
        
        conn.commit()
        
        # Get IDs of inserted nodes
        # SQLite's lastrowid only works reliably for single inserts, not executemany
        # Query to get the node IDs we just inserted
        cursor.execute(
            """
            SELECT id FROM nodes 
            WHERE node_type IN ({}) 
            AND name IN ({})
            ORDER BY id DESC
            LIMIT ?
            """.format(
                ",".join("?" * len(set(nt for nt, _, _ in nodes_data))),
                ",".join("?" * len(nodes_data))
            ),
            list(set(nt for nt, _, _ in nodes_data)) + [name for _, name, _ in nodes_data] + [len(nodes_data)]
        )
        
        rows = cursor.fetchall()
        node_ids = [row[0] for row in reversed(rows)]  # Reverse to maintain insertion order
        
        logger.debug(f"Bulk inserted {len(nodes_data)} nodes")
        return node_ids
    
    def export_to_json(self) -> str:
        """
        Export entire graph to JSON string.
        
        Returns:
            JSON string with nodes and edges
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Get all nodes
        cursor.execute("SELECT id, node_type, name, properties FROM nodes")
        nodes = []
        for row in cursor.fetchall():
            nodes.append({
                "id": row[0],
                "node_type": row[1],
                "name": row[2],
                "properties": json.loads(row[3]) if row[3] else {}
            })
        
        # Get all edges
        cursor.execute("SELECT id, source_id, target_id, edge_type, properties FROM edges")
        edges = []
        for row in cursor.fetchall():
            edges.append({
                "id": row[0],
                "source_id": row[1],
                "target_id": row[2],
                "edge_type": row[3],
                "properties": json.loads(row[4]) if row[4] else {}
            })
        
        graph = {
            "nodes": nodes,
            "edges": edges,
            "exported_at": datetime.utcnow().isoformat()
        }
        
        return json.dumps(graph, indent=2)
    
    def close(self) -> None:
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
            logger.debug("Closed database connection")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# AC_COMPLETE: AC-PHASE66-S2-003 ✅ GraphStorage implementation complete
