"""
Knowledge Graph Database Layer

SQLite-based graph database with JSON property storage.
Implements atomic transactions and validation gates for disaster prevention.
"""

import sqlite3
import json
import uuid
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path
from contextlib import contextmanager

from .schema import (
    NodeType,
    RelationshipType,
    NodeStatus,
    validate_node,
    validate_relationship
)


class GraphDatabase:
    """SQLite-based graph database with ACID guarantees"""
    
    def __init__(self, db_path: str):
        """
        Initialize graph database
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_schema()
    
    def _initialize_schema(self):
        """Create database schema if not exists"""
        with self.connection() as conn:
            cursor = conn.cursor()
            
            # Nodes table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS nodes (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    properties TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # Relationships table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS relationships (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    from_node_id TEXT NOT NULL,
                    to_node_id TEXT NOT NULL,
                    properties TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (from_node_id) REFERENCES nodes(id) ON DELETE CASCADE,
                    FOREIGN KEY (to_node_id) REFERENCES nodes(id) ON DELETE CASCADE
                )
            """)
            
            # Metadata table (for checksums, sync status)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # Indexes for fast queries
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_node_type ON nodes(type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_relationship_type ON relationships(type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_relationship_from ON relationships(from_node_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_relationship_to ON relationships(to_node_id)")
            
            conn.commit()
    
    @contextmanager
    def connection(self):
        """Context manager for database connections with automatic commit/rollback"""
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def create_node(
        self,
        node_type: NodeType,
        properties: Dict[str, Any],
        node_id: Optional[str] = None
    ) -> str:
        """
        Create a new node with validation
        
        Args:
            node_type: Type of node to create
            properties: Node properties
            node_id: Optional custom node ID (generates UUID if not provided)
            
        Returns:
            Node ID
            
        Raises:
            ValueError: If validation fails
        """
        # Validate properties
        is_valid, error = validate_node(node_type, properties)
        if not is_valid:
            raise ValueError(f"Node validation failed: {error}")
        
        node_id = node_id or str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO nodes (id, type, properties, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (node_id, node_type.value, json.dumps(properties), now, now)
            )
        
        return node_id
    
    def update_node(self, node_id: str, properties: Dict[str, Any]):
        """
        Update node properties with validation
        
        Args:
            node_id: Node ID to update
            properties: New properties (merges with existing)
            
        Raises:
            ValueError: If validation fails or node not found
        """
        with self.connection() as conn:
            cursor = conn.cursor()
            
            # Get current node
            cursor.execute("SELECT type, properties FROM nodes WHERE id = ?", (node_id,))
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Node not found: {node_id}")
            
            node_type = NodeType(row[0])
            current_props = json.loads(row[1])
            
            # Merge properties
            current_props.update(properties)
            
            # Validate merged properties
            is_valid, error = validate_node(node_type, current_props)
            if not is_valid:
                raise ValueError(f"Node validation failed: {error}")
            
            # Update
            now = datetime.utcnow().isoformat()
            cursor.execute(
                """
                UPDATE nodes
                SET properties = ?, updated_at = ?
                WHERE id = ?
                """,
                (json.dumps(current_props), now, node_id)
            )
    
    def delete_node(self, node_id: str):
        """Delete a node and all connected relationships"""
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM nodes WHERE id = ?", (node_id,))
    
    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Get node by ID"""
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT type, properties, created_at, updated_at FROM nodes WHERE id = ?",
                (node_id,)
            )
            row = cursor.fetchone()
            if not row:
                return None
            
            return {
                "id": node_id,
                "type": row[0],
                "properties": json.loads(row[1]),
                "created_at": row[2],
                "updated_at": row[3]
            }
    
    def find_nodes(
        self,
        node_type: Optional[NodeType] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Find nodes by type and property filters
        
        Args:
            node_type: Filter by node type
            filters: Property filters (key-value pairs)
            
        Returns:
            List of matching nodes
        """
        with self.connection() as conn:
            cursor = conn.cursor()
            
            query = "SELECT id, type, properties, created_at, updated_at FROM nodes"
            params = []
            
            if node_type:
                query += " WHERE type = ?"
                params.append(node_type.value)
            
            cursor.execute(query, params)
            nodes = []
            
            for row in cursor.fetchall():
                node = {
                    "id": row[0],
                    "type": row[1],
                    "properties": json.loads(row[2]),
                    "created_at": row[3],
                    "updated_at": row[4]
                }
                
                # Apply property filters
                if filters:
                    matches = all(
                        node["properties"].get(key) == value
                        for key, value in filters.items()
                    )
                    if not matches:
                        continue
                
                nodes.append(node)
            
            return nodes
    
    def create_relationship(
        self,
        relationship_type: RelationshipType,
        from_node_id: str,
        to_node_id: str,
        properties: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a relationship with validation
        
        Args:
            relationship_type: Type of relationship
            from_node_id: Source node ID
            to_node_id: Target node ID
            properties: Optional relationship properties
            
        Returns:
            Relationship ID
            
        Raises:
            ValueError: If validation fails or nodes not found
        """
        properties = properties or {}
        
        with self.connection() as conn:
            cursor = conn.cursor()
            
            # Get node types for validation
            cursor.execute("SELECT type FROM nodes WHERE id = ?", (from_node_id,))
            from_row = cursor.fetchone()
            if not from_row:
                raise ValueError(f"Source node not found: {from_node_id}")
            
            cursor.execute("SELECT type FROM nodes WHERE id = ?", (to_node_id,))
            to_row = cursor.fetchone()
            if not to_row:
                raise ValueError(f"Target node not found: {to_node_id}")
            
            from_node_type = NodeType(from_row[0])
            to_node_type = NodeType(to_row[0])
            
            # Validate relationship
            is_valid, error = validate_relationship(
                relationship_type, from_node_type, to_node_type, properties
            )
            if not is_valid:
                raise ValueError(f"Relationship validation failed: {error}")
            
            # Create relationship
            rel_id = str(uuid.uuid4())
            now = datetime.utcnow().isoformat()
            
            cursor.execute(
                """
                INSERT INTO relationships (id, type, from_node_id, to_node_id, properties, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (rel_id, relationship_type.value, from_node_id, to_node_id, json.dumps(properties), now)
            )
            
            return rel_id
    
    def find_relationships(
        self,
        from_node_id: Optional[str] = None,
        to_node_id: Optional[str] = None,
        relationship_type: Optional[RelationshipType] = None
    ) -> List[Dict[str, Any]]:
        """Find relationships by node IDs and/or type"""
        with self.connection() as conn:
            cursor = conn.cursor()
            
            query = """
                SELECT id, type, from_node_id, to_node_id, properties, created_at
                FROM relationships
                WHERE 1=1
            """
            params = []
            
            if from_node_id:
                query += " AND from_node_id = ?"
                params.append(from_node_id)
            
            if to_node_id:
                query += " AND to_node_id = ?"
                params.append(to_node_id)
            
            if relationship_type:
                query += " AND type = ?"
                params.append(relationship_type.value)
            
            cursor.execute(query, params)
            
            relationships = []
            for row in cursor.fetchall():
                relationships.append({
                    "id": row[0],
                    "type": row[1],
                    "from_node_id": row[2],
                    "to_node_id": row[3],
                    "properties": json.loads(row[4]),
                    "created_at": row[5]
                })
            
            return relationships
    
    def delete_relationship(self, relationship_id: str):
        """Delete a relationship"""
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM relationships WHERE id = ?", (relationship_id,))
    
    def get_metadata(self, key: str) -> Optional[str]:
        """Get metadata value"""
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM metadata WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row[0] if row else None
    
    def set_metadata(self, key: str, value: str):
        """Set metadata value"""
        with self.connection() as conn:
            cursor = conn.cursor()
            now = datetime.utcnow().isoformat()
            cursor.execute(
                """
                INSERT OR REPLACE INTO metadata (key, value, updated_at)
                VALUES (?, ?, ?)
                """,
                (key, value, now)
            )
    
    def clear_all(self):
        """Clear all nodes and relationships (for testing/bootstrap)"""
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM relationships")
            cursor.execute("DELETE FROM nodes")
            cursor.execute("DELETE FROM metadata")
